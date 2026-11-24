# Ultimate Arabic Tutor

An Expo / React Native app for learning Arabic with flashcards and conjugation practice — same
layout and build setup as the Italian tutor, using Latin transcription (no Arabic script).

## What's inside

| Tab | What it does |
| --- | --- |
| **Flashcards** | 368 cards (142 nouns, 61 verbs, 59 adjectives, 27 adverbs, 79 pronouns / particles / phrases / numbers). Tap to flip, swipe right = learned, swipe left = still learning, undo, shuffle, matching game. Nouns show gender + plural, adjectives show the feminine form, verbs show the past form. |
| **Conjugate** | Type the conjugated form for 61 common verbs in **present, past and future**, for all 10 persons (ana, anta, anti, huwa, hiya, nahnu, antum, antunna, hum, hunna). "Arabic prompt" mode (see `ktubu` + `anta`) or "English prompt" mode (see "you (m) write"). Filter by regular / irregular / derived (Forms II–X) or pick individual verbs. |
| **Tenses** | Pronoun + `a- / ta- / ya- / na-` pattern chart, plus present / past / future cards with full tables for a regular, hollow, defective and derived verb. |
| **Profile** | Daily streak, level, accuracy, recent sessions. |

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
