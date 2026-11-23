import React, { useState, useCallback } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  useColorScheme,
  Pressable,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import Colors from "@/constants/colors";
import {
  TENSE_INFO,
  VERBS,
  EXAMPLE_VERBS,
  PRONOUNS,
  PRONOUN_EN,
  Conjugation,
  TenseId,
} from "@/lib/arabic-data";
import { checkAndRecordStudyDay } from "@/lib/progress-storage";

// The a- / ta- / ya- / na- chart from the study notes.
const PRESENT_PATTERN: Record<(typeof PRONOUNS)[number], string> = {
  ana: "a- … -u",
  anta: "ta- … -u",
  anti: "ta- … -iina",
  huwa: "ya- … -u",
  hiya: "ta- … -u",
  nahnu: "na- … -u",
  antum: "ta- … -uuna",
  antunna: "ta- … -na",
  hum: "ya- … -uuna",
  hunna: "ya- … -na",
};

export default function TensesScreen() {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === "dark";
  const theme = isDark ? Colors.dark : Colors.light;
  const insets = useSafeAreaInsets();
  const [expanded, setExpanded] = useState<string | null>(null);

  useFocusEffect(
    useCallback(() => {
      checkAndRecordStudyDay();
    }, [])
  );

  const getVerbExample = (tenseId: TenseId, verbId: string) => {
    const verb = VERBS.find((v) => v.id === verbId);
    if (!verb) return null;
    const conjugation = verb.tenses[tenseId];
    if (!conjugation) return null;
    return { verb, conjugation };
  };

  const kataba = VERBS.find((v) => v.id === "kataba");
  const patternOpen = expanded === "pattern";

  return (
    <View style={[styles.container, { backgroundColor: theme.background }]}>
      <ScrollView
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + 16, paddingBottom: insets.bottom + 96 },
        ]}
        showsVerticalScrollIndicator={false}
      >
        <Text style={[styles.title, { color: theme.text }]}>Arabic Tenses</Text>

        {/* Pronouns + present tense pattern */}
        <View>
          <Pressable
            onPress={() => setExpanded(patternOpen ? null : "pattern")}
            style={[styles.tenseButton, { backgroundColor: theme.card, borderColor: theme.border }]}
          >
            <View style={{ flex: 1 }}>
              <Text style={[styles.tenseName, { color: theme.tint }]}>Pronouns & Present Pattern</Text>
              <Text style={[styles.englishName, { color: theme.textSecondary }]}>
                The a- / ta- / ya- / na- chart
              </Text>
            </View>
            <Ionicons
              name={patternOpen ? "chevron-up" : "chevron-down"}
              size={20}
              color={theme.textSecondary}
            />
          </Pressable>

          {patternOpen && (
            <View
              style={[
                styles.expandedContent,
                { backgroundColor: theme.backgroundSecondary, borderColor: theme.border },
              ]}
            >
              <View style={styles.section}>
                <Text style={[styles.sectionText, { color: theme.tabIconDefault }]}>
                  Arabic has separate forms for masculine (m) and feminine (f) "you" and "they". Present
                  tense = prefix + stem + ending. Example with ktubu (write):
                </Text>
              </View>
              <View style={styles.table}>
                {PRONOUNS.map((p) => (
                  <View key={p} style={[styles.patternRow, { borderBottomColor: theme.separator }]}>
                    <View style={{ minWidth: 92 }}>
                      <Text style={[styles.tableLabel, { color: theme.tint }]}>{p}</Text>
                      <Text style={[styles.pronounEn, { color: theme.textMuted }]}>{PRONOUN_EN[p]}</Text>
                    </View>
                    <Text style={[styles.patternText, { color: theme.textSecondary }]}>{PRESENT_PATTERN[p]}</Text>
                    <Text style={[styles.tableValue, { color: theme.text }]}>
                      {kataba ? kataba.tenses.present[p] : ""}
                    </Text>
                  </View>
                ))}
              </View>
            </View>
          )}
        </View>

        {TENSE_INFO.map((tense) => {
          const isExpanded = expanded === tense.id;

          return (
            <View key={tense.id}>
              <Pressable
                onPress={() => setExpanded(isExpanded ? null : tense.id)}
                style={[styles.tenseButton, { backgroundColor: theme.card, borderColor: theme.border }]}
              >
                <View style={{ flex: 1 }}>
                  <Text style={[styles.tenseName, { color: theme.tint }]}>{tense.arabicName}</Text>
                  <Text style={[styles.englishName, { color: theme.textSecondary }]}>{tense.name}</Text>
                </View>
                <Ionicons
                  name={isExpanded ? "chevron-up" : "chevron-down"}
                  size={20}
                  color={theme.textSecondary}
                />
              </Pressable>

              {isExpanded && (
                <View
                  style={[
                    styles.expandedContent,
                    { backgroundColor: theme.backgroundSecondary, borderColor: theme.border },
                  ]}
                >
                  {/* When to use */}
                  <View style={styles.section}>
                    <Text style={[styles.sectionTitle, { color: theme.text }]}>When to use</Text>
                    <Text style={[styles.sectionText, { color: theme.tabIconDefault }]}>{tense.when}</Text>
                  </View>

                  {/* Trigger */}
                  {tense.trigger && (
                    <View style={styles.section}>
                      <Text style={[styles.sectionTitle, { color: theme.text }]}>Marker</Text>
                      <Text style={[styles.sectionText, { color: theme.tabIconDefault }]}>{tense.trigger}</Text>
                    </View>
                  )}

                  {/* Formation */}
                  {tense.formation && (
                    <View style={styles.section}>
                      <Text style={[styles.sectionTitle, { color: theme.text }]}>Formation</Text>
                      <Text style={[styles.sectionText, { color: theme.tabIconDefault }]}>{tense.formation}</Text>
                    </View>
                  )}

                  {/* Examples */}
                  <View style={styles.section}>
                    <Text style={[styles.sectionTitle, { color: theme.text }]}>Examples</Text>
                    {tense.examples.map((example, idx) => (
                      <View key={idx} style={styles.exampleBox}>
                        <Text style={[styles.exampleArabic, { color: theme.text }]}>{example.arabic}</Text>
                        <Text style={[styles.exampleEnglish, { color: theme.textSecondary }]}>
                          {example.english}
                        </Text>
                      </View>
                    ))}
                  </View>

                  {/* Conjugation tables */}
                  <View style={styles.section}>
                    <Text style={[styles.sectionTitle, { color: theme.text }]}>Conjugation Examples</Text>
                    {EXAMPLE_VERBS.map((ex) => {
                      const found = getVerbExample(tense.id, ex.id);
                      if (!found) return null;
                      return (
                        <View key={ex.id} style={styles.verbSection}>
                          <Text style={[styles.verbLabel, { color: theme.tint }]}>
                            {ex.label}: {found.verb.stem} · {found.verb.english}
                          </Text>
                          <ConjugationTable conjugation={found.conjugation} theme={theme} />
                        </View>
                      );
                    })}
                  </View>
                </View>
              )}
            </View>
          );
        })}
      </ScrollView>
    </View>
  );
}

