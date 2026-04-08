/**
 * VoiceRecorder — microphone button that records audio via the MediaRecorder
 * API, then calls the backend STT endpoint and returns the transcript.
 */

"use client";

import { useCallback, useRef, useState } from "react";
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

export function VoiceRecorder({ language, onTranscript, disabled, className }: VoiceRecorderProps) {
  const [state, setState] = useState<State>("idle");
  const mediaRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const handleClick = useCallback(async () => {
    if (disabled) return;

    if (state === "recording") {
      mediaRef.current?.stop();
      return;
    }

    if (state !== "idle") return;

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
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
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
    }
  }, [state, language, onTranscript, disabled]);

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
