#!/usr/bin/env python3
"""Generate lib/phrases.ts for the sentence-builder game.

Run from the project root:  python3 tools/gen_phrases.py

Every phrase is a list of word BLOCKS (Latin shown on screen + hidden vocalised Arabic for the voice),
an English translation and a syntax tip. Blocks are built from vocab/verb data, and every block's
Arabic is verified (tools/arabic.py) against the Latin it is displayed with.
"""
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import verbs as V  # noqa: E402
import verbs_ar as VA  # noqa: E402
from arabic import FATHA, SHADDA, matches, reverse  # noqa: E402

rng = random.Random(20261123)
errors = []


# ------------------------------------------------------------ script data --
def parse_script(path):
    out = {}
    for raw in open(path, encoding='utf-8'):
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        p = [x.strip() for x in line.split('|')]
        out[p[0]] = (p[1], p[2] if len(p) == 3 else None)
    return out


SCRIPT = parse_script(os.path.join(HERE, 'script_ar.txt'))
SCRIPT['hal'] = ('هَلْ', None)           # question particle (not a flashcard word)

PRON_EN = dict(ana='I', anta='you (m)', anti='you (f)', huwa='he', hiya='she', nahnu='we',
               antum='you all (m)', antunna='you all (f)', hum='they (m)', hunna='they (f)')
VERB = {v['id']: v for v in V.VERBS}


# ------------------------------------------------------------ definiteness --
SUN_LATIN = ['sh', 'th', 'dh', 't', 'd', 'r', 'z', 's', 'n', 'l']
SUN_AR = set('تثدذرزسشصضطظلن')


def definite_latin(w):
    for c in SUN_LATIN:
        if w.startswith(c):
            return f'a{c}-{w}'
    return 'al-' + w


def definite_ar(ar):
    if ar[0] in SUN_AR:
        return 'ال' + ar[0] + SHADDA + ar[1:]
    return 'الْ' + ar


# ------------------------------------------------------------ block registry --
BLOCKS, _index = {}, {}


def blk(pos, latin, arabic, en, tag='', reads_as=None, clitic=False):
    k = (pos, latin, arabic, en, tag)
    if k not in _index:
        try:
            ok = matches(arabic, latin, reads_as)
        except ValueError as ex:
            ok = False
            arabic = f'{arabic} ({ex})'
        if not ok:
            errors.append(f"block '{latin}' ({pos}): arabic {arabic} reads '{reverse(arabic) if ok is not False else '?'}'")
        bid = f'b{len(BLOCKS)}'
        BLOCKS[bid] = dict(latin=latin, arabic=arabic, en=en, pos=pos)
        if tag:
            BLOCKS[bid]['tag'] = tag
        if clitic:
            BLOCKS[bid]['clitic'] = True
        _index[k] = bid
    return _index[k]


# ---------------------------------------------------------------- lexicon --
# latin headword: (english, gender, mass noun?)
NOUNS = {
    # people
    'walad': ('boy', 'm', 0), 'bint': ('girl', 'f', 0), 'rajul': ('man', 'm', 0), "imra'a": ('woman', 'f', 0),
    "mu'allim": ('teacher (m)', 'm', 0), "mu'allima": ('teacher (f)', 'f', 0), 'tabiib': ('doctor', 'm', 0),
    'taalib': ('student', 'm', 0), 'tifl': ('child', 'm', 0), 'jadda': ('grandmother', 'f', 0),
    'umm': ('mother', 'f', 0), 'ab': ('father', 'm', 0), 'sadiiq': ('friend (m)', 'm', 0), 'sadiiqa': ('friend (f)', 'f', 0),
    # places
    'madrasa': ('school', 'f', 0), 'suuq': ('market', 'm', 0), "jaami'a": ('university', 'f', 0),
    'maktaba': ('library', 'f', 0), 'hadiiqa': ('garden', 'f', 0), "mat'am": ('restaurant', 'm', 0),
    'mustashfaa': ('hospital', 'm', 0), 'bahr': ('sea', 'm', 0), 'masjid': ('mosque', 'm', 0),
    'funduq': ('hotel', 'm', 0), 'bayt': ('house', 'm', 0), 'ghurfa': ('room', 'f', 0), 'matbakh': ('kitchen', 'm', 0),
    'madiina': ('city', 'f', 0), "shaati'": ('beach', 'm', 0), 'maktab': ('office', 'm', 0), "shaari'": ('street', 'm', 0),
    # things
    'kitaab': ('book', 'm', 0), 'qalam': ('pen', 'm', 0), 'daftar': ('notebook', 'm', 0), 'haqiiba': ('bag', 'f', 0),
    'miftaah': ('key', 'm', 0), 'haatif': ('phone', 'm', 0), 'sayyaara': ('car', 'f', 0), 'qitaar': ('train', 'm', 0),
    'taawila': ('table', 'f', 0), 'kursii': ('chair', 'm', 0), 'baab': ('door', 'm', 0), 'naafidha': ('window', 'f', 0),
    'jariida': ('newspaper', 'f', 0), 'risaala': ('letter', 'f', 0), 'kalima': ('word', 'f', 0),
    'suura': ('picture', 'f', 0), 'lawha': ('painting', 'f', 0), 'haasuub': ('computer', 'm', 0),
    'sariir': ('bed', 'm', 0), 'qamiis': ('shirt', 'm', 0), 'ughniya': ('song', 'f', 0), 'film': ('film', 'm', 0),
    'tilfaaz': ('television', 'm', 0), 'muusiiqaa': ('music', 'f', 1), 'dars': ('lesson', 'm', 0),
    "su'aal": ('question', 'm', 0),
    # food and drink
    'khubz': ('bread', 'm', 1), 'tuffaaha': ('apple', 'f', 0), 'mawza': ('banana', 'f', 0),
    'burtuqaal': ('orange', 'm', 0), 'jubn': ('cheese', 'm', 1), 'haliib': ('milk', 'm', 1), 'lahm': ('meat', 'm', 1),
    'dajaaj': ('chicken', 'm', 1), 'aruzz': ('rice', 'm', 1), 'bayda': ('egg', 'f', 0), 'samak': ('fish', 'm', 1),
    'qahwa': ('coffee', 'f', 1), 'shaay': ('tea', 'm', 1), "maa'": ('water', 'm', 1), "'asiir": ('juice', 'm', 1),
    # animals, nature
    'kalb': ('dog', 'm', 0), 'qitta': ('cat', 'f', 0), 'tayr': ('bird', 'm', 0), 'shajara': ('tree', 'f', 0),
    'nahr': ('river', 'm', 0), 'jabal': ('mountain', 'm', 0), 'najm': ('star', 'm', 0), 'qamar': ('moon', 'm', 0),
    'jaww': ('weather', 'm', 1),
}
NOUN_KEYS = sorted(NOUNS)
PEOPLE = ['walad', 'bint', 'rajul', "imra'a", "mu'allim", "mu'allima", 'tabiib', 'taalib', 'tifl', 'jadda', 'sadiiq', 'sadiiqa', 'umm', 'ab']
PLACES = ['madrasa', 'suuq', "jaami'a", 'maktaba', 'hadiiqa', "mat'am", 'mustashfaa', 'bahr', 'masjid', 'funduq', 'bayt', 'ghurfa',
          'matbakh', 'madiina', "shaati'", 'maktab']

