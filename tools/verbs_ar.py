"""Vocalised Arabic forms for every verb in verbs.py (used only for text-to-speech).

Mirrors the Latin generator: the same stems / endings, but written in Arabic script. Stem strings
are written with the LAST radical bare (no vowel) because the ending supplies it. A bare 'ء' in a
stem is a hamza placeholder; arabic.seat_hamza() chooses أ ؤ ئ or ء after the ending is attached.
"""
from arabic import FATHA, DAMMA, KASRA, SUKUN, SHADDA, norm, seat_hamza

A_PRE = ('أَ', 'تَ', 'يَ', 'نَ')
U_PRE = ('أُ', 'تُ', 'يُ', 'نُ')
D, K, F, S = DAMMA, KASRA, FATHA, SUKUN


def join(body, suffix):
    """Attach an ending; a stem ending in nun + feminine -na merges into a doubled nun (taskunna)."""
    if body.endswith('ن') and suffix.startswith(S + 'ن' + F):
        return body + SHADDA + F + suffix[3:]
    return body + suffix


def _fin(forms):
    return {p: norm(seat_hamza(f)) for p, f in forms.items()}


# ---------------------------------------------------------------- present --
def pres_regular(B, pf=A_PRE):
    p1, p2, p3, p4 = pf
    return dict(
        ana=p1 + B + D, anta=p2 + B + D, anti=p2 + B + K + 'ينَ',
        huwa=p3 + B + D, hiya=p2 + B + D, nahnu=p4 + B + D,
        antum=p2 + B + D + 'ونَ', antunna=p2 + join(B, S + 'نَ'),
        hum=p3 + B + D + 'ونَ', hunna=p3 + join(B, S + 'نَ'))


def pres_hollow(Bl, Bs, pf=A_PRE):
    p1, p2, p3, p4 = pf
    return dict(
        ana=p1 + Bl + D, anta=p2 + Bl + D, anti=p2 + Bl + K + 'ينَ',
        huwa=p3 + Bl + D, hiya=p2 + Bl + D, nahnu=p4 + Bl + D,
        antum=p2 + Bl + D + 'ونَ', antunna=p2 + join(Bs, S + 'نَ'),
        hum=p3 + Bl + D + 'ونَ', hunna=p3 + join(Bs, S + 'نَ'))


def pres_def_aa(b, pf=A_PRE):
    p1, p2, p3, p4 = pf
    return dict(
        ana=p1 + b + F + 'ى', anta=p2 + b + F + 'ى', anti=p2 + b + F + 'يْنَ',
        huwa=p3 + b + F + 'ى', hiya=p2 + b + F + 'ى', nahnu=p4 + b + F + 'ى',
        antum=p2 + b + F + 'وْنَ', antunna=p2 + b + F + 'يْنَ',
        hum=p3 + b + F + 'وْنَ', hunna=p3 + b + F + 'يْنَ')


def pres_def_ii(b, pf=A_PRE):
    p1, p2, p3, p4 = pf
    return dict(
        ana=p1 + b + K + 'ي', anta=p2 + b + K + 'ي', anti=p2 + b + K + 'ينَ',
        huwa=p3 + b + K + 'ي', hiya=p2 + b + K + 'ي', nahnu=p4 + b + K + 'ي',
        antum=p2 + b + D + 'ونَ', antunna=p2 + b + K + 'ينَ',
        hum=p3 + b + D + 'ونَ', hunna=p3 + b + K + 'ينَ')


# ------------------------------------------------------------------- past --
def past_regular(st):
    return dict(
        ana=st + S + 'تُ', anta=st + S + 'تَ', anti=st + S + 'تِ',
        huwa=st + F, hiya=st + F + 'تْ', nahnu=join(st, S + 'نَا'),
        antum=st + S + 'تُمْ', antunna=st + S + 'تُنَّ',
        hum=st + D + 'وا', hunna=join(st, S + 'نَ'))


