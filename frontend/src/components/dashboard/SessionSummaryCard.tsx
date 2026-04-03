/**
 * SessionSummaryCard — a compact card showing a session recap.
 * Used in the Weekly Report page.
 */

"use client";

interface SessionSummaryCardProps {
  timestamp: string;
  dominantEmotion: string;
  confidence: number;
  isHighRisk: boolean;
}

const EMOTION_EMOJI: Record<string, string> = {
  joy: "😊",
  neutral: "😐",
  sadness: "😢",
  anger: "😠",
  fear: "😨",
  anxiety: "😰",
  stress: "😤",
  crisis: "🆘",
};

export function SessionSummaryCard({
  timestamp,
  dominantEmotion,
  confidence,
  isHighRisk,
}: SessionSummaryCardProps) {
  const emoji = EMOTION_EMOJI[dominantEmotion.toLowerCase()] ?? "💭";
  const date = new Date(timestamp);
  const timeStr = date.toLocaleString([], {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div
      className={`flex items-center gap-3 rounded-xl border px-4 py-3 backdrop-blur-sm ${
        isHighRisk
          ? "border-red-500/30 bg-red-900/10"
          : "border-glass-border bg-glass"
      }`}
    >
      <span className="text-2xl flex-shrink-0">{emoji}</span>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-gray-100 capitalize">{dominantEmotion}</p>
        <p className="text-xs text-gray-500">{timeStr}</p>
      </div>
      <div className="text-right flex-shrink-0">
        <p className="text-sm font-semibold text-gray-300">
          {Math.round(confidence * 100)}%
        </p>
        {isHighRisk && (
          <p className="text-xs text-red-400">⚠️ Risk</p>
        )}
      </div>
    </div>
  );
}
