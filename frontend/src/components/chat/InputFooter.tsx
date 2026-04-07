/**
 * InputFooter — chat input bar with voice recorder, auto-expanding textarea,
 * and send button. Extracted into a reusable component so the page layout
 * can place it independently of the message list.
 */

"use client";

import { type RefObject } from "react";
import { Send } from "lucide-react";
import { VoiceRecorder } from "@/components/chat/VoiceRecorder";
import { Button } from "@/components/ui/Button";
import { t, type LanguagePreference } from "@/lib/i18n";

interface InputFooterProps {
  language: LanguagePreference;
  input: string;
  isLoading: boolean;
  textareaRef: RefObject<HTMLTextAreaElement>;
  onInputChange: (value: string) => void;
  onKeyDown: (e: React.KeyboardEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;
  onVoiceTranscript: (text: string) => void;
}

export function InputFooter({
  language,
  input,
  isLoading,
  textareaRef,
  onInputChange,
  onKeyDown,
  onSend,
  onVoiceTranscript,
}: InputFooterProps) {
  return (
    <footer className="relative z-10 border-t border-glass-border bg-gray-950/80 backdrop-blur-sm px-4 py-3">
      <div className="mx-auto max-w-full flex items-end gap-2">
        {/* Voice recorder button */}
        <VoiceRecorder
          language={language}
          onTranscript={onVoiceTranscript}
          disabled={isLoading}
        />
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={t("chat.placeholder", language)}
          disabled={isLoading}
          className="flex-1 resize-none rounded-xl border border-glass-border bg-white/5 px-4 py-2.5 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500 disabled:opacity-50 max-h-40 overflow-y-auto"
        />
        <Button
          onClick={onSend}
          loading={isLoading}
          disabled={!input.trim()}
          className="h-10 w-10 p-0 flex-shrink-0"
          aria-label={t("chat.send", language)}
        >
          <Send className="w-4 h-4" />
        </Button>
      </div>
      <p className="text-center text-xs text-gray-600 mt-2">
        AI Wellness Buddy is not a substitute for professional mental health care.
      </p>
    </footer>
  );
}
