/**
 * Dashboard page — emotion analytics and risk summary.
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { getDashboard, getJourney, getGuardianAlerts, DashboardData, JourneyData, GuardianAlertRecord } from "@/lib/api";
import { isAuthenticated } from "@/lib/auth";
import { MoodTrendExtended } from "@/components/dashboard/MoodTrendExtended";

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

function getEmotionColor(emotion: string): string {
  return EMOTION_COLORS[emotion.toLowerCase()] ?? "#6b7280";
}

const MOOD_LABELS: Record<string, { label: string; color: string; emoji: string }> = {
  improving: { label: "Improving", color: "text-green-400", emoji: "📈" },
  stable: { label: "Stable", color: "text-blue-400", emoji: "➡️" },
  declining: { label: "Declining", color: "text-red-400", emoji: "📉" },
};

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData | null>(null);
  const [journeyData, setJourneyData] = useState<JourneyData | null>(null);
  const [guardianAlerts, setGuardianAlerts] = useState<GuardianAlertRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    Promise.all([
      getDashboard(),
      getJourney().catch(() => null),
      getGuardianAlerts().catch(() => ({ alerts: [], total: 0 })),
    ])
      .then(([dash, journey, ga]) => {
        setData(dash);
        setJourneyData(journey);
        setGuardianAlerts(ga.alerts);
      })
      .catch((e) => setError(e?.response?.data?.detail ?? "Failed to load dashboard."))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <div className="animate-pulse text-center space-y-2">
          <div className="text-4xl">📊</div>
          <p>Loading dashboard…</p>
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
          <div className="text-5xl">💬</div>
          <h2 className="text-xl font-semibold text-gray-200">No data yet</h2>
          <p className="text-sm max-w-xs">
            Start chatting to build your emotion history and see analytics here.
          </p>
        </div>
      </div>
    );
  }

  const moodInfo = MOOD_LABELS[data.mood_trend] ?? MOOD_LABELS.stable;

  // Prepare trend data: shorten timestamps for display
  const trendData = data.emotion_trend.map((p, i) => ({
    idx: i + 1,
    emotion: p.emotion,
    confidence: Math.round(p.confidence * 100),
    is_high_risk: p.is_high_risk,
    time: new Date(p.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
  }));

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Emotion Dashboard</h1>
        <p className="text-sm text-gray-400 mt-1">
          Based on your last {data.total_sessions} recorded emotion{data.total_sessions !== 1 ? "s" : ""}.
        </p>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {/* Mood trend */}
        <div className="rounded-xl border border-glass-border bg-glass p-4 backdrop-blur-sm space-y-1">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Mood Trend</p>
          <p className={`text-xl font-bold ${moodInfo.color}`}>
            {moodInfo.emoji} {moodInfo.label}
          </p>
        </div>

        {/* Escalation */}
        <div className={`rounded-xl border p-4 backdrop-blur-sm space-y-1 ${data.escalation_detected ? "border-red-500/40 bg-red-900/20" : "border-glass-border bg-glass"}`}>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Escalation Risk</p>
          <p className={`text-xl font-bold ${data.escalation_detected ? "text-red-400" : "text-green-400"}`}>
            {data.escalation_detected ? "⚠️ Detected" : "✅ None"}
          </p>
        </div>

        {/* Risk alerts count */}
        <div className="rounded-xl border border-glass-border bg-glass p-4 backdrop-blur-sm space-y-1">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Risk Alerts</p>
          <p className={`text-xl font-bold ${data.risk_alerts.length > 0 ? "text-red-400" : "text-gray-100"}`}>
            🆘 {data.risk_alerts.length}
          </p>
        </div>
      </div>

      {/* Emotion trend (line chart) */}
      <div className="rounded-xl border border-glass-border bg-glass p-4 backdrop-blur-sm">
        <h2 className="text-sm font-semibold text-gray-300 mb-4">Emotion Trend (Confidence %)</h2>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="time" tick={{ fill: "#6b7280", fontSize: 11 }} />
            <YAxis domain={[0, 100]} tick={{ fill: "#6b7280", fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: "rgba(17,24,39,0.95)", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 8, color: "#f3f4f6" }}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              formatter={(value: any) => [`${value ?? 0}%`, "Confidence"] as [string, string]}
            />
            <Line
              type="monotone"
              dataKey="confidence"
              stroke="#818cf8"
              strokeWidth={2}
              dot={(props) => {
                const { cx, cy, payload } = props;
                return (
                  <circle
                    key={`dot-${payload.idx}`}
                    cx={cx}
                    cy={cy}
                    r={4}
                    fill={payload.is_high_risk ? "#ef4444" : getEmotionColor(payload.emotion)}
                    stroke="none"
                  />
                );
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Emotion distribution (bar chart) */}
      <div className="rounded-xl border border-glass-border bg-glass p-4 backdrop-blur-sm">
        <h2 className="text-sm font-semibold text-gray-300 mb-4">Emotion Distribution</h2>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={data.emotion_distribution} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis type="number" tick={{ fill: "#6b7280", fontSize: 11 }} />
            <YAxis dataKey="emotion" type="category" tick={{ fill: "#9ca3af", fontSize: 12 }} width={70} />
            <Tooltip
              contentStyle={{ background: "rgba(17,24,39,0.95)", border: "1px solid rgba(255,255,255,0.12)", borderRadius: 8, color: "#f3f4f6" }}
            />
            <Bar dataKey="count" radius={[0, 4, 4, 0]}>
              {data.emotion_distribution.map((entry) => (
                <Cell key={entry.emotion} fill={getEmotionColor(entry.emotion)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Risk alerts */}
      {data.risk_alerts.length > 0 && (
        <div className="rounded-xl border border-red-500/30 bg-red-900/10 p-4 space-y-2">
          <h2 className="text-sm font-semibold text-red-400 mb-2">🆘 Risk Alerts</h2>
          {data.risk_alerts.map((alert, i) => (
            <div key={i} className="text-xs text-red-300 flex items-start gap-2">
              <span className="text-red-500 mt-0.5">•</span>
              <span>
                <span className="font-medium capitalize">[{alert.level}]</span> {alert.message}{" "}
                <span className="text-red-500 text-[10px]">
                  {new Date(alert.timestamp).toLocaleString()}
                </span>
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Extended analytics — stability, CDI, moving average */}
      {journeyData && journeyData.total_points > 0 && (
        <div className="space-y-2">
          <h2 className="text-sm font-semibold text-gray-300">Extended Analytics</h2>
          <MoodTrendExtended
            movingAverage={journeyData.moving_average}
            stabilityIndex={journeyData.stability_index}
            volatilityLabel={journeyData.volatility_label}
            cdiScore={journeyData.cdi_score}
            cdiLevel={journeyData.cdi_level}
          />
        </div>
      )}

      {/* Guardian Alert Status Card */}
      <div className="rounded-xl border border-amber-500/30 bg-amber-900/10 p-4 space-y-3">
        <h2 className="text-sm font-semibold text-amber-300">🛡️ Guardian Alert Status</h2>
        {guardianAlerts.length === 0 ? (
          <p className="text-xs text-gray-400">No guardian alerts have been sent yet.</p>
        ) : (
          <div className="space-y-2">
            {guardianAlerts.slice(0, 5).map((alert) => (
              <div
                key={alert.id}
                className="flex items-start gap-3 rounded-xl border border-white/5 bg-white/5 px-3 py-2.5"
              >
                <span className="text-lg mt-0.5">
                  {alert.channel === "email" ? "📧" : "📱"}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`text-xs font-medium uppercase px-1.5 py-0.5 rounded ${
                        alert.risk_level === "critical"
                          ? "bg-red-900/50 text-red-300"
                          : "bg-amber-900/50 text-amber-300"
                      }`}
                    >
                      {alert.risk_level}
                    </span>
                    <span className="text-xs text-gray-400 capitalize">{alert.channel}</span>
                    <span
                      className={`text-xs ml-auto ${
                        alert.delivery_status === "sent" ? "text-green-400" : "text-red-400"
                      }`}
                    >
                      {alert.delivery_status === "sent" ? "✅ Sent" : "❌ Failed"}
                    </span>
                  </div>
                  {alert.risk_reason && (
                    <p className="text-xs text-gray-400 mt-0.5 truncate">{alert.risk_reason}</p>
                  )}
                  <p className="text-[10px] text-gray-600 mt-0.5">
                    {new Date(alert.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
            {guardianAlerts.length > 5 && (
              <p className="text-xs text-gray-500 text-center">
                +{guardianAlerts.length - 5} more alerts
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