# adjective: (english, nouns it sensibly describes)
ADJ = {
    'jamiil': ('beautiful', ['madiina', 'hadiiqa', 'sayyaara', 'madrasa', 'ghurfa', 'lawha', 'suura', 'ughniya', 'shajara', 'zahra_', 'bayt',
                             'bahr', 'jabal', "shaati'", 'bint', "imra'a", 'film']),
    'kabiir': ('big', ['bayt', 'madiina', 'madrasa', 'sayyaara', 'ghurfa', 'hadiiqa', 'haqiiba', 'kitaab', "mat'am", 'funduq', 'maktab',
                       "jaami'a", 'maktaba', 'shajara', 'jabal', 'nahr', 'kalb', 'qitta', 'taawila', 'sariir', 'mustashfaa', 'masjid',
                       'suuq', 'matbakh']),
    'saghiir': ('small', ['bayt', 'ghurfa', 'sayyaara', 'haqiiba', 'kitaab', 'kalb', 'qitta', 'tayr', 'madrasa', 'hadiiqa', 'taawila',
                          'matbakh', "mat'am", 'funduq', 'maktab', 'tifl', 'haatif', 'daftar', 'qalam']),
    'jayyid': ('good', ["mu'allim", "mu'allima", 'tabiib', 'taalib', "mat'am", 'kitaab', 'film', 'sayyaara', 'funduq', 'madrasa',
                        "jaami'a", 'sadiiq', 'sadiiqa', 'ughniya', 'suura', 'haasuub', 'haatif']),
    'jadiid': ('new', ['bayt', 'sayyaara', 'haatif', 'haasuub', 'kitaab', 'haqiiba', 'qamiis', 'daftar', 'qalam', 'madrasa', 'film',
                       'ughniya', 'sariir', 'kursii', 'taawila', 'jariida', "mat'am"]),
    'qadiim': ('old', ['bayt', 'kitaab', 'madiina', 'masjid', 'sayyaara', "jaami'a", 'funduq', 'kursii', 'taawila', 'sariir', 'haatif']),
    'tawiil': ('long', ['nahr', 'risaala', 'film', 'ughniya', "shaari'"]),
    'qasiir': ('short', ['risaala', 'film', 'ughniya', "shaari'", 'kalima']),
    "sarii'": ('fast', ['sayyaara', 'qitaar']),
    'naziif': ('clean', ['ghurfa', 'matbakh', 'bayt', 'sayyaara', 'qamiis', "mat'am", 'madrasa', 'funduq', 'maktab', 'sariir']),
    'thaqiil': ('heavy', ['haqiiba', 'kitaab', 'taawila', 'haasuub']),
    'ladhiidh': ('delicious', ['khubz', 'tuffaaha', 'mawza', 'burtuqaal', 'jubn', 'lahm', 'dajaaj', 'aruzz', 'bayda', 'samak', 'qahwa',
                               'shaay', "'asiir", 'haliib']),
    'baarid': ('cold', ["maa'", 'shaay', 'qahwa', 'haliib', "'asiir", 'jaww']),
    'haarr': ('hot', ['shaay', 'qahwa', 'jaww']),
    'qariib': ('near', ['madrasa', 'bayt', 'mustashfaa', 'funduq', "mat'am", 'maktaba', "jaami'a", 'suuq', 'masjid', "shaati'", 'hadiiqa',
                        'maktab']),
    "ba'iid": ('far', ['madrasa', 'bayt', 'mustashfaa', 'funduq', "mat'am", 'maktaba', "jaami'a", 'suuq', 'masjid', "shaati'", 'hadiiqa',
                       'maktab']),
}
# a few extra nouns referenced above
NOUNS['zahra_'] = ('flower', 'f', 0)
SCRIPT['zahra_'] = SCRIPT['zahra']
for _a in ADJ.values():
    for _n in _a[1]:
        assert _n in NOUNS, _n

