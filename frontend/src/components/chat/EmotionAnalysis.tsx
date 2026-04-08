/**
 * EmotionAnalysis — right-panel widget showing the session-level emotion
 * distribution derived from all assistant messages in the current session.
 */

"use client";

import { Brain } from "lucide-react";

const EMOTION_COLORS: Record<string, string> = {
  joy:     "bg-yellow-400",
  sadness: "bg-blue-400",
  anger:   "bg-red-400",
  fear:    "bg-purple-400",
  anxiety: "bg-orange-400",
  stress:  "bg-orange-500",
  neutral: "bg-gray-400",
  crisis:  "bg-red-600",
};

interface Message {
  role: "user" | "assistant";
  emotion?: string | null;
  confidence?: number;
}

interface EmotionAnalysisProps {
  messages: Message[];
}

export function EmotionAnalysis({ messages }: EmotionAnalysisProps) {
  // Build frequency map from all assistant messages that have an emotion label
  const counts: Record<string, number> = {};
  for (const msg of messages) {
    if (msg.role === "assistant" && msg.emotion) {
      counts[msg.emotion] = (counts[msg.emotion] ?? 0) + 1;
    }
  }

  const total = Object.values(counts).reduce((s, v) => s + v, 0);
  if (total === 0) return null;

  const sorted = Object.entries(counts).sort(([, a], [, b]) => b - a);
  const dominant = sorted[0]?.[0] ?? null;

  return (
    <div className="rounded-xl border border-glass-border bg-gray-900/60 backdrop-blur-sm p-4 space-y-3">
      <div className="flex items-center gap-2">
        <Brain className="w-4 h-4 text-brand-400 flex-shrink-0" />
        <span className="text-xs font-semibold text-gray-300 uppercase tracking-wide">
          Emotion Analysis
        </span>
      </div>

      {dominant && (
        <div className="flex items-center justify-between">
          <span className="text-xs text-gray-500">Dominant emotion</span>
          <span className="text-xs font-medium text-brand-300 capitalize">{dominant}</span>
        </div>
      )}

      <div className="space-y-1.5">
        {sorted.map(([emotion, count]) => {
          const pct = Math.round((count / total) * 100);
          const barColor = EMOTION_COLORS[emotion.toLowerCase()] ?? "bg-gray-400";
          return (
            <div key={emotion} className="flex items-center gap-2">
              <span className="w-14 text-xs text-gray-400 capitalize truncate">{emotion}</span>
              <div className="flex-1 h-1.5 rounded-full bg-white/10 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${barColor}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
              <span className="w-8 text-right text-xs text-gray-500">{pct}%</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
