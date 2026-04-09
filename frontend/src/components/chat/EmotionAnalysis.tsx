/**
 * EmotionAnalysis — displays emotion probabilities from recent messages in a compact card.
 */

"use client";

import { EmotionBadge } from "@/components/emotion/EmotionBadge";

export interface EmotionMetric {
  emotion: string;
  confidence: number;
  count?: number;
}

interface EmotionAnalysisProps {
  isLoading?: boolean;
  dominantEmotion?: string | null;
  confidenceScore?: number;
  emotionHistory?: EmotionMetric[];
}

export function EmotionAnalysis({
  isLoading = false,
  dominantEmotion = null,
  confidenceScore = 0,
  emotionHistory = [],
}: EmotionAnalysisProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-slate-600/60 bg-slate-900/85 backdrop-blur-sm p-4 space-y-3">
        <h3 className="text-xs font-semibold text-slate-100 uppercase tracking-wide">
          Emotion Analysis
        </h3>
        <div className="space-y-2">
          {[1, 2, 3].map((idx) => (
            <div key={idx} className="h-6 bg-slate-700/70 rounded animate-pulse" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-slate-600/60 bg-slate-900/85 backdrop-blur-sm p-4 space-y-4">
      <h3 className="text-xs font-semibold text-slate-100 uppercase tracking-wide">
        📊 Emotion Analysis
      </h3>

      {dominantEmotion ? (
        <>
          <div className="space-y-2">
            <div className="text-xs text-slate-300">Dominant Emotion</div>
            <EmotionBadge emotion={dominantEmotion} confidence={confidenceScore} />
          </div>

          {emotionHistory.length > 0 && (
            <div className="space-y-2 pt-3 border-t border-slate-600/50">
              <div className="text-xs text-slate-300">Recent Pattern</div>
              <div className="space-y-1.5">
                {emotionHistory.slice(0, 5).map((metric, i) => (
                  <div key={i} className="flex items-center justify-between text-xs">
                    <span className="text-slate-200 capitalize">{metric.emotion}</span>
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-blue-500 to-cyan-400"
                          style={{
                            width: `${(metric.confidence || 0) * 100}%`,
                          }}
                        />
                      </div>
                      <span className="text-slate-300 w-8 text-right">
                        {Math.round((metric.confidence || 0) * 100)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="rounded-lg border border-slate-600/60 bg-slate-800/65 text-sm text-slate-300 py-4 text-center">
          No emotion data yet. Start chatting to see analysis.
        </div>
      )}
    </div>
  );
}
