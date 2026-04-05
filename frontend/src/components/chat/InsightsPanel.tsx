/**
 * InsightsPanel — collapsible per-message emotion scores panel.
 *
 * Displayed below each assistant bubble when emotion score data is available.
 * Shows the full probability distribution returned by the backend alongside
 * a personalization indicator.
 */

"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import { clsx } from "clsx";
import type { EmotionScore } from "@/lib/api";

const EMOTION_BAR_COLORS: Record<string, string> = {
  joy:     "bg-yellow-400",
  sadness: "bg-blue-400",
  anger:   "bg-red-400",
  fear:    "bg-purple-400",
  anxiety: "bg-orange-400",
  stress:  "bg-orange-500",
  neutral: "bg-gray-400",
  crisis:  "bg-red-600",
};

interface InsightsPanelProps {
  scores: EmotionScore[];
  responseType?: "generic" | "personalized";
  personalizationScore?: number;
}

export function InsightsPanel({
  scores,
  responseType,
  personalizationScore,
}: InsightsPanelProps) {
  const [open, setOpen] = useState(false);

  if (!scores || scores.length === 0) return null;

  // Sort descending by score for display
  const sorted = [...scores].sort((a, b) => b.score - a.score);

  return (
    <div className="ml-11 mt-1">
      <button
        type="button"
        onClick={() => setOpen((s) => !s)}
        className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-300 transition-colors"
        aria-expanded={open}
      >
        <Sparkles className="w-3 h-3" />
        Emotion insights
        {open ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>

      {open && (
        <div className="mt-2 rounded-xl border border-glass-border bg-gray-900/60 backdrop-blur-sm px-4 py-3 space-y-2 max-w-xs">
          {/* Personalization badge */}
          {responseType === "personalized" && (
            <p className="text-xs text-brand-400 flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              Personalized response
              {personalizationScore !== undefined && (
                <span className="text-gray-500 ml-1">
                  ({Math.round(personalizationScore * 100)}%)
                </span>
              )}
            </p>
          )}

          {/* Score bars */}
          <div className="space-y-1.5">
            {sorted.map(({ emotion, score }) => {
              const pct = Math.round(score * 100);
              const barColor =
                EMOTION_BAR_COLORS[emotion.toLowerCase()] ?? "bg-gray-400";
              return (
                <div key={emotion} className="flex items-center gap-2">
                  <span className="w-16 text-xs text-gray-400 capitalize truncate">
                    {emotion}
                  </span>
                  <div className="flex-1 h-1.5 rounded-full bg-white/10 overflow-hidden">
                    <div
                      className={clsx("h-full rounded-full transition-all", barColor)}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  <span className="w-8 text-right text-xs text-gray-500">{pct}%</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
