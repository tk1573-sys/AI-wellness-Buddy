/**
<<<<<<< HEAD
 * InputFooter — handles message input area with voice recorder and send button.
=======
 * InputFooter — chat input bar with voice recorder, auto-expanding textarea,
 * and send button. Extracted into a reusable component so the page layout
 * can place it independently of the message list.
>>>>>>> 4362f5eb8d9a4933237299b50fce9fb5d12654d1
 */

"use client";

<<<<<<< HEAD
import { Send } from "lucide-react";
import { Button } from "@/components/ui/Button";
import { LanguagePreference, t } from "@/lib/i18n";
import type { KeyboardEvent, RefObject } from "react";

interface InputFooterProps {
  value: string;
  onChange: (value: string) => void;
  onKeyDown: (e: KeyboardEvent<HTMLTextAreaElement>) => void;
  onSend: () => void;
  isLoading?: boolean;
  language?: LanguagePreference;
  disabled?: boolean;
  textareaRef?: RefObject<HTMLTextAreaElement>;
}

export function InputFooter({
  value,
  onChange,
  onKeyDown,
  onSend,
  isLoading = false,
  language = "english",
  disabled = false,
  textareaRef,
}: InputFooterProps) {
  return (
    <footer className="border-t border-glass-border bg-gray-950/80 backdrop-blur-sm px-4 py-3 flex-shrink-0">
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          rows={1}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={t("chat.placeholder", language)}
          disabled={isLoading || disabled}
          className="flex-1 resize-none rounded-xl border border-glass-border bg-white/5 px-4 py-2.5 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500 disabled:opacity-50 max-h-40 overflow-y-auto"
          aria-label="Message input"
=======
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
>>>>>>> 4362f5eb8d9a4933237299b50fce9fb5d12654d1
        />
        <Button
          onClick={onSend}
          loading={isLoading}
<<<<<<< HEAD
          disabled={!value.trim() || disabled}
=======
          disabled={!input.trim()}
>>>>>>> 4362f5eb8d9a4933237299b50fce9fb5d12654d1
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
