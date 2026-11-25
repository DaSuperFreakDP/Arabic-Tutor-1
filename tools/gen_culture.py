#!/usr/bin/env python3
"""Generate lib/culture-data.ts for the Culture tab (the "why learn Arabic" section).

Run from the project root:  python3 tools/gen_culture.py

Content rules
  * Facts only from sources checked while writing (listed in SOURCES, shown in the app). Where historians
    disagree or a source hedges, the text says so ("is credited with", "probably", "debated").
  * Every Arabic word that can be played aloud carries hidden vocalised script for the Arabic voice, and that
    script is verified (tools/arabic.py) against the Latin transcription shown on screen. Words that are
    flashcards reuse tools/script_ar.txt so there is exactly one spelling per word.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from arabic import matches, reverse  # noqa: E402

errors = []


# ------------------------------------------------------------------ words --
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
WORDS = {}


def W(latin, en, script=None, reads_as=None):
    """A playable word. Script comes from script_ar.txt unless given; always verified against the Latin."""
    if script is None:
        if latin not in SCRIPT:
            errors.append(f"no script for '{latin}' (add it here or in script_ar.txt)")
            return dict(latin=latin, script='', en=en)
        script, reads_as = SCRIPT[latin]
    try:
        ok = matches(script, latin, reads_as)
    except ValueError as ex:
        ok = False
        errors.append(f"'{latin}': {ex}")
    if not ok:
        errors.append(f"'{latin}': script {script} reads '{reverse(script)}'")
    WORDS[latin] = dict(latin=latin, script=script, en=en)
    return WORDS[latin]


# words that are not flashcards (script given and verified)
w_zabiib = W('zabiib', 'raisin / dried grape', 'زَبِيب')
w_saaqiya = W('saaqiya', 'irrigation channel', 'سَاقِيَة')
w_raiis = W("ra'iis", 'chief / president', 'رَئِيس')
w_miskiin = W('miskiin', 'poor / wretched', 'مِسْكِين')
w_makhzan = W('makhzan', 'storehouse', 'مَخْزَن')
w_taasa = W('taasa', 'bowl / cup', 'طَاسَة')
w_lazaward = W('laazaward', 'lapis lazuli (the blue stone)', 'لَازَوَرْد')
w_zafaraan = W("za'faraan", 'saffron', 'زَعْفَرَان')
w_sifr = W('sifr', 'zero / empty', 'صِفْر')
w_qala = W("qal'a", 'fortress / castle', 'قَلْعَة')
w_daar = W('daar', 'house', 'دَار')
w_sayf = W('sayf', 'summer', 'صَيْف')
w_kataba = W('kataba', 'he wrote', 'كَتَبَ')
w_kaatib = W('kaatib', 'writer', 'كَاتِب')
w_darasa = W('darasa', 'he studied', 'دَرَسَ')
w_mudarris = W('mudarris', 'teacher', 'مُدَرِّس')

# words that are flashcards (script from script_ar.txt)
w_sukkar = W('sukkar', 'sugar')
w_qahwa = W('qahwa', 'coffee')
w_funduq = W('funduq', 'hotel / inn')
w_suuq = W('suuq', 'market')
w_zahra = W('zahra', 'flower')
w_madiina = W('madiina', 'city')
w_baab = W('baab', 'door / gate')
w_burtuqaal = W('burtuqaal', 'orange (fruit)')
w_rajul = W('rajul', 'man')
w_tifl = W('tifl', 'child / boy')
w_shams = W('shams', 'sun')
w_kitaab = W('kitaab', 'book')
w_maktab = W('maktab', 'office / desk')
w_maktaba = W('maktaba', 'library')
w_madrasa = W('madrasa', 'school')
w_dars = W('dars', 'lesson')
w_salaam = W("as-salaamu 'alaykum", 'peace be upon you (greeting)')
w_marhaban = W('marhaban', 'hello')
w_shukran = W('shukran', 'thank you')
w_ahlan = W('ahlan wa sahlan', 'welcome')
w_kayfa = W('kayfa haaluka', 'how are you? (to a man)')
w_shaay = W('shaay', 'tea')
w_khubz = W('khubz', 'bread')
w_jamia = W("jaami'a", 'university')
w_film = W('film', 'film')
w_ughniya = W('ughniya', 'song')
w_music = W('muusiiqaa', 'music')


def word_ref(w):
    return dict(latin=w['latin'], script=w['script'], en=w['en'])


# ---------------------------------------------------------------- bridges --
# (lang, word, the word it became, story, in flashcards?)
BRIDGES = [
    ('Italian', w_sukkar, 'zucchero',
     "Italian zucchero comes from Arabic sukkar. English 'sugar' travelled the same road.", True),
    ('Italian', w_qahwa, 'caffè',
     "Italian caffè reached Italy by way of Turkish kahve, which took it from Arabic qahwa. Every espresso is an Arabic lesson.", True),
    ('Italian', w_funduq, 'fondaco',
     "Italian trading cities called their merchant posts fondaci (an inn or trading post). The Arabic word itself came from Greek "
     "pandokheion, 'a place that receives everyone'.", True),
    ('Italian', w_makhzan, 'magazzino',
     "Italian magazzino (warehouse) comes from Arabic makhaazin, the plural of makhzan, 'storehouse'.", False),
    ('Italian', w_taasa, 'tazza',
     "Italian tazza (cup) comes from Arabic taasa, which first meant a bowl.", False),
    ('Italian', w_lazaward, 'azzurro',
     "Italian azzurro ('sky blue') comes from Arabic laazaward, the name of the blue stone lapis lazuli.", False),
    ('Italian', w_miskiin, 'meschino',
     "Italian meschino comes from Arabic miskiin, 'poor'. It is common in southern Italy.", False),
    ('Italian', w_sifr, 'zero / cifra',
     "Arabic sifr means 'empty'. It became Medieval Latin zephirum, then Italian zero, and also cifra (and English 'cipher').", False),
    ('Italian', w_salaam, 'salamelecco',
     "Italian salamelecco, an over-polite bow or greeting, is an adaptation of the Arabic greeting as-salaamu 'alaykum.", False),
    ('Sicilian', w_suuq, 'zuccu',
     "Sicilian zuccu (market) comes from Arabic suuq. You already have this one as a flashcard.", True),
    ('Sicilian', w_zahra, 'zàgara',
     "Sicilian zàgara (blossom) comes from Arabic zahra, 'flower'.", True),
    ('Sicilian', w_zabiib, 'zibbibbu',
     "Sicilian zibbibbu, the dried Muscat of Alexandria grape, comes from Arabic zabiib, 'raisin'.", False),
    ('Sicilian', w_saaqiya, 'saia',
     "Sicilian saia (a canal) comes from Arabic saaqiya, an irrigation channel. Water words are everywhere in Sicilian.", False),
    ('Sicilian', w_raiis, 'ràisi',
     "Sicilian ràisi (leader) comes from Arabic ra'iis, 'chief'. In Arabic today it also means 'president'.", False),
    ('Sicilian', w_zafaraan, 'zaffarana',
     "Sicilian zaffarana (saffron) comes from Arabic za'faraan.", False),
    ('Place', w_madiina, 'Palermo = al-Madiina',
     "When Palermo became the capital of Muslim Sicily in 831 it was renamed al-Madiina, 'the City'.", True),
    ('Place', w_baab, 'Bibbirria (Agrigento)',
     "Bibbirria, the northern gate of Agrigento, comes from Arabic bab ar-riyaah, 'Gate of the Winds'. baab = gate.", True),
    ('Place', w_qala, 'Caltanissetta',
     "Caltanissetta comes from Arabic Qal'at an-nisaa', 'castle of the women', recorded by al-Idrisi in 1154 "
     "(why it was called that is debated).", False),
]

# ------------------------------------------------------------------ roots --
ROOTS = [
    dict(root='k-t-b', meaning='writing', words=[w_kataba, w_kitaab, w_maktab, w_maktaba, w_kaatib],
         note="maktab = 'place of writing' (office / desk), maktaba = 'place of books' (library). The ma- pattern means 'place of'."),
    dict(root='d-r-s', meaning='studying', words=[w_darasa, w_dars, w_madrasa, w_mudarris],
         note="madrasa = 'place of studying' (school). Same ma- 'place of' pattern as maktab."),
]

# -------------------------------------------------------------- greetings --
GREETINGS = [
    dict(region='Standard Arabic (news, books, school)', say='kayfa haaluka?', word=w_kayfa),
    dict(region='Egypt', say='izzayyak?'),
    dict(region='Levant (Lebanon, Syria, Jordan, Palestine)', say='kiifak?'),
    dict(region='Gulf and Iraq', say='shlonak?'),
    dict(region='Morocco and the Maghreb', say='labaas?'),
]

# ------------------------------------------------------------------ regions --
REGIONS = [
    dict(name='Maghreb', where='Morocco, Algeria, Tunisia, Libya', icon='sunny-outline',
         text="The Arabic closest to Sicily's past: the Arabic of Muslim Sicily was a Maghrebi dialect. Other Arabic speakers find "
              "Moroccan Arabic especially hard to follow. Arabic lives beside the Berber (Amazigh) languages here, and French is "
              "common in daily life in much of the region. Think couscous and mint tea."),
    dict(name='Egypt', where='Cairo and the Nile', icon='film-outline',
         text="Egyptian Arabic is understood across most of the Arab world, thanks to Egyptian cinema, music and other media "
              "since the early 1900s."),
    dict(name='Levant', where='Lebanon, Syria, Jordan, Palestine', icon='restaurant-outline',
         text="A Mediterranean coast like Italy's, and a table culture that will feel familiar: shared small plates (mezze), olive "
              "oil, long meals. Levantine speakers and Gulf speakers understand each other much better than they understand the Maghreb."),
    dict(name='Gulf', where='Saudi Arabia, UAE, Qatar, Kuwait, Bahrain', icon='cafe-outline',
         text="Bedouin roots and fast-growing modern cities. Coffee (qahwa) with dates is the classic welcome."),
    dict(name='Iraq', where='Mesopotamia, between the Tigris and Euphrates', icon='water-outline',
         text="One of the oldest homelands of writing and cities, and the Baghdad of the Abbasid translators. Iraqis call their own "
              "everyday Arabic 'Aamiyah."),
]

# ---------------------------------------------------------------- scenarios --
SCENARIOS = [
    dict(id='travel', icon='airplane-outline', title='Travel and markets',
         text="Morocco, Tunisia, Egypt, Jordan, the Gulf: greet people, ask a price in the suuq, find the funduq. "
              "A few words in Arabic change how you are welcomed.",
         words=[w_marhaban, w_shukran, w_suuq, w_funduq]),
    dict(id='italy', icon='people-outline', title='Your neighbours in Italy',
         text="Moroccan, Egyptian and Tunisian citizens alone are about 665,000 people legally resident in Italy (end of 2024). "
              "Shops, schools, clinics, volunteering, friendships. Tunisians settle most in Sicily.",
         words=[w_salaam, w_ahlan, w_shukran]),
    dict(id='food', icon='cafe-outline', title='Food and café culture',
         text="Order, compliment the cook, read a menu, and know that qahwa, sukkar and zucchero are one family of words.",
         words=[w_qahwa, w_shaay, w_sukkar, w_khubz]),
    dict(id='work', icon='briefcase-outline', title='Study, work and careers',
         text="Arabic is one of the six official languages of the United Nations. Translation and interpreting, international "
              "organisations, journalism, and trade with the Gulf and North Africa all use it.",
         words=[w_jamia, w_maktab, w_madrasa]),
    dict(id='media', icon='musical-notes-outline', title='Music, film and news',
         text="Understand a song lyric, a film title or a headline without waiting for subtitles. Egyptian cinema and music "
              "have reached the whole region since the early 1900s.",
         words=[w_music, w_ughniya, w_film]),
    dict(id='sicily', icon='map-outline', title='Sicily and Malta trips',
         text="Read the Arabic hiding in place names and everyday words, and in Malta hear a language that is about one-third "
              "Arabic vocabulary, mostly the core everyday words.",
         words=[w_madiina, w_baab, w_qala]),
]

MISSIONS = [
    ('m_kitchen', "Find an Arabic-origin word in your own kitchen: zucchero (sukkar) or caffè (qahwa)."),
    ('m_greet', "Greet someone (or say it out loud) with marhaban or as-salaamu 'alaykum."),
    ('m_teach', "Teach one bridge word to a friend or family member. Explaining it makes it stick."),
    ('m_why', "Write your reason in 'My Why' above, then re-read it on a day you don't feel like studying."),
    ('m_build', "Build 5 sentences in the Build tab without using a hint."),
    ('m_listen', "Listen to 10 minutes of Arabic music or news, just to get used to the sounds."),
]

REASONS = [
    ('italy', 'Italy and Sicily', 'pizza-outline'),
    ('history', 'Mediterranean history', 'compass-outline'),
    ('travel', 'Travel', 'airplane-outline'),
    ('food', 'Food and café culture', 'cafe-outline'),
    ('people', 'Meeting people', 'people-outline'),
    ('career', 'Work and career', 'briefcase-outline'),
    ('challenge', 'The challenge', 'flash-outline'),
    ('curious', 'Curiosity', 'bulb-outline'),
]

PEP = [
    "You don't need family ties to belong in this language. About 70 million people use Arabic as a second language.",
    "Every Italian coffee you order is an Arabic lesson: caffè comes from qahwa.",
    "Hard days mean a pattern is forming. Do the five-minute version: one flashcard set and one Build sentence.",
    "Ten focused minutes a day beats one long Sunday. Keep the streak alive, not the perfection.",
    "You are learning the language behind words and numbers you use every day, from zero and zucchero to algebra.",
    "You don't have to learn every dialect. Learn the next small thing.",
]

# ------------------------------------------------------------------ sparks --
SPARKS = [
    ("When Palermo became the capital of Muslim Sicily in 831 it was renamed al-Madiina, 'the City'.", w_madiina),
    ("Italian zucchero comes from Arabic sukkar. So does English 'sugar'.", w_sukkar),
    ("The Arabic word funduq (hotel) came from Greek pandokheion, 'a place that receives everyone', and became Italian fondaco.", w_funduq),
    ("Sicilian zuccu means 'market' and is the Arabic word suuq. About 300 Sicilian words come from Arabic, mostly farming and water words.", w_suuq),
    ("Maltese tifel ('boy') is the Arabic tifl. Maltese is the only standardised Semitic language written in Latin letters.", w_tifl),
    ("Fibonacci, born in Pisa, learned the Hindu–Arabic numerals as a boy in Bugia (today Béjaïa, Algeria). His book of 1202 brought them to Europe.", None),
    ("In Arabic, orange is burtuqaal, literally 'Portuguese'. Greek, Turkish and the Neapolitan dialect do the same.", w_burtuqaal),
    ("Arabic sifr means 'empty'. It became Medieval Latin zephirum, then Italian zero, and 'cipher' in English.", w_sifr),
    ("Caltanissetta in Sicily is Arabic: Qal'at an-nisaa', 'castle of the women'.", w_qala),
    ("Italian azzurro ('sky blue') comes from the Arabic name of the stone lapis lazuli, laazaward.", w_lazaward),
    ("al-Idrisi drew a 70-map world atlas in Palermo for the Norman king Roger II and finished it in 1154. South is at the top.", None),
    ("Arabic became the sixth official language of the United Nations in 1973. World Arabic Language Day is 18 December.", None),
    ("Say 'how are you?' in Arabic: kayfa haaluka (standard), izzayyak (Egypt), kiifak (Levant), shlonak (Gulf, Iraq), labaas (Morocco).", w_kayfa),
    ("The Phoenician alphabet, from the same Semitic family as Arabic, is the ancestor of the Greek alphabet and so of Latin letters.", None),
    ("Italian salamelecco, an over-polite bow, is a worn-down as-salaamu 'alaykum.", w_salaam),
    ("Tunisians in Italy settle in Sicily more than anywhere else: about 22% of them live there.", None),
    ("One root, many words: k-t-b gives kataba (he wrote), kitaab (book), maktab (office), maktaba (library), kaatib (writer).", w_maktaba),
    ("Muslim Sicily is credited with introducing or spreading oranges, lemons, pistachio and sugarcane, and with better irrigation.", None),
    ("Sicilian saia (a canal) is Arabic saaqiya, an irrigation channel.", w_saaqiya),
    ("Arabic stayed a language of government in Sicily for about a century after the Normans took over.", None),
    ("Italian albicocca (apricot) and algebra both keep Arabic al-, 'the', stuck to the front of the word.", None),
    ("The word madrasa is just 'place of studying': the root d-r-s, plus the ma- 'place of' pattern.", w_madrasa),
    ("Arabic is used every day by more than 400 million people and is official in 24 states and territories.", None),
    ("Maltese xemx ('sun', said roughly 'shemsh') is the Arabic shams.", w_shams),
]

# ---------------------------------------------------------------- timelines --
TL_SICILY = [
    ('827', "Muslim forces from Ifriqiya (roughly today's Tunisia) land in Sicily and win at Mazara del Vallo on 15 July."),
    ('831', "Palermo falls after a year-long siege and becomes the capital, renamed al-Madiina."),
    ('902', "The fall of Taormina completes the conquest of the island (a few holdouts, such as Rometta, last until 965)."),
    ('1072', "Palermo falls to the Normans after a five-month siege."),
    ('1091', "Noto, Butera and Malta fall, ending independent Islamic rule in Sicily."),
]
TL_SEA = [
    ('before c. 1050 BC', "Phoenician, Hebrew and other Canaanite dialects are still hard to tell apart."),
    ('814 BC (traditional)', "Phoenicians from Tyre found Carthage. They also settle at Motya and Lilybaeum (modern Marsala) in Sicily, and in Malta."),
    ('c. 800s–900s', "In Abbasid Baghdad scholars translate Greek works (Aristotle, Galen, Euclid, Ptolemy) into Arabic over about two centuries."),
    ('827–1091', "Sicily is part of the Arabic-speaking world (see the Sicily card)."),
    ('1138–1154', "In Palermo, al-Idrisi makes a 70-map atlas of the known world for Roger II, finished in 1154."),
    ('1202', "Fibonacci's Liber Abaci introduces the Hindu–Arabic numerals to Europe."),
    ('1973', "Arabic becomes the sixth official language of the United Nations."),
]

# ------------------------------------------------------------------- topics --
# Part kinds: p (paragraph), bullets, timeline, facts (label/value rows), note (callout),
# and the structured blocks: bridges, greetings, regions, roots, scenarios, missions.
TOPICS = [
    dict(id='bridges', icon='language-outline', title='Arabic is already in your kitchen',
         hook="Words you already say came from Arabic. Tap one to hear it.",
         parts=[
             dict(t='p', text="When goods travelled around the Mediterranean, words travelled with them. Italian picked up Arabic "
                              "words through trade, and Sicilian through centuries of living side by side. Each card shows the "
                              "Arabic word, what it became, and the story."),
             dict(t='bridges'),
             dict(t='note', text="Honest scale check: about 300 Sicilian words come from Arabic, mostly farming and water words. "
                                 "Spanish borrowed far more. Arabic didn't replace Sicilian; it seasoned it."),
             dict(t='p', text="Spot a pattern: Arabic 'the' is al-, and it often got glued to the front. Italian albicocca "
                              "(apricot) and algebra both keep it. When you meet al- in this app, think 'the'."),
         ]),
    dict(id='sicily', icon='business-outline', title='When Palermo spoke Arabic',
         hook="Sicily was part of the Arabic-speaking world for over two centuries.",
         parts=[
             dict(t='timeline', items=[dict(when=a, text=b) for a, b in TL_SICILY]),
             dict(t='p', text="Daily life was multilingual: Classical Arabic was the official language, alongside Sicilian, "
                              "Byzantine Greek, Berber and Judeo-Arabic. Arabic stayed a language of government for about a "
                              "century into Norman rule, and Muslims were probably still a majority of the island's people "
                              "until at least the late 12th century."),
             dict(t='p', text="In the fields: the Arab period is credited with introducing or spreading oranges, lemons, "
                              "pistachio, sugarcane, dates and mulberries, and with better irrigation by qanats. The Sicilian "
                              "words zàgara (blossom), saia (canal) and zuccu (market) are Arabic."),
             dict(t='bullets', items=[
                 "Caltanissetta: Arabic Qal'at an-nisaa', 'castle of the women'.",
                 "Bibbirria, a gate of Agrigento: Arabic bab ar-riyaah, 'Gate of the Winds'.",
             ]),
             dict(t='note', text="Think layers, not replacement: Arab, Byzantine Greek, Norman and Latin worlds shared this one island."),
         ]),
    dict(id='maltese', icon='boat-outline', title='Maltese: Arabic in Italian clothes',
         hook="A living language that sounds like your two interests at once.",
         parts=[
             dict(t='p', text="Maltese descends from Siculo-Arabic, a Maghrebi Arabic dialect that developed in Muslim Sicily "
                              "(831–1091). It is now the only standardised Semitic language written entirely in Latin letters, "
                              "and the only Semitic language official in the European Union."),
             dict(t='facts', rows=[
                 dict(label='Speakers', value='roughly half a million (sources give 530,000–570,000)'),
                 dict(label='Vocabulary', value='about 52% Romance (Sicilian and Italian), about 32% Arabic'),
                 dict(label='But', value='most of the core, everyday words and grammar words are Arabic'),
                 dict(label='Official', value='spelling standard 1924, official language 1934'),
             ]),
             dict(t='p', text="Same word, two spellings. Tap the Arabic to hear it:"),
             dict(t='pairs', items=[
                 dict(left='raġel (man)', word=w_rajul),
                 dict(left='tifel (boy)', word=w_tifl),
                 dict(left='dar (house)', word=w_daar),
                 dict(left='xemx (sun; x = sh)', word=w_shams),
                 dict(left='sajf (summer)', word=w_sayf),
             ]),
             dict(t='note', text="Maltese is the living descendant of Sicily's Arabic: it kept an Arabic core while borrowing "
                                 "Sicilian and Italian vocabulary."),
         ]),
    dict(id='sea', icon='compass-outline', title='The sea that connected everything',
         hook="From Carthage to Fibonacci: the Mediterranean as one long conversation.",
         parts=[
             dict(t='timeline', items=[dict(when=a, text=b) for a, b in TL_SEA]),
             dict(t='p', text="Distant cousins: Phoenician, the language of Carthage, and Arabic are both Semitic languages. The "
                              "Phoenician alphabet is the ancestor of the Greek alphabet, and through Greek of Latin; it also "
                              "influenced Syriac and Arabic writing."),
             dict(t='p', text="Ideas travelled too. Historians debate how formal Baghdad's famous 'House of Wisdom' really was, "
                              "but the translation of Greek science and philosophy into Arabic is well documented. And a boy from "
                              "Pisa, Leonardo Fibonacci, was educated in Bugia (now Béjaïa, Algeria), where his father ran a "
                              "trading post, and learned the numerals Europe later adopted."),
             dict(t='p', text="Even small words made the trip: Greek pandokheion became Arabic funduq, then Italian fondaco."),
         ]),
    dict(id='homes', icon='earth-outline', title='One language, many homes',
         hook="Same Arabic, very different street life.",
         parts=[
             dict(t='p', text="Modern Standard Arabic (MSA) is what you read in books and newspapers and hear in news and formal "
                              "speech, and what schools teach. Everyday speech is in dialects, learned at home and mostly "
                              "unwritten. The words and verb patterns in this app are MSA-style, which people understand "
                              "everywhere; each home dialect then bends them."),
             dict(t='greetings'),
             dict(t='regions'),
             dict(t='note', text="Broad strokes, not rules: every country and city differs. Some linguists call the dialects "
                                 "separate languages, while Arabic speakers generally say they speak one language."),
         ]),
    dict(id='use', icon='airplane-outline', title="Where you'd actually use it",
         hook="Real situations, starting with your own neighbourhood.",
         parts=[
             dict(t='facts', rows=[
                 dict(label='Native speakers', value='about 411 million'),
                 dict(label='Second-language users', value='about 70 million more'),
                 dict(label='Official in', value='24 states and territories'),
                 dict(label='United Nations', value='official language since 1973 (World Arabic Language Day, 18 December)'),
             ]),
             dict(t='scenarios'),
             dict(t='p', text="Italy, end of 2024 (Italian Ministry of Labour): 377,554 Moroccan, 175,236 Egyptian and 112,486 "
                              "Tunisian citizens were legally resident. Most speak a local dialect at home, so what you "
                              "hear will sound different from MSA. See 'One language, many homes'."),
             dict(t='p', text="Try this week. Small, real, doable. Tap to tick them off:"),
             dict(t='missions'),
         ]),
    dict(id='roots', icon='git-branch-outline', title='The secret that makes Arabic learnable',
         hook="Learn one root, unlock a whole family of words.",
         parts=[
             dict(t='p', text="Many Arabic words are built from a root of consonants (often three) fitted into vowel patterns. "
                              "Learn the root once and you recognise the whole family. Tap to hear each word."),
             dict(t='roots'),
             dict(t='p', text="This is why Conjugate practice pays off twice: the same patterns that change a verb for 'I' or "
                              "'you' also build nouns, so new words stop feeling random."),
             dict(t='note', text="When it feels hard: new sounds and patterns with few familiar cousins make Arabic feel slow at "
                                 "first, and that is normal. It is also why early wins feel big. Ten minutes a day beats a long "
                                 "Sunday. You only need the next small step."),
         ]),
]

SOURCES = [
    ('Muslim Sicily (dates, languages, crops)', 'https://en.wikipedia.org/wiki/Muslim_Sicily'),
    ('Sicilian language (Arabic words, about 300)', 'https://en.wikipedia.org/wiki/Sicilian_language'),
    ('Maltese language', 'https://en.wikipedia.org/wiki/Maltese_language'),
    ('Arabic language (speakers, dialects, UN)', 'https://en.wikipedia.org/wiki/Arabic'),
    ('Egyptian Arabic', 'https://en.wikipedia.org/wiki/Egyptian_Arabic'),
    ('United Nations: Arabic Language Day', 'https://www.un.org/en/node/139271'),
    ('Tabula Rogeriana (al-Idrisi)', 'https://en.wikipedia.org/wiki/Tabula_Rogeriana'),
    ('Fibonacci', 'https://en.wikipedia.org/wiki/Fibonacci'),
    ('Phoenicia', 'https://en.wikipedia.org/wiki/Phoenicia'),
    ('House of Wisdom (and the historians’ debate)', 'https://en.wikipedia.org/wiki/House_of_Wisdom'),
    ('Caltanissetta (name)', 'https://en.wikipedia.org/wiki/Caltanissetta'),
    ('Wiktionary: fondaco', 'https://en.wiktionary.com/wiki/fondaco'),
    ('Etymonline: zero', 'https://www.etymonline.com/index.php?term=zero'),
    ('The Local Italy: Italian words from Arabic', 'https://www.thelocal.it/20240711/11-italian-words-that-are-originally-arabic'),
    ('SBS: Salamelecco!', 'https://www.sbs.com.au/language/english/salamelecco-how-arabic-influenced-italy-s-language-and-culture'),
    ('Italian Ministry of Labour: Moroccan community 2025', 'https://lavoro.gov.it/documenti-e-norme/studi-e-statistiche/moroccan-community-italy-2025'),
    ('Italian Ministry of Labour: Egyptian community 2025', 'https://lavoro.gov.it/documenti-e-norme/studi-e-statistiche/egyptian-community-italy-2025'),
    ('Italian Ministry of Labour: Tunisian community 2025', 'https://lavoro.gov.it/documenti-e-norme/studi-e-statistiche/tunisian-community-italy-2025'),
]

# ------------------------------------------------------------ sanity checks --
ids = [t['id'] for t in TOPICS]
assert len(ids) == len(set(ids))
assert len({m[0] for m in MISSIONS}) == len(MISSIONS)
for sp in SPARKS:
    assert len(sp[0]) < 220, sp[0]
if errors:
    print('ERRORS:')
    for e in errors:
        print('  ', e)
    sys.exit(1)


# ---------------------------------------------------------------------- TS --
def j(x):
    return json.dumps(x, ensure_ascii=False)


out = []
w = out.append
w("// GENERATED by tools/gen_culture.py. Do not edit by hand.")
w("// Culture and motivation content. Facts come from the sources listed in SOURCES (shown in the app).")
w("")
w("export interface Word { latin: string; script: string; en: string }")
w("export interface Bridge { id: string; lang: 'Italian' | 'Sicilian' | 'Place'; word: Word; became: string; story: string; card: boolean }")
w("export interface Root { root: string; meaning: string; words: Word[]; note: string }")
w("export interface Greeting { region: string; say: string; word?: Word }")
w("export interface Region { name: string; where: string; icon: string; text: string }")
w("export interface Scenario { id: string; icon: string; title: string; text: string; words: Word[] }")
w("export interface Spark { text: string; word?: Word }")
w("export interface TimelineItem { when: string; text: string }")
w("export type Part =")
w("  | { t: 'p'; text: string }")
w("  | { t: 'note'; text: string }")
w("  | { t: 'bullets'; items: string[] }")
w("  | { t: 'timeline'; items: TimelineItem[] }")
w("  | { t: 'facts'; rows: { label: string; value: string }[] }")
w("  | { t: 'pairs'; items: { left: string; word: Word }[] }")
w("  | { t: 'bridges' }")
w("  | { t: 'greetings' }")
w("  | { t: 'regions' }")
w("  | { t: 'roots' }")
w("  | { t: 'scenarios' }")
w("  | { t: 'missions' };")
w("export interface Topic { id: string; icon: string; title: string; hook: string; parts: Part[] }")
w("")

bridges = [dict(id=f'br{i}', lang=b[0], word=word_ref(b[1]), became=b[2], story=b[3], card=b[4]) for i, b in enumerate(BRIDGES)]
w("export const BRIDGES: Bridge[] = " + j(bridges) + ";")
w("")
roots = [dict(root=r['root'], meaning=r['meaning'], words=[word_ref(x) for x in r['words']], note=r['note']) for r in ROOTS]
w("export const ROOTS: Root[] = " + j(roots) + ";")
w("")
greet = []
for g in GREETINGS:
    d = dict(region=g['region'], say=g['say'])
    if g.get('word'):
        d['word'] = word_ref(g['word'])
    greet.append(d)
w("export const GREETINGS: Greeting[] = " + j(greet) + ";")
w("")
w("export const REGIONS: Region[] = " + j(REGIONS) + ";")
w("")
scen = [dict(id=s['id'], icon=s['icon'], title=s['title'], text=s['text'], words=[word_ref(x) for x in s['words']]) for s in SCENARIOS]
w("export const SCENARIOS: Scenario[] = " + j(scen) + ";")
w("")
w("export const MISSIONS: { id: string; text: string }[] = " + j([dict(id=a, text=b) for a, b in MISSIONS]) + ";")
w("")
w("export const REASONS: { id: string; label: string; icon: string }[] = " + j([dict(id=a, label=b, icon=c) for a, b, c in REASONS]) + ";")
w("")
w("export const PEP: string[] = " + j(PEP) + ";")
w("")
sparks = []
for text, wd in SPARKS:
    d = dict(text=text)
    if wd:
        d['word'] = word_ref(wd)
    sparks.append(d)
w("export const SPARKS: Spark[] = " + j(sparks) + ";")
w("")


def conv_part(p):
    p = dict(p)
    if p['t'] == 'pairs':
        p['items'] = [dict(left=i['left'], word=word_ref(i['word'])) for i in p['items']]
    return p


topics = [dict(id=t['id'], icon=t['icon'], title=t['title'], hook=t['hook'], parts=[conv_part(p) for p in t['parts']]) for t in TOPICS]
w("export const TOPICS: Topic[] = " + j(topics) + ";")
w("")
w("export const SOURCES: { label: string; url: string }[] = " + j([dict(label=a, url=b) for a, b in SOURCES]) + ";")
w("")
open(os.path.join(ROOT, 'lib', 'culture-data.ts'), 'w', encoding='utf-8').write('\n'.join(out))
print(f"wrote lib/culture-data.ts: {len(TOPICS)} topics, {len(BRIDGES)} bridges, {len(SPARKS)} sparks, "
      f"{len(ROOTS)} roots, {len(SCENARIOS)} scenarios, {len(MISSIONS)} missions | {len(WORDS)} verified Arabic words")
