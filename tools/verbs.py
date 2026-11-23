"""Verb tables for the Arabic tutor app.

Every conjugated form is derived from a small number of explicit stems per verb,
using the rule for its class (sound / hollow / defective / ...). Transliteration
matches the user's notes: long vowels doubled (aa, ii, uu), apostrophe for ayn
and hamza, no dots for emphatic letters.
"""

PRON = ['ana', 'anta', 'anti', 'huwa', 'hiya', 'nahnu', 'antum', 'antunna', 'hum', 'hunna']

A_PREFIX = ('a', 'ta', 'ya', 'na')   # Forms I, V, VI, VII, VIII, X
U_PREFIX = ('u', 'tu', 'yu', 'nu')   # Forms II, III, IV


# ---------------------------------------------------------------- present --
def pres_regular(B, pf=A_PREFIX):
    p1, p2, p3, p4 = pf
    return dict(
        ana=p1 + B + 'u', anta=p2 + B + 'u', anti=p2 + B + 'iina',
        huwa=p3 + B + 'u', hiya=p2 + B + 'u', nahnu=p4 + B + 'u',
        antum=p2 + B + 'uuna', antunna=p2 + B + 'na',
        hum=p3 + B + 'uuna', hunna=p3 + B + 'na',
    )


def pres_hollow(Bl, Bs, pf=A_PREFIX):
    """Long vowel everywhere except the feminine plurals (taqulna / yaqulna)."""
    p1, p2, p3, p4 = pf
    return dict(
        ana=p1 + Bl + 'u', anta=p2 + Bl + 'u', anti=p2 + Bl + 'iina',
        huwa=p3 + Bl + 'u', hiya=p2 + Bl + 'u', nahnu=p4 + Bl + 'u',
        antum=p2 + Bl + 'uuna', antunna=p2 + Bs + 'na',
        hum=p3 + Bl + 'uuna', hunna=p3 + Bs + 'na',
    )


def pres_def_aa(b, pf=A_PREFIX):
    """Defective verbs whose present ends in -aa (yaraa, yansaa, yabqaa)."""
    p1, p2, p3, p4 = pf
    return dict(
        ana=p1 + b + 'aa', anta=p2 + b + 'aa', anti=p2 + b + 'ayna',
        huwa=p3 + b + 'aa', hiya=p2 + b + 'aa', nahnu=p4 + b + 'aa',
        antum=p2 + b + 'awna', antunna=p2 + b + 'ayna',
        hum=p3 + b + 'awna', hunna=p3 + b + 'ayna',
    )


def pres_def_ii(b, pf=A_PREFIX):
    """Defective verbs whose present ends in -ii (yamshii, yu'tii, yantahii)."""
    p1, p2, p3, p4 = pf
    return dict(
        ana=p1 + b + 'ii', anta=p2 + b + 'ii', anti=p2 + b + 'iina',
        huwa=p3 + b + 'ii', hiya=p2 + b + 'ii', nahnu=p4 + b + 'ii',
        antum=p2 + b + 'uuna', antunna=p2 + b + 'iina',
        hum=p3 + b + 'uuna', hunna=p3 + b + 'iina',
    )


# ------------------------------------------------------------------- past --
def past_regular(stem):
    return dict(
        ana=stem + 'tu', anta=stem + 'ta', anti=stem + 'ti',
        huwa=stem + 'a', hiya=stem + 'at', nahnu=stem + 'naa',
        antum=stem + 'tum', antunna=stem + 'tunna',
        hum=stem + 'uu', hunna=stem + 'na',
    )


def past_hollow(Pl, Ps):
    """qaala -> qultu ... qaala, qaalat ... qaaluu, qulna."""
    return dict(
        ana=Ps + 'tu', anta=Ps + 'ta', anti=Ps + 'ti',
        huwa=Pl + 'a', hiya=Pl + 'at', nahnu=Ps + 'naa',
        antum=Ps + 'tum', antunna=Ps + 'tunna',
        hum=Pl + 'uu', hunna=Ps + 'na',
    )


def past_def_ay(b):
    """ra'aa -> ra'aytu ... ra'aa, ra'at ... ra'aw, ra'ayna."""
    return dict(
        ana=b + 'aytu', anta=b + 'ayta', anti=b + 'ayti',
        huwa=b + 'aa', hiya=b + 'at', nahnu=b + 'aynaa',
        antum=b + 'aytum', antunna=b + 'aytunna',
        hum=b + 'aw', hunna=b + 'ayna',
    )


