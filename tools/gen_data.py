#!/usr/bin/env python3
"""Generate lib/arabic-data.ts from verbs.py + vocab.txt + verb_examples.txt.

Run from the project root:  python3 tools/gen_data.py
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import verbs as V  # noqa: E402
import verbs_ar as VA  # noqa: E402
from arabic import matches, reverse  # noqa: E402

PRON = V.PRON


def j(s):
    return json.dumps(s, ensure_ascii=False)


def conj_obj(forms):
    return '{ ' + ', '.join(f'{p}: {j(forms[p])}' for p in PRON) + ' }'


# ----------------------------------------------------------------- parse ---
def parse_vocab(path):
    sections, cur = {}, None
    for raw in open(path, encoding='utf-8'):
        line = raw.rstrip('\n')
        if not line.strip() or line.startswith('#') and not line.startswith('##'):
            continue
        if line.startswith('##'):
            cur = line[2:].strip()
            sections[cur] = []
            continue
        parts = [p.strip() for p in line.split('|')]
        assert len(parts) == 6, f'bad vocab line ({len(parts)} fields): {line}'
        ar, en, g, note, ex, ex_en = parts
        sections[cur].append(dict(arabic=ar, english=en, gender=g, note=note, example=ex, exampleTranslation=ex_en))
    return sections


def parse_verb_examples(path):
    out = {}
    for raw in open(path, encoding='utf-8'):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        parts = [p.strip() for p in line.split('|')]
        assert len(parts) == 3, line
        out[parts[0]] = (parts[1], parts[2])
    return out


def parse_script(path):
    """latin headword | arabic | reads-as (optional)  ->  {latin: (arabic, reads_as)}"""
    out = {}
    for raw in open(path, encoding='utf-8'):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        parts = [p.strip() for p in line.split('|')]
        assert len(parts) in (2, 3), f'bad script line: {line}'
        out[parts[0]] = (parts[1], parts[2] if len(parts) == 3 else None)
    return out


vocab = parse_vocab(os.path.join(HERE, 'vocab.txt'))
vex = parse_verb_examples(os.path.join(HERE, 'verb_examples.txt'))
script = parse_script(os.path.join(HERE, 'script_ar.txt'))

# ---------------------------------------------------------------- checks ---
errors = []

# Arabic script (speech only) must back-transliterate to the Latin shown on screen.
all_heads = [e['arabic'] for sec in vocab.values() for e in sec]
for h in all_heads:
    if h not in script:
        errors.append(f"no Arabic script for headword '{h}' (tools/script_ar.txt)")
        continue
    ar, reads_as = script[h]
    try:
        ok = matches(ar, h, reads_as)
    except ValueError as ex:
        ok, ar = False, f'{ar} ({ex})'
    if not ok:
        errors.append(f"script for '{h}' reads as '{reverse(script[h][0])}': {ar}")
for k in script:
    if k not in all_heads:
        errors.append(f"script entry for unknown headword '{k}'")
for v in V.VERBS:
    if v['id'] not in VA.AR:
        errors.append(f"no Arabic forms for verb {v['id']}")
        continue
    for tense, forms in zip(('present', 'past'), VA.AR[v['id']]):
        for p in PRON:
            if not matches(forms[p], v[tense][p]):
                errors.append(f"{v['id']} {tense} {p}: latin '{v[tense][p]}' vs arabic {forms[p]} "
                              f"(reads '{reverse(forms[p])}')")

ids = [v['id'] for v in V.VERBS]
if len(ids) != len(set(ids)):
    errors.append('duplicate verb ids')
for v in V.VERBS:
    if v['id'] not in vex:
        errors.append(f"no example for verb {v['id']}")
        continue
    ex = vex[v['id']][0]
    toks = set(re.findall(r"[a-z']+", ex.lower().replace('-', ' ')))
    forms = set(v['present'].values())
    if not (toks & forms):
        errors.append(f"example for {v['id']} contains none of its present forms: {ex}")
for k in vex:
    if k not in ids:
        errors.append(f'example for unknown verb {k}')

# ------------------------------------------------------------- flashcards --
cards = []
seen_en, seen_ar = {}, {}


def add_card(card):
    key_en = card['english'].lower()
    key_ar = card['arabic'].lower()
    if key_en in seen_en:
        errors.append(f"duplicate english '{card['english']}' ({card['id']} vs {seen_en[key_en]})")
    if key_ar in seen_ar:
        errors.append(f"duplicate arabic '{card['arabic']}' ({card['id']} vs {seen_ar[key_ar]})")
    seen_en[key_en] = card['id']
    seen_ar[key_ar] = card['id']
    cards.append(card)


prefix = {'noun': 'n', 'adjective': 'a', 'adverb': 'ad', 'other': 'o'}
for typ in ('noun', 'verb', 'adjective', 'adverb', 'other'):
    if typ == 'verb':
        for i, v in enumerate(V.VERBS, 1):
            ex = vex[v['id']]
            en_inf = v['english']
            note = f"past: {v['past3']} · I {v['en'][0]}: {v['present']['ana']}"
            if v['id'] == 'kaana':
                note = f"past: {v['past3']} · I will be: {v['present']['ana']}"
            pres_ar, past_ar = VA.AR[v['id']]
            spoken = f"{past_ar['huwa']}، {pres_ar['ana']}"   # "kataba, aktubu" (same two forms as the note)
            add_card(dict(id=f'v{i}', arabic=v['stem'], english=en_inf, type='verb', gender='',
                          note=note, example=ex[0], exampleTranslation=ex[1], script=spoken))
        continue
    for i, e in enumerate(vocab[typ], 1):
        gender = {'m': 'masculine', 'f': 'feminine', '': ''}[e['gender']]
        add_card(dict(id=f'{prefix[typ]}{i}', arabic=e['arabic'], english=e['english'], type=typ,
                      gender=gender, note=e['note'], example=e['example'],
                      exampleTranslation=e['exampleTranslation'], script=script[e['arabic']][0]))

if errors:
    print('DATA ERRORS:')
    for e in errors:
        print('  -', e)
    sys.exit(1)

# ------------------------------------------------------------------ emit ---
out = []
w = out.append
w('// AUTO-GENERATED by tools/gen_data.py -- edit tools/verbs.py / vocab.txt / verb_examples.txt, then re-run.')
w('// Latin transcription: long vowels doubled (aa, ii, uu); \' = hamza / ayn; emphatic letters written plain.')
w('')
w("export type WordType = 'noun' | 'verb' | 'adjective' | 'adverb' | 'other';")
w('')
w('export interface Flashcard {')
w('  id: string;')
w('  arabic: string;')
w('  arabic_alias?: string;')
w('  english: string;')
w('  type: WordType;')
w("  gender?: 'masculine' | 'feminine';")
w('  note?: string;')
w('  example?: string;')
w('  exampleTranslation?: string;')
w('  /** Vocalised Arabic script, never shown: it is what the Arabic voice speaks. */')
w('  script: string;')
w('}')
w('')
w('export interface Conjugation {')
for p in PRON:
    w(f'  {p}: string;')
w('}')
w('')
w("export type TenseId = 'present' | 'past' | 'future';")
w('')
w('export interface Verb {')
w('  id: string;')
w('  /** Dictionary headword in the style of the notes: 3rd person present minus ya-/yu- (e.g. ktubu). */')
w('  stem: string;')
w('  /** 3rd person masculine past (e.g. kataba). */')
w('  past3: string;')
w('  root: string;')
w('  english: string;')
w('  en: { base: string; third: string; past: string };')
w("  type: 'regular' | 'irregular' | 'derived';")
w('  form: string;')
w('  isBe?: boolean;')
w('  tenses: Record<TenseId, Conjugation>;')
w('  /** Vocalised Arabic script of every form in `tenses` (speech only, never shown). */')
w('  script: Record<TenseId, Conjugation>;')
w('}')
w('')
w('export interface TenseInfo {')
w('  id: TenseId;')
w('  name: string;')
w('  arabicName: string;')
w('  when: string;')
w('  trigger?: string;')
w('  examples: { arabic: string; english: string }[];')
w('  formation?: string;')
w('}')
w('')

w('export const FLASHCARDS: Flashcard[] = [')
last = None
for c in cards:
    if c['type'] != last:
        w(f"  // {c['type']}s")
        last = c['type']
    fields = [f"id: {j(c['id'])}", f"arabic: {j(c['arabic'])}", f"english: {j(c['english'])}", f"type: {j(c['type'])}",
              f"script: {j(c['script'])}"]
    if c['gender']:
        fields.append(f"gender: {j(c['gender'])}")
    if c['note']:
        fields.append(f"note: {j(c['note'])}")
    if c['example']:
        fields.append(f"example: {j(c['example'])}")
        fields.append(f"exampleTranslation: {j(c['exampleTranslation'])}")
    w('  { ' + ', '.join(fields) + ' },')
w('];')
w('')

w('export const VERBS: Verb[] = [')
for v in V.VERBS:
    fut = {p: 'sa-' + f for p, f in v['present'].items()}
    w('  {')
    w(f"    id: {j(v['id'])},")
    w(f"    stem: {j(v['stem'])},")
    w(f"    past3: {j(v['past3'])},")
    w(f"    root: {j(v['root'])},")
    w(f"    english: {j(v['english'])},")
    w(f"    en: {{ base: {j(v['en'][0])}, third: {j(v['en'][1])}, past: {j(v['en'][2])} }},")
    w(f"    type: {j(v['type'])},")
    w(f"    form: {j(v['form'])},")
    if v['extra'].get('be'):
        w('    isBe: true,')
    w('    tenses: {')
    w(f"      present: {conj_obj(v['present'])},")
    w(f"      past: {conj_obj(v['past'])},")
    w(f"      future: {conj_obj(fut)},")
    w('    },')
    pres_ar, past_ar = VA.AR[v['id']]
    fut_ar = {p: 'سَ' + f for p, f in pres_ar.items()}
    w('    script: {')
    w(f"      present: {conj_obj(pres_ar)},")
    w(f"      past: {conj_obj(past_ar)},")
    w(f"      future: {conj_obj(fut_ar)},")
    w('    },')
    w('  },')
w('];')
w('')

w('export const PRONOUNS = [' + ', '.join(j(p) for p in PRON) + '] as const;')
w('')
w('export type Pronoun = typeof PRONOUNS[number];')
w('')
w('export const PRONOUN_KEYS: Record<Pronoun, keyof Conjugation> = {')
for p in PRON:
    w(f'  {p}: {j(p)},')
w('};')
w('')
EN = dict(ana='I', anta='you (m)', anti='you (f)', huwa='he', hiya='she', nahnu='we',
          antum='you all (m)', antunna='you all (f)', hum='they (m)', hunna='they (f)')
w('/** English labels used in prompts and tables. */')
w('export const PRONOUN_EN: Record<Pronoun, string> = {')
for p in PRON:
    w(f'  {p}: {j(EN[p])},')
w('};')
w('')
w('export const TENSE_NAMES: Record<TenseId, string> = {')
w("  present: 'Present',")
w("  past: 'Past',")
w("  future: 'Future',")
w('};')
w('')
w('/** Verbs shown as worked examples on the Tenses tab. */')
w('export const EXAMPLE_VERBS: { label: string; id: string }[] = [')
w("  { label: 'Regular verb', id: 'kataba' },")
w("  { label: 'Hollow verb (middle weak letter)', id: 'qaala' },")
w("  { label: 'Defective verb (last weak letter)', id: 'mashaa' },")
w("  { label: 'Derived verb (Form V)', id: 'takallama' },")
w('];')
w('')
w('export const TENSE_INFO: TenseInfo[] = [')
w('  {')
w("    id: 'present',")
w("    name: 'Present',")
w("    arabicName: \"Al-Mudaari'\",")
w("    when: 'Actions happening now, habits and general truths. After \"an\" (to) it also means \"to ...\": uriidu an aktuba = I want to write.',")
w("    formation: 'Prefix + stem + ending. Prefixes: a- (I), ta- (you / she), ya- (he / they), na- (we). Endings: -u, -iina (you f), -uuna (you all m / they m), -na (you all f / they f).',")
w('    examples: [')
w("      { arabic: 'aktubu risaala.', english: 'I write a letter.' },")
w("      { arabic: 'hiya tatakallamu al-\\'arabiyya.', english: 'She speaks Arabic.' },")
w("      { arabic: 'nadhhabu ilaa al-madrasa kulla yawm.', english: 'We go to school every day.' },")
w('    ],')
w('  },')
w('  {')
w("    id: 'past',")
w("    name: 'Past',")
w("    arabicName: 'Al-Maadii',")
w("    when: 'Completed actions in the past.',")
w("    formation: 'Stem (3rd person masculine, e.g. kataba) + endings: -tu (I), -ta (you m), -ti (you f), -a (he), -at (she), -naa (we), -tum (you all m), -tunna (you all f), -uu (they m), -na (they f).',")
w('    examples: [')
w("      { arabic: 'ams katabtu risaala.', english: 'Yesterday I wrote a letter.' },")
w("      { arabic: 'dhahaba ilaa as-suuq.', english: 'He went to the market.' },")
w("      { arabic: 'akalnaa fii al-mat\\'am.', english: 'We ate at the restaurant.' },")
w('    ],')
w('  },')
w('  {')
w("    id: 'future',")
w("    name: 'Future',")
w("    arabicName: 'Al-Mustaqbal',")
w("    when: 'Actions that will happen.',")
w("    trigger: 'sa- or sawfa + present tense',")
w("    formation: 'Attach sa- to the front of the present tense form (sa-aktubu = I will write). The word sawfa + present works the same way.',")
w('    examples: [')
w("      { arabic: 'sa-aktubu risaala ghadan.', english: 'I will write a letter tomorrow.' },")
w("      { arabic: 'sa-nadhhabu ilaa al-bahr.', english: 'We will go to the sea.' },")
w("      { arabic: 'sawfa yaktubuuna ad-dars.', english: 'They will write the lesson.' },")
w('    ],')
w('  },')
w('];')
w('')

target = os.path.join(ROOT, 'lib', 'arabic-data.ts')
open(target, 'w', encoding='utf-8').write('\n'.join(out))
by_type = {}
for c in cards:
    by_type[c['type']] = by_type.get(c['type'], 0) + 1
print('wrote', target)
print('flashcards:', len(cards), by_type)
print('verbs:', len(V.VERBS), {t: sum(1 for v in V.VERBS if v['type'] == t) for t in ('regular', 'irregular', 'derived')})
