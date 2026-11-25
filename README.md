# Ultimate Arabic Tutor

An Expo / React Native app for learning Arabic with flashcards, conjugation practice, a sentence-building game and a
culture / motivation section — same
layout and build setup as the Italian tutor, using Latin transcription (no Arabic script).

## What's inside

| Tab | What it does |
| --- | --- |
| **Flashcards** | 368 cards (142 nouns, 61 verbs, 59 adjectives, 27 adverbs, 79 pronouns / particles / phrases / numbers). Tap to flip, swipe right = learned, swipe left = still learning, undo, shuffle, matching game. Nouns show gender + plural, adjectives show the feminine form, verbs show the past form. |
| **Conjugate** | Type the conjugated form for 61 common verbs in **present, past and future**, for all 10 persons (ana, anta, anti, huwa, hiya, nahnu, antum, antunna, hum, hunna). "Arabic prompt" mode (see `ktubu` + `anta`) or "English prompt" mode (see "you (m) write"). Filter by regular / irregular / derived (Forms II–X) or pick individual verbs. |
| **Build** | Sentence-building game: arrange colour-coded word blocks into the correct Arabic word order for an English sentence. 822 sentences in 3 levels (see below). |
| **Culture** | Why learn Arabic: your own "My Why", a daily fact, and seven topics on Italian / Sicilian links, Muslim Sicily, Maltese, the Mediterranean, regional dialects and lifestyles, where it is useful and how roots work (see below). |
| **Tenses** | Pronoun + `a- / ta- / ya- / na-` pattern chart, plus present / past / future cards with full tables for a regular, hollow, defective and derived verb. Not in the tab bar (iOS shows at most 5 tabs): open it with the **Tense charts** button on Conjugate. |
| **Profile** | Daily streak, level, accuracy, recent sessions. |

### Culture (why this language is worth it)

A separate tab for finding purpose in the language, not an exercise.

* **My Why** – write your own reason and tick the reasons that fit. It is saved on the phone, shown at the top of the tab,
  and *kept* when you reset your scores. Underneath: your days studied / cards learned / sentences built, and a short
  daily encouragement line.
* **Today's Spark** – one surprising fact a day (24 of them); **Another** shows the next. Facts with an Arabic word have a
  play button.
* **Seven topics** (tap to open; a tick shows the ones you have read):
  *Arabic is already in your kitchen* (18 Arabic words behind Italian and Sicilian words and place names, filterable) ·
  *When Palermo spoke Arabic* · *Maltese: Arabic in Italian clothes* · *The sea that connected everything* (Phoenicians,
  Baghdad translators, al-Idrisi in Palermo, Fibonacci) · *One language, many homes* (standard Arabic vs dialects,
  Maghreb / Egypt / Levant / Gulf / Iraq, "how are you?" in each) · *Where you'd actually use it* (travel, neighbours in
  Italy, food, work, media, with figures from Italy's Ministry of Labour, plus six "try this week" missions you can tick
  off) · *The secret that makes Arabic learnable* (roots: k-t-b and d-r-s).
* **Audio** – every Arabic word on this tab plays the Arabic voice when you tap it. Nothing plays automatically, so the
  Auto-play mute switch does not apply here.