def past_def_iya(b):
    """nasiya -> nasiitu ... nasiya, nasiyat ... nasuu, nasiina."""
    return dict(
        ana=b + 'iitu', anta=b + 'iita', anti=b + 'iiti',
        huwa=b + 'iya', hiya=b + 'iyat', nahnu=b + 'iinaa',
        antum=b + 'iitum', antunna=b + 'iitunna',
        hum=b + 'uu', hunna=b + 'iina',
    )


def past_doubled(short, long_):
    """ahabba -> ahbabtu ... ahabba, ahabbat, ahbabnaa ... ahabbuu, ahbabna."""
    return dict(
        ana=short + 'tu', anta=short + 'ta', anti=short + 'ti',
        huwa=long_ + 'a', hiya=long_ + 'at', nahnu=short + 'naa',
        antum=short + 'tum', antunna=short + 'tunna',
        hum=long_ + 'uu', hunna=short + 'na',
    )


# ----------------------------------------------------------------- verbs ---
# (id, root, english, (en base, en 3rd person, en past), type, form, present, past, extras)
# type: regular = sound Form I | irregular = weak/hamzated Form I | derived = Forms II-X
def V(id, root, english, en, type_, form, pres, past, **extra):
    return dict(id=id, root=root, english=english, en=en, type=type_, form=form,
                present=pres, past=past, extra=extra)


def sound_I(id, root, english, en, B, past_stem):
    return V(id, root, english, en, 'regular', 'I', pres_regular(B), past_regular(past_stem))


def sound_I_irreg(id, root, english, en, B, past_stem, **ov):
    pres = pres_regular(B)
    pres.update(ov)
    return V(id, root, english, en, 'irregular', 'I', pres, past_regular(past_stem))