function ConjugationTable({
  conjugation,
  theme,
}: {
  conjugation: Conjugation;
  theme: typeof Colors.light | typeof Colors.dark;
}) {
  return (
    <View style={styles.table}>
      {PRONOUNS.map((key) => (
        <View key={key} style={[styles.tableRow, { borderBottomColor: theme.separator }]}>
          <View style={{ minWidth: 92 }}>
            <Text style={[styles.tableLabel, { color: theme.tint }]}>{key}</Text>
            <Text style={[styles.pronounEn, { color: theme.textMuted }]}>{PRONOUN_EN[key]}</Text>
          </View>
          <Text style={[styles.tableValue, { color: theme.text }]}>{conjugation[key] || "—"}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  content: {
    paddingHorizontal: 16,
  },
  title: {
    fontSize: 28,
    fontFamily: "Inter_700Bold",
    marginBottom: 16,
  },
  tenseButton: {
    flexDirection: "row",
    alignItems: "center",
    borderRadius: 12,
    borderWidth: 1,
    paddingVertical: 14,
    paddingHorizontal: 16,
    marginBottom: 12,
  },
  tenseName: {
    fontSize: 16,
    fontFamily: "Inter_600SemiBold",
  },
  englishName: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
    marginTop: 2,
  },
  expandedContent: {
    borderRadius: 12,
    borderWidth: 1,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginBottom: 12,
    marginTop: -10,
  },
  section: {
    marginBottom: 14,
  },
  sectionTitle: {
    fontSize: 13,
    fontFamily: "Inter_600SemiBold",
    marginBottom: 6,
  },
  sectionText: {
    fontSize: 12,
    fontFamily: "Inter_400Regular",
    lineHeight: 16,
  },
  exampleBox: {
    backgroundColor: "rgba(0, 0, 0, 0.05)",
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 10,
    marginBottom: 6,
  },
  exampleArabic: {
    fontSize: 12,
    fontFamily: "Inter_500Medium",
    marginBottom: 2,
  },
  exampleEnglish: {
    fontSize: 11,
    fontFamily: "Inter_400Regular",
  },
  verbSection: {
    marginBottom: 12,
  },
  verbLabel: {
    fontSize: 12,
    fontFamily: "Inter_600SemiBold",
    marginBottom: 6,
  },
  table: {
    borderRadius: 8,
    overflow: "hidden",
  },
  tableRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 6,
    paddingHorizontal: 8,
    borderBottomWidth: 0.5,
  },
  patternRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingVertical: 6,
    paddingHorizontal: 8,
    borderBottomWidth: 0.5,
  },
  tableLabel: {
    fontSize: 12,
    fontFamily: "Inter_600SemiBold",
  },
  pronounEn: {
    fontSize: 10,
    fontFamily: "Inter_400Regular",
  },
  patternText: {
    fontSize: 11,
    fontFamily: "Inter_500Medium",
    minWidth: 78,
  },
  tableValue: {
    fontSize: 12,
    fontFamily: "Inter_500Medium",
    flex: 1,
    textAlign: "right",
  },
});
