/**
 * AIInsightsCard — concise model-level insights with robust fallbacks.
 *
 * Accepts both live session data (responseType, personalizationScore, etc.)
 * and backend insights summary (insightsData from /api/v1/insights).
 */

"use client";

import type { InsightsData } from "@/lib/api";

const RISK_COLOR: Record<string, string> = {
  low: "text-green-400",
  moderate: "text-amber-400",
  high: "text-orange-400",
  critical: "text-red-400",
};

const TREND_EMOJI: Record<string, string> = {
  improving: "📈",
  stable: "➡️",
  declining: "📉",
};

interface AIInsightsCardProps {
  isLoading?: boolean;
  responseType?: "generic" | "personalized";
  personalizationScore?: number;
  usedTriggers?: string[];
  dominantEmotion?: string | null;
  insightsData?: InsightsData | null;
}

export function AIInsightsCard({
  isLoading = false,
  responseType,
  personalizationScore,
  usedTriggers = [],
  dominantEmotion = null,
  insightsData = null,
}: AIInsightsCardProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-slate-600/60 bg-slate-900/85 p-4 backdrop-blur-sm space-y-3">
        <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wide">AI Insights</h3>
        <div className="h-8 rounded bg-slate-700/60 animate-pulse" />
        <div className="h-8 rounded bg-slate-700/60 animate-pulse" />
      </div>
    );
  }

  const hasSignals = Boolean(responseType || dominantEmotion || usedTriggers.length > 0 || insightsData);

  // Prefer live session data when available, fall back to backend insights
  const displayEmotion = dominantEmotion ?? insightsData?.dominant_emotion ?? null;
  const displayScore =
    typeof personalizationScore === "number"
      ? personalizationScore
      : (typeof insightsData?.personalization_score === "number"
          ? insightsData.personalization_score
          : null);
  const displayTriggers =
    usedTriggers.length > 0 ? usedTriggers : (insightsData?.trigger_signals ?? []);

  return (
    <section className="rounded-xl border border-slate-600/60 bg-slate-900/85 p-4 backdrop-blur-sm space-y-4">
      <h3 className="text-xs font-semibold text-slate-100 uppercase tracking-wide">🧠 AI Insights</h3>

      {hasSignals ? (
        <>
          <div className="rounded-lg border border-slate-600/60 bg-slate-800/65 px-3 py-2 text-xs text-slate-200">
            <span className="text-slate-400">Response Mode: </span>
            <span className="font-semibold text-cyan-300 uppercase">{responseType ?? "unknown"}</span>
          </div>

          <div className="rounded-lg border border-slate-600/60 bg-slate-800/65 px-3 py-2 text-xs text-slate-200">
            <span className="text-slate-400">Dominant Emotion: </span>
            <span className="font-semibold text-violet-300">{displayEmotion ?? "Not available"}</span>
          </div>

          <div className="rounded-lg border border-slate-600/60 bg-slate-800/65 px-3 py-2 text-xs text-slate-200">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-slate-400">Personalization Score</span>
              <span className="font-semibold text-blue-300">
                {typeof displayScore === "number" ? `${Math.round(displayScore * 100)}%` : "N/A"}
              </span>
            </div>
            <div className="h-1.5 rounded-full bg-slate-700 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 to-cyan-400"
                style={{ width: `${Math.round((displayScore ?? 0) * 100)}%` }}
              />
            </div>
          </div>

          <div className="rounded-lg border border-slate-600/60 bg-slate-800/65 px-3 py-2 text-xs text-slate-200">
            <span className="text-slate-400">Trigger Signals: </span>
            {displayTriggers.length > 0 ? (
              <span className="text-amber-200">{displayTriggers.slice(0, 4).join(", ")}</span>
            ) : (
              <span className="text-slate-400">No trigger signals detected</span>
            )}
          </div>

          {/* Backend insights summary section */}
          {insightsData && (
            <>
              <div className="rounded-lg border border-slate-600/60 bg-slate-800/65 px-3 py-2 text-xs text-slate-200 flex items-center justify-between">
                <span className="text-slate-400">Risk Level: </span>
                <span className={`font-semibold capitalize ${RISK_COLOR[insightsData.risk_level] ?? "text-slate-300"}`}>
                  {insightsData.risk_level}
                </span>
              </div>

              <div className="rounded-lg border border-slate-600/60 bg-slate-800/65 px-3 py-2 text-xs text-slate-200 flex items-center justify-between">
                <span className="text-slate-400">Mood Trend: </span>
                <span className="font-semibold text-slate-100 capitalize">
                  {TREND_EMOJI[insightsData.trend] ?? ""} {insightsData.trend}
                </span>
              </div>
            </>
          )}
        </>
      ) : (
        <div className="rounded-lg border border-slate-600/60 bg-slate-800/65 px-3 py-4 text-sm text-slate-300 text-center">
          AI insight data is not available yet. Send a message to generate analysis.
        </div>
      )}
    </section>
  );
}