VERBS = [
    # ---------------------------------------------- regular (sound) Form I --
    sound_I('kataba', 'k-t-b', 'to write', ('write', 'writes', 'wrote'), 'ktub', 'katab'),
    sound_I('jaala', 'j-\'-l', 'to make / put', ('make', 'makes', 'made'), "j'al", "ja'al"),
    sound_I('shariba', 'sh-r-b', 'to drink', ('drink', 'drinks', 'drank'), 'shrab', 'sharib'),
    sound_I('faala', 'f-\'-l', 'to do', ('do', 'does', 'did'), "f'al", "fa'al"),
    sound_I('darasa', 'd-r-s', 'to study', ('study', 'studies', 'studied'), 'drus', 'daras'),
    sound_I('fataha', 'f-t-h', 'to open', ('open', 'opens', 'opened'), 'ftah', 'fatah'),
    sound_I('dhahaba', 'dh-h-b', 'to go', ('go', 'goes', 'went'), 'dhhab', 'dhahab'),
    sound_I('arafa', '\'-r-f', 'to know (someone)', ('know (someone)', 'knows (someone)', 'knew (someone)'), "'rif", "'araf"),
    sound_I('jalasa', 'j-l-s', 'to sit', ('sit', 'sits', 'sat'), 'jlis', 'jalas'),
    sound_I('samia', 's-m-\'', 'to hear', ('hear', 'hears', 'heard'), "sma'", "sami'"),
    sound_I('talaba', 't-l-b', 'to request / ask for', ('request', 'requests', 'requested'), 'tlub', 'talab'),
    sound_I('saala', 's-\'-l', 'to ask (a question)', ('ask', 'asks', 'asked'), "s'al", "sa'al"),
    sound_I('amila', '\'-m-l', 'to work', ('work', 'works', 'worked'), "'mal", "'amil"),
    sound_I('rajaa', 'r-j-\'', 'to return', ('return', 'returns', 'returned'), "rji'", "raja'"),
    sound_I('dakhala', 'd-kh-l', 'to enter', ('enter', 'enters', 'entered'), 'dkhul', 'dakhal'),
    sound_I('kharaja', 'kh-r-j', 'to go out / exit', ('go out', 'goes out', 'went out'), 'khruj', 'kharaj'),
    sound_I('nazala', 'n-z-l', 'to go down / get off', ('go down', 'goes down', 'went down'), 'nzil', 'nazal'),
    sound_I('sakana', 's-k-n', 'to reside / dwell', ('reside', 'resides', 'resided'), 'skun', 'sakan'),
    sound_I('alima', '\'-l-m', 'to know (a fact)', ('know (a fact)', 'knows (a fact)', 'knew (a fact)'), "'lam", "'alim"),
    sound_I('fahima', 'f-h-m', 'to understand', ('understand', 'understands', 'understood'), 'fham', 'fahim'),
    sound_I('qaraa', 'q-r-\'', 'to read', ('read', 'reads', 'read'), "qra'", "qara'"),
    sound_I('badaa', 'b-d-\'', 'to begin / start', ('begin', 'begins', 'began'), "bda'", "bada'"),
    sound_I('nazara', 'n-z-r', 'to look (at)', ('look', 'looks', 'looked'), 'nzur', 'nazar'),
    sound_I('tabakha', 't-b-kh', 'to cook', ('cook', 'cooks', 'cooked'), 'tbukh', 'tabakh'),

    # ---------------------------------------- irregular Form I (weak etc.) --
    # hamzated: ana form is aakulu / aakhudhu (two hamzas fuse into a long aa)
    sound_I_irreg('akala', '\'-k-l', 'to eat', ('eat', 'eats', 'ate'), "'kul", 'akal', ana='aakulu'),
    sound_I_irreg('akhadha', '\'-kh-dh', 'to take', ('take', 'takes', 'took'), "'khudh", 'akhadh', ana='aakhudhu'),
    # hollow verbs (middle weak letter)
    V('qaala', 'q-w-l', 'to say', ('say', 'says', 'said'), 'irregular', 'I',
      pres_hollow('quul', 'qul'), past_hollow('qaal', 'qul')),
    V('kaana', 'k-w-n', 'to be', ('be', 'is', 'was'), 'irregular', 'I',
      pres_hollow('kuun', 'kun'), past_hollow('kaan', 'kun'), be=True),
    V('naama', 'n-w-m', 'to sleep', ('sleep', 'sleeps', 'slept'), 'irregular', 'I',
      pres_hollow('naam', 'nam'), past_hollow('naam', 'nim')),
    V('zaara', 'z-w-r', 'to visit', ('visit', 'visits', 'visited'), 'irregular', 'I',
      pres_hollow('zuur', 'zur'), past_hollow('zaar', 'zur')),
    V('baaa', 'b-y-\'', 'to sell', ('sell', 'sells', 'sold'), 'irregular', 'I',
      pres_hollow("bii'", "bi'"), past_hollow("baa'", "bi'")),
    V('jaaa', 'j-y-\'', 'to come', ('come', 'comes', 'came'), 'irregular', 'I',
      pres_hollow("jii'", "ji'"), past_hollow("jaa'", "ji'")),
    V('qaama', 'q-w-m', 'to stand up / get up', ('get up', 'gets up', 'got up'), 'irregular', 'I',
      pres_hollow('quum', 'qum'), past_hollow('qaam', 'qum')),
    V('aasha', '\'-y-sh', 'to live (be alive)', ('live', 'lives', 'lived'), 'irregular', 'I',
      pres_hollow("'iish", "'ish"), past_hollow("'aash", "'ish")),
    # defective verbs (last weak letter)
    V('raa', 'r-\'-y', 'to see', ('see', 'sees', 'saw'), 'irregular', 'I',
      pres_def_aa('r'), past_def_ay("ra'")),
    V('mashaa', 'm-sh-y', 'to walk', ('walk', 'walks', 'walked'), 'irregular', 'I',
      pres_def_ii('msh'), past_def_ay('mash')),
    V('nasiya', 'n-s-y', 'to forget', ('forget', 'forgets', 'forgot'), 'irregular', 'I',
      pres_def_aa('ns'), past_def_iya('nas')),
    V('baqiya', 'b-q-y', 'to stay / remain', ('stay', 'stays', 'stayed'), 'irregular', 'I',
      pres_def_aa('bq'), past_def_iya('baq')),
    # assimilated (initial waw drops in the present)
    sound_I_irreg('wajada', 'w-j-d', 'to find', ('find', 'finds', 'found'), 'jid', 'wajad'),
    sound_I_irreg('wasala', 'w-s-l', 'to arrive', ('arrive', 'arrives', 'arrived'), 'sil', 'wasal'),
    sound_I_irreg('wadaa', 'w-d-\'', 'to put / place', ('put', 'puts', 'put'), "da'", "wada'"),

    # ------------------------------------------------- derived Forms II-X --
    V('allama', '\'-l-m', 'to teach', ('teach', 'teaches', 'taught'), 'derived', 'II',
      pres_regular("'allim", U_PREFIX), past_regular("'allam")),
    V('fakkara', 'f-k-r', 'to think', ('think', 'thinks', 'thought'), 'derived', 'II',
      pres_regular('fakkir', U_PREFIX), past_regular('fakkar')),
    V('saafara', 's-f-r', 'to travel', ('travel', 'travels', 'traveled'), 'derived', 'III',
      pres_regular('saafir', U_PREFIX), past_regular('saafar')),
    V('saaada', 's-\'-d', 'to help', ('help', 'helps', 'helped'), 'derived', 'III',
      pres_regular("saa'id", U_PREFIX), past_regular("saa'ad")),
    V('shaahada', 'sh-h-d', 'to watch', ('watch', 'watches', 'watched'), 'derived', 'III',
      pres_regular('shaahid', U_PREFIX), past_regular('shaahad')),
    V('qaabala', 'q-b-l', 'to meet', ('meet', 'meets', 'met'), 'derived', 'III',
      pres_regular('qaabil', U_PREFIX), past_regular('qaabal')),
    V('arsala', 'r-s-l', 'to send', ('send', 'sends', 'sent'), 'derived', 'IV',
      pres_regular('rsil', U_PREFIX), past_regular('arsal')),
    V('aghlaqa', 'gh-l-q', 'to close', ('close', 'closes', 'closed'), 'derived', 'IV',
      pres_regular('ghliq', U_PREFIX), past_regular('aghlaq')),
    V('ahabba', 'h-b-b', 'to love / like', ('love', 'loves', 'loved'), 'derived', 'IV',
      pres_regular('hibb', U_PREFIX), past_doubled('ahbab', 'ahabb')),
    V('araada', 'r-w-d', 'to want', ('want', 'wants', 'wanted'), 'derived', 'IV',
      pres_hollow('riid', 'rid', U_PREFIX), past_hollow('araad', 'arad')),
    V('ataa', '\'-t-w', 'to give', ('give', 'gives', 'gave'), 'derived', 'IV',
      pres_def_ii("'t", U_PREFIX), past_def_ay("a't")),
    V('takallama', 'k-l-m', 'to speak', ('speak', 'speaks', 'spoke'), 'derived', 'V',
      pres_regular('takallam'), past_regular('takallam')),
    V('taallama', '\'-l-m', 'to learn', ('learn', 'learns', 'learned'), 'derived', 'V',
      pres_regular("ta'allam"), past_regular("ta'allam")),
    V('tadhakkara', 'dh-k-r', 'to remember', ('remember', 'remembers', 'remembered'), 'derived', 'V',
      pres_regular('tadhakkar'), past_regular('tadhakkar')),
    V('intazara', 'n-z-r', 'to wait', ('wait', 'waits', 'waited'), 'derived', 'VIII',
      pres_regular('ntazir'), past_regular('intazar')),
    V('istamaa', 's-m-\'', 'to listen', ('listen', 'listens', 'listened'), 'derived', 'VIII',
      pres_regular("stami'"), past_regular("istama'")),
    V('ihtaaja', 'h-w-j', 'to need', ('need', 'needs', 'needed'), 'derived', 'VIII',
      pres_hollow('htaaj', 'htaj'), past_hollow('ihtaaj', 'ihtaj')),
    V('intahaa', 'n-h-y', 'to finish / end', ('finish', 'finishes', 'finished'), 'derived', 'VIII',
      pres_def_ii('ntah'), past_def_ay('intah')),
    V('istakhdama', 'kh-d-m', 'to use', ('use', 'uses', 'used'), 'derived', 'X',
      pres_regular('stakhdim'), past_regular('istakhdam')),
    V('istataa', 't-w-\'', 'to be able to / can', ('can', 'can', 'could'), 'derived', 'X',
      pres_hollow("statii'", "stati'"), past_hollow("istataa'", "istata'")),
]

def finish(v):
    """Add the headword in the user's style: 3rd person present minus ya-/yu-."""
    huwa = v['present']['huwa']
    assert huwa[:2] in ('ya', 'yu'), (v['id'], huwa)
    v['stem'] = huwa[2:]
    v['past3'] = v['past']['huwa']
    v['present3'] = huwa
    return v


VERBS = [finish(v) for v in VERBS]
