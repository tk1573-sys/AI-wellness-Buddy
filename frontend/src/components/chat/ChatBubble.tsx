/**
 * ChatBubble — renders a single chat message with emotion badge and confidence score.
 */

import { clsx } from "clsx";
import { EmotionBadge } from "@/components/emotion/EmotionBadge";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
  emotion?: string | null;
  confidence?: number;
  isHighRisk?: boolean;
  escalationMessage?: string | null;
}

export function ChatBubble({
  role,
  content,
  emotion,
  confidence,
  isHighRisk,
  escalationMessage,
}: ChatBubbleProps) {
  const isUser = role === "user";

  return (
    <div
      className={clsx(
        "flex gap-3 animate-slide-up",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={clsx(
          "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold",
          isUser
            ? "bg-brand-600 text-white"
            : "bg-glass border border-glass-border text-gray-300"
        )}
      >
        {isUser ? "U" : "🤖"}
      </div>

      {/* Bubble */}
      <div
        className={clsx(
          "max-w-[75%] space-y-2",
          isUser ? "items-end" : "items-start",
          "flex flex-col"
        )}
      >
        <div
          className={clsx(
            "rounded-2xl px-4 py-3 text-sm leading-relaxed",
            isUser
              ? "bg-brand-600 text-white rounded-tr-sm"
              : isHighRisk
              ? "bg-red-900/30 border border-red-500/50 text-gray-100 rounded-tl-sm backdrop-blur-sm"
              : "bg-glass border border-glass-border text-gray-100 rounded-tl-sm backdrop-blur-sm"
          )}
        >
          {content}
        </div>

        {/* Emotion badge + confidence (assistant only) */}
        {!isUser && emotion && (
          <div className="flex items-center gap-2">
            <EmotionBadge emotion={emotion} confidence={confidence} size="sm" />
            {confidence !== undefined && (
              <span className="text-xs text-gray-500">
                {Math.round(confidence * 100)}% confidence
              </span>
            )}
          </div>
        )}

        {/* High-risk alert */}
        {isHighRisk && escalationMessage && (
          <div className="rounded-lg border border-red-500/40 bg-red-900/20 px-3 py-2 text-xs text-red-300 backdrop-blur-sm">
            🆘 {escalationMessage}
          </div>
        )}
      </div>
    </div>
  );
}
