import React, { useCallback, useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  useColorScheme,
  Platform,
} from "react-native";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSequence,
  withSpring,
  withTiming,
} from "react-native-reanimated";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import Colors from "@/constants/colors";
import { BLOCKS, PHRASES, Phrase, Pos, phraseScript } from "@/lib/phrases";
import { speakArabic, speakAuto, stopSpeaking, useSpeechMuted } from "@/lib/speech";
import {
  BuilderStats,
  checkAndRecordStudyDay,
  getBuilderStats,
  recordBuilderResult,
} from "@/lib/progress-storage";

// ---------------------------------------------------------------------------------------------
// Word types: every block is colour-coded AND labelled, so type never depends on colour alone.
// ---------------------------------------------------------------------------------------------
const POS_META: Record<
  Pos,
  { label: string; name: string; light: string; dark: string; what: string; example: string }
> = {
  noun: {
    label: "NOUN", name: "Noun", light: "#2457B8", dark: "#8DB4FF",
    what: "A person, place or thing. Masculine (m) or feminine (f). al- means “the”.",
    example: "bayt = house · al-bayt = the house",
  },
  verb: {
    label: "VERB", name: "Verb", light: "#B8401F", dark: "#FF9C7A",
    what: "An action. The ending / prefix shows who does it and when.",
    example: "aktubu = I write · kataba = he wrote",
  },
  adjective: {
    label: "ADJ", name: "Adjective", light: "#1F7A4A", dark: "#6FD6A0",
    what: "Describes a noun. Comes AFTER it and matches its gender and al-.",
    example: "kabiir (m) · kabiira (f) = big",
  },
  adverb: {
    label: "ADV", name: "Adverb", light: "#7A3FB0", dark: "#CBA3F2",
    what: "Says how, when or how much.",
    example: "ghadan = tomorrow · jiddan = very",
  },
  preposition: {
    label: "PREP", name: "Preposition", light: "#9A6A12", dark: "#E8B85A",
    what: "A little word that links to a noun, placed BEFORE it.",
    example: "fii = in · ilaa = to · 'alaa = on",
  },
  pronoun: {
    label: "PRON", name: "Pronoun / this", light: "#0F7C8C", dark: "#6ED3E0",
    what: "Stands in for a noun (I, you, he …) or points (this).",
    example: "ana = I · huwa = he · hadha = this",
  },
  conjunction: {
    label: "CONJ", name: "Conjunction", light: "#B03470", dark: "#F29CC4",
    what: "Joins words or phrases.",
    example: "wa = and",
  },
  particle: {
    label: "PART", name: "Particle", light: "#4A5878", dark: "#AEB9D2",
    what: "Small function words: question markers, negation.",
    example: "hal = (yes/no question) · laa = not · ayna = where",
  },
};
const POS_ORDER: Pos[] = ["noun", "verb", "adjective", "adverb", "preposition", "pronoun", "conjunction", "particle"];

type Level = 0 | 1 | 2 | 3; // 0 = mix of everything
const LEVELS: { key: Level; label: string; about: string }[] = [
  { key: 1, label: "Easy", about: "Two-block phrases. No extra blocks." },
  { key: 2, label: "Medium", about: "2–4 blocks, plus 1 decoy block you must NOT use." },
  { key: 3, label: "Hard", about: "3–5 blocks, plus 2 decoys. Watch the gender of verbs and adjectives!" },
  { key: 0, label: "Mix", about: "Everything, in random order." },
];

// ---------------------------------------------------------------------------------------------
// Round logic
// ---------------------------------------------------------------------------------------------
interface Tile {
  uid: number;
  id: string;
}

