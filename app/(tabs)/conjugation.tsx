import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
  Platform,
  useColorScheme,
  Keyboard,
  KeyboardAvoidingView,
} from "react-native";
import Animated, {
  useSharedValue,
  useAnimatedStyle,
  withSpring,
  withSequence,
  withTiming,
} from "react-native-reanimated";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import * as Haptics from "expo-haptics";
import Colors from "@/constants/colors";
import {
  VERBS,
  PRONOUNS,
  PRONOUN_KEYS,
  PRONOUN_EN,
  TENSE_NAMES,
  TenseId,
  Pronoun,
} from "@/lib/arabic-data";
import {
  getConjugationStats,
  recordConjugationAnswer,
  recordSessionResult,
  ConjugationStats,
  checkAndRecordStudyDay,
  getEnabledVerbs,
  setEnabledVerbs,
  getConjugationMode,
  setConjugationMode,
} from "@/lib/progress-storage";
import { answersMatch } from "@/lib/utils";
import StreakBanner from "@/components/StreakBanner";

const TENSE_ORDER: TenseId[] = ['present', 'past', 'future'];

const COUNT_OPTIONS = [10, 20, 50, 100] as const;
type CountOption = typeof COUNT_OPTIONS[number];

interface Question {
  verb: typeof VERBS[0];
  tense: TenseId;
  pronoun: Pronoun;
  answer: string;
}

interface VerbFilters {
  includeRegular: boolean;
  includeIrregular: boolean;
  includeDerived: boolean;
}

function buildQueue(tenses: TenseId[], count: number, filters: VerbFilters, enabledVerbs: Set<string> | null): Question[] {
  const eligibleVerbs = VERBS.filter(v => {
    if (enabledVerbs && !enabledVerbs.has(v.id)) return false;
    if (v.type === 'derived') return filters.includeDerived;
    if (v.type === 'irregular') return filters.includeIrregular;
    return filters.includeRegular;
  }).filter(v => tenses.some(t => v.tenses[t]));

  if (eligibleVerbs.length === 0) return [];

  const queue: Question[] = [];
  const seen = new Set<string>();

  let attempts = 0;
  while (queue.length < count && attempts < count * 20) {
    attempts++;
    const verb = eligibleVerbs[Math.floor(Math.random() * eligibleVerbs.length)];
    const validTenses = tenses.filter(t => verb.tenses[t]);
    if (validTenses.length === 0) continue;
    const tense = validTenses[Math.floor(Math.random() * validTenses.length)];
    const pronoun = PRONOUNS[Math.floor(Math.random() * PRONOUNS.length)];
    const conjugation = verb.tenses[tense];
    if (!conjugation) continue;
    const answer = conjugation[PRONOUN_KEYS[pronoun]];
    if (!answer || answer === '-') continue;
    const key = `${verb.id}-${tense}-${pronoun}`;
    if (queue.length < count / 2 && seen.has(key)) continue;
    seen.add(key);
    queue.push({ verb, tense, pronoun, answer });
  }
  
  // Shuffle the final queue
  return queue.sort(() => Math.random() - 0.5);
}

type Phase = 'setup' | 'testing' | 'results';
type QuestionState = 'idle' | 'correct' | 'wrong' | 'revealed';

function ToggleRow({ label, sub, value, onChange, color }: {
  label: string;
  sub?: string;
  value: boolean;
  onChange: (v: boolean) => void;
  color: string;
}) {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === "dark";
  const theme = isDark ? Colors.dark : Colors.light;
  return (
    <TouchableOpacity
      style={[styles.toggleRow, { borderBottomColor: theme.separator }]}
      onPress={() => { onChange(!value); Haptics.selectionAsync(); }}
      activeOpacity={0.7}
    >
      <View style={{ flex: 1 }}>
        <Text style={[styles.toggleLabel, { color: theme.text }]}>{label}</Text>
        {sub && <Text style={[styles.toggleSub, { color: theme.textMuted }]}>{sub}</Text>}
      </View>
      <View style={[styles.toggleTrack, { backgroundColor: value ? color : theme.border }]}>
        <View style={[styles.toggleThumb, { alignSelf: value ? 'flex-end' : 'flex-start' }]} />
      </View>
    </TouchableOpacity>
  );
}

const regularVerbCount = VERBS.filter(v => v.type === 'regular').length;
const irregularVerbCount = VERBS.filter(v => v.type === 'irregular').length;
const derivedVerbCount = VERBS.filter(v => v.type === 'derived').length;

