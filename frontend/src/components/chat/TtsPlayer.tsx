/**
 * TtsPlayer — plays TTS audio for an assistant message.
 * Fetches MP3 from the backend /api/v1/voice/tts endpoint and plays it.
 */

"use client";

import { useCallback, useRef, useState } from "react";
import { Volume2, Loader2 } from "lucide-react";
import toast from "react-hot-toast";
import { getTts } from "@/lib/api";
import { t, type LanguagePreference } from "@/lib/i18n";

interface TtsPlayerProps {
  text: string;
  language: LanguagePreference;
  /** Small index key so React can distinguish buttons per message */
  messageKey: string | number;
}

export function TtsPlayer({ text, language, messageKey }: TtsPlayerProps) {
  const [loading, setLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const handlePlay = useCallback(async () => {
    if (loading) return;

    // If already playing, stop
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
      return;
    }

    setLoading(true);
    try {
      const blob = await getTts(text, language);
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audioRef.current = audio;
      audio.onended = () => {
        URL.revokeObjectURL(url);
        audioRef.current = null;
      };
      audio.onerror = () => {
        URL.revokeObjectURL(url);
        audioRef.current = null;
      };
      await audio.play();
    } catch {
      toast.error("TTS playback unavailable.");
    } finally {
      setLoading(false);
    }
  }, [text, language, loading]);

  return (
    <button
      type="button"
      onClick={handlePlay}
      aria-label={t("chat.tts.replay", language)}
      title={t("chat.tts.replay", language)}
      key={messageKey}
      disabled={loading}
      className="ml-1 inline-flex items-center justify-center w-6 h-6 rounded-full text-gray-500 hover:text-brand-400 hover:bg-white/5 transition-colors disabled:opacity-40"
    >
      {loading ? (
        <Loader2 className="w-3 h-3 animate-spin" />
      ) : (
        <Volume2 className="w-3 h-3" />
      )}
    </button>
  );
}
