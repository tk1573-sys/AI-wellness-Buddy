/**
 * InputFooter — handles message input area with voice recorder and send button.
 */

"use client";

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
        />
        <Button
          onClick={onSend}
          loading={isLoading}
          disabled={!value.trim() || disabled}
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
