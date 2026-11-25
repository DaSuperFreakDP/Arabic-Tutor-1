import React, { useCallback, useEffect, useState } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Linking,
  Platform,
  useColorScheme,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import Colors from "@/constants/colors";
import {
  BRIDGES,
  GREETINGS,
  MISSIONS,
  PEP,
  REASONS,
  REGIONS,
  ROOTS,
  SCENARIOS,
  SOURCES,
  SPARKS,
  TOPICS,
  Part,
  Word,
} from "@/lib/culture-data";
import { speakArabic, stopSpeaking } from "@/lib/speech";
import {
  getBuilderStats,
  getCultureProgress,
  getProfileStats,
  getWhy,
  markTopicExplored,
  saveWhy,
  toggleMission,
  checkAndRecordStudyDay,
} from "@/lib/progress-storage";

type IconName = React.ComponentProps<typeof Ionicons>["name"];
const icon = (n: string) => n as IconName;

const dayNumber = () => Math.floor((Date.now() - new Date().getTimezoneOffset() * 60000) / 86400000);

function useTheme() {
  const isDark = useColorScheme() === "dark";
  return { isDark, theme: isDark ? Colors.dark : Colors.light };
}

// ---------------------------------------------------------------------------------------------
// A tappable Arabic word: shows the Latin transcription, plays the Arabic voice when tapped.
// (Culture audio is always tap-to-play, never automatic.)
// ---------------------------------------------------------------------------------------------
function WordChip({ word, compact }: { word: Word; compact?: boolean }) {
  const { theme } = useTheme();
  return (
    <TouchableOpacity
      activeOpacity={0.7}
      onPress={() => {
        Haptics.selectionAsync();
        speakArabic(word.script);
      }}
      accessibilityLabel={`Hear ${word.latin}, ${word.en}, in Arabic`}
      style={[styles.chip, { backgroundColor: theme.tint + "14", borderColor: theme.tint + "55" }]}
    >
      <Ionicons name="volume-medium-outline" size={compact ? 15 : 17} color={theme.tint} />
      <View>
        <Text style={[styles.chipLatin, { color: theme.text }]}>{word.latin}</Text>
        <Text style={[styles.chipEn, { color: theme.textSecondary }]}>{word.en}</Text>
      </View>
    </TouchableOpacity>
  );
}

// ---------------------------------------------------------------------------------------------
// Part renderers
// ---------------------------------------------------------------------------------------------
function BridgesBlock() {
  const { theme, isDark } = useTheme();
  const [filter, setFilter] = useState<"All" | "Italian" | "Sicilian" | "Place">("All");
  const langs = ["All", "Italian", "Sicilian", "Place"] as const;
  const list = BRIDGES.filter((b) => filter === "All" || b.lang === filter);
  const langColor = (l: string) =>
    l === "Italian" ? (isDark ? "#8DB4FF" : "#2457B8") : l === "Sicilian" ? (isDark ? "#FF9C7A" : "#B8401F") : isDark ? "#6FD6A0" : "#1F7A4A";
  return (
    <View style={{ gap: 10 }}>
      <View style={styles.filterRow}>
        {langs.map((l) => {
          const sel = filter === l;
          return (
            <TouchableOpacity
              key={l}
              onPress={() => { Haptics.selectionAsync(); setFilter(l); }}
              style={[styles.filterChip, { backgroundColor: sel ? Colors.palette.wine : theme.card, borderColor: sel ? Colors.palette.wine : theme.border }]}
            >
              <Text style={[styles.filterText, { color: sel ? "#FFF" : theme.textSecondary }]}>{l === "Place" ? "Places" : l}</Text>
            </TouchableOpacity>
          );
        })}
      </View>
      {list.map((b) => (
        <View key={b.id} style={[styles.bridgeCard, { backgroundColor: theme.card, borderColor: theme.border }]}>
          <View style={styles.bridgeTop}>
            <WordChip word={b.word} />
            <Ionicons name="arrow-forward" size={18} color={theme.textMuted} />
            <View style={{ flex: 1 }}>
              <Text style={[styles.langTag, { color: langColor(b.lang) }]}>{b.lang === "Place" ? "PLACE NAME" : b.lang.toUpperCase()}</Text>
              <Text style={[styles.became, { color: theme.text }]}>{b.became}</Text>
            </View>
          </View>
          <Text style={[styles.body, { color: theme.textSecondary }]}>{b.story}</Text>
          {b.card && (
            <View style={styles.inCardsRow}>
              <Ionicons name="layers-outline" size={13} color={Colors.palette.success} />
              <Text style={[styles.inCards, { color: Colors.palette.success }]}>Already in your flashcards</Text>
            </View>
          )}
        </View>
      ))}
    </View>
  );
}

