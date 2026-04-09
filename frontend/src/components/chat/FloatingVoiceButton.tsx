/**
 * FloatingVoiceButton — fixed bottom-right microphone action.
 */

"use client";

import { VoiceRecorder } from "./VoiceRecorder";
import type { LanguagePreference } from "@/lib/i18n";

interface FloatingVoiceButtonProps {
  language: LanguagePreference;
  onTranscript: (text: string) => void;
  disabled?: boolean;
}

export function FloatingVoiceButton({
  language,
  onTranscript,
  disabled = false,
}: FloatingVoiceButtonProps) {
  return (
    <div className="fixed right-4 bottom-24 z-50 lg:bottom-6">
      <div className="rounded-2xl border border-brand-500/50 bg-gray-950/85 p-2 shadow-2xl backdrop-blur-md">
        <VoiceRecorder
          language={language}
          onTranscript={onTranscript}
          disabled={disabled}
        />
      </div>
    </div>
  );
}