# adjectives for people (masc -> fem by adding -a)
ADJP = {'sa\'iid': 'happy', 'haziin': 'sad', "ta'baan": 'tired', "jaw'aan": 'hungry', "'atshaan": 'thirsty',
        'mashghuul': 'busy', 'mariid': 'sick', 'jaahiz': 'ready', 'latiif': 'nice'}


def a_(word):
    return ('an ' if word[0] in 'aeiou' and not word.startswith('uni') else 'a ') + word


def cap(s):
    return s[0].upper() + s[1:]


# ------------------------------------------------------------ block makers --
def noun_b(key, definite=False):
    en, g, _m = NOUNS[key]
    latin = key.rstrip('_')
    ar = SCRIPT[key][0]
    if definite:
        latin, ar = definite_latin(latin), definite_ar(ar)
    return blk('noun', latin, ar, ('the ' if definite else '') + en, g + (' · the' if definite else ''))


def adj_b(key, fem=False, definite=False):
    en = ADJ[key][0] if key in ADJ else ADJP[key]
    ar, latin = SCRIPT[key][0], key
    if fem:
        ar, latin = ar + FATHA + 'ة', key + 'a'
    if definite:
        latin, ar = definite_latin(latin), definite_ar(ar)
    return blk('adjective', latin, ar, ('the ' if definite else '') + en, ('f' if fem else 'm') + (' · the' if definite else ''))


def pron_b(p):
    ar, ra = SCRIPT[p]
    return blk('pronoun', p, ar, PRON_EN[p], '', ra)


def dem_b(fem):
    k = 'hadhihi' if fem else 'hadha'
    ar, ra = SCRIPT[k]
    return blk('pronoun', k, ar, 'this', 'f' if fem else 'm', ra)


def simple(pos, key, en, tag='', clitic=False):
    ar, ra = SCRIPT[key]
    return blk(pos, key, ar, en, tag, ra, clitic)


def prep_b(key):
    en = {'fii': 'in', "'alaa": 'on', 'ilaa': 'to', 'min': 'from', "ma'a": 'with', "'indii": 'I have'}[key]
    return simple('preposition', key, en)


def adv_b(key):
    en = {'jiddan': 'very', 'ghadan': 'tomorrow', 'ams': 'yesterday', 'al-aan': 'now', "daa'iman": 'always', 'ghaaliban': 'often',
          'ahyaanan': 'sometimes', 'naadiran': 'rarely', 'hunaa': 'here', "ma'an": 'together'}[key]
    return simple('adverb', key, en)


def verb_b(vid, tense, pron):
    v = VERB[vid]
    latin = v[tense][pron]
    ar = VA.AR[vid][0 if tense == 'present' else 1][pron]
    third = pron in ('huwa', 'hiya')
    form = v['en'][2] if tense == 'past' else (v['en'][1] if third else v['en'][0])
    return blk('verb', latin, ar, f'{PRON_EN[pron]} {form}', tense)


WA = lambda: simple('conjunction', 'wa', 'and', clitic=True)   # noqa: E731
HAL = lambda: simple('particle', 'hal', 'yes/no question')     # noqa: E731
LAA = lambda: simple('particle', 'laa', 'not')                 # noqa: E731
AYNA = lambda: simple('particle', 'ayna', 'where')             # noqa: E731


# ---------------------------------------------------------------- phrases --
PHRASES, SEEN = [], set()
GENERIC = []


def other_gender_adj(key, fem, definite):
    return adj_b(key, fem=not fem, definite=definite)


def phrase(level, tokens, english, tip, extras=(), accept=None):
    t = tuple(tokens)
    if t in SEEN:
        return
    SEEN.add(t)
    ex = []
    for e in extras:
        if e not in tokens and e not in ex:
            ex.append(e)
    tries = 0
    while len(ex) < 2 and tries < 50:
        tries += 1
        e = rng.choice(GENERIC)
        if e not in tokens and e not in ex:
            ex.append(e)
    PHRASES.append(dict(id=f'p{len(PHRASES) + 1}', level=level, tokens=list(tokens), english=english, tip=tip, extras=ex[:3],
                        **({'accept': accept} if accept else {})))


def rand_noun(excl, definite=True, pool=None):
    cand = [k for k in (pool or NOUN_KEYS) if k not in excl and not k.endswith('_')]
    return noun_b(rng.choice(cand), definite)


def en_def(k):
    return 'the ' + NOUNS[k][0]


def en_indef(k):
    en, _g, mass = NOUNS[k]
    return en if mass else a_(en)


