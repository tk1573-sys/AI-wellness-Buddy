/**
 * Chat page — the main ChatGPT-style interface.
 *
 * Features:
 *  - Conversation history loaded from API on mount
 *  - Real-time message exchange with typing indicator
 *  - Emotion badge on every assistant message
 *  - High-risk alert banner
 *  - Mobile-responsive layout
 */

"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import toast from "react-hot-toast";
import { Send } from "lucide-react";

import { sendMessage, getChatHistory, ChatMessage, ChatResponse } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { ChatBubble } from "@/components/chat/ChatBubble";
import { TypingIndicator } from "@/components/chat/TypingIndicator";
import { Button } from "@/components/ui/Button";

interface Message {
  role: "user" | "assistant";
  content: string;
  emotion?: string | null;
  confidence?: number;
  isHighRisk?: boolean;
  escalationMessage?: string | null;
}

export default function ChatPage() {
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>(undefined);
  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    }
  }, [router]);

  // Load existing chat history on mount
  useEffect(() => {
    getChatHistory()
      .then((history: ChatMessage[]) => {
        if (history.length > 0) {
          setMessages(
            history.map((m) => ({
              role: m.role as "user" | "assistant",
              content: m.content,
              emotion: m.emotion,
            }))
          );
        }
      })
      .catch(() => {
        // First-time user — no history yet, that's fine
      });
  }, []);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setIsLoading(true);

    try {
      const res: ChatResponse = await sendMessage(text, sessionId);
      if (!sessionId) setSessionId(res.session_id);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.reply,
          emotion: res.primary_emotion,
          confidence: res.confidence,
          isHighRisk: res.is_high_risk,
          escalationMessage: res.escalation_message,
        },
      ]);

      if (res.is_high_risk) {
        toast.error("High-risk content detected. Please seek support.", {
          duration: 8000,
          icon: "🆘",
        });
      }
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : "Something went wrong.");
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
      textareaRef.current?.focus();
    }
  }, [input, isLoading, sessionId]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gray-950">
      {/* Background blobs */}
      <div className="pointer-events-none fixed inset-0 overflow-hidden">
        <div className="absolute top-0 left-1/4 w-80 h-80 rounded-full bg-brand-600/10 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-80 h-80 rounded-full bg-purple-600/10 blur-3xl" />
      </div>

      {/* Message area */}
      <main className="relative z-10 flex-1 overflow-y-auto px-4 py-6 space-y-5">
        {messages.length === 0 && !isLoading && (
          <div className="flex flex-col items-center justify-center h-full space-y-3 text-center animate-fade-in">
            <span className="text-5xl">💬</span>
            <h2 className="text-xl font-semibold text-gray-200">
              How are you feeling today?
            </h2>
            <p className="text-gray-500 text-sm max-w-xs">
              Share what&apos;s on your mind. I&apos;m here to listen without judgment.
            </p>
          </div>
        )}

        {messages.map((msg, i) => (
          <ChatBubble
            key={i}
            role={msg.role}
            content={msg.content}
            emotion={msg.emotion}
            confidence={msg.confidence}
            isHighRisk={msg.isHighRisk}
            escalationMessage={msg.escalationMessage}
          />
        ))}

        {isLoading && <TypingIndicator />}

        <div ref={bottomRef} />
      </main>

      {/* Input area */}
      <footer className="relative z-10 border-t border-glass-border bg-gray-950/80 backdrop-blur-sm px-4 py-3">
        <div className="mx-auto max-w-3xl flex items-end gap-2">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message… (Enter to send, Shift+Enter for newline)"
            disabled={isLoading}
            className="flex-1 resize-none rounded-xl border border-glass-border bg-white/5 px-4 py-2.5 text-sm text-gray-100 placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-brand-500 disabled:opacity-50 max-h-40 overflow-y-auto"
          />
          <Button
            onClick={handleSend}
            loading={isLoading}
            disabled={!input.trim()}
            className="h-10 w-10 p-0 flex-shrink-0"
            aria-label="Send message"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-center text-xs text-gray-600 mt-2">
          AI Wellness Buddy is not a substitute for professional mental health care.
        </p>
      </footer>
    </div>
  );
}