def past_hollow(Pl, Ps):
    return dict(
        ana=Ps + S + 'تُ', anta=Ps + S + 'تَ', anti=Ps + S + 'تِ',
        huwa=Pl + F, hiya=Pl + F + 'تْ', nahnu=join(Ps, S + 'نَا'),
        antum=Ps + S + 'تُمْ', antunna=Ps + S + 'تُنَّ',
        hum=Pl + D + 'وا', hunna=join(Ps, S + 'نَ'))


def past_def_ay(b):
    return dict(
        ana=b + F + 'يْتُ', anta=b + F + 'يْتَ', anti=b + F + 'يْتِ',
        huwa=b + F + 'ى', hiya=b + F + 'تْ', nahnu=b + F + 'يْنَا',
        antum=b + F + 'يْتُمْ', antunna=b + F + 'يْتُنَّ',
        hum=b + F + 'وْا', hunna=b + F + 'يْنَ')


def past_def_iya(b):
    return dict(
        ana=b + K + 'يتُ', anta=b + K + 'يتَ', anti=b + K + 'يتِ',
        huwa=b + K + 'يَ', hiya=b + K + 'يَتْ', nahnu=b + K + 'ينَا',
        antum=b + K + 'يتُمْ', antunna=b + K + 'يتُنَّ',
        hum=b + D + 'وا', hunna=b + K + 'ينَ')


def past_doubled(short, long_):
    return dict(
        ana=short + S + 'تُ', anta=short + S + 'تَ', anti=short + S + 'تِ',
        huwa=long_ + F, hiya=long_ + F + 'تْ', nahnu=short + S + 'نَا',
        antum=short + S + 'تُمْ', antunna=short + S + 'تُنَّ',
        hum=long_ + D + 'وا', hunna=short + S + 'نَ')


# ----------------------------------------------------------------- verbs ---
# id -> (present forms, past forms)       (same ids / order as verbs.py)
def _v(base_pres, base_past, **override):
    pres = dict(base_pres)
    pres.update(override.get('pres', {}))
    return _fin(pres), _fin(dict(base_past))


def _sound(B, st, **kw):
    return _v(pres_regular(B), past_regular(st), **kw)