TIP = dict(
    dem="Arabic has no word for 'is' in the present tense: hadha kitaab is literally 'this book'. Use hadha with masculine nouns and hadhihi with feminine nouns.",
    na_sent="No 'is' needed: a noun WITH al- (the) followed by an adjective WITHOUT al- is a full sentence. al-bayt kabiir = 'the house (is) big'. The adjective comes AFTER the noun.",
    na_np="The adjective comes AFTER the noun and copies its al- (the) and its gender. When both words have al-, it is only a phrase ('the big house'), not a sentence.",
    na_ind="Adjectives follow the noun and match its gender: a feminine noun takes the feminine adjective ending -a (madrasa kabiira), a masculine noun takes the plain form (bayt kabiir).",
    pron_adj="There is no 'am / is / are' in the Arabic present tense: huwa ta'baan = 'he (is) tired'. The adjective matches the gender: masculine ta'baan, feminine ta'baana.",
    ayna="Question words come first and no 'is' is needed: ayna al-bayt? = 'where (is) the house?'.",
    indii="'indii (literally 'at me') is how Arabic says 'I have'. What you have comes right after it, and an adjective comes after its noun.",
    pp="A preposition (fii in, 'alaa on, ma'a with, min from) comes BEFORE its noun, and there is still no 'is': al-kitaab 'alaa at-taawila = 'the book (is) on the table'.",
    vso="Arabic sentences usually start with the VERB: verb - subject - object. The verb copies the subject's gender (masculine ya-/-a, feminine ta-/-at) and stays singular.",
    svo="The verb ending already shows who is acting, so the pronoun is optional (it adds emphasis). Pronoun - verb - object is also correct.",
    vprep_ilaa="Verbs of going and arriving take ilaa (to) before the place: dhahaba ilaa = 'went to'.",
    vprep_fii="Some verbs need fii (in / at) before the place: jalasa fii = 'sat in', 'amila fii = 'worked in'.",
    vprep_min="min (from / out of) comes before the place you leave: kharaja min = 'went out of'.",
    time="Time words like ghadan (tomorrow), ams (yesterday) and al-aan (now) are flexible: they can start the sentence or end it.",
    freq="Frequency adverbs (daa'iman always, ghaaliban often, ahyaanan sometimes, naadiran rarely) usually sit right before the verb, but can also go at the end.",
    neg="laa + a present-tense verb = 'do / does not'. The pronoun comes first, then laa, then the verb.",
    hal="hal turns any statement into a yes/no question. Put it first and keep the rest of the word order the same.",
    wa="wa (and) joins two words of the same kind. In real Arabic writing it is attached to the next word.",
    idaafa="Possession (idaafa): the thing owned comes FIRST with no al-, then the owner WITH al-: bayt al-mu'allim = 'the teacher's house'. Never put al- on the first word.",
    idaafa_adj="Possession (idaafa): owned thing first (no al-), owner second (with al-). A describing adjective goes at the END and matches the owned thing: bayt al-mu'allim kabiir.",
    jiddan="Adverbs like jiddan (very) come AFTER the adjective they strengthen: al-bayt kabiir jiddan.",
)

# ================================================================ frames ====
# generic distractor pool (different parts of speech so the user must identify types)
for k in ('jiddan', 'ghadan', 'ams', 'daa\'iman', 'hunaa'):
    GENERIC.append(adv_b(k))
for k in ('fii', "'alaa", 'min', 'ilaa', "ma'a"):
    GENERIC.append(prep_b(k))
GENERIC += [adj_b('kabiir'), adj_b('jadiid'), adj_b('jamiil'), noun_b('bayt'), noun_b('kitaab'), noun_b('sayyaara')]

# ---- L1: this is a ... -----------------------------------------------------
for k in rng.sample([n for n in NOUN_KEYS if n not in PEOPLE], 40):
    f = NOUNS[k][1] == 'f'
    phrase(1, [dem_b(f), noun_b(k)], f'This is {en_indef(k)}.', TIP['dem'],
           [dem_b(not f)])

# ---- L1: noun + adjective sentences / phrases -------------------------------
na_pairs = [(a, n) for a, (_e, ns) in sorted(ADJ.items()) for n in ns]
rng.shuffle(na_pairs)
cnt = {}
for a, n in na_pairs:
    if cnt.get(a, 0) >= 5:
        continue
    cnt[a] = cnt.get(a, 0) + 1
    en_adj, en_n = ADJ[a][0], NOUNS[n][0]
    f = NOUNS[n][1] == 'f'
    phrase(1, [noun_b(n, True), adj_b(a, f)], f'The {en_n} is {en_adj}.', TIP['na_sent'],
           [adj_b(a, not f)])
# sentence with 'very'
for a, n in rng.sample(na_pairs, 30):
    f = NOUNS[n][1] == 'f'
    phrase(2, [noun_b(n, True), adj_b(a, f), adv_b('jiddan')], f'The {NOUNS[n][0]} is very {ADJ[a][0]}.', TIP['jiddan'],
           [adj_b(a, not f)])
# the big house (NP)
for a, n in rng.sample(na_pairs, 26):
    f = NOUNS[n][1] == 'f'
    phrase(1, [noun_b(n, True), adj_b(a, f, True)], f'The {ADJ[a][0]} {NOUNS[n][0]}.', TIP['na_np'],
           [adj_b(a, f), adj_b(a, not f, True)])
# a big house (indefinite NP)
ind_pairs = [(a, n) for a, n in na_pairs if a not in ('qariib', "ba'iid")]
for a, n in rng.sample(ind_pairs, 30):
    f = NOUNS[n][1] == 'f'
    mass = NOUNS[n][2]
    eng = f'{ADJ[a][0]} {NOUNS[n][0]}' if mass else f'{a_(ADJ[a][0])} {NOUNS[n][0]}'
    phrase(1, [noun_b(n), adj_b(a, f)], cap(eng) + '.', TIP['na_ind'], [adj_b(a, not f)])

# ---- L1: he is tired ---------------------------------------------------------
for a in sorted(ADJP):
    for p in ('anta', 'anti', 'huwa', 'hiya'):
        f = p in ('anti', 'hiya')
        be = 'are' if p in ('anta', 'anti') else 'is'
        who = PRON_EN[p]
        phrase(1, [pron_b(p), adj_b(a, f)], f'{cap(who)} {be} {ADJP[a]}.', TIP['pron_adj'], [adj_b(a, not f)])

