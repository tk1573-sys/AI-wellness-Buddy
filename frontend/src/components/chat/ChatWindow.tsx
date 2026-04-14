/**
 * ChatWindow — renders the conversation message area with chat history.
 * Handles message display, typing indicator, and auto-scroll.
 *
 * Ordering guarantee:
 *  - Messages are sorted ascending by `timestamp` before rendering so the
 *    conversation order is always correct regardless of React state merge order.
 *  - Scroll behaviour: instant (no animation) for history restore; smooth only
 *    for new messages appended during an active session.
 */

"use client";

import { useEffect, useRef } from "react";
import { ChatBubble } from "./ChatBubble";
import { TypingIndicator } from "./TypingIndicator";
import { LanguagePreference, t } from "@/lib/i18n";
import type { EmotionScore } from "@/lib/api";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  emotion?: string | null;
  confidence?: number;
  isHighRisk?: boolean;
  escalationMessage?: string | null;
  scores?: EmotionScore[];
  responseType?: "generic" | "personalized";
  personalizationScore?: number;
  /** ISO-8601 timestamp used for strict chronological ordering. */
  timestamp?: string;
}

interface ChatWindowProps {
  messages: ChatMessage[];
  isLoading: boolean;
  language?: LanguagePreference;
  /** Pass true while the initial history load is running. */
  isRestoringHistory?: boolean;
}

/**
 * Skeleton loader for message history.
 */
function MessageSkeleton() {
  return (
    <div className="flex gap-3 animate-pulse">
      <div className="w-8 h-8 rounded-full bg-gray-800" />
      <div className="flex-1 space-y-2">
        <div className="h-4 bg-gray-800 rounded w-3/4" />
        <div className="h-4 bg-gray-800 rounded w-1/2" />
      </div>
    </div>
  );
}

/** Sort messages ascending by timestamp so ordering is always correct. */
function sortedMessages(msgs: ChatMessage[]): ChatMessage[] {
  return [...msgs].sort((a, b) => {
    if (!a.timestamp && !b.timestamp) return 0;
    if (!a.timestamp) return -1;
    if (!b.timestamp) return 1;
    return a.timestamp < b.timestamp ? -1 : a.timestamp > b.timestamp ? 1 : 0;
  });
}

/** Stable message key: prefer timestamp+role, fall back to index. */
function messageKey(msg: ChatMessage, i: number): string {
  return msg.timestamp ? `${msg.timestamp}-${msg.role}` : `idx-${i}`;
}

export function ChatWindow({
  messages,
  isLoading,
  language = "english",
  isRestoringHistory = false,
}: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  // Track the previous message count to distinguish new messages from history restores.
  const prevCountRef = useRef(messages.length);

  useEffect(() => {
    const prevCount = prevCountRef.current;
    const currentCount = messages.length;
    prevCountRef.current = currentCount;

    if (!bottomRef.current) return;

    // History restore or initial load: jump instantly to the bottom (no animation).
    if (isRestoringHistory || prevCount === 0) {
      bottomRef.current.scrollIntoView({ behavior: "instant" as ScrollBehavior });
      return;
    }

    // New message appended: smooth scroll so the user sees the transition.
    if (currentCount > prevCount) {
      bottomRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isLoading, isRestoringHistory]);

  const sorted = sortedMessages(messages);

  return (
    <main className="flex-1 overflow-y-auto px-4 py-6 space-y-5 scroll-smooth">
      {sorted.length === 0 && !isLoading && (
        <div className="flex flex-col items-center justify-center h-full space-y-3 text-center animate-fade-in">
          <span className="text-5xl">💬</span>
          <h2 className="text-xl font-semibold text-gray-200">
            {t("chat.welcome.title", language)}
          </h2>
          <p className="text-gray-500 text-sm max-w-xs">
            {t("chat.welcome.subtitle", language)}
          </p>
        </div>
      )}

      {/* Show loading skeletons while loading history */}
      {isLoading && sorted.length === 0 && (
        <div className="space-y-5">
          {[1, 2, 3].map((i) => (
            <MessageSkeleton key={i} />
          ))}
        </div>
      )}

      {sorted.map((msg, i) => (
        <div key={messageKey(msg, i)} className="flex flex-col">
          <ChatBubble
            role={msg.role}
            content={msg.content}
            scores={msg.scores}
            responseType={msg.responseType}
            personalizationScore={msg.personalizationScore}
          />
        </div>
      ))}

      {/* Show typing indicator when sending new message */}
      {isLoading && sorted.length > 0 && <TypingIndicator />}

      <div ref={bottomRef} />
    </main>
  );
}

