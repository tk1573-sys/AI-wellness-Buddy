/**
 * VoiceRecorder — microphone button that transcribes speech to text.
 *
 * Strategy:
 *  1. Web Speech API (SpeechRecognition) — real-time, client-side, no backend
 *     round-trip.  Available in Chrome, Edge, and most Chromium-based browsers.
 *  2. MediaRecorder fallback — records a WAV/WebM blob and sends it to the
 *     backend /api/v1/voice/transcribe endpoint if the Web Speech API is
 *     unavailable.
 */

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { Mic, MicOff, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import { transcribeVoice } from "@/lib/api";
import { t, type LanguagePreference } from "@/lib/i18n";

interface VoiceRecorderProps {
  language: LanguagePreference;
  onTranscript: (text: string) => void;
  disabled?: boolean;
  className?: string;
}

type State = "idle" | "recording" | "transcribing";

// Map our language preference to BCP-47 STT locale codes.
// Bilingual / Tanglish uses en-IN because Tanglish is Tamil words spoken in
// Latin/English script — Google STT's en-IN model handles Indian-English
// code-switching far better than ta-IN for this use-case.
const LANG_TO_LOCALE: Record<LanguagePreference, string> = {
  english: "en-IN",
  tamil: "ta-IN",
  bilingual: "en-IN",
};

/** Return true when the browser's Web Speech API is available. */
function hasSpeechRecognitionApi(): boolean {
  if (typeof window === "undefined") return false;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const w = window as any;
  return typeof w.SpeechRecognition === "function" || typeof w.webkitSpeechRecognition === "function";
}

export function VoiceRecorder({ language, onTranscript, disabled, className }: VoiceRecorderProps) {
  const [state, setState] = useState<State>("idle");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const recognitionRef = useRef<any>(null);
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  // Stop the Web Speech API session on unmount.
  useEffect(() => {
    return () => {
      recognitionRef.current?.abort();
      mediaRef.current?.stop();
    };
  }, []);

  // ── Web Speech API path ──────────────────────────────────────────────────
  const startWebSpeech = useCallback(() => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const w = window as any;
    const SpeechRecognitionCtor = w.SpeechRecognition ?? w.webkitSpeechRecognition;
    if (!SpeechRecognitionCtor) return false;

    const recognition = new SpeechRecognitionCtor();
    recognitionRef.current = recognition;
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = LANG_TO_LOCALE[language] ?? "en-IN";

    recognition.onstart = () => setState("recording");

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    recognition.onresult = (event: any) => {
      const transcript = Array.from(event.results as ArrayLike<{ 0: { transcript: string } }>)
        .map((r) => r[0].transcript)
        .join(" ")
        .trim();
      if (transcript) {
        onTranscript(transcript);
      } else {
        toast.error("Could not understand audio. Please try again.");
      }
      setState("idle");
    };

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    recognition.onerror = (event: any) => {
      if (event.error === "not-allowed") {
        toast.error("Microphone access denied. Please allow microphone in browser settings.");
      } else if (event.error !== "aborted") {
        toast.error("Speech recognition failed. Please try again or type your message.");
      }
      setState("idle");
    };

    recognition.onend = () => {
      // Unconditionally reset — this fires after stop() or on natural end
      setState("idle");
    };

    try {
      recognition.start();
      return true;
    } catch {
      return false;
    }
  }, [language, onTranscript]);

  // ── MediaRecorder fallback path ──────────────────────────────────────────
  const startMediaRecorder = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      chunksRef.current = [];
      const recorder = new MediaRecorder(stream);
      mediaRef.current = recorder;

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        setState("transcribing");
        const mimeType = recorder.mimeType || "audio/webm";
        const blob = new Blob(chunksRef.current, { type: mimeType });
        try {
          const transcript = await transcribeVoice(blob, language);
          if (transcript.trim()) {
            onTranscript(transcript);
          } else {
            toast.error("Could not understand audio. Please try again.");
          }
        } catch {
          toast.error("Transcription failed. Please type your message.");
        } finally {
          setState("idle");
        }
      };

      recorder.start();
      setState("recording");
    } catch {
      toast.error("Microphone access denied or unavailable.");
      setState("idle");
    }
  }, [language, onTranscript]);

  const handleClick = useCallback(async () => {
    if (disabled) return;

    // Stop in progress
    if (state === "recording") {
      recognitionRef.current?.stop();
      mediaRef.current?.stop();
      return;
    }

    if (state !== "idle") return;

    // Prefer Web Speech API; fall back to MediaRecorder
    if (hasSpeechRecognitionApi()) {
      startWebSpeech();
    } else {
      await startMediaRecorder();
    }
  }, [state, disabled, startWebSpeech, startMediaRecorder]);

  const label =
    state === "recording"
      ? t("chat.voice.stop", language)
      : state === "transcribing"
      ? "Transcribing…"
      : t("chat.voice.start", language);

  return (
    <button
      type="button"
      onClick={handleClick}
      disabled={disabled || state === "transcribing"}
      aria-label={label}
      title={label}
      className={`h-10 w-10 flex-shrink-0 flex items-center justify-center rounded-xl border transition-colors disabled:opacity-40 ${
        state === "recording"
          ? "bg-red-700/45 border-red-400/70 text-red-200 animate-pulse"
          : "border-brand-500/50 text-brand-200 bg-brand-600/15 hover:text-white hover:bg-brand-600/30"
      } ${className ?? ""}`}
    >
      {state === "transcribing" ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : state === "recording" ? (
        <MicOff className="w-4 h-4" />
      ) : (
        <Mic className="w-4 h-4" />
      )}
    </button>
  );
}