function PartView({ part, missions, onMission }: { part: Part; missions: string[]; onMission: (id: string) => void }) {
  const { theme } = useTheme();
  switch (part.t) {
    case "p":
      return <Text style={[styles.body, { color: theme.text }]}>{part.text}</Text>;
    case "note":
      return (
        <View style={[styles.note, { backgroundColor: theme.tint + "14", borderLeftColor: theme.tint }]}>
          <Ionicons name="bulb-outline" size={17} color={theme.tint} style={{ marginTop: 1 }} />
          <Text style={[styles.noteText, { color: theme.text }]}>{part.text}</Text>
        </View>
      );
    case "bullets":
      return (
        <View style={{ gap: 6 }}>
          {part.items.map((t, i) => (
            <View key={i} style={styles.bulletRow}>
              <Text style={[styles.bulletDot, { color: theme.tint }]}>•</Text>
              <Text style={[styles.body, { color: theme.text, flex: 1 }]}>{t}</Text>
            </View>
          ))}
        </View>
      );
    case "timeline":
      return (
        <View>
          {part.items.map((it, i) => (
            <View key={i} style={styles.tlRow}>
              <View style={styles.tlRail}>
                <View style={[styles.tlDot, { backgroundColor: Colors.palette.wine }]} />
                {i < part.items.length - 1 && <View style={[styles.tlLine, { backgroundColor: theme.border }]} />}
              </View>
              <View style={styles.tlBody}>
                <Text style={[styles.tlWhen, { color: Colors.palette.wine }]}>{it.when}</Text>
                <Text style={[styles.body, { color: theme.text }]}>{it.text}</Text>
              </View>
            </View>
          ))}
        </View>
      );
    case "facts":
      return (
        <View style={[styles.facts, { backgroundColor: theme.backgroundSecondary }]}>
          {part.rows.map((r, i) => (
            <View key={i} style={styles.factRow}>
              <Text style={[styles.factLabel, { color: theme.textMuted }]}>{r.label}</Text>
              <Text style={[styles.factValue, { color: theme.text }]}>{r.value}</Text>
            </View>
          ))}
        </View>
      );
    case "pairs":
      return (
        <View style={{ gap: 8 }}>
          {part.items.map((it, i) => (
            <View key={i} style={styles.pairRow}>
              <Text style={[styles.pairLeft, { color: theme.text }]}>{it.left}</Text>
              <Ionicons name="arrow-back" size={14} color={theme.textMuted} />
              <WordChip word={it.word} compact />
            </View>
          ))}
        </View>
      );
    case "bridges":
      return <BridgesBlock />;
    case "greetings":
      return (
        <View style={[styles.facts, { backgroundColor: theme.backgroundSecondary }]}>
          <Text style={[styles.subHead, { color: theme.textMuted }]}>HOW ARE YOU?</Text>
          {GREETINGS.map((g, i) => (
            <View key={i} style={styles.greetRow}>
              <Text style={[styles.greetRegion, { color: theme.textSecondary }]}>{g.region}</Text>
              {g.word ? <WordChip word={g.word} compact /> : <Text style={[styles.greetSay, { color: theme.text }]}>{g.say}</Text>}
            </View>
          ))}
          <Text style={[styles.tiny, { color: theme.textMuted }]}>
            Only the standard form can be played; the voice is a standard Arabic voice, not a regional one.
          </Text>
        </View>
      );
    case "regions":
      return (
        <View style={{ gap: 10 }}>
          {REGIONS.map((r) => (
            <View key={r.name} style={[styles.regionCard, { backgroundColor: theme.card, borderColor: theme.border }]}>
              <View style={styles.regionHead}>
                <View style={[styles.iconCircle, { backgroundColor: theme.tint + "18" }]}>
                  <Ionicons name={icon(r.icon)} size={18} color={theme.tint} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={[styles.regionName, { color: theme.text }]}>{r.name}</Text>
                  <Text style={[styles.regionWhere, { color: theme.textMuted }]}>{r.where}</Text>
                </View>
              </View>
              <Text style={[styles.body, { color: theme.textSecondary }]}>{r.text}</Text>
            </View>
          ))}
        </View>
      );
    case "roots":
      return (
        <View style={{ gap: 10 }}>
          {ROOTS.map((r) => (
            <View key={r.root} style={[styles.regionCard, { backgroundColor: theme.card, borderColor: theme.border }]}>
              <View style={styles.regionHead}>
                <View style={[styles.rootBadge, { backgroundColor: Colors.palette.wine }]}>
                  <Text style={styles.rootBadgeText}>{r.root}</Text>
                </View>
                <Text style={[styles.regionName, { color: theme.text }]}>{r.meaning}</Text>
              </View>
              <View style={styles.chipWrap}>
                {r.words.map((w) => (
                  <WordChip key={w.latin} word={w} compact />
                ))}
              </View>
              <Text style={[styles.body, { color: theme.textSecondary }]}>{r.note}</Text>
            </View>
          ))}
        </View>
      );
    case "scenarios":
      return (
        <View style={{ gap: 10 }}>
          {SCENARIOS.map((s) => (
            <View key={s.id} style={[styles.regionCard, { backgroundColor: theme.card, borderColor: theme.border }]}>
              <View style={styles.regionHead}>
                <View style={[styles.iconCircle, { backgroundColor: theme.tint + "18" }]}>
                  <Ionicons name={icon(s.icon)} size={18} color={theme.tint} />
                </View>
                <Text style={[styles.regionName, { color: theme.text, flex: 1 }]}>{s.title}</Text>
              </View>
              <Text style={[styles.body, { color: theme.textSecondary }]}>{s.text}</Text>
              <View style={styles.chipWrap}>
                {s.words.map((w) => (
                  <WordChip key={w.latin} word={w} compact />
                ))}
              </View>
            </View>
          ))}
        </View>
      );
    case "missions":
      return (
        <View style={{ gap: 8 }}>
          {MISSIONS.map((m) => {
            const done = missions.includes(m.id);
            return (
              <TouchableOpacity
                key={m.id}
                onPress={() => { Haptics.selectionAsync(); onMission(m.id); }}
                activeOpacity={0.7}
                accessibilityRole="checkbox"
                aria-checked={done}
                style={[styles.mission, { backgroundColor: done ? Colors.palette.success + "18" : theme.card, borderColor: done ? Colors.palette.success : theme.border }]}
              >
                <Ionicons
                  name={done ? "checkmark-circle" : "ellipse-outline"}
                  size={22}
                  color={done ? Colors.palette.success : theme.textMuted}
                />
                <Text style={[styles.missionText, { color: theme.text }, done && { textDecorationLine: "line-through", opacity: 0.7 }]}>{m.text}</Text>
              </TouchableOpacity>
            );
          })}
        </View>
      );
  }
}