# ---- L1: where is the ...? ---------------------------------------------------
for k in rng.sample([n for n in NOUN_KEYS if not NOUNS[n][2]], 26):
    phrase(1, [AYNA(), noun_b(k, True)], f'Where is the {NOUNS[k][0]}?', TIP['ayna'])

# ---- L1/L2: I have ... -------------------------------------------------------
# only things a person can sensibly own (no "I have a far university")
OWNABLE = [n for n in ('bayt', 'sayyaara', 'haatif', 'haasuub', 'kitaab', 'haqiiba', 'daftar', 'qalam', 'kursii', 'taawila',
                       'sariir', 'qamiis', 'kalb', 'qitta', 'ghurfa', 'miftaah', 'jariida', 'suura', 'lawha', 'tilfaaz') if n in NOUNS]
own_pairs = [(a, n) for a, n in na_pairs if n in OWNABLE and a not in ('qariib', "ba'iid")]
for k in rng.sample(OWNABLE, min(20, len(OWNABLE))):
    phrase(1, [prep_b("'indii"), noun_b(k)], f'I have {en_indef(k)}.', TIP['indii'])
for a, n in rng.sample(own_pairs, min(24, len(own_pairs))):
    f = NOUNS[n][1] == 'f'
    mass = NOUNS[n][2]
    eng = f'{ADJ[a][0]} {NOUNS[n][0]}' if mass else f'{a_(ADJ[a][0])} {NOUNS[n][0]}'
    phrase(2, [prep_b("'indii"), noun_b(n), adj_b(a, f)], f'I have {eng}.', TIP['indii'], [adj_b(a, not f)])

# ---- L2: prepositions (the book is on the table) -----------------------------
PP = [('kitaab', "'alaa", 'taawila'), ('qalam', "'alaa", 'taawila'), ('haqiiba', "'alaa", 'kursii'), ('haatif', "'alaa", 'sariir'),
      ('miftaah', 'fii', 'haqiiba'), ('daftar', 'fii', 'haqiiba'), ('walad', 'fii', 'madrasa'), ("mu'allim", 'fii', 'madrasa'),
      ('tabiib', 'fii', 'mustashfaa'), ('rajul', 'fii', 'suuq'), ("imra'a", 'fii', 'hadiiqa'), ('jadda', 'fii', 'bayt'),
      ('qitta', "'alaa", 'kursii'), ('kalb', 'fii', 'hadiiqa'), ('samak', 'fii', 'bahr'), ('tayr', 'fii', 'shajara'),
      ('tifl', 'fii', 'ghurfa'), ('bint', 'fii', 'matbakh'), ('taalib', 'fii', 'maktaba'), ('walad', "ma'a", "mu'allim"),
      ('bint', "ma'a", 'jadda'), ('tifl', "ma'a", 'umm'), ('taalib', "ma'a", 'sadiiq'), ('rajul', "ma'a", 'kalb'),
      ("imra'a", "ma'a", 'tabiib'), ('qahwa', 'min', 'matbakh'), ('khubz', 'min', 'suuq'), ('jubn', 'min', 'suuq'),
      ('sadiiq', 'min', 'madiina'), ('tabiib', 'min', 'madiina')]
PREP_EN = {'fii': 'in', "'alaa": 'on', "ma'a": 'with', 'min': 'from'}
for a, p, b in PP:
    be = 'is'
    phrase(2, [noun_b(a, True), prep_b(p), noun_b(b, True)], f'The {NOUNS[a][0]} is {PREP_EN[p]} the {NOUNS[b][0]}.', TIP['pp'],
           [prep_b(rng.choice([x for x in ('fii', "'alaa", 'min', "ma'a", 'ilaa') if x != p]))])

# ---- L2: verb - subject - object (VSO) ---------------------------------------
OBJ = {
    'kataba': ['risaala', 'kitaab', 'kalima'], 'qaraa': ['kitaab', 'jariida', 'risaala', 'kalima'],
    'shariba': ['qahwa', 'shaay', "maa'", 'haliib', "'asiir"],
    'akala': ['khubz', 'tuffaaha', 'mawza', 'burtuqaal', 'jubn', 'lahm', 'dajaaj', 'aruzz', 'bayda', 'samak'],
    'fataha': ['baab', 'naafidha', 'kitaab', 'haqiiba'], 'aghlaqa': ['baab', 'naafidha', 'haqiiba', 'kitaab'],
    'ahabba': ['qahwa', 'shaay', 'bahr', 'madiina', 'muusiiqaa', 'kalb', 'qitta'],
    'shaahada': ['tilfaaz', 'film'], 'fahima': ['kalima', "su'aal", 'dars', 'risaala'],
    'tabakha': ['dajaaj', 'aruzz', 'samak', 'lahm', 'bayda'],
    'raa': ['qamar', 'najm', 'bahr', 'jabal', 'shajara', 'tayr', 'kalb', 'qitta'],
    'darasa': ['dars', 'kitaab', 'kalima'], 'zaara': ['madiina', 'jadda', 'usra_', 'sadiiq'],
    'istakhdama': ['haatif', 'haasuub', 'qalam'], 'arsala': ['risaala'], 'wajada': ['miftaah', 'haqiiba', 'kitaab'],
    'dakhala': ['ghurfa', 'madrasa', 'matbakh', 'bayt', "mat'am"],
}
NOUNS['usra_'] = ('family', 'f', 0)
SCRIPT['usra_'] = SCRIPT['usra']
SUBJ = [k for k in PEOPLE if k not in ('umm', 'ab')]