function SetupScreen({ onStart, stats }: { onStart: (tenses: TenseId[], count: CountOption, filters: VerbFilters, mode: 'arabic' | 'english') => void; stats: ConjugationStats }) {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === "dark";
  const theme = isDark ? Colors.dark : Colors.light;
  const insets = useSafeAreaInsets();

  const [selectedTenses, setSelectedTenses] = useState<Set<TenseId>>(new Set(['present']));
  const [selectedCount, setSelectedCount] = useState<CountOption>(10);
  const [verbFilters, setVerbFilters] = useState<VerbFilters>({
    includeRegular: true,
    includeIrregular: true,
    includeDerived: true,
  });
  const [enabledVerbIds, setEnabledVerbIds] = useState<Set<string> | null>(null);
  const [isVerbsExpanded, setIsVerbsExpanded] = useState(false);
  const [mode, setMode] = useState<'arabic' | 'english'>('arabic');

  useEffect(() => {
    getEnabledVerbs().then(setEnabledVerbIds);
  }, []);

  const toggleVerb = async (verbId: string) => {
    const next = new Set(enabledVerbIds || VERBS.map(v => v.id));
    if (next.has(verbId)) {
      if (next.size > 1) next.delete(verbId);
    } else {
      next.add(verbId);
    }
    setEnabledVerbIds(next);
    await setEnabledVerbs(Array.from(next));
    Haptics.selectionAsync();
  };

  const topPad = Platform.OS === "web" ? 67 : insets.top;
  const bottomPad = Platform.OS === "web" ? 34 : insets.bottom;
  const accuracy = stats.total > 0 ? Math.round((stats.score / stats.total) * 100) : 0;

  const toggleTense = (t: TenseId) => {
    setSelectedTenses(prev => {
      const next = new Set(prev);
      if (next.has(t)) { if (next.size === 1) return prev; next.delete(t); }
      else next.add(t);
      return next;
    });
    Haptics.selectionAsync();
  };

  const canStart = verbFilters.includeRegular || verbFilters.includeIrregular || verbFilters.includeDerived;

  return (
    <ScrollView
      style={[styles.screen, { backgroundColor: theme.background }]}
      contentContainerStyle={[styles.setupContent, { paddingTop: topPad + 16, paddingBottom: bottomPad + 24 }]}
      showsVerticalScrollIndicator={false}
    >
      <View style={styles.setupHeader}>
        <Text style={[styles.headerTitle, { color: theme.text }]}>Tasriif</Text>
        <Text style={[styles.headerSub, { color: theme.textSecondary }]}>Set up your practice session</Text>
      </View>

      {stats.total > 0 && (
        <View style={styles.statsRow}>
          <View style={[styles.statCard, { backgroundColor: theme.card }]}>
            <Text style={[styles.statValue, { color: Colors.palette.success }]}>{stats.score}</Text>
            <Text style={[styles.statLabel, { color: theme.textMuted }]}>Correct</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: theme.card }]}>
            <Text style={[styles.statValue, { color: theme.text }]}>{accuracy}%</Text>
            <Text style={[styles.statLabel, { color: theme.textMuted }]}>Accuracy</Text>
          </View>
          <View style={[styles.statCard, { backgroundColor: theme.card }]}>
            <Text style={[styles.statValue, { color: Colors.palette.gold }]}>{stats.streak}</Text>
            <Text style={[styles.statLabel, { color: theme.textMuted }]}>Streak</Text>
          </View>
        </View>
      )}

      <View style={[styles.sectionCard, { backgroundColor: theme.card }]}>
        <View style={styles.sectionHeader}>
          <Text style={[styles.sectionTitle, { color: theme.text }]}>Tenses</Text>
          <TouchableOpacity onPress={() => setSelectedTenses(new Set(TENSE_ORDER))}>
            <Text style={[styles.selectAllText, { color: theme.tint }]}>All</Text>
          </TouchableOpacity>
        </View>
        <View style={styles.tenseGrid}>
          {TENSE_ORDER.map(t => {
            const selected = selectedTenses.has(t);
            return (
              <TouchableOpacity
                key={t}
                style={[styles.tenseOption, { backgroundColor: selected ? Colors.palette.wine : theme.backgroundSecondary, borderColor: selected ? Colors.palette.wine : theme.border }]}
                onPress={() => toggleTense(t)}
              >
                {selected && <Ionicons name="checkmark" size={14} color="#FFF" style={{ position: 'absolute', top: 8, right: 8 }} />}
                <Text style={[styles.tenseOptionTitle, { color: selected ? '#FFF' : theme.text }]}>{TENSE_NAMES[t]}</Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>

      <View style={[styles.sectionCard, { backgroundColor: theme.card }]}>
        <Text style={[styles.sectionTitle, { color: theme.text, marginBottom: 12 }]}>Mode</Text>
        <View style={{ gap: 8 }}>
          <TouchableOpacity
            style={[styles.modeBtn, { backgroundColor: mode === 'arabic' ? Colors.palette.wine : theme.backgroundSecondary, borderColor: mode === 'arabic' ? Colors.palette.wine : theme.border }]}
            onPress={() => { setMode('arabic'); setConjugationMode('arabic'); Haptics.selectionAsync(); }}
          >
            <Text style={[styles.modeBtnText, { color: mode === 'arabic' ? '#FFF' : theme.text }]}>Arabic prompt</Text>
            <Text style={[styles.modeBtnSub, { color: mode === 'arabic' ? '#FFF' : theme.textMuted }]}>See the Arabic verb + pronoun, type the form</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.modeBtn, { backgroundColor: mode === 'english' ? Colors.palette.wine : theme.backgroundSecondary, borderColor: mode === 'english' ? Colors.palette.wine : theme.border }]}
            onPress={() => { setMode('english'); setConjugationMode('english'); Haptics.selectionAsync(); }}
          >
            <Text style={[styles.modeBtnText, { color: mode === 'english' ? '#FFF' : theme.text }]}>English prompt</Text>
            <Text style={[styles.modeBtnSub, { color: mode === 'english' ? '#FFF' : theme.textMuted }]}>See an English phrase, type the Arabic form</Text>
          </TouchableOpacity>
        </View>
      </View>

      <View style={[styles.sectionCard, { backgroundColor: theme.card }]}>
        <Text style={[styles.sectionTitle, { color: theme.text, marginBottom: 12 }]}>Questions</Text>
        <View style={styles.countRow}>
          {COUNT_OPTIONS.map(c => (
            <TouchableOpacity
              key={c}
              style={[styles.countBtn, { backgroundColor: selectedCount === c ? Colors.palette.wine : theme.backgroundSecondary, borderColor: selectedCount === c ? Colors.palette.wine : theme.border }]}
              onPress={() => { setSelectedCount(c); Haptics.selectionAsync(); }}
            >
              <Text style={[styles.countBtnText, { color: selectedCount === c ? '#FFF' : theme.text }]}>{c}</Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      <View style={[styles.sectionCard, { backgroundColor: theme.card }]}>
        <Text style={[styles.sectionTitle, { color: theme.text, marginBottom: 4 }]}>Verb Types</Text>
        <ToggleRow
          label={`Regular Verbs`}
          sub={`${regularVerbCount} verbs (sound Form I: kataba, shariba, fataha…)`}
          value={verbFilters.includeRegular}
          onChange={v => setVerbFilters(f => ({ ...f, includeRegular: v }))}
          color={Colors.palette.success}
        />
        <ToggleRow
          label={`Irregular Verbs`}
          sub={`${irregularVerbCount} verbs (hollow, defective: qaala, kaana, mashaa…)`}
          value={verbFilters.includeIrregular}
          onChange={v => setVerbFilters(f => ({ ...f, includeIrregular: v }))}
          color={Colors.palette.terracotta}
        />
        <ToggleRow
          label={`Derived Verbs (Forms II–X)`}
          sub={`${derivedVerbCount} verbs (takallama, istata'a, ahabba…)`}
          value={verbFilters.includeDerived}
          onChange={v => setVerbFilters(f => ({ ...f, includeDerived: v }))}
          color={Colors.palette.gold}
        />
        <View style={[styles.reflexiveHint, { backgroundColor: Colors.palette.gold + "18" }]}>
          <Ionicons name="information-circle-outline" size={14} color={Colors.palette.gold} />
          <Text style={[styles.reflexiveHintText, { color: Colors.palette.gold }]}>
            Type in Latin letters: double the long vowels (aa, ii, uu) and use ' for hamza / ayn. Example: aj'alu
          </Text>
        </View>
      </View>

      <View style={[styles.sectionCard, { backgroundColor: theme.card }]}>
        <View style={styles.sectionHeader}>
          <TouchableOpacity 
            style={{ flex: 1, flexDirection: 'row', alignItems: 'center' }}
            onPress={() => { setIsVerbsExpanded(!isVerbsExpanded); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); }}
          >
            <Text style={[styles.sectionTitle, { color: theme.text }]}>Individual Verbs</Text>
            <Ionicons name={isVerbsExpanded ? "chevron-up" : "chevron-down"} size={20} color={theme.textSecondary} />
          </TouchableOpacity>
          {isVerbsExpanded && enabledVerbIds && (
            <TouchableOpacity 
              onPress={() => { 
                const allVerbIds = VERBS.map(v => v.id);
                const isAllSelected = enabledVerbIds.size === allVerbIds.length;
                const next = new Set(isAllSelected ? [] : allVerbIds);
                setEnabledVerbIds(next);
                setEnabledVerbs(Array.from(next));
                Haptics.selectionAsync();
              }}
            >
              <Text style={[styles.selectAllText, { color: theme.tint }]}>
                {enabledVerbIds.size === VERBS.length ? 'Deselect All' : 'Select All'}
              </Text>
            </TouchableOpacity>
          )}
        </View>
        
        {isVerbsExpanded && (
          <View style={{ marginTop: 12, maxHeight: 300 }}>
            <ScrollView nestedScrollEnabled style={{ maxHeight: 250 }}>
              {VERBS.map(v => {
                const isEnabled = !enabledVerbIds || enabledVerbIds.has(v.id);
                return (
                  <TouchableOpacity
                    key={v.id}
                    style={[styles.verbToggleRow, { borderBottomColor: theme.separator }]}
                    onPress={() => toggleVerb(v.id)}
                  >
                    <View style={{ flex: 1 }}>
                      <View style={{ flexDirection: 'row', alignItems: 'center', gap: 8 }}>
                        <Text style={[styles.verbToggleLabel, { color: theme.text }]}>{v.stem}</Text>
                        <View style={[styles.typeBadge, { backgroundColor: v.type === 'irregular' ? Colors.palette.terracotta + '22' : theme.backgroundSecondary }]}>
                          <Text style={[styles.typeBadgeText, { color: v.type === 'irregular' ? Colors.palette.terracotta : theme.textMuted }]}>
                            {v.type === 'irregular' ? 'Irregular' : v.type === 'derived' ? `Form ${v.form}` : 'Regular'}
                          </Text>
                        </View>
                      </View>
                      <Text style={[styles.verbToggleSub, { color: theme.textMuted }]}>{v.english}</Text>
                    </View>
                    <Ionicons 
                      name={isEnabled ? "checkbox" : "square-outline"} 
                      size={24} 
                      color={isEnabled ? Colors.palette.wine : theme.textMuted} 
                    />
                  </TouchableOpacity>
                );
              })}
            </ScrollView>
          </View>
        )}
      </View>

      {!canStart && (
        <View style={[styles.warningBox, { backgroundColor: Colors.palette.error + "18", borderColor: Colors.palette.error + "44" }]}>
          <Ionicons name="warning-outline" size={16} color={Colors.palette.error} />
          <Text style={[styles.warningText, { color: Colors.palette.error }]}>Select at least one verb type to start</Text>
        </View>
      )}

      <TouchableOpacity
        style={[styles.startBtn, { backgroundColor: Colors.palette.wine, opacity: canStart ? 1 : 0.4 }]}
        onPress={() => canStart && (Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success), onStart(Array.from(selectedTenses), selectedCount, verbFilters, mode))}
        disabled={!canStart}
      >
        <Ionicons name="play" size={18} color="#FFF" />
        <Text style={styles.startBtnText}>Start Practice</Text>
      </TouchableOpacity>
    </ScrollView>
  );
}

function ResultsScreen({ score, total, onRetry, onNewSetup }: { score: number; total: number; onRetry: () => void; onNewSetup: () => void }) {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === "dark";
  const theme = isDark ? Colors.dark : Colors.light;
  const insets = useSafeAreaInsets();
  const topPad = Platform.OS === "web" ? 67 : insets.top;
  const bottomPad = Platform.OS === "web" ? 34 : insets.bottom;
  const accuracy = total > 0 ? Math.round((score / total) * 100) : 0;
  const emoji = accuracy >= 90 ? 'Mumtaaz!' : accuracy >= 70 ? 'Jayyid jiddan!' : accuracy >= 50 ? 'Jayyid!' : 'Istamirr!';
  const accentColor = accuracy >= 90 ? Colors.palette.success : accuracy >= 70 ? Colors.palette.gold : Colors.palette.terracotta;

  return (
    <View style={[styles.screen, { backgroundColor: theme.background }]}>
      <ScrollView contentContainerStyle={[styles.resultsContent, { paddingTop: topPad + 32, paddingBottom: bottomPad + 24 }]}>
        <View style={[styles.resultsCard, { backgroundColor: theme.card }]}>
          <View style={[styles.accuracyCircle, { borderColor: accentColor }]}>
            <Text style={[styles.accuracyPct, { color: accentColor }]}>{accuracy}%</Text>
            <Text style={[styles.accuracyLabel, { color: theme.textMuted }]}>accuracy</Text>
          </View>
          <Text style={[styles.resultsTitle, { color: theme.text }]}>{emoji}</Text>
          <Text style={[styles.resultsSubtitle, { color: theme.textSecondary }]}>{score} correct out of {total} questions</Text>
          <View style={[styles.resultsBar, { backgroundColor: theme.backgroundSecondary }]}>
            <View style={[styles.resultsBarFill, { width: `${accuracy}%`, backgroundColor: accentColor }]} />
          </View>
        </View>
        <TouchableOpacity style={[styles.startBtn, { backgroundColor: Colors.palette.wine }]} onPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium); onRetry(); }}>
          <Ionicons name="refresh" size={18} color="#FFF" />
          <Text style={styles.startBtnText}>Same Settings Again</Text>
        </TouchableOpacity>
        <TouchableOpacity style={[styles.outlineBtn, { borderColor: theme.border, backgroundColor: theme.backgroundSecondary }]} onPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); onNewSetup(); }}>
          <Ionicons name="settings-outline" size={18} color={theme.text} />
          <Text style={[styles.outlineBtnText, { color: theme.text }]}>Change Settings</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
}