// ---------------------------------------------------------------------------------------------
// Screen
// ---------------------------------------------------------------------------------------------
export default function CultureScreen() {
  const { theme } = useTheme();
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === "web" ? 67 : insets.top;
  const bottomPad = Platform.OS === "web" ? 34 : insets.bottom;

  const [why, setWhy] = useState({ text: "", reasons: [] as string[] });
  const [draft, setDraft] = useState({ text: "", reasons: [] as string[] });
  const [editing, setEditing] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [explored, setExplored] = useState<string[]>([]);
  const [missions, setMissions] = useState<string[]>([]);
  const [openId, setOpenId] = useState<string | null>(null);
  const [sparkOffset, setSparkOffset] = useState(0);
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const [journey, setJourney] = useState({ days: 0, cards: 0, built: 0, streak: 0 });

  useEffect(() => {
    (async () => {
      const [w, c] = await Promise.all([getWhy(), getCultureProgress()]);
      setWhy(w);
      setExplored(c.explored);
      setMissions(c.missions);
      setLoaded(true);
    })();
  }, []);

  useFocusEffect(
    useCallback(() => {
      checkAndRecordStudyDay();
      Promise.all([getProfileStats(), getBuilderStats()]).then(([p, b]) =>
        setJourney({ days: p.daysStudied, cards: p.masteredCards, built: b.solved, streak: p.dailyStreak })
      );
      return () => stopSpeaking();
    }, [])
  );

  const startEdit = () => {
    Haptics.selectionAsync();
    setDraft({ text: why.text, reasons: [...why.reasons] });
    setEditing(true);
  };
  const saveEdit = async () => {
    Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    const next = { text: draft.text.trim(), reasons: draft.reasons };
    setWhy(next);
    setEditing(false);
    await saveWhy(next);
  };
  const toggleReason = (id: string) => {
    Haptics.selectionAsync();
    setDraft((d) => ({ ...d, reasons: d.reasons.includes(id) ? d.reasons.filter((r) => r !== id) : [...d.reasons, id] }));
  };

  const toggleTopic = (id: string) => {
    Haptics.selectionAsync();
    stopSpeaking();
    if (openId === id) {
      setOpenId(null);
      return;
    }
    setOpenId(id);
    markTopicExplored(id).then(setExplored);
  };

  const onMission = async (id: string) => setMissions(await toggleMission(id));

  const spark = SPARKS[(dayNumber() + sparkOffset) % SPARKS.length];
  const pep = PEP[dayNumber() % PEP.length];
  const hasWhy = why.text.length > 0 || why.reasons.length > 0;
  const hasJourney = journey.days > 0 || journey.cards > 0 || journey.built > 0;
  const reasonLabel = (id: string) => REASONS.find((r) => r.id === id);

  return (
    <View style={[styles.screen, { backgroundColor: theme.background }]}>
      <ScrollView
        contentContainerStyle={[styles.content, { paddingTop: topPad + 16, paddingBottom: bottomPad + 110 }]}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
        automaticallyAdjustKeyboardInsets
      >
        <Text style={[styles.title, { color: theme.text }]}>Culture</Text>
        <Text style={[styles.subtitle, { color: theme.textSecondary }]}>Why this language is worth your time</Text>

        {/* ---------------------------------------------------------------- My Why */}
        <View style={[styles.whyCard, { backgroundColor: theme.card, borderColor: Colors.palette.wine }]}>
          <View style={styles.whyHead}>
            <Ionicons name="heart" size={16} color={Colors.palette.wine} />
            <Text style={[styles.cardLabel, { color: Colors.palette.wine }]}>MY WHY</Text>
            {!editing && loaded && (
              <TouchableOpacity onPress={startEdit} style={styles.editBtn} accessibilityLabel={hasWhy ? "Edit my reason" : "Write my reason"}>
                <Ionicons name="create-outline" size={16} color={theme.tint} />
                <Text style={[styles.editText, { color: theme.tint }]}>{hasWhy ? "Edit" : "Write it"}</Text>
              </TouchableOpacity>
            )}
          </View>

          {editing ? (
            <View style={{ gap: 12 }}>
              <TextInput
                value={draft.text}
                onChangeText={(t) => setDraft((d) => ({ ...d, text: t }))}
                placeholder="I'm learning Arabic because…"
                placeholderTextColor={theme.textMuted}
                multiline
                maxLength={400}
                style={[styles.input, { color: theme.text, borderColor: theme.border, backgroundColor: theme.background }]}
                accessibilityLabel="Why I am learning Arabic"
              />
              <Text style={[styles.tiny, { color: theme.textMuted }]}>Pick any that fit:</Text>
              <View style={styles.chipWrap}>
                {REASONS.map((r) => {
                  const sel = draft.reasons.includes(r.id);
                  return (
                    <TouchableOpacity
                      key={r.id}
                      onPress={() => toggleReason(r.id)}
                      style={[styles.reasonChip, { backgroundColor: sel ? Colors.palette.wine : theme.background, borderColor: sel ? Colors.palette.wine : theme.border }]}
                      aria-selected={sel}
                    >
                      <Ionicons name={icon(r.icon)} size={14} color={sel ? "#FFF" : theme.textSecondary} />
                      <Text style={[styles.reasonText, { color: sel ? "#FFF" : theme.textSecondary }]}>{r.label}</Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
              <View style={styles.btnRow}>
                <TouchableOpacity onPress={() => setEditing(false)} style={[styles.ghostBtn, { borderColor: theme.border }]}>
                  <Text style={[styles.ghostText, { color: theme.textSecondary }]}>Cancel</Text>
                </TouchableOpacity>
                <TouchableOpacity onPress={saveEdit} style={[styles.saveBtn, { backgroundColor: Colors.palette.wine }]}>
                  <Ionicons name="checkmark" size={18} color="#FFF" />
                  <Text style={styles.saveText}>Save</Text>
                </TouchableOpacity>
              </View>
            </View>
          ) : hasWhy ? (
            <View style={{ gap: 10 }}>
              {why.text.length > 0 && <Text style={[styles.whyText, { color: theme.text }]}>{why.text}</Text>}
              {why.reasons.length > 0 && (
                <View style={styles.chipWrap}>
                  {why.reasons.map((id) => {
                    const r = reasonLabel(id);
                    return r ? (
                      <View key={id} style={[styles.reasonChip, { backgroundColor: Colors.palette.wine + "18", borderColor: Colors.palette.wine + "66" }]}>
                        <Ionicons name={icon(r.icon)} size={14} color={Colors.palette.wine} />
                        <Text style={[styles.reasonText, { color: theme.text }]}>{r.label}</Text>
                      </View>
                    ) : null;
                  })}
                </View>
              )}
            </View>
          ) : (
            <Text style={[styles.body, { color: theme.textSecondary }]}>
              Write down why you started, in your own words. On the days you don't feel like studying, this is the first thing
              to read. It stays on your phone.
            </Text>
          )}

          <View style={[styles.divider, { backgroundColor: theme.separator }]} />
          {hasJourney && (
            <Text style={[styles.journey, { color: theme.text }]}>
              So far: <Text style={styles.bold}>{journey.days}</Text> {journey.days === 1 ? "day" : "days"} studied
              {journey.cards > 0 ? <> · <Text style={styles.bold}>{journey.cards}</Text> cards learned</> : null}
              {journey.built > 0 ? <> · <Text style={styles.bold}>{journey.built}</Text> sentences built</> : null}
              {journey.streak > 1 ? <> · <Text style={styles.bold}>{journey.streak}</Text>-day streak</> : null}
            </Text>
          )}
          <Text style={[styles.pep, { color: theme.textSecondary }]}>{pep}</Text>
        </View>

        {/* ---------------------------------------------------------------- spark */}
        <View style={[styles.sparkCard, { backgroundColor: theme.card, borderColor: theme.border }]}>
          <View style={styles.whyHead}>
            <Ionicons name="sparkles" size={16} color={Colors.palette.gold} />
            <Text style={[styles.cardLabel, { color: Colors.palette.gold }]}>TODAY'S SPARK</Text>
            <TouchableOpacity
              onPress={() => { Haptics.selectionAsync(); stopSpeaking(); setSparkOffset(sparkOffset + 1); }}
              style={styles.editBtn}
              accessibilityLabel="Show another fact"
            >
              <Ionicons name="refresh-outline" size={16} color={theme.tint} />
              <Text style={[styles.editText, { color: theme.tint }]}>Another</Text>
            </TouchableOpacity>
          </View>
          <Text style={[styles.sparkText, { color: theme.text }]}>{spark.text}</Text>
          {spark.word && (
            <View style={{ alignSelf: "flex-start" }}>
              <WordChip word={spark.word} />
            </View>
          )}
        </View>

        {/* ---------------------------------------------------------------- topics */}
        <View style={styles.exploreHead}>
          <Text style={[styles.sectionLabel, { color: theme.textMuted }]}>EXPLORE</Text>
          <Text style={[styles.sectionCount, { color: theme.textMuted }]}>
            {explored.filter((id) => TOPICS.some((t) => t.id === id)).length} of {TOPICS.length} opened
          </Text>
        </View>

        {TOPICS.map((t) => {
          const open = openId === t.id;
          const seen = explored.includes(t.id);
          return (
            <View key={t.id} style={[styles.topic, { backgroundColor: theme.card, borderColor: open ? theme.tint : theme.border }]}>
              <TouchableOpacity
                onPress={() => toggleTopic(t.id)}
                activeOpacity={0.75}
                style={styles.topicHead}
                accessibilityRole="button"
                aria-expanded={open}
                accessibilityLabel={`${t.title}. ${t.hook}`}
              >
                <View style={[styles.iconCircle, { backgroundColor: theme.tint + "18" }]}>
                  <Ionicons name={icon(t.icon)} size={20} color={theme.tint} />
                </View>
                <View style={{ flex: 1 }}>
                  <Text style={[styles.topicTitle, { color: theme.text }]}>{t.title}</Text>
                  <Text style={[styles.topicHook, { color: theme.textSecondary }]}>{t.hook}</Text>
                </View>
                {seen && !open && <Ionicons name="checkmark-circle" size={18} color={Colors.palette.success} />}
                <Ionicons name={open ? "chevron-up" : "chevron-down"} size={18} color={theme.textMuted} />
              </TouchableOpacity>
              {open && (
                <View style={styles.topicBody}>
                  {t.parts.map((p, i) => (
                    <PartView key={i} part={p} missions={missions} onMission={onMission} />
                  ))}
                </View>
              )}
            </View>
          );
        })}

        {/* ---------------------------------------------------------------- sources */}
        <TouchableOpacity onPress={() => setSourcesOpen(!sourcesOpen)} style={styles.sourcesToggle}>
          <Ionicons name="link-outline" size={16} color={theme.textMuted} />
          <Text style={[styles.sourcesText, { color: theme.textMuted }]}>Where these facts come from</Text>
          <Ionicons name={sourcesOpen ? "chevron-up" : "chevron-down"} size={14} color={theme.textMuted} />
        </TouchableOpacity>
        {sourcesOpen && (
          <View style={[styles.facts, { backgroundColor: theme.backgroundSecondary }]}>
            {SOURCES.map((s) => (
              <TouchableOpacity key={s.url} onPress={() => Linking.openURL(s.url)} accessibilityRole="link" style={{ paddingVertical: 5 }}>
                <Text style={[styles.sourceLink, { color: theme.tint }]}>{s.label}</Text>
              </TouchableOpacity>
            ))}
            <Text style={[styles.tiny, { color: theme.textMuted }]}>
              Where historians disagree, the text says so. Dates and figures are as given by these sources.
            </Text>
          </View>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  content: { paddingHorizontal: 20, gap: 14 },
  title: { fontSize: 28, fontFamily: "Inter_700Bold", letterSpacing: -0.5 },
  subtitle: { fontSize: 13, fontFamily: "Inter_400Regular", marginTop: -10 },
  body: { fontSize: 14, fontFamily: "Inter_400Regular", lineHeight: 21 },
  bold: { fontFamily: "Inter_700Bold" },
  tiny: { fontSize: 12, fontFamily: "Inter_400Regular", lineHeight: 17 },
  subHead: { fontSize: 11, fontFamily: "Inter_600SemiBold", letterSpacing: 1 },

  whyCard: { borderRadius: 18, borderWidth: 1.5, padding: 16, gap: 12 },
  whyHead: { flexDirection: "row", alignItems: "center", gap: 6 },
  cardLabel: { fontSize: 12, fontFamily: "Inter_700Bold", letterSpacing: 1, flex: 1 },
  editBtn: { flexDirection: "row", alignItems: "center", gap: 4, paddingVertical: 4, paddingHorizontal: 6 },
  editText: { fontSize: 13, fontFamily: "Inter_600SemiBold" },
  whyText: { fontSize: 18, fontFamily: "Inter_600SemiBold", lineHeight: 26 },
  input: { minHeight: 96, borderWidth: 1, borderRadius: 12, padding: 12, fontSize: 15, fontFamily: "Inter_400Regular", textAlignVertical: "top" },
  divider: { height: StyleSheet.hairlineWidth },
  journey: { fontSize: 13, fontFamily: "Inter_400Regular", lineHeight: 19 },
  pep: { fontSize: 13, fontFamily: "Inter_500Medium", lineHeight: 19, fontStyle: "italic" },
  btnRow: { flexDirection: "row", gap: 10 },
  ghostBtn: { paddingVertical: 13, paddingHorizontal: 18, borderRadius: 12, borderWidth: 1 },
  ghostText: { fontSize: 14, fontFamily: "Inter_600SemiBold" },
  saveBtn: { flex: 1, flexDirection: "row", gap: 6, alignItems: "center", justifyContent: "center", paddingVertical: 13, borderRadius: 12 },
  saveText: { color: "#FFF", fontSize: 15, fontFamily: "Inter_700Bold" },
  reasonChip: { flexDirection: "row", alignItems: "center", gap: 6, paddingVertical: 7, paddingHorizontal: 11, borderRadius: 18, borderWidth: 1 },
  reasonText: { fontSize: 13, fontFamily: "Inter_500Medium" },

  sparkCard: { borderRadius: 18, borderWidth: 1, padding: 16, gap: 12 },
  sparkText: { fontSize: 16, fontFamily: "Inter_500Medium", lineHeight: 24 },

  exploreHead: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginTop: 6 },
  sectionLabel: { fontSize: 12, fontFamily: "Inter_700Bold", letterSpacing: 1 },
  sectionCount: { fontSize: 12, fontFamily: "Inter_500Medium" },
  topic: { borderRadius: 16, borderWidth: 1.5, overflow: "hidden" },
  topicHead: { flexDirection: "row", alignItems: "center", gap: 12, padding: 14 },
  iconCircle: { width: 38, height: 38, borderRadius: 19, alignItems: "center", justifyContent: "center" },
  topicTitle: { fontSize: 16, fontFamily: "Inter_700Bold", lineHeight: 21 },
  topicHook: { fontSize: 12.5, fontFamily: "Inter_400Regular", lineHeight: 18, marginTop: 2 },
  topicBody: { paddingHorizontal: 14, paddingBottom: 16, gap: 14 },

  chip: { flexDirection: "row", alignItems: "center", gap: 8, paddingVertical: 7, paddingHorizontal: 11, borderRadius: 12, borderWidth: 1 },
  chipLatin: { fontSize: 15, fontFamily: "Inter_700Bold" },
  chipEn: { fontSize: 11, fontFamily: "Inter_400Regular" },
  chipWrap: { flexDirection: "row", flexWrap: "wrap", gap: 8 },

  filterRow: { flexDirection: "row", gap: 8 },
  filterChip: { paddingVertical: 7, paddingHorizontal: 14, borderRadius: 18, borderWidth: 1 },
  filterText: { fontSize: 13, fontFamily: "Inter_600SemiBold" },
  bridgeCard: { borderRadius: 14, borderWidth: 1, padding: 12, gap: 8 },
  bridgeTop: { flexDirection: "row", alignItems: "center", gap: 8 },
  langTag: { fontSize: 10, fontFamily: "Inter_700Bold", letterSpacing: 0.8 },
  became: { fontSize: 17, fontFamily: "Inter_700Bold", lineHeight: 22 },
  inCardsRow: { flexDirection: "row", alignItems: "center", gap: 5 },
  inCards: { fontSize: 12, fontFamily: "Inter_600SemiBold" },

  note: { flexDirection: "row", gap: 10, borderLeftWidth: 3, borderRadius: 8, padding: 12 },
  noteText: { flex: 1, fontSize: 13.5, fontFamily: "Inter_500Medium", lineHeight: 20 },
  bulletRow: { flexDirection: "row", gap: 8 },
  bulletDot: { fontSize: 16, lineHeight: 21, fontFamily: "Inter_700Bold" },

  tlRow: { flexDirection: "row", gap: 12 },
  tlRail: { width: 14, alignItems: "center" },
  tlDot: { width: 11, height: 11, borderRadius: 6, marginTop: 5 },
  tlLine: { width: 2, flex: 1, marginTop: 3 },
  tlBody: { flex: 1, paddingBottom: 14, gap: 2 },
  tlWhen: { fontSize: 13, fontFamily: "Inter_700Bold" },

  facts: { borderRadius: 12, padding: 12, gap: 8 },
  factRow: { flexDirection: "row", gap: 10 },
  factLabel: { width: 96, fontSize: 12, fontFamily: "Inter_600SemiBold", lineHeight: 19 },
  factValue: { flex: 1, fontSize: 13.5, fontFamily: "Inter_500Medium", lineHeight: 19 },

  pairRow: { flexDirection: "row", alignItems: "center", gap: 10 },
  pairLeft: { flex: 1, fontSize: 15, fontFamily: "Inter_600SemiBold" },

  greetRow: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", gap: 10 },
  greetRegion: { flex: 1, fontSize: 13, fontFamily: "Inter_400Regular", lineHeight: 18 },
  greetSay: { fontSize: 15, fontFamily: "Inter_700Bold" },

  regionCard: { borderRadius: 14, borderWidth: 1, padding: 12, gap: 8 },
  regionHead: { flexDirection: "row", alignItems: "center", gap: 10 },
  regionName: { fontSize: 15, fontFamily: "Inter_700Bold" },
  regionWhere: { fontSize: 12, fontFamily: "Inter_400Regular", marginTop: 1 },
  rootBadge: { borderRadius: 8, paddingVertical: 4, paddingHorizontal: 10 },
  rootBadgeText: { color: "#FFF", fontSize: 14, fontFamily: "Inter_700Bold", letterSpacing: 1 },

  mission: { flexDirection: "row", alignItems: "center", gap: 10, padding: 12, borderRadius: 12, borderWidth: 1 },
  missionText: { flex: 1, fontSize: 14, fontFamily: "Inter_500Medium", lineHeight: 20 },

  sourcesToggle: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 6, paddingVertical: 10 },
  sourcesText: { fontSize: 13, fontFamily: "Inter_500Medium" },
  sourceLink: { fontSize: 13, fontFamily: "Inter_500Medium", textDecorationLine: "underline" },
});