def gloss_form(vid, tense, third=True):
    v = VERB[vid]
    return v['en'][2] if tense == 'past' else (v['en'][1] if third else v['en'][0])


for vid, objs in sorted(OBJ.items()):
    for o in objs:
        for tense in ('present', 'past'):
            s = rng.choice(SUBJ)
            fem = NOUNS[s][1] == 'f'
            p = 'hiya' if fem else 'huwa'
            vb = verb_b(vid, tense, p)
            trap = verb_b(vid, tense, 'huwa' if fem else 'hiya')
            vl = VERB[vid][tense][p]
            tip = TIP['vso'] + f" Here {vl} is the {'feminine' if fem else 'masculine'} form because {s} is {'feminine' if fem else 'masculine'}."
            eng = f"The {NOUNS[s][0]} {gloss_form(vid, tense)} the {NOUNS[o][0]}."
            phrase(2, [vb, noun_b(s, True), noun_b(o, True)], eng, tip, [trap, rand_noun({s, o})])

# ---- L2: pronoun - verb - object ----------------------------------------------
SVO_P = ['ana', 'anta', 'anti', 'huwa', 'hiya', 'nahnu', 'antum', 'hum']
for vid, objs in sorted(OBJ.items()):
    for o in objs:
        p = rng.choice(SVO_P)
        tense = rng.choice(['present', 'present', 'past'])
        third = p in ('huwa', 'hiya')
        eng = f"{cap(PRON_EN[p])} {gloss_form(vid, tense, third)} the {NOUNS[o][0]}."
        phrase(2, [pron_b(p), verb_b(vid, tense, p), noun_b(o, True)], eng, TIP['svo'], [rand_noun({o}), adv_b('jiddan')])

# ---- L2: verb + preposition + place --------------------------------------------
VP = [
    ('dhahaba', 'ilaa', ['madrasa', 'suuq', "jaami'a", 'maktaba', 'hadiiqa', "mat'am", 'mustashfaa', 'bahr', 'masjid', 'funduq', "shaati'", 'bayt'], 'ilaa', 'to'),
    ('jalasa', 'fii', ['hadiiqa', 'ghurfa', 'matbakh', 'maktaba', "mat'am"], 'fii', 'in'),
    ("amila", 'fii', ['maktab', 'mustashfaa', 'madrasa', "mat'am", "jaami'a", 'matbakh'], 'fii', 'in'),
    ('sakana', 'fii', ['madiina', 'bayt', 'funduq'], 'fii', 'in'),
    ('rajaa', 'ilaa', ['bayt', 'madrasa', 'madiina', 'maktab'], 'ilaa', 'to'),
    ('kharaja', 'min', ['bayt', 'madrasa', 'ghurfa', 'matbakh', 'maktab'], 'min', 'of'),
    ('wasala', 'ilaa', ['madrasa', 'funduq', "mat'am", "jaami'a", 'mustashfaa', 'maktab'], 'ilaa', 'at'),
]
VP_EN_EXTRA = {}  # the verb gloss already says 'go out'
VP_PREP = {'ilaa': 'vprep_ilaa', 'fii': 'vprep_fii', 'min': 'vprep_min'}
vp_all = [(vid, pr, pl, key) for vid, pr, places, key, _e in VP for pl in places]
for vid, pr, pl, key in vp_all:
    pen = [x for x in VP if x[0] == vid][0][4]
    for variant in (0, 1):
        tense = rng.choice(['present', 'past'])
        if variant == 0:
            p = rng.choice(['ana', 'anta', 'huwa', 'hiya', 'nahnu'])
            third = p in ('huwa', 'hiya')
            verb_en = gloss_form(vid, tense, third) + VP_EN_EXTRA.get(vid, '')
            eng = f"{cap(PRON_EN[p])} {verb_en} {pen} the {NOUNS[pl][0]}."
            toks = [pron_b(p), verb_b(vid, tense, p), prep_b(pr), noun_b(pl, True)]
        else:
            p = rng.choice(['ana', 'nahnu', 'huwa', 'hiya'])
            third = p in ('huwa', 'hiya')
            verb_en = gloss_form(vid, tense, third) + VP_EN_EXTRA.get(vid, '')
            eng = f"{cap(PRON_EN[p])} {verb_en} {pen} the {NOUNS[pl][0]}."
            toks = [verb_b(vid, tense, p), prep_b(pr), noun_b(pl, True)]
        other = rng.choice([x for x in ('fii', 'ilaa', 'min', "'alaa") if x != pr])
        phrase(2, toks, eng, TIP[VP_PREP[pr]], [prep_b(other), rand_noun({pl})])

# ---- L2: idaafa (possession), noun phrase ---------------------------------------
OWNED_M = ['bayt', 'kitaab', 'qalam', 'haatif', 'miftaah', 'daftar', 'haasuub', "mat'am", 'maktab']
OWNER = ['walad', 'bint', 'rajul', "imra'a", 'tabiib', 'taalib', 'tifl', 'jadda', 'umm', 'ab']
combos = [(o, w) for o in OWNED_M for w in OWNER]
rng.shuffle(combos)
for o, w in combos[:24]:
    phrase(2, [noun_b(o), noun_b(w, True)], f"The {NOUNS[w][0]}'s {NOUNS[o][0]}.", TIP['idaafa'],
           [noun_b(o, True), noun_b(w)])
