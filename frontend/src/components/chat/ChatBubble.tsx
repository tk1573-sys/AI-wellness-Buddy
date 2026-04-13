/**
 * ChatBubble — renders a single chat message in the conversation stream.
 *
 * For assistant messages, an optional collapsible InsightsPanel shows the
 * full emotion score distribution when score data is available.
 */

import { clsx } from "clsx";
import { InsightsPanel } from "./InsightsPanel";
import type { EmotionScore } from "@/lib/api";

interface ChatBubbleProps {
  role: "user" | "assistant";
  content: string;
  scores?: EmotionScore[];
  responseType?: "generic" | "personalized";
  personalizationScore?: number;
}

export function ChatBubble({
  role,
  content,
  scores,
  responseType,
  personalizationScore,
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

      {/* Bubble + optional per-message insights */}
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
              : "bg-glass border border-glass-border text-gray-100 rounded-tl-sm backdrop-blur-sm"
          )}
        >
          {content}
        </div>

        {/* Per-message emotion score breakdown (assistant only) */}
        {!isUser && scores && scores.length > 0 && (
          <InsightsPanel
            scores={scores}
            responseType={responseType}
            personalizationScore={personalizationScore}
          />
        )}
      </div>
    </div>
  );
}