function shuffle<T>(arr: T[]): T[] {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// A shuffled "deck" so a sentence is not repeated until the whole level has been seen.
const deck: { level: number; order: Phrase[]; idx: number } = { level: -1, order: [], idx: 0 };

function nextPhrase(level: Level): Phrase {
  if (deck.level !== level || deck.idx >= deck.order.length) {
    deck.level = level;
    deck.order = shuffle(level === 0 ? PHRASES : PHRASES.filter((p) => p.level === level));
    deck.idx = 0;
  }
  return deck.order[deck.idx++];
}

function deal(phrase: Phrase): Tile[] {
  const ids = [...phrase.tokens, ...phrase.extras.slice(0, phrase.level - 1)];
  const tiles = ids.map((id, i) => ({ uid: i + 1, id }));
  let out = shuffle(tiles);
  for (let k = 0; k < 6; k++) {
    const inOrder = out.slice(0, phrase.tokens.length).every((t, i) => t.id === phrase.tokens[i]);
    if (!inOrder) break;
    out = shuffle(tiles);
  }
  return out;
}

function newRound(level: Level) {
  const phrase = nextPhrase(level);
  return { phrase, tiles: deal(phrase) };
}

const candidates = (p: Phrase): string[][] => [p.tokens, ...(p.accept ?? [])];
const matchCount = (seq: (string | null)[], cand: string[]) =>
  seq.reduce<number>((n, id, i) => n + (id === cand[i] ? 1 : 0), 0);

// ---------------------------------------------------------------------------------------------
// Tile (one word block)
// ---------------------------------------------------------------------------------------------
type TileState = "normal" | "ok" | "bad";

function BlockTile({
  id,
  state = "normal",
  onPress,
  hint,
}: {
  id: string;
  state?: TileState;
  onPress?: () => void;
  hint?: string;
}) {
  const isDark = useColorScheme() === "dark";
  const theme = isDark ? Colors.dark : Colors.light;
  const b = BLOCKS[id];
  const meta = POS_META[b.pos];
  const posColor = isDark ? meta.dark : meta.light;
  const border =
    state === "ok" ? Colors.palette.success : state === "bad" ? Colors.palette.error : posColor;
  return (
    <TouchableOpacity
      activeOpacity={0.75}
      onPress={onPress}
      disabled={!onPress}
      accessibilityLabel={`${meta.name}: ${b.latin}, ${b.en}${b.tag ? ", " + b.tag : ""}${hint ? ". " + hint : ""}`}
      style={[
        styles.tile,
        { borderColor: border, backgroundColor: posColor + "1F", borderWidth: state === "normal" ? 1.5 : 2.5 },
      ]}
    >
      <View style={styles.tileHead}>
        <Text style={[styles.tilePos, { color: posColor }]}>{meta.label}</Text>
        {b.tag ? <Text style={[styles.tileTag, { color: theme.textSecondary }]}> · {b.tag}</Text> : null}
      </View>
      <Text style={[styles.tileLatin, { color: theme.text }]}>{b.latin}</Text>
      <Text style={[styles.tileEn, { color: theme.textSecondary }]}>{b.en}</Text>
    </TouchableOpacity>
  );
}

// ---------------------------------------------------------------------------------------------
// Screen
// ---------------------------------------------------------------------------------------------
export default function BuildScreen() {
  const isDark = useColorScheme() === "dark";
  const theme = isDark ? Colors.dark : Colors.light;
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === "web" ? 67 : insets.top;
  const bottomPad = Platform.OS === "web" ? 34 : insets.bottom;

  const [level, setLevel] = useState<Level>(1);
  const [round, setRound] = useState(() => newRound(1));
  const [slots, setSlots] = useState<(number | null)[]>(() => Array(round.phrase.tokens.length).fill(null));
  const [active, setActive] = useState<number | null>(null);
  const [state, setState] = useState<"playing" | "correct" | "revealed">("playing");
  const [marks, setMarks] = useState<(TileState)[]>([]);
  const [feedback, setFeedback] = useState<{ ok: number; total: number } | null>(null);
  const [attempts, setAttempts] = useState(0);
  const [hinted, setHinted] = useState(false);
  const [stats, setStats] = useState<BuilderStats>({ solved: 0, firstTry: 0, total: 0, streak: 0, best: 0 });
  const [legendOpen, setLegendOpen] = useState(false);
  const [muted, toggleMuted] = useSpeechMuted();

  const shake = useSharedValue(0);
  const bounce = useSharedValue(1);
  const shakeStyle = useAnimatedStyle(() => ({ transform: [{ translateX: shake.value }] }));
  const bounceStyle = useAnimatedStyle(() => ({ transform: [{ scale: bounce.value }] }));

  useEffect(() => {
    getBuilderStats().then(setStats);
  }, []);

  useFocusEffect(
    useCallback(() => {
      checkAndRecordStudyDay();
      return () => stopSpeaking();
    }, [])
  );

  const { phrase, tiles } = round;
  const tileById = (uid: number) => tiles.find((t) => t.uid === uid)!;
  const seq: (string | null)[] = slots.map((uid) => (uid === null ? null : tileById(uid).id));
  const filled = slots.every((s) => s !== null);
  const placedUids = new Set(slots.filter((s): s is number => s !== null));
  const done = state !== "playing";

  const startRound = (lv: Level) => {
    const r = newRound(lv);
    setRound(r);
    setSlots(Array(r.phrase.tokens.length).fill(null));
    setActive(null);
    setState("playing");
    setMarks([]);
    setFeedback(null);
    setAttempts(0);
    setHinted(false);
    stopSpeaking();
  };

  const changeLevel = (lv: Level) => {
    if (lv === level) return;
    Haptics.selectionAsync();
    deck.level = -1; // rebuild the deck for the new level
    setLevel(lv);
    startRound(lv);
  };

  const clearFeedback = () => {
    setMarks([]);
    setFeedback(null);
  };

  const place = (uid: number) => {
    if (done) return;
    Haptics.selectionAsync();
    setSlots((prev) => {
      const next = [...prev];
      const idx = active !== null && next[active] === null ? active : next.indexOf(null);
      if (idx === -1) return prev;
      next[idx] = uid;
      return next;
    });
    setActive(null);
    clearFeedback();
    speakAuto(BLOCKS[tileById(uid).id].arabic); // hear each word as you place it
  };

  const unplace = (slotIndex: number) => {
    if (done) return;
    Haptics.selectionAsync();
    setSlots((prev) => prev.map((u, i) => (i === slotIndex ? null : u)));
    setActive(null);
    clearFeedback();
  };

  const tapSlot = (i: number) => {
    if (slots[i] !== null) unplace(i);
    else setActive(active === i ? null : i);
  };

  const clearAll = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    setSlots(Array(phrase.tokens.length).fill(null));
    setActive(null);
    clearFeedback();
  };

  const check = async () => {
    if (!filled || done) return;
    const cands = candidates(phrase);
    const correct = cands.some((c) => c.every((id, i) => id === seq[i]));
    if (correct) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      setState("correct");
      setMarks(seq.map(() => "ok"));
      setFeedback(null);
      bounce.value = withSequence(withSpring(1.04, { damping: 4 }), withSpring(1, { damping: 10 }));
      speakAuto(phraseScript(seq as string[]));
      setStats(await recordBuilderResult(true, attempts === 0 && !hinted));
    } else {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      const best = cands.reduce((b, c) => (matchCount(seq, c) > matchCount(seq, b) ? c : b), cands[0]);
      const m: TileState[] = seq.map((id, i) => (id === best[i] ? "ok" : "bad"));
      setMarks(m);
      setFeedback({ ok: m.filter((x) => x === "ok").length, total: m.length });
      setAttempts((a) => a + 1);
      shake.value = withSequence(
        withTiming(-8, { duration: 55 }), withTiming(8, { duration: 55 }),
        withTiming(-6, { duration: 55 }), withTiming(6, { duration: 55 }),
        withTiming(0, { duration: 55 })
      );
    }
  };

  const hint = () => {
    if (done) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    const canonical = phrase.tokens;
    const next = [...slots];
    const wrongAt = canonical.findIndex((id, k) => next[k] === null || tileById(next[k] as number).id !== id);
    if (wrongAt === -1) return;
    next[wrongAt] = null;
    const tile = tiles.find((t) => t.id === canonical[wrongAt] && !next.includes(t.uid)) ??
      tiles.find((t) => t.id === canonical[wrongAt])!;
    const elsewhere = next.indexOf(tile.uid);
    if (elsewhere !== -1) next[elsewhere] = null;
    next[wrongAt] = tile.uid;
    setSlots(next);
    setHinted(true);
    setActive(null);
    clearFeedback();
    speakAuto(BLOCKS[tile.id].arabic);
  };

  const reveal = async () => {
    if (done) return;
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    const used = new Set<number>();
    const next = phrase.tokens.map((id) => {
      const t = tiles.find((x) => x.id === id && !used.has(x.uid))!;
      used.add(t.uid);
      return t.uid;
    });
    setSlots(next);
    setState("revealed");
    setMarks(next.map(() => "ok"));
    setFeedback(null);
    speakAuto(phraseScript(phrase.tokens));
    setStats(await recordBuilderResult(false, false));
  };

  const nextRound = () => {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
    startRound(level);
  };

  const finalIds = (done ? seq : phrase.tokens) as string[];
  const latinSentence = finalIds.map((id) => BLOCKS[id].latin).join(" ");
  const bank = tiles.filter((t) => !placedUids.has(t.uid));
  const accuracy = stats.solved > 0 ? Math.round((stats.firstTry / Math.max(stats.total, 1)) * 100) : 0;
  const levelInfo = LEVELS.find((l) => l.key === level)!;

  return (
    <View style={[styles.screen, { backgroundColor: theme.background }]}>
      <ScrollView
        contentContainerStyle={[styles.content, { paddingTop: topPad + 16, paddingBottom: bottomPad + 110 }]}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={[styles.title, { color: theme.text }]}>Build</Text>
        <Text style={[styles.subtitle, { color: theme.textSecondary }]}>
          Put the word blocks in the right Arabic order
        </Text>

        {/* stats */}
        <View style={styles.statsRow}>
          <View style={[styles.statBox, { backgroundColor: theme.card, borderColor: theme.border }]}>
            <Text style={[styles.statNum, { color: Colors.palette.gold }]}>{stats.streak}</Text>
            <Text style={[styles.statLbl, { color: theme.textMuted }]}>No-hint streak</Text>
          </View>
          <View style={[styles.statBox, { backgroundColor: theme.card, borderColor: theme.border }]}>
            <Text style={[styles.statNum, { color: Colors.palette.success }]}>{stats.solved}</Text>
            <Text style={[styles.statLbl, { color: theme.textMuted }]}>Built</Text>
          </View>
          <View style={[styles.statBox, { backgroundColor: theme.card, borderColor: theme.border }]}>
            <Text style={[styles.statNum, { color: theme.tint }]}>{accuracy}%</Text>
            <Text style={[styles.statLbl, { color: theme.textMuted }]}>First try</Text>
          </View>
        </View>

        {/* level chips */}
        <View style={styles.chipRow}>
          {LEVELS.map((l) => {
            const sel = level === l.key;
            return (
              <TouchableOpacity
                key={l.label}
                onPress={() => changeLevel(l.key)}
                style={[
                  styles.chip,
                  { backgroundColor: sel ? Colors.palette.wine : theme.card, borderColor: sel ? Colors.palette.wine : theme.border },
                ]}
              >
                <Text style={[styles.chipText, { color: sel ? "#FFF" : theme.textSecondary }]}>{l.label}</Text>
              </TouchableOpacity>
            );
          })}
        </View>
        <Text style={[styles.levelAbout, { color: theme.textMuted }]}>{levelInfo.about}</Text>

        {/* legend + audio toggle */}
        <View style={styles.toolRow}>
          <TouchableOpacity
            style={[styles.toolBtn, { backgroundColor: theme.backgroundSecondary }]}
            onPress={() => setLegendOpen(!legendOpen)}
          >
            <Ionicons name="color-palette-outline" size={16} color={theme.tint} />
            <Text style={[styles.toolText, { color: theme.tint }]}>Word types</Text>
            <Ionicons name={legendOpen ? "chevron-up" : "chevron-down"} size={14} color={theme.tint} />
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.toolBtn, { backgroundColor: muted ? Colors.palette.gold + "22" : theme.backgroundSecondary }]}
            onPress={() => { toggleMuted(); Haptics.selectionAsync(); }}
            accessibilityLabel={muted ? "Turn automatic pronunciation on" : "Mute automatic pronunciation"}
          >
            <Ionicons
              name={muted ? "volume-mute-outline" : "volume-medium-outline"}
              size={16}
              color={muted ? Colors.palette.gold : theme.textSecondary}
            />
            <Text style={[styles.toolText, { color: muted ? Colors.palette.gold : theme.textSecondary }]}>
              {muted ? "Auto-play off" : "Auto-play on"}
            </Text>
          </TouchableOpacity>
        </View>

        {legendOpen && (
          <View style={[styles.legend, { backgroundColor: theme.card, borderColor: theme.border }]}>
            {POS_ORDER.map((p) => {
              const m = POS_META[p];
              const c = isDark ? m.dark : m.light;
              return (
                <View key={p} style={styles.legendRow}>
                  <View style={[styles.legendBadge, { backgroundColor: c + "1F", borderColor: c }]}>
                    <Text style={[styles.legendBadgeText, { color: c }]}>{m.label}</Text>
                  </View>
                  <View style={{ flex: 1 }}>
                    <Text style={[styles.legendName, { color: theme.text }]}>{m.name}</Text>
                    <Text style={[styles.legendWhat, { color: theme.textSecondary }]}>{m.what}</Text>
                    <Text style={[styles.legendEx, { color: theme.textMuted }]}>{m.example}</Text>
                  </View>
                </View>
              );
            })}
          </View>
        )}

        {/* the prompt */}
        <Animated.View style={[styles.promptCard, { backgroundColor: theme.card, borderColor: theme.border }, bounceStyle]}>
          <Text style={[styles.promptLabel, { color: theme.textMuted }]}>BUILD THIS IN ARABIC</Text>
          <Text style={[styles.promptEn, { color: theme.text }]}>{phrase.english}</Text>
          <Text style={[styles.promptNote, { color: theme.textMuted }]}>
            Blocks read left → right in the order you would say them.
          </Text>
        </Animated.View>

        {/* answer slots */}
        <Animated.View style={[styles.slotsWrap, shakeStyle]}>
          {slots.map((uid, i) => {
            if (uid !== null) {
              return (
                <BlockTile
                  key={`s${i}`}
                  id={tileById(uid).id}
                  state={marks[i] ?? "normal"}
                  onPress={done ? undefined : () => tapSlot(i)}
                  hint="Tap to take it back"
                />
              );
            }
            const isActive = active === i;
            return (
              <TouchableOpacity
                key={`s${i}`}
                onPress={() => tapSlot(i)}
                activeOpacity={0.7}
                accessibilityLabel={`Empty slot ${i + 1}`}
                style={[
                  styles.slot,
                  { borderColor: isActive ? theme.tint : theme.border, backgroundColor: isActive ? theme.tint + "14" : "transparent" },
                ]}
              >
                <Text style={[styles.slotNum, { color: isActive ? theme.tint : theme.textMuted }]}>{i + 1}</Text>
              </TouchableOpacity>
            );
          })}
        </Animated.View>

        {/* feedback */}
        {!done && feedback && (
          <View style={[styles.feedback, { backgroundColor: Colors.palette.errorLight }]}>
            <Ionicons name="close-circle" size={20} color={Colors.palette.error} />
            <Text style={[styles.feedbackText, { color: Colors.palette.error }]}>
              Not quite: {feedback.ok} of {feedback.total} blocks are in the right place. Red blocks are wrong; tap one to take it back.
            </Text>
          </View>
        )}
        {!done && !feedback && (
          <Text style={[styles.helper, { color: theme.textMuted }]}>
            Tap a block below to place it. Tap a placed block (or an empty slot, then a block) to change it.
          </Text>
        )}

        {/* bank */}
        {!done && (
          <View style={styles.bank}>
            {bank.map((t) => (
              <BlockTile key={t.uid} id={t.id} onPress={() => place(t.uid)} />
            ))}
            {bank.length === 0 && (
              <Text style={[styles.helper, { color: theme.textMuted }]}>
                {phrase.extras.length > 0 && phrase.level > 1 ? "Unused blocks are decoys. " : ""}Tap Check when you are ready.
              </Text>
            )}
          </View>
        )}

        {/* actions while playing */}
        {!done && (
          <>
            <View style={styles.btnRow}>
              <TouchableOpacity style={[styles.smallBtn, { backgroundColor: theme.backgroundSecondary, borderColor: theme.border }]} onPress={hint}>
                <Ionicons name="bulb-outline" size={18} color={Colors.palette.gold} />
                <Text style={[styles.smallBtnText, { color: theme.textSecondary }]}>Hint</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.smallBtn, { backgroundColor: theme.backgroundSecondary, borderColor: theme.border }]} onPress={clearAll}>
                <Ionicons name="backspace-outline" size={18} color={theme.textSecondary} />
                <Text style={[styles.smallBtnText, { color: theme.textSecondary }]}>Clear</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.checkBtn, { backgroundColor: Colors.palette.wine, opacity: filled ? 1 : 0.45 }]}
                onPress={check}
                disabled={!filled}
              >
                <Ionicons name="checkmark" size={20} color="#FFF" />
                <Text style={styles.checkText}>Check</Text>
              </TouchableOpacity>
            </View>
            {attempts > 0 && (
              <TouchableOpacity style={styles.revealLink} onPress={reveal}>
                <Ionicons name="eye-outline" size={16} color={theme.textMuted} />
                <Text style={[styles.revealText, { color: theme.textMuted }]}>Show me the answer</Text>
              </TouchableOpacity>
            )}
          </>
        )}

        {/* result */}
        {done && (
          <View style={[styles.resultCard, { backgroundColor: theme.card, borderColor: state === "correct" ? Colors.palette.success : Colors.palette.gold }]}>
            <View style={styles.resultHead}>
              <Ionicons
                name={state === "correct" ? "checkmark-circle" : "eye-outline"}
                size={22}
                color={state === "correct" ? Colors.palette.success : Colors.palette.gold}
              />
              <Text style={[styles.resultTitle, { color: state === "correct" ? Colors.palette.success : Colors.palette.gold }]}>
                {state === "correct" ? (attempts === 0 && !hinted ? "Mumtaaz! First try." : "Mumtaaz!") : "Here is the answer"}
              </Text>
            </View>
            <Text style={[styles.resultLatin, { color: theme.text }]}>{latinSentence}</Text>
            <Text style={[styles.resultEn, { color: theme.textSecondary }]}>{phrase.english}</Text>

            <View style={styles.patternRow}>
              {finalIds.map((id, i) => {
                const m = POS_META[BLOCKS[id].pos];
                const c = isDark ? m.dark : m.light;
                return (
                  <View key={i} style={[styles.patternChip, { borderColor: c, backgroundColor: c + "1F" }]}>
                    <Text style={[styles.patternChipText, { color: c }]}>{m.label}</Text>
                  </View>
                );
              })}
            </View>

            <View style={[styles.tipBox, { backgroundColor: theme.backgroundSecondary }]}>
              <Ionicons name="school-outline" size={16} color={theme.tint} style={{ marginTop: 2 }} />
              <Text style={[styles.tipText, { color: theme.text }]}>{phrase.tip}</Text>
            </View>

            <View style={styles.btnRow}>
              <TouchableOpacity
                style={[styles.smallBtn, { backgroundColor: theme.backgroundSecondary, borderColor: theme.border }]}
                onPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); speakArabic(phraseScript(finalIds)); }}
                accessibilityLabel="Hear the sentence in Arabic"
              >
                <Ionicons name="volume-high-outline" size={18} color={theme.tint} />
                <Text style={[styles.smallBtnText, { color: theme.tint }]}>Listen</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.checkBtn, { backgroundColor: Colors.palette.wine }]} onPress={nextRound}>
                <Text style={styles.checkText}>Next sentence</Text>
                <Ionicons name="arrow-forward" size={18} color="#FFF" />
              </TouchableOpacity>
            </View>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  content: { paddingHorizontal: 20, gap: 12 },
  title: { fontSize: 28, fontFamily: "Inter_700Bold", letterSpacing: -0.5 },
  subtitle: { fontSize: 13, fontFamily: "Inter_400Regular", marginTop: -8 },
  statsRow: { flexDirection: "row", gap: 10 },
  statBox: { flex: 1, borderRadius: 12, borderWidth: 1, paddingVertical: 10, alignItems: "center" },
  statNum: { fontSize: 20, fontFamily: "Inter_700Bold" },
  statLbl: { fontSize: 11, fontFamily: "Inter_500Medium", marginTop: 1 },
  chipRow: { flexDirection: "row", gap: 8 },
  chip: { flex: 1, borderRadius: 20, borderWidth: 1, paddingVertical: 9, alignItems: "center" },
  chipText: { fontSize: 13, fontFamily: "Inter_600SemiBold" },
  levelAbout: { fontSize: 12, fontFamily: "Inter_400Regular", marginTop: -4 },
  toolRow: { flexDirection: "row", gap: 10, flexWrap: "wrap" },
  toolBtn: { flexDirection: "row", alignItems: "center", gap: 6, paddingVertical: 9, paddingHorizontal: 12, borderRadius: 12 },
  toolText: { fontSize: 13, fontFamily: "Inter_500Medium" },
  legend: { borderRadius: 14, borderWidth: 1, padding: 12, gap: 12 },
  legendRow: { flexDirection: "row", gap: 10, alignItems: "flex-start" },
  legendBadge: { borderWidth: 1.5, borderRadius: 8, paddingVertical: 4, width: 58, alignItems: "center" },
  legendBadgeText: { fontSize: 10, fontFamily: "Inter_700Bold", letterSpacing: 0.5 },
  legendName: { fontSize: 14, fontFamily: "Inter_600SemiBold" },
  legendWhat: { fontSize: 12, fontFamily: "Inter_400Regular", lineHeight: 17, marginTop: 1 },
  legendEx: { fontSize: 12, fontFamily: "Inter_500Medium", marginTop: 2 },
  promptCard: { borderRadius: 16, borderWidth: 1, padding: 18, gap: 6 },
  promptLabel: { fontSize: 11, fontFamily: "Inter_600SemiBold", letterSpacing: 1 },
  promptEn: { fontSize: 24, fontFamily: "Inter_700Bold", lineHeight: 31 },
  promptNote: { fontSize: 12, fontFamily: "Inter_400Regular" },
  slotsWrap: { flexDirection: "row", flexWrap: "wrap", gap: 8, minHeight: 80 },
  slot: {
    minWidth: 72, height: 78, borderRadius: 12, borderWidth: 1.5, borderStyle: "dashed",
    alignItems: "center", justifyContent: "center", paddingHorizontal: 14,
  },
  slotNum: { fontSize: 16, fontFamily: "Inter_600SemiBold" },
  tile: { borderRadius: 12, paddingVertical: 8, paddingHorizontal: 12, minWidth: 72, maxWidth: "100%" },
  tileHead: { flexDirection: "row", alignItems: "center" },
  tilePos: { fontSize: 10, fontFamily: "Inter_700Bold", letterSpacing: 0.6 },
  tileTag: { fontSize: 10, fontFamily: "Inter_500Medium" },
  tileLatin: { fontSize: 18, fontFamily: "Inter_700Bold", marginTop: 2 },
  tileEn: { fontSize: 12, fontFamily: "Inter_400Regular", marginTop: 1 },
  bank: { flexDirection: "row", flexWrap: "wrap", gap: 8, marginTop: 4 },
  helper: { fontSize: 12, fontFamily: "Inter_400Regular", lineHeight: 17 },
  feedback: { flexDirection: "row", gap: 8, alignItems: "flex-start", borderRadius: 12, padding: 12 },
  feedbackText: { flex: 1, fontSize: 13, fontFamily: "Inter_600SemiBold", lineHeight: 18 },
  btnRow: { flexDirection: "row", gap: 10, alignItems: "center", marginTop: 4 },
  smallBtn: { flexDirection: "row", alignItems: "center", gap: 6, paddingVertical: 14, paddingHorizontal: 14, borderRadius: 14, borderWidth: 1 },
  smallBtnText: { fontSize: 14, fontFamily: "Inter_600SemiBold" },
  checkBtn: { flex: 1, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, paddingVertical: 15, borderRadius: 14 },
  checkText: { color: "#FFF", fontSize: 16, fontFamily: "Inter_700Bold" },
  revealLink: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, paddingVertical: 8 },
  revealText: { fontSize: 13, fontFamily: "Inter_500Medium" },
  resultCard: { borderRadius: 16, borderWidth: 2, padding: 16, gap: 10 },
  resultHead: { flexDirection: "row", alignItems: "center", gap: 8 },
  resultTitle: { fontSize: 17, fontFamily: "Inter_700Bold" },
  resultLatin: { fontSize: 22, fontFamily: "Inter_700Bold", lineHeight: 30 },
  resultEn: { fontSize: 14, fontFamily: "Inter_400Regular" },
  patternRow: { flexDirection: "row", flexWrap: "wrap", gap: 6 },
  patternChip: { borderWidth: 1.5, borderRadius: 8, paddingVertical: 3, paddingHorizontal: 8 },
  patternChipText: { fontSize: 10, fontFamily: "Inter_700Bold", letterSpacing: 0.6 },
  tipBox: { flexDirection: "row", gap: 8, borderRadius: 12, padding: 12 },
  tipText: { flex: 1, fontSize: 13, fontFamily: "Inter_400Regular", lineHeight: 19 },
});