# ---- L3: idaafa + adjective ---------------------------------------------------------
for o, w in combos[24:60]:
    adjs = [a for a, (_e, ns) in ADJ.items() if o in ns]
    if not adjs:
        continue
    a = rng.choice(sorted(adjs))
    phrase(3, [noun_b(o), noun_b(w, True), adj_b(a)], f"The {NOUNS[w][0]}'s {NOUNS[o][0]} is {ADJ[a][0]}.", TIP['idaafa_adj'],
           [adj_b(a, True), noun_b(o, True)])

# ---- L2: time adverb placement --------------------------------------------------------
TIME = [('ghadan', 'present'), ('ams', 'past'), ('al-aan', 'present')]
tv = [(vid, pr, pl) for vid, pr, pl, _k in vp_all]
rng.shuffle(tv)
for vid, pr, pl in tv[:30]:
    adv, tense = rng.choice(TIME)
    p = rng.choice(['ana', 'ana', 'nahnu'])
    pen = [x for x in VP if x[0] == vid][0][4]
    eng = f"{cap(PRON_EN[p])} {gloss_form(vid, tense, False) if p != 'ana' or True else ''}"
    verb_en = gloss_form(vid, tense, False) + VP_EN_EXTRA.get(vid, '')
    eng = f"{cap(PRON_EN[p])} {verb_en} {pen} the {NOUNS[pl][0]} {adv_b(adv) and BLOCKS[adv_b(adv)]['en']}."
    base = [verb_b(vid, tense, p), prep_b(pr), noun_b(pl, True)]
    a_b = adv_b(adv)
    phrase(3, base + [a_b], eng, TIP['time'], [adv_b('jiddan')], accept=[[a_b] + base])

# ---- L3: frequency adverbs --------------------------------------------------------------
FREQ = ["daa'iman", 'ghaaliban', 'ahyaanan', 'naadiran']
for vid in ('shariba', 'akala', 'qaraa', 'kataba', 'shaahada', 'tabakha', 'ahabba'):
    for o in rng.sample(OBJ[vid], min(2, len(OBJ[vid]))):
        fq = rng.choice(FREQ)
        p = rng.choice(['ana', 'ana', 'nahnu'])
        base = [verb_b(vid, 'present', p), noun_b(o, True)]
        fb = adv_b(fq)
        eng = f"{cap(PRON_EN[p])} {BLOCKS[fb]['en']} {gloss_form(vid, 'present', False)} the {NOUNS[o][0]}."
        phrase(3, [fb] + base, eng, TIP['freq'], [adv_b('ghadan'), rand_noun({o})], accept=[base + [fb]])

# ---- L3: negation ---------------------------------------------------------------------------
for vid, objs in sorted(OBJ.items()):
    if vid in ('arsala', 'wajada'):
        continue
    o = rng.choice(objs)
    p = rng.choice(['ana', 'anta', 'huwa', 'hiya', 'nahnu', 'hum'])
    third = p in ('huwa', 'hiya')
    aux = "doesn't" if third else "don't"
    eng = f"{cap(PRON_EN[p])} {aux} {gloss_form(vid, 'present', False)} the {NOUNS[o][0]}."
    phrase(3, [pron_b(p), LAA(), verb_b(vid, 'present', p), noun_b(o, True)], eng, TIP['neg'], [rand_noun({o}), adv_b('jiddan')])

# ---- L3: yes/no questions with hal --------------------------------------------------------------
for vid, objs in sorted(OBJ.items()):
    o = rng.choice(objs)
    if rng.random() < 0.5:
        p = rng.choice(['anta', 'anti'])
        eng = f"Do you ({'f' if p == 'anti' else 'm'}) {gloss_form(vid, 'present', False)} the {NOUNS[o][0]}?"
        phrase(3, [HAL(), verb_b(vid, 'present', p), noun_b(o, True)], eng, TIP['hal'], [pron_b(p), rand_noun({o})])
    else:
        s = rng.choice(SUBJ)
        fem = NOUNS[s][1] == 'f'
        p = 'hiya' if fem else 'huwa'
        eng = f"Does the {NOUNS[s][0]} {gloss_form(vid, 'present', False)} the {NOUNS[o][0]}?"
        phrase(3, [HAL(), verb_b(vid, 'present', p), noun_b(s, True), noun_b(o, True)], eng,
               TIP['hal'] + f" The verb {VERB[vid]['present'][p]} still agrees with {s}.",
               [verb_b(vid, 'present', 'hiya' if not fem else 'huwa'), rand_noun({s, o})])
for a in sorted(ADJP):
    p = rng.choice(['anta', 'anti'])
    f = p == 'anti'
    phrase(3, [HAL(), pron_b(p), adj_b(a, f)], f"Are you ({'f' if f else 'm'}) {ADJP[a]}?", TIP['hal'], [adj_b(a, not f)])

# ---- L3: 'and' ---------------------------------------------------------------------------------------
pairs = rng.sample([(a, b) for a in PEOPLE[:12] for b in PEOPLE[:12] if a < b and NOUNS[a][1] != NOUNS[b][1] or (a < b and a in ('walad', 'rajul', 'tifl') and b in ('rajul', 'taalib', 'tabiib'))], 12)
for a, b in pairs:
    pl = rng.choice(['madrasa', 'bayt', 'hadiiqa', 'suuq', 'maktaba', "mat'am"])
    phrase(3, [noun_b(a, True), WA(), noun_b(b, True), prep_b('fii'), noun_b(pl, True)],
           f"The {NOUNS[a][0]} and the {NOUNS[b][0]} are in the {NOUNS[pl][0]}.", TIP['wa'], [prep_b("'alaa"), adv_b('hunaa')])
