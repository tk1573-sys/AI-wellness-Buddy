/**
 * EmotionBadge — displays the detected emotion with a colour-coded pill.
 */

import { clsx } from "clsx";

const EMOTION_STYLES: Record<string, string> = {
  joy:      "bg-yellow-400/20 text-yellow-300 border-yellow-400/30",
  sadness:  "bg-blue-400/20   text-blue-300   border-blue-400/30",
  anger:    "bg-red-400/20    text-red-300    border-red-400/30",
  fear:     "bg-purple-400/20 text-purple-300 border-purple-400/30",
  anxiety:  "bg-orange-400/20 text-orange-300 border-orange-400/30",
  stress:   "bg-orange-500/20 text-orange-200 border-orange-500/30",
  neutral:  "bg-gray-400/20   text-gray-300   border-gray-400/30",
  crisis:   "bg-red-600/30    text-red-200    border-red-500/50",
};

const EMOTION_EMOJI: Record<string, string> = {
  joy: "😊", sadness: "😢", anger: "😠", fear: "😨",
  anxiety: "😰", stress: "😓", neutral: "😐", crisis: "🆘",
};

interface EmotionBadgeProps {
  emotion: string;
  confidence?: number;
  size?: "sm" | "md";
}

export function EmotionBadge({ emotion, confidence, size = "md" }: EmotionBadgeProps) {
  const key = emotion.toLowerCase();
  const style = EMOTION_STYLES[key] ?? "bg-gray-400/20 text-gray-300 border-gray-400/30";
  const emoji = EMOTION_EMOJI[key] ?? "🤔";

  return (
    <span
      className={clsx(
        "inline-flex items-center gap-1 rounded-full border font-medium capitalize",
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm",
        style
      )}
    >
      <span>{emoji}</span>
      <span>{emotion}</span>
      {confidence !== undefined && (
        <span className="opacity-70 text-xs">
          {Math.round(confidence * 100)}%
        </span>
      )}
    </span>
  );
}