AR = {
    # regular (sound) Form I
    'kataba': _sound('كْتُب', 'كَتَب'),
    'jaala': _sound('جْعَل', 'جَعَل'),
    'shariba': _sound('شْرَب', 'شَرِب'),
    'faala': _sound('فْعَل', 'فَعَل'),
    'darasa': _sound('دْرُس', 'دَرَس'),
    'fataha': _sound('فْتَح', 'فَتَح'),
    'dhahaba': _sound('ذْهَب', 'ذَهَب'),
    'arafa': _sound('عْرِف', 'عَرَف'),
    'jalasa': _sound('جْلِس', 'جَلَس'),
    'samia': _sound('سْمَع', 'سَمِع'),
    'talaba': _sound('طْلُب', 'طَلَب'),
    'saala': _sound('سْءَل', 'سَءَل'),
    'amila': _sound('عْمَل', 'عَمِل'),
    'rajaa': _sound('رْجِع', 'رَجَع'),
    'dakhala': _sound('دْخُل', 'دَخَل'),
    'kharaja': _sound('خْرُج', 'خَرَج'),
    'nazala': _sound('نْزِل', 'نَزَل'),
    'sakana': _sound('سْكُن', 'سَكَن'),
    'alima': _sound('عْلَم', 'عَلِم'),
    'fahima': _sound('فْهَم', 'فَهِم'),
    'qaraa': _sound('قْرَء', 'قَرَء'),
    'badaa': _sound('بْدَء', 'بَدَء'),
    'nazara': _sound('نْظُر', 'نَظَر'),
    'tabakha': _sound('طْبُخ', 'طَبَخ'),
    # irregular Form I: two hamzas fuse into long aa in the "I" form (aakulu, aakhudhu)
    'akala': _v(pres_regular('ءْكُل'), past_regular('أَكَل'), pres=dict(ana='آكُلُ')),
    'akhadha': _v(pres_regular('ءْخُذ'), past_regular('أَخَذ'), pres=dict(ana='آخُذُ')),
    'qaala': _v(pres_hollow('قُول', 'قُل'), past_hollow('قَال', 'قُل')),
    'kaana': _v(pres_hollow('كُون', 'كُن'), past_hollow('كَان', 'كُن')),
    'naama': _v(pres_hollow('نَام', 'نَم'), past_hollow('نَام', 'نِم')),
    'zaara': _v(pres_hollow('زُور', 'زُر'), past_hollow('زَار', 'زُر')),
    'baaa': _v(pres_hollow('بِيع', 'بِع'), past_hollow('بَاع', 'بِع')),
    'jaaa': _v(pres_hollow('جِيء', 'جِء'), past_hollow('جَاء', 'جِء')),
    'qaama': _v(pres_hollow('قُوم', 'قُم'), past_hollow('قَام', 'قُم')),
    'aasha': _v(pres_hollow('عِيش', 'عِش'), past_hollow('عَاش', 'عِش')),
    'raa': _v(pres_def_aa('ر'), past_def_ay('رَء')),
    'mashaa': _v(pres_def_ii('مْش'), past_def_ay('مَش')),
    'nasiya': _v(pres_def_aa('نْس'), past_def_iya('نَس')),
    'baqiya': _v(pres_def_aa('بْق'), past_def_iya('بَق')),
    'wajada': _sound('جِد', 'وَجَد'),
    'wasala': _sound('صِل', 'وَصَل'),
    'wadaa': _sound('ضَع', 'وَضَع'),
    # derived Forms II-X
    'allama': _v(pres_regular('عَلِّم', U_PRE), past_regular('عَلَّم')),
    'fakkara': _v(pres_regular('فَكِّر', U_PRE), past_regular('فَكَّر')),
    'saafara': _v(pres_regular('سَافِر', U_PRE), past_regular('سَافَر')),
    'saaada': _v(pres_regular('سَاعِد', U_PRE), past_regular('سَاعَد')),
    'shaahada': _v(pres_regular('شَاهِد', U_PRE), past_regular('شَاهَد')),
    'qaabala': _v(pres_regular('قَابِل', U_PRE), past_regular('قَابَل')),
    'arsala': _v(pres_regular('رْسِل', U_PRE), past_regular('أَرْسَل')),
    'aghlaqa': _v(pres_regular('غْلِق', U_PRE), past_regular('أَغْلَق')),
    'ahabba': _v(pres_regular('حِبّ', U_PRE), past_doubled('أَحْبَب', 'أَحَبّ'),
                 pres=dict(antunna='تُحْبِبْنَ', hunna='يُحْبِبْنَ')),
    'araada': _v(pres_hollow('رِيد', 'رِد', U_PRE), past_hollow('أَرَاد', 'أَرَد')),
    'ataa': _v(pres_def_ii('عْط', U_PRE), past_def_ay('أَعْط')),
    'takallama': _v(pres_regular('تَكَلَّم'), past_regular('تَكَلَّم')),
    'taallama': _v(pres_regular('تَعَلَّم'), past_regular('تَعَلَّم')),
    'tadhakkara': _v(pres_regular('تَذَكَّر'), past_regular('تَذَكَّر')),
    'intazara': _v(pres_regular('نْتَظِر'), past_regular('اِنْتَظَر')),
    'istamaa': _v(pres_regular('سْتَمِع'), past_regular('اِسْتَمَع')),
    'ihtaaja': _v(pres_hollow('حْتَاج', 'حْتَج'), past_hollow('اِحْتَاج', 'اِحْتَج')),
    'intahaa': _v(pres_def_ii('نْتَه'), past_def_ay('اِنْتَه')),
    'istakhdama': _v(pres_regular('سْتَخْدِم'), past_regular('اِسْتَخْدَم')),
    'istataa': _v(pres_hollow('سْتَطِيع', 'سْتَطِع'), past_hollow('اِسْتَطَاع', 'اِسْتَطَع')),
}