DRINKS = ['qahwa', 'shaay', "maa'", 'haliib', "'asiir"]
FOODS = ['khubz', 'jubn', 'aruzz', 'dajaaj', 'samak', 'tuffaaha', 'mawza', 'bayda']
for pool, vid in ((DRINKS, 'shariba'), (FOODS, 'akala'), (FOODS, 'tabakha')):
    for _ in range(5):
        a, b = rng.sample(pool, 2)
        p = rng.choice(['ana', 'nahnu', 'anta'])
        eng = f"{cap(PRON_EN[p])} {gloss_form(vid, 'present', False)} the {NOUNS[a][0]} and the {NOUNS[b][0]}."
        phrase(3, [verb_b(vid, 'present', p), noun_b(a, True), WA(), noun_b(b, True)], eng, TIP['wa'], [prep_b('min'), rand_noun({a, b})])
NP_PAIRS = [('kitaab', 'qalam'), ('baab', 'naafidha'), ('shams', 'qamar'), ('bayt', 'sayyaara'), ('khubz', 'jubn'), ('shaay', 'qahwa'),
            ('walad', 'bint'), ('kalb', 'qitta'), ('taawila', 'kursii'), ('haatif', 'haasuub')]
NOUNS['shams'] = ('sun', 'f', 0)
for a, b in NP_PAIRS:
    phrase(2, [noun_b(a, True), WA(), noun_b(b, True)], f"The {NOUNS[a][0]} and the {NOUNS[b][0]}.", TIP['wa'], [prep_b('fii'), adj_b('kabiir')])

# ===================================================================== emit ====
if errors:
    print('PHRASE DATA ERRORS:')
    for e in errors:
        print('  -', e)
    sys.exit(1)

used = set()
for ph in PHRASES:
    used.update(ph['tokens'])
    used.update(ph['extras'])
    for alt in ph.get('accept', []):
        used.update(alt)
    assert len(ph['extras']) >= 2, ph
    # every alternative order must be a permutation of the same blocks
    for alt in ph.get('accept', []):
        assert sorted(alt) == sorted(ph['tokens']), ph

out = []
w = out.append
w("// AUTO-GENERATED by tools/gen_phrases.py -- edit that script (or tools/script_ar.txt / verbs_ar.py), then re-run.")
w("// Word blocks and ready-made phrases for the Build tab (sentence-order game).")
w("")
w("export type Pos = 'noun' | 'verb' | 'adjective' | 'adverb' | 'preposition' | 'pronoun' | 'conjunction' | 'particle';")
w("")
w("export interface Block {")
w("  latin: string;      // shown on the tile")
w("  arabic: string;     // vocalised Arabic script, never shown: spoken by the Arabic voice")
w("  en: string;         // English gloss shown under the word")
w("  pos: Pos;")
w("  tag?: string;       // gender / tense / 'the'")
w("  clitic?: boolean;   // written attached to the next word (wa)")
w("}")
w("")
w("export interface Phrase {")
w("  id: string;")
w("  level: 1 | 2 | 3;")
w("  tokens: string[];   // block ids in the correct order")
w("  accept?: string[][]; // other correct orders (flexible adverbs)")
w("  english: string;")
w("  tip: string;        // syntax tip shown after answering")
w("  extras: string[];   // distractor block ids (extras[0] is usually a gender trap)")
w("}")
w("")
w("export const BLOCKS: Record<string, Block> = {")
for bid in sorted(used, key=lambda x: int(x[1:])):
    b = BLOCKS[bid]
    parts = [f"latin: {json.dumps(b['latin'], ensure_ascii=False)}", f"arabic: {json.dumps(b['arabic'], ensure_ascii=False)}",
             f"en: {json.dumps(b['en'], ensure_ascii=False)}", f"pos: {json.dumps(b['pos'])}"]
    if b.get('tag'):
        parts.append(f"tag: {json.dumps(b['tag'], ensure_ascii=False)}")
    if b.get('clitic'):
        parts.append('clitic: true')
    w(f"  {bid}: {{ " + ', '.join(parts) + ' },')
w("};")
w("")
w("export const PHRASES: Phrase[] = [")
for ph in PHRASES:
    parts = [f"id: {json.dumps(ph['id'])}", f"level: {ph['level']}", f"tokens: {json.dumps(ph['tokens'])}"]
    if ph.get('accept'):
        parts.append(f"accept: {json.dumps(ph['accept'])}")
    parts += [f"english: {json.dumps(ph['english'], ensure_ascii=False)}", f"tip: {json.dumps(ph['tip'], ensure_ascii=False)}",
              f"extras: {json.dumps(ph['extras'])}"]
    w('  { ' + ', '.join(parts) + ' },')
w("];")
w("")
w("/** The Arabic sentence as one string for the voice (wa is written attached to the next word). */")
w("export function phraseScript(tokens: string[]): string {")
w("  let s = '';")
w("  tokens.forEach((id) => {")
w("    const b = BLOCKS[id];")
w("    s += b.arabic + (b.clitic ? '' : ' ');")
w("  });")
w("  return s.trim();")
w("}")
w("")
open(os.path.join(ROOT, 'lib', 'phrases.ts'), 'w', encoding='utf-8').write('\n'.join(out))

by_level = {1: 0, 2: 0, 3: 0}
for ph in PHRASES:
    by_level[ph['level']] += 1
print('wrote lib/phrases.ts:', len(PHRASES), 'phrases', by_level, '|', len(used), 'blocks')
print('sample phrases:')
for ph in rng.sample(PHRASES, 14):
    print(f"  L{ph['level']}  ", ' '.join(BLOCKS[t]['latin'] for t in ph['tokens']), '  =>', ph['english'])
