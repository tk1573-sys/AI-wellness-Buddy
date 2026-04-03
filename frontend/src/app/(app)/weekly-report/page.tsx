/**
 * Weekly Report page — 7-day narrative summary, daily breakdown bar chart,
 * emotion distribution, and session summaries.
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from "recharts";
import { getWeeklyReport, type WeeklyReportData } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { SessionSummaryCard } from "@/components/dashboard/SessionSummaryCard";

const EMOTION_COLORS: Record<string, string> = {
  joy: "#22c55e",
  neutral: "#6b7280",
  sadness: "#3b82f6",
  anger: "#ef4444",
  fear: "#8b5cf6",
  anxiety: "#f59e0b",
  crisis: "#dc2626",
  stress: "#f97316",
};

function emotionColor(emotion: string): string {
  return EMOTION_COLORS[emotion.toLowerCase()] ?? "#6b7280";
}

const MOOD_DIRECTION_LABELS: Record<string, { label: string; emoji: string; color: string }> = {
  improving: { label: "Improving", emoji: "📈", color: "text-green-400" },
  stable: { label: "Stable", emoji: "➡️", color: "text-blue-400" },
  declining: { label: "Declining", emoji: "📉", color: "text-red-400" },
};

export default function WeeklyReportPage() {
  const router = useRouter();
  const [data, setData] = useState<WeeklyReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    getWeeklyReport()
      .then(setData)
      .catch((e) => setError(e?.response?.data?.detail ?? "Failed to load weekly report."))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <div className="animate-pulse text-center space-y-2">
          <div className="text-4xl">📋</div>
          <p>Generating report…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full text-red-400">
        <div className="text-center space-y-2">
          <div className="text-4xl">⚠️</div>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!data || data.total_sessions === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <div className="text-center space-y-3">
          <div className="text-5xl">📋</div>
          <h2 className="text-xl font-semibold text-gray-200">No data this week</h2>
          <p className="text-sm max-w-xs">
            Your weekly report will appear here after you have a few chat sessions.
          </p>
        </div>
      </div>
    );
  }

  const moodInfo = MOOD_DIRECTION_LABELS[data.mood_direction] ?? MOOD_DIRECTION_LABELS.stable;

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Weekly Report</h1>
        <p className="text-sm text-gray-400 mt-1">Past 7 days · {data.total_sessions} session{data.total_sessions !== 1 ? "s" : ""}</p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-xl border border-glass-border bg-glass p-4 backdrop-blur-sm space-y-1">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Mood Direction</p>
          <p className={`text-xl font-bold ${moodInfo.color}`}>
            {moodInfo.emoji} {moodInfo.label}
          </p>
        </div>
        <div className="rounded-xl border border-glass-border bg-glass p-4 backdrop-blur-sm space-y-1">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Dominant Emotion</p>
          <p className="text-xl font-bold text-gray-100 capitalize">{data.dominant_emotion_week}</p>
        </div>
        <div className={`rounded-xl border p-4 backdrop-blur-sm space-y-1 ${
          data.high_risk_count > 0 ? "border-red-500/40 bg-red-900/20" : "border-glass-border bg-glass"
        }`}>
          <p className="text-xs text-gray-500 uppercase tracking-wide">High-Risk Moments</p>
          <p className={`text-xl font-bold ${data.high_risk_count > 0 ? "text-red-400" : "text-green-400"}`}>
            {data.high_risk_count > 0 ? `⚠️ ${data.high_risk_count}` : "✅ None"}
          </p>
        </div>
      </div>

      {/* Narrative summary */}
      <div className="rounded-xl border border-glass-border bg-glass p-5 backdrop-blur-sm">
        <h2 className="text-sm font-semibold text-gray-300 mb-3">Summary</h2>
        <p className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
          {data.summary_text.replace(/\*\*/g, "")}
        </p>
      </div>

      {/* Daily breakdown bar chart */}
      {data.daily_breakdown.length > 0 && (
        <div className="rounded-xl border border-glass-border bg-glass p-4 backdrop-blur-sm">
          <h2 className="text-sm font-semibold text-gray-300 mb-4">Daily Activity</h2>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={data.daily_breakdown}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="date" tick={{ fill: "#6b7280", fontSize: 10 }} />
              <YAxis tick={{ fill: "#6b7280", fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  background: "rgba(17,24,39,0.95)",
                  border: "1px solid rgba(255,255,255,0.12)",
                  borderRadius: 8,
                  color: "#f3f4f6",
                  fontSize: 12,
                }}
              />
              <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                {data.daily_breakdown.map((entry, i) => (
                  <Cell key={i} fill={emotionColor(entry.dominant_emotion)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Emotion distribution this week */}
      {data.emotion_distribution.length > 0 && (
        <div className="rounded-xl border border-glass-border bg-glass p-4 backdrop-blur-sm">
          <h2 className="text-sm font-semibold text-gray-300 mb-4">Emotion Distribution (7 days)</h2>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={data.emotion_distribution} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis type="number" tick={{ fill: "#6b7280", fontSize: 10 }} />
              <YAxis dataKey="emotion" type="category" tick={{ fill: "#9ca3af", fontSize: 11 }} width={70} />
              <Tooltip
                contentStyle={{
                  background: "rgba(17,24,39,0.95)",
                  border: "1px solid rgba(255,255,255,0.12)",
                  borderRadius: 8,
                  color: "#f3f4f6",
                  fontSize: 12,
                }}
              />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {data.emotion_distribution.map((entry, i) => (
                  <Cell key={i} fill={emotionColor(entry.emotion)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Session summaries */}
      {data.session_summaries.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-gray-300">Sessions This Week</h2>
          <div className="space-y-2">
            {data.session_summaries.slice(-20).reverse().map((s, i) => (
              <SessionSummaryCard
                key={i}
                timestamp={s.timestamp}
                dominantEmotion={s.dominant_emotion}
                confidence={s.confidence}
                isHighRisk={s.is_high_risk}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
