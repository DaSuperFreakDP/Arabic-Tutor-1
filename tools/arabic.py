"""Arabic-script helpers for the speech layer.

The app DISPLAYS Latin transcription but SPEAKS vocalised Arabic script (an Arabic TTS voice
cannot read Latin transcription). To make sure the hidden script really matches the Latin shown
on screen, `reverse()` transliterates Arabic back into the app's Latin convention and
`matches()` compares it with the Latin text. gen_data.py refuses to build if anything differs.

Latin convention (lossy, as in the user's notes): long vowels doubled, ' = hamza AND ayn,
emphatics written plain, word-initial hamza not written, no case endings on nouns.
"""
import re

FATHA, DAMMA, KASRA = 'َ', 'ُ', 'ِ'
SUKUN, SHADDA, DAGGER, WASLA = 'ْ', 'ّ', 'ٰ', 'ٱ'
FATHATAN, DAMMATAN, KASRATAN = 'ً', 'ٌ', 'ٍ'

VOWEL = {FATHA: 'a', DAMMA: 'u', KASRA: 'i'}
TANWIN = {FATHATAN: 'an', DAMMATAN: 'un', KASRATAN: 'in'}

LATIN = {
    'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j', 'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'dh',
    'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh', 'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z',
    'ع': "'", 'غ': 'gh', 'ف': 'f', 'ق': 'q', 'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
    'ه': 'h',
}
HAMZA_LETTERS = set('ءأإؤئ')
LETTERS = set(LATIN) | HAMZA_LETTERS | set('آاٱةىوي')


def norm(s):
    """Canonical mark order: shadda before the vowel mark (so both typing orders compare equal)."""
    s = re.sub('([ً-ِ])ّ', 'ّ\\1', s)
    return s.replace('ـ', '')


# ------------------------------------------------------------------ hamza --
def seat_hamza(w):
    """Replace each bare placeholder 'ء' by its correct seat (أ ؤ ئ or ء on the line).

    Medial hamza: strongest of (own vowel, preceding vowel), kasra > damma > fatha > none.
    Final hamza: seat decided by the preceding vowel only.
    """
    strength = {FATHA: 1, DAMMA: 2, KASRA: 3}
    seat_of = {0: 'ء', 1: 'أ', 2: 'ؤ', 3: 'ئ'}
    n, res = len(w), ''
    for i, c in enumerate(w):
        if c != 'ء':
            res += c
            continue
        own = w[i + 1] if i + 1 < n and w[i + 1] in (FATHA, DAMMA, KASRA, SUKUN) else None
        k = i + 1 + (1 if own else 0)
        final = k >= n or w[k] == ' '
        own_s = strength.get(own, 0)
        prev = w[i - 1] if i else ''
        if prev == 'ا':                       # after long aa: on the line unless own vowel is u / i
            seat = 'ء' if (final or own_s <= 1) else seat_of[own_s]
        elif prev == 'ي':                     # after long ii
            seat = 'ء' if final else 'ئ'
        elif prev == 'و':                     # after long uu
            seat = 'ء' if final else seat_of[own_s]
        else:
            ps = strength.get(prev, 0)
            seat = seat_of[ps if final else max(ps, own_s)]
        res += seat
    return res


# ---------------------------------------------------------------- reverse --
def _units(word):
    units = []
    for ch in word:
        if ch in LETTERS:
            units.append(dict(c=ch, sh=False, v=None, dag=False))
        elif ch == SHADDA:
            units[-1]['sh'] = True
        elif ch in VOWEL:
            units[-1]['v'] = VOWEL[ch]
        elif ch == SUKUN:
            units[-1]['v'] = '0'
        elif ch in TANWIN:
            units[-1]['v'] = TANWIN[ch]
        elif ch == DAGGER:
            units[-1]['dag'] = True
        else:
            raise ValueError(f'unexpected character {ch!r} (U+{ord(ch):04X}) in {word!r}')
    return units


def _vs(v):
    return '' if v in (None, '0') else v


def reverse_word(word, first=True):
    units = _units(norm(word))
    n, out, start = len(units), '', 0
    # definite article: alif + lam (+ sun letter carries the shadda)
    if (n >= 3 and units[0]['c'] in 'اٱ' and units[1]['c'] == 'ل'
            and units[1]['v'] in (None, '0') and not units[1]['sh'] and units[0]['v'] in (None, 'a')):
        elided = units[0]['c'] == 'ٱ' and not first
        sun = units[2]['sh']
        out += ('' if elided else 'a') + ('' if sun else 'l')
        start = 2
    for i in range(start, n):
        u, c, v = units[i], units[i]['c'], units[i]['v']
        prev = units[i - 1] if i > start else None
        pv = prev['v'] if prev else None
        initial = (i == start)
        if c in 'اٱ':
            if initial:
                if v is None:
                    raise ValueError(f'initial alif without vowel in {word!r}')
                out += _vs(v)
            elif prev and prev['c'] == 'و' and prev['v'] in (None, '0'):
                pass                                   # silent alif after -uu / -aw
            elif pv and pv.endswith('n') and pv in TANWIN.values():
                pass                                   # tanwin carrier
            elif pv == 'a' or (prev and prev['dag']):
                out += 'a'
            else:
                raise ValueError(f'long alif after non-fatha in {word!r}')
        elif c == 'ى':
            if pv == 'an':
                pass
            elif pv == 'a':
                out += 'a'
            else:
                raise ValueError(f'alif maqsura after non-fatha in {word!r}')
        elif c == 'آ':
            out += 'aa' if initial else "'aa"
        elif c in HAMZA_LETTERS:
            if initial and c in 'أإ':
                out += _vs(v)
            else:
                out += ("'" * (2 if u['sh'] else 1)) + _vs(v)
        elif c == 'ة':
            out += ('t' + _vs(v)) if _vs(v) else ''
        elif c == 'و':
            if v is None:
                out += ('w' * 2) if u['sh'] else ('u' if pv == 'u' else 'w')
            else:
                out += 'w' * (2 if u['sh'] else 1) + _vs(v)
        elif c == 'ي':
            if v is None:
                out += ('y' * 2) if u['sh'] else ('i' if pv == 'i' else 'y')
            else:
                out += 'y' * (2 if u['sh'] else 1) + _vs(v)
        else:
            out += LATIN[c] * (2 if u['sh'] else 1) + _vs(v)
        if u['dag']:
            out += 'a'
    return out


def reverse(text):
    words = text.split()
    return ' '.join(reverse_word(w, first=(k == 0)) for k, w in enumerate(words))


def latin_key(s):
    s = s.lower().replace('’', "'").replace('ʼ', "'").replace('`', "'")
    return re.sub(r"[-\s]", '', s)


def matches(arabic, latin, reads_as=None):
    """True when the Arabic back-transliterates to the Latin (or to the `reads_as` override)."""
    return latin_key(reverse(arabic)) == latin_key(reads_as or latin)
