import { useCallback, useEffect, useState } from "react";
import { Alert } from "react-native";
import * as Speech from "expo-speech";
import AsyncStorage from "@react-native-async-storage/async-storage";

/**
 * Arabic text-to-speech.
 *
 * The app DISPLAYS Latin transcription, but phone voices cannot read that as Arabic. Every word and
 * verb form therefore also carries a hidden, fully-vowelled Arabic-script string (`script`, generated
 * and verified by tools/gen_data.py) which is what the Arabic voice (ar-SA) actually speaks.
 *
 * Mute only stops AUTOMATIC playback (card appears, answer revealed). Tapping a speaker button
 * always plays, because that is a deliberate request.
 */

const MUTE_KEY = "speech_muted";
const ARABIC_LANG = "ar-SA";
const ARABIC_RATE = 0.8; // a little slower than normal so the sounds are easy to hear

let muted = false;
let loaded: Promise<void> | null = null;
const listeners = new Set<(m: boolean) => void>();

function ensureLoaded(): Promise<void> {
  if (!loaded) {
    loaded = AsyncStorage.getItem(MUTE_KEY)
      .then((v) => {
        muted = v === "1";
        listeners.forEach((l) => l(muted));
      })
      .catch(() => {});
  }
  return loaded;
}

export function setSpeechMuted(value: boolean) {
  muted = value;
  if (value) Speech.stop();
  listeners.forEach((l) => l(muted));
  AsyncStorage.setItem(MUTE_KEY, value ? "1" : "0").catch(() => {});
}

/** [muted, toggle] — shared across screens and remembered between launches. */
export function useSpeechMuted(): readonly [boolean, () => void] {
  const [value, setValue] = useState(muted);
  useEffect(() => {
    let alive = true;
    ensureLoaded().then(() => alive && setValue(muted));
    listeners.add(setValue);
    return () => {
      alive = false;
      listeners.delete(setValue);
    };
  }, []);
  const toggle = useCallback(() => setSpeechMuted(!muted), []);
  return [value, toggle] as const;
}

// undefined = not looked up yet, null = use the system default for ar-SA, "missing" = no Arabic voice installed
let arabicVoice: string | null | "missing" | undefined;
let warned = false;

async function resolveArabicVoice(): Promise<string | null | "missing"> {
  if (arabicVoice !== undefined) return arabicVoice;
  try {
    // Never let the voice lookup block speech (on some platforms it can wait for a voice list that never comes).
    const voices = await Promise.race([
      Speech.getAvailableVoicesAsync(),
      new Promise<Speech.Voice[]>((resolve) => setTimeout(() => resolve([]), 1500)),
    ]);
    const arabic = voices.filter((v) => (v.language ?? "").toLowerCase().startsWith("ar"));
    if (voices.length > 0 && arabic.length === 0) {
      arabicVoice = "missing";
    } else if (arabic.length > 0) {
      const rank = (v: (typeof arabic)[number]) =>
        (v.quality === Speech.VoiceQuality.Enhanced ? 2 : 0) + ((v.language ?? "").toLowerCase() === "ar-sa" ? 1 : 0);
      arabic.sort((a, b) => rank(b) - rank(a));
      arabicVoice = arabic[0].identifier;
    } else {
      arabicVoice = null;
    }
  } catch {
    arabicVoice = null;
  }
  return arabicVoice;
}

function warnNoVoice() {
  if (warned) return;
  warned = true;
  Alert.alert(
    "Arabic voice not installed",
    "Your phone has no Arabic text-to-speech voice yet, so it cannot pronounce Arabic.\n\n" +
      "Install one in Settings ▸ Accessibility ▸ Spoken Content ▸ Voices ▸ Arabic, then come back. " +
      "(If you hear nothing at all, also check the silent switch.)"
  );
}

/** Speak vocalised Arabic script with an Arabic voice. */
export async function speakArabic(script: string | undefined | null): Promise<void> {
  if (!script) return;
  const voice = await resolveArabicVoice();
  if (voice === "missing") {
    warnNoVoice();
    return;
  }
  Speech.stop();
  Speech.speak(script, {
    language: ARABIC_LANG,
    rate: ARABIC_RATE,
    ...(voice ? { voice } : {}),
  });
}

/** Automatic playback: does nothing while muted. */
export async function speakAuto(script: string | undefined | null): Promise<void> {
  await ensureLoaded();
  if (muted) return;
  await speakArabic(script);
}

export function stopSpeaking() {
  Speech.stop();
}