export default function ConjugationScreen() {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === "dark";
  const theme = isDark ? Colors.dark : Colors.light;
  const insets = useSafeAreaInsets();

  const [phase, setPhase] = useState<Phase>('setup');
  const [queue, setQueue] = useState<Question[]>([]);
  const [queueIdx, setQueueIdx] = useState(0);
  const [sessionScore, setSessionScore] = useState(0);
  const [lastTenses, setLastTenses] = useState<TenseId[]>(['present']);
  const [lastCount, setLastCount] = useState<CountOption>(10);
  const [lastFilters, setLastFilters] = useState<VerbFilters>({ includeRegular: true, includeIrregular: true, includeDerived: true });
  const [mode, setMode] = useState<'arabic' | 'english'>('arabic');

  const [input, setInput] = useState('');
  const [state, setState] = useState<QuestionState>('idle');
  const [stats, setStats] = useState<ConjugationStats>({ score: 0, total: 0, streak: 0 });

  const [streakVisible, setStreakVisible] = useState(false);
  const [streakCount, setStreakCount] = useState(0);
  const streakChecked = useRef(false);

  const shake = useSharedValue(0);
  const bounce = useSharedValue(1);
  const inputRef = useRef<TextInput>(null);

  useEffect(() => { getConjugationStats().then(setStats); }, []);
  
  useEffect(() => { getConjugationMode().then(setMode); }, []);

  useFocusEffect(useCallback(() => {
    streakChecked.current = false;
  }, []));

  const handleFirstActivity = useCallback(async () => {
    if (streakChecked.current) return;
    streakChecked.current = true;
    const result = await checkAndRecordStudyDay();
    if (result.shouldCelebrate) {
      setStreakCount(result.streak);
      setStreakVisible(true);
    }
  }, []);

  const startSession = useCallback(async (tenses: TenseId[], count: CountOption, filters: VerbFilters, selectedMode: 'arabic' | 'english') => {
    const enabledVerbs = await getEnabledVerbs();
    const q = buildQueue(tenses, count, filters, enabledVerbs);
    setLastTenses(tenses);
    setLastCount(count);
    setLastFilters(filters);
    setMode(selectedMode);
    setQueue(q);
    setQueueIdx(0);
    setSessionScore(0);
    setInput('');
    setState('idle');
    setPhase('testing');
    setTimeout(() => inputRef.current?.focus(), 300);
  }, []);

  const retrySession = useCallback(() => {
    startSession(lastTenses, lastCount, lastFilters, mode);
  }, [lastTenses, lastCount, lastFilters, mode, startSession]);

  const getEnglishPrompt = (pronoun: Pronoun, verb: typeof VERBS[0], tense: TenseId): string => {
    const who = PRONOUN_EN[pronoun];
    const third = pronoun === 'huwa' || pronoun === 'hiya';
    const first = pronoun === 'ana';
    const { base, third: thirdForm, past } = verb.en;

    if (verb.isBe) {
      if (tense === 'present') return `${who} (will) be`;
      if (tense === 'past') return `${who} ${first || third ? 'was' : 'were'}`;
      return `${who} will be`;
    }

    switch (tense) {
      case 'present':
        return `${who} ${third ? thirdForm : base}`;
      case 'past':
        return `${who} ${past}`;
      case 'future':
        return `${who} will ${base === 'can' ? 'be able to' : base}`;
      default:
        return `${who} ${base}`;
    }
  };

  const currentQ = queue[queueIdx];
  const isAnswered = state !== 'idle';
  const isLastQuestion = queueIdx === queue.length - 1;

  const checkAnswer = async () => {
    if (!input.trim() || !currentQ) return;
    Keyboard.dismiss();
    await handleFirstActivity();
    
    let correct = answersMatch(input, currentQ.answer);
    
    // Also accept pronoun + conjugation (e.g., "ana aktubu" when the answer is "aktubu")
    if (!correct) {
      const inputLower = input.trim().toLowerCase();
      const answerLower = currentQ.answer.toLowerCase();
      // Check if user answered with "pronoun conjugation" pattern
      const withPronoun = `${currentQ.pronoun} ${answerLower}`;
      if (inputLower === withPronoun || answersMatch(inputLower, withPronoun)) {
        correct = true;
      }
    }
    
    if (correct) {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      setState('correct');
      setSessionScore(s => s + 1);
      bounce.value = withSequence(withSpring(1.05, { damping: 4 }), withSpring(1, { damping: 10 }));
    } else {
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Error);
      setState('wrong');
      shake.value = withSequence(
        withTiming(-8, { duration: 55 }), withTiming(8, { duration: 55 }),
        withTiming(-6, { duration: 55 }), withTiming(6, { duration: 55 }),
        withTiming(0, { duration: 55 })
      );
    }
    const newStats = await recordConjugationAnswer(correct);
    setStats(newStats);
  };

  const nextQuestion = useCallback(async () => {
    if (isLastQuestion) {
      await recordSessionResult(sessionScore, queue.length);
      setPhase('results');
    } else {
      setQueueIdx(i => i + 1);
      setInput('');
      setState('idle');
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isLastQuestion, sessionScore, queue.length, state]);

  const shakeStyle = useAnimatedStyle(() => ({ transform: [{ translateX: shake.value }] }));
  const bounceStyle = useAnimatedStyle(() => ({ transform: [{ scale: bounce.value }] }));

  const topPad = Platform.OS === "web" ? 67 : insets.top;
  const bottomPad = Platform.OS === "web" ? 34 : insets.bottom;

  if (phase === 'setup') return <SetupScreen onStart={startSession} stats={stats} />;
  if (phase === 'results') return <ResultsScreen score={sessionScore} total={queue.length} onRetry={retrySession} onNewSetup={() => setPhase('setup')} />;
  if (!currentQ) return null;

  const progressPct = queue.length > 0 ? (queueIdx / queue.length) * 100 : 0;

  return (
    <KeyboardAvoidingView
      style={[styles.screen, { backgroundColor: theme.background }]}
      behavior={Platform.OS === "ios" ? "padding" : "height"}
      keyboardVerticalOffset={0}
    >
      <StreakBanner streak={streakCount} visible={streakVisible} onHide={() => setStreakVisible(false)} />
      <ScrollView
        contentContainerStyle={[styles.content, { paddingTop: topPad + 16, paddingBottom: bottomPad + 24 }]}
        keyboardShouldPersistTaps="handled"
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.testHeader}>
          <TouchableOpacity onPress={() => { Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light); setPhase('setup'); }} style={[styles.backBtn, { backgroundColor: theme.backgroundSecondary }]}>
            <Ionicons name="chevron-back" size={18} color={theme.text} />
          </TouchableOpacity>
          <View style={styles.testProgress}>
            <Text style={[styles.testProgressText, { color: theme.textSecondary }]}>{queueIdx + 1} / {queue.length}</Text>
            <View style={[styles.progressTrack, { backgroundColor: theme.border }]}>
              <View style={[styles.progressFill, { width: `${progressPct}%`, backgroundColor: Colors.palette.wine }]} />
            </View>
          </View>
          <View style={[styles.scoreChip, { backgroundColor: Colors.palette.success + "22" }]}>
            <Text style={[styles.scoreChipText, { color: Colors.palette.success }]}>{sessionScore}</Text>
          </View>
        </View>

        <Animated.View style={[styles.questionCard, { backgroundColor: theme.card }, bounceStyle]}>
          <View style={styles.questionTop}>
            <View style={{ flexDirection: "row", gap: 6, flexWrap: "wrap", flex: 1 }}>
              <View style={[styles.tensePill, { backgroundColor: Colors.palette.wine + "18" }]}>
                <Text style={[styles.tensePillText, { color: Colors.palette.wine }]}>{TENSE_NAMES[currentQ.tense]}</Text>
              </View>
              {currentQ.verb.type !== 'regular' && (
                <View style={[styles.tensePill, { backgroundColor: Colors.palette.gold + "18" }]}>
                  <Text style={[styles.tensePillText, { color: Colors.palette.gold }]}>
                    {currentQ.verb.type === 'derived' ? `Form ${currentQ.verb.form}` : 'Irregular'}
                  </Text>
                </View>
              )}
            </View>
          </View>
          {mode === 'arabic' ? (
            <>
              <Text style={[styles.verbEnglish, { color: theme.textSecondary }]}>{currentQ.verb.english}</Text>
              <Text style={[styles.verbItalian, { color: theme.text }]}>{currentQ.verb.stem}</Text>
              {currentQ.tense !== 'past' && (
                <Text style={[styles.verbEnglish, { color: theme.textMuted }]}>past: {currentQ.verb.past3} · root: {currentQ.verb.root}</Text>
              )}
              <View style={styles.promptRow}>
                <View style={[styles.pronounBubble, { backgroundColor: Colors.palette.gold + "22" }]}>
                  <Text style={[styles.pronounText, { color: Colors.palette.gold }]}>{currentQ.pronoun}</Text>
                </View>
                <Text numberOfLines={1} style={[styles.pronounEn, { color: theme.textMuted }]}>({PRONOUN_EN[currentQ.pronoun]})</Text>
                <Text style={[styles.blankLine, { color: theme.border }]}>_______________</Text>
              </View>
            </>
          ) : (
            <>
              <Text style={[styles.verbEnglish, { color: theme.textSecondary }]}>Conjugate for:</Text>
              <Text style={[styles.verbItalian, { color: theme.text }]}>{getEnglishPrompt(currentQ.pronoun, currentQ.verb, currentQ.tense)}</Text>
              <View style={styles.promptRow}>
                <Text style={[styles.blankLine, { color: theme.border }]}>_______________</Text>
              </View>
            </>
          )}
          <Text style={[styles.reflexiveNote, { color: theme.textMuted }]}>
            Long vowels are doubled (aa, ii, uu) · ' = hamza / ayn
          </Text>
        </Animated.View>

        <Animated.View style={shakeStyle}>
          <TextInput
            ref={inputRef}
            style={[styles.input, { backgroundColor: theme.card, color: theme.text, borderColor: state === 'correct' ? Colors.palette.success : state === 'wrong' ? Colors.palette.error : state === 'revealed' ? Colors.palette.gold : theme.border }]}
            placeholder="Type conjugation..."
            placeholderTextColor={theme.textMuted}
            value={input}
            onChangeText={setInput}
            autoCapitalize="none"
            autoCorrect={false}
            returnKeyType="done"
            onSubmitEditing={!isAnswered ? checkAnswer : undefined}
            editable={!isAnswered}
          />
        </Animated.View>

        {state === 'correct' && (
          <View style={[styles.feedbackBox, { backgroundColor: Colors.palette.successLight }]}>
            <Ionicons name="checkmark-circle" size={20} color={Colors.palette.success} />
            <Text style={[styles.feedbackText, { color: Colors.palette.success }]}>Mumtaaz! "{currentQ.answer}"</Text>
          </View>
        )}
        {state === 'wrong' && (
          <View style={[styles.feedbackBox, { backgroundColor: Colors.palette.errorLight }]}>
            <Ionicons name="close-circle" size={20} color={Colors.palette.error} />
            <View style={{ flex: 1 }}>
              <Text style={[styles.feedbackText, { color: Colors.palette.error }]}>Answer: "{currentQ.answer}"</Text>
              <Text style={[styles.feedbackSub, { color: Colors.palette.error }]}>You wrote: "{input}"</Text>
            </View>
          </View>
        )}
        {state === 'revealed' && (
          <View style={[styles.feedbackBox, { backgroundColor: Colors.palette.gold + "22" }]}>
            <Ionicons name="eye-outline" size={20} color={Colors.palette.gold} />
            <Text style={[styles.feedbackText, { color: Colors.palette.gold }]}>Answer: "{currentQ.answer}"</Text>
          </View>
        )}

        {!isAnswered ? (
          <View style={styles.btnRow}>
            <TouchableOpacity style={[styles.revealBtn, { backgroundColor: theme.backgroundSecondary, borderColor: theme.border }]} onPress={() => { setState('revealed'); Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium); }}>
              <Ionicons name="eye-outline" size={18} color={theme.textSecondary} />
            </TouchableOpacity>
            <TouchableOpacity style={[styles.checkBtn, { backgroundColor: Colors.palette.wine, opacity: input.trim() ? 1 : 0.5 }]} onPress={checkAnswer} disabled={!input.trim()}>
              <Ionicons name="checkmark" size={20} color="#FFF" />
              <Text style={styles.checkBtnText}>Check</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <TouchableOpacity style={[styles.nextBtn, { backgroundColor: isLastQuestion ? Colors.palette.gold : Colors.palette.wine }]} onPress={nextQuestion}>
            <Text style={styles.nextBtnText}>{isLastQuestion ? 'See Results' : 'Next Question'}</Text>
            <Ionicons name={isLastQuestion ? "trophy-outline" : "arrow-forward"} size={18} color="#FFF" />
          </TouchableOpacity>
        )}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  setupContent: { paddingHorizontal: 20, gap: 14 },
  content: { paddingHorizontal: 20, gap: 14 },
  resultsContent: { paddingHorizontal: 20, gap: 14 },
  setupHeader: { marginBottom: 4 },
  headerTitle: { fontSize: 28, fontFamily: "Inter_700Bold", letterSpacing: -0.5 },
  headerSub: { fontSize: 13, fontFamily: "Inter_400Regular", marginTop: 2 },
  statsRow: { flexDirection: "row", gap: 10 },
  statCard: { flex: 1, paddingVertical: 14, borderRadius: 14, alignItems: "center", shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.06, shadowRadius: 8, elevation: 2 },
  statValue: { fontSize: 22, fontFamily: "Inter_700Bold", letterSpacing: -0.5 },
  statLabel: { fontSize: 10, fontFamily: "Inter_500Medium", marginTop: 2, textTransform: "uppercase", letterSpacing: 0.5 },
  sectionCard: { borderRadius: 16, padding: 16, shadowColor: "#000", shadowOffset: { width: 0, height: 2 }, shadowOpacity: 0.06, shadowRadius: 8, elevation: 2 },
  sectionHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12 },
  sectionTitle: { fontSize: 15, fontFamily: "Inter_600SemiBold" },
  selectAllText: { fontSize: 13, fontFamily: "Inter_600SemiBold" },
  tenseGrid: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  tenseOption: { paddingHorizontal: 14, paddingVertical: 10, paddingRight: 30, borderRadius: 12, borderWidth: 1, position: "relative" },
  tenseOptionTitle: { fontSize: 13, fontFamily: "Inter_500Medium" },
  countRow: { flexDirection: "row", gap: 10 },
  countBtn: { flex: 1, paddingVertical: 14, borderRadius: 12, borderWidth: 1, alignItems: "center", justifyContent: "center" },
  countBtnText: { fontSize: 18, fontFamily: "Inter_700Bold" },
  modeBtn: { paddingVertical: 14, paddingHorizontal: 12, borderRadius: 12, borderWidth: 1 },
  modeBtnText: { fontSize: 14, fontFamily: "Inter_600SemiBold" },
  modeBtnSub: { fontSize: 11, fontFamily: "Inter_400Regular", marginTop: 2 },
  toggleRow: { flexDirection: "row", alignItems: "center", paddingVertical: 12, borderBottomWidth: 0.5 },
  toggleLabel: { fontSize: 14, fontFamily: "Inter_500Medium" },
  toggleSub: { fontSize: 11, fontFamily: "Inter_400Regular", marginTop: 1 },
  toggleTrack: { width: 44, height: 26, borderRadius: 13, padding: 3, justifyContent: "center" },
  toggleThumb: { width: 20, height: 20, borderRadius: 10, backgroundColor: "#FFF" },
  reflexiveHint: { flexDirection: "row", alignItems: "flex-start", gap: 8, paddingHorizontal: 12, paddingVertical: 8, borderRadius: 8, marginTop: 8 },
  reflexiveHintText: { fontSize: 12, fontFamily: "Inter_400Regular", flex: 1 },
  verbToggleRow: { flexDirection: 'row', alignItems: 'center', paddingVertical: 10, borderBottomWidth: 1 },
  verbToggleLabel: { fontSize: 16, fontFamily: "Inter_600SemiBold" },
  verbToggleSub: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
  },
  typeBadge: {
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    marginLeft: 8,
  },
  typeBadgeText: {
    fontSize: 10,
    fontFamily: "Inter_600SemiBold",
    textTransform: "uppercase",
  },
  warningBox: { flexDirection: "row", alignItems: "center", gap: 8, paddingHorizontal: 14, paddingVertical: 10, borderRadius: 10, borderWidth: 1 },
  warningText: { fontSize: 12, fontFamily: "Inter_500Medium" },
  startBtn: { height: 54, borderRadius: 14, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 10 },
  startBtnText: { color: "#FFF", fontSize: 16, fontFamily: "Inter_600SemiBold" },
  outlineBtn: { height: 54, borderRadius: 14, borderWidth: 1.5, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 10 },
  outlineBtnText: { fontSize: 16, fontFamily: "Inter_600SemiBold" },
  testHeader: { flexDirection: "row", alignItems: "center", gap: 12 },
  backBtn: { width: 36, height: 36, borderRadius: 18, alignItems: "center", justifyContent: "center" },
  testProgress: { flex: 1, gap: 4 },
  testProgressText: { fontSize: 12, fontFamily: "Inter_500Medium" },
  progressTrack: { height: 4, borderRadius: 2, overflow: "hidden" },
  progressFill: { height: "100%", borderRadius: 2 },
  scoreChip: { paddingHorizontal: 12, paddingVertical: 6, borderRadius: 12 },
  scoreChipText: { fontSize: 16, fontFamily: "Inter_700Bold" },
  questionCard: { borderRadius: 20, padding: 22, gap: 10, shadowColor: "#000", shadowOffset: { width: 0, height: 6 }, shadowOpacity: 0.08, shadowRadius: 16, elevation: 4 },
  questionTop: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" },
  tensePill: { paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12 },
  tensePillText: { fontSize: 11, fontFamily: "Inter_600SemiBold", letterSpacing: 0.3 },
  speakBtn: { width: 32, height: 32, borderRadius: 16, alignItems: "center", justifyContent: "center" },
  verbEnglish: { fontSize: 13, fontFamily: "Inter_400Regular" },
  verbItalian: { fontSize: 28, fontFamily: "Inter_700Bold", letterSpacing: -0.5 },
  promptRow: { flexDirection: "row", alignItems: "center", gap: 12, marginTop: 4 },
  pronounBubble: { paddingHorizontal: 14, paddingVertical: 6, borderRadius: 20 },
  pronounText: { fontSize: 16, fontFamily: "Inter_600SemiBold" },
  pronounEn: { fontSize: 12, fontFamily: "Inter_400Regular", flexShrink: 0 },
  blankLine: { fontSize: 20, fontFamily: "Inter_400Regular", flex: 1, letterSpacing: 3 },
  reflexiveNote: { fontSize: 11, fontFamily: "Inter_400Regular", fontStyle: "italic" },
  input: { height: 54, borderRadius: 14, paddingHorizontal: 18, fontSize: 18, fontFamily: "Inter_500Medium", borderWidth: 2 },
  feedbackBox: { flexDirection: "row", alignItems: "flex-start", gap: 10, paddingHorizontal: 16, paddingVertical: 12, borderRadius: 12 },
  feedbackText: { fontSize: 15, fontFamily: "Inter_600SemiBold", flex: 1 },
  feedbackSub: { fontSize: 12, fontFamily: "Inter_400Regular", marginTop: 2, opacity: 0.8 },
  btnRow: { flexDirection: "row", gap: 10 },
  revealBtn: { width: 54, height: 54, borderRadius: 14, alignItems: "center", justifyContent: "center", borderWidth: 1 },
  checkBtn: { flex: 1, height: 54, borderRadius: 14, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8 },
  checkBtnText: { color: "#FFF", fontSize: 16, fontFamily: "Inter_600SemiBold" },
  nextBtn: { height: 54, borderRadius: 14, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8 },
  nextBtnText: { color: "#FFF", fontSize: 16, fontFamily: "Inter_600SemiBold" },
  resultsCard: { borderRadius: 20, padding: 32, alignItems: "center", gap: 12, shadowColor: "#000", shadowOffset: { width: 0, height: 6 }, shadowOpacity: 0.08, shadowRadius: 16, elevation: 4 },
  accuracyCircle: { width: 120, height: 120, borderRadius: 60, borderWidth: 4, alignItems: "center", justifyContent: "center", marginBottom: 8 },
  accuracyPct: { fontSize: 32, fontFamily: "Inter_700Bold", letterSpacing: -1 },
  accuracyLabel: { fontSize: 12, fontFamily: "Inter_400Regular" },
  resultsTitle: { fontSize: 26, fontFamily: "Inter_700Bold", letterSpacing: -0.5 },
  resultsSubtitle: { fontSize: 14, fontFamily: "Inter_400Regular" },
  resultsBar: { width: "100%", height: 8, borderRadius: 4, overflow: "hidden", marginTop: 8 },
  resultsBarFill: { height: "100%", borderRadius: 4 },
});
