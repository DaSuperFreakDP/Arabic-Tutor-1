/**
 * Normalise a typed Arabic (Latin transcription) answer for comparison.
 *  - case / accents / macrons are ignored (ā -> aa, ī -> ii, ū -> uu)
 *  - every apostrophe-like mark (' ’ ʿ ʾ ` ´) counts as the same hamza/ayn mark
 *  - hyphens are ignored (sa-aktubu == saaktubu)
 *  - ee / oo are accepted for ii / uu
 */
export function normalizeAnswer(s: string): string {
  return s
    .toLowerCase()
    .trim()
    .replace(/[āâ]/g, 'aa')
    .replace(/[īî]/g, 'ii')
    .replace(/[ūû]/g, 'uu')
    .normalize('NFD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[‘’ʻʼʿʾ`´]/g, "'")
    .replace(/-/g, '')
    .replace(/ee/g, 'ii')
    .replace(/oo/g, 'uu')
    .replace(/\s+/g, ' ');
}

function dropMarks(s: string): string {
  return s.replace(/'/g, '');
}

/**
 * True when the typed answer matches. A missing hamza/ayn mark is forgiven,
 * but vowel length (a vs aa) still has to be right.
 */
export function answersMatch(userInput: string, correctAnswer: string): boolean {
  const normUser = normalizeAnswer(userInput);
  const alternatives = correctAnswer.split('/').map(a => normalizeAnswer(a.trim()));
  return alternatives.some(a => normUser === a || dropMarks(normUser) === dropMarks(a));
}

export function getTodayKey(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
}

export function getPreviousDay(dateKey: string): string {
  const [year, month, day] = dateKey.split('-').map(Number);
  const d = new Date(year, month - 1, day);
  d.setDate(d.getDate() - 1);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
}

export function calculateDailyStreak(days: string[]): number {
  if (days.length === 0) return 0;
  const daySet = new Set(days);
  const today = getTodayKey();
  let streak = 0;
  let current = today;
  while (daySet.has(current)) {
    streak++;
    current = getPreviousDay(current);
  }
  return streak;
}

export function getStreakMessage(streak: number): string {
  if (streak >= 30) return `Shahr kaamil! Thirty days of pure dedication!`;
  if (streak >= 21) return `Thalaathat asaabii'! Twenty-one days - you're a linguist!`;
  if (streak >= 14) return `Usbuu'aan! Two incredible weeks straight!`;
  if (streak >= 10) return `'Ashrat ayyaam! Ten days strong - you're on fire!`;
  if (streak >= 7) return `Usbuu' kaamil! One full week - absolutely unstoppable!`;
  if (streak >= 5) return `Khamsat ayyaam! Five days of hard work pays off!`;
  if (streak >= 4) return `Arba'at ayyaam! Four days and going strong!`;
  if (streak >= 3) return `Thalaathat ayyaam! Three days in - a habit is forming!`;
  if (streak >= 2) return `Yawmaan! Two days in a row - keep the momentum!`;
  return `Yawm waahid! Today is just the beginning!`;
}

export function getStreakFireEmojis(streak: number): string {
  if (streak >= 30) return '🔥🔥🔥🔥🔥';
  if (streak >= 14) return '🔥🔥🔥🔥';
  if (streak >= 7) return '🔥🔥🔥';
  if (streak >= 3) return '🔥🔥';
  return '🔥';
}