* **Sources** – "Where these facts come from" at the bottom links the pages used. Where historians disagree (for example how
  formal Baghdad's House of Wisdom was, or why Caltanissetta is "castle of the women") the text says so.

### Build (sentence-building game)

You get an English sentence (*"The student reads a book."*) and a pile of word blocks. Tap the blocks in
the order you would say them in Arabic. Every block is colour-coded **and** labelled with its word type, so
you learn to see the grammar, not just the words:

| Label | Word type | Tip |
| --- | --- | --- |
| **NOUN** | noun (m / f) | `al-` = "the" |
| **VERB** | verb | ending / prefix = who and when |
| **ADJ** | adjective | comes *after* its noun and matches gender + `al-` |
| **ADV** | adverb | how / when / how much |
| **PREP** | preposition | placed *before* its noun |
| **PRON** | pronoun / "this" | I, you, he … / hadha |
| **CONJ** | conjunction | `wa` = and |
| **PART** | particle | `hal` (yes/no question), `laa` (not), `ayna` (where) |

* **Levels** – *Easy* 2 blocks, no extras · *Medium* 2–4 blocks plus 1 decoy · *Hard* 3–5 blocks plus 2 decoys
  (decoys are often the wrong gender, e.g. *kabiira* when the noun is masculine) · *Mix*.
* **Check** marks each slot right or wrong · **Hint** fills the next correct block (and breaks your no-hint streak) ·
  **Clear** empties the slots · **Show me the answer** appears after a miss.
* After a sentence you see the Latin sentence, its word-type pattern (e.g. VERB · NOUN · PREP · NOUN) and a one-line
  syntax tip: verb-first order, adjective after noun, possession (*idaafa*), negation with `laa`, `hal` questions,
  no "is/are" in the present tense, and so on. Some sentences accept more than one valid order.
* **Audio** – each block is spoken in Arabic as you place it and the whole sentence is spoken when you finish
  (the same Auto-play on/off toggle as the other tabs; **Listen** always plays).
* Stats (sentences built, first-try accuracy, no-hint streak) are saved on the phone and count toward your daily streak.

### Arabic audio

Everything is *shown* in Latin transcription but *spoken* by an Arabic voice (`ar-SA`). Phone voices
can't read Latin transcription as Arabic, so every flashcard word and every conjugated verb form also
carries a hidden, fully-vowelled Arabic-script string (never displayed) that the voice reads.

* **Flashcards** – **Listen** plays the Arabic word (verbs: past form, then the "I" form, e.g. *kataba, aktubu*).
  Auto-play says the word when it appears (or when you flip it, in English-first mode).
* **Conjugate** – speaker button says the verb before you answer and the correct form after; the correct
  form also plays automatically once you check / reveal.
* **Mute** – the "Auto-play on/off" button stops automatic playback; it is remembered between launches.
  The Listen / speaker buttons always play when tapped.
* Needs an Arabic voice on the phone: *Settings ▸ Accessibility ▸ Spoken Content ▸ Voices ▸ Arabic*
  (the app tells you once if none is installed). Audio follows the iPhone silent switch.

### Transcription used everywhere

Long vowels are doubled (`aa`, `ii`, `uu`); `'` is hamza / ayn; `kh sh dh th gh` digraphs; emphatic
letters are written plain. Answer checking ignores case, accents, hyphens and a missing `'`, and
accepts `ee`/`oo` for `ii`/`uu` — but vowel length still has to be right (`taktubuna` ≠ `taktubuuna`).
The verb headword follows your notes: `ktubu`, `j'alu`, `takallamu`, `statii'u`.

## Build with Codemagic (unsigned IPA)

`codemagic.yaml` is the Italian app's workflow with the output renamed to `Arabic.ipa`:
`npm install` → `expo prebuild --platform ios` → `pod install` → unsigned `xcodebuild archive` → `build/Arabic.ipa`.

1. Push this folder to a new GitHub repo (`.gitignore` already skips `node_modules`, `ios`, etc.).
2. In Codemagic add the repo and run the **iOS Build** workflow.
3. Download `Arabic.ipa` from the build artifacts and sideload it as you do the Italian app.

Bundle id is `com.arabic` (Italian app: `com.italiano`), so both apps can be installed side by side.
Change it in `app.json` (`ios.bundleIdentifier`, `android.package`) if you want something else.

## Editing the word lists

The data file `lib/arabic-data.ts` is **generated** — don't edit it by hand.

* `tools/vocab.txt` — flashcard words (`arabic | english | m/f | note | example | translation`)
* `tools/script_ar.txt` — the hidden Arabic script for every word in `vocab.txt` (`latin | arabic`), used for audio
* `tools/verb_examples.txt` — one example sentence per verb
* `tools/gen_culture.py` — all Culture tab content (topics, sparks, word bridges, roots, missions, sources); every Arabic
  word is checked against its Latin spelling. Run `python3 tools/gen_culture.py` to regenerate `lib/culture-data.ts`
  (generated — don't edit by hand)
* `tools/gen_phrases.py` — builds the Build game's word blocks and sentences (grammar frames + verified Arabic per block);
  run `python3 tools/gen_phrases.py` to regenerate `lib/phrases.ts` (also generated — don't edit by hand)
* `tools/verbs.py` — verb conjugation rules / the list of verbs (Latin)
* `tools/verbs_ar.py` — the same verbs in Arabic script (audio); `tools/arabic.py` checks it

After changing any of them run `python3 tools/gen_data.py` from the project root. The generator
fails loudly on duplicate words, a verb example that doesn't contain one of that verb's forms, a word with
no Arabic script, or any Arabic that does not transliterate back to the Latin shown on screen (all 1,220
verb forms and all 307 words are checked this way). A new word needs a line in both `vocab.txt` and `script_ar.txt`.

## Local development

```
npm install
npx tsc --noEmit        # type-check
npx expo start          # run (Expo Go / simulator)
```

## Known limitations

* Audio quality is whatever Arabic voice iOS has installed (a downloaded "Enhanced" voice sounds best).
  Example sentences on the back of cards are not spoken — only words and verb forms.
* Hamza/ayn are both written `'` (as in your notes).
* Case endings are dropped on nouns (`kitaab`, not `kitaabun`); verbs keep the final `-u` like your notes.
