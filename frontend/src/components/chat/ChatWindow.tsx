/**
 * ChatWindow — renders the conversation message area with chat history.
 * Handles message display, typing indicator, and auto-scroll.
 */

"use client";

import { useEffect, useRef } from "react";
import { ChatBubble } from "./ChatBubble";
import { TypingIndicator } from "./TypingIndicator";
import { LanguagePreference, t } from "@/lib/i18n";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  emotion?: string | null;
  confidence?: number;
  isHighRisk?: boolean;
  escalationMessage?: string | null;
}

interface ChatWindowProps {
  messages: ChatMessage[];
  isLoading: boolean;
  language?: LanguagePreference;
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

export function ChatWindow({ messages, isLoading, language = "english" }: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <main className="flex-1 overflow-y-auto px-4 py-6 space-y-5 scroll-smooth">
      {messages.length === 0 && !isLoading && (
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
      {isLoading && messages.length === 0 && (
        <div className="space-y-5">
          {[1, 2, 3].map((i) => (
            <MessageSkeleton key={i} />
          ))}
        </div>
      )}

      {messages.map((msg, i) => (
        <div key={i} className="flex flex-col">
          <ChatBubble
            role={msg.role}
            content={msg.content}
          />
        </div>
      ))}

      {/* Show typing indicator when sending new message */}
      {isLoading && messages.length > 0 && <TypingIndicator />}

      <div ref={bottomRef} />
    </main>
  );
}

