/**
 * Emotional Journey page — emotion trend line, stress gauge, heatmap,
 * moving-average chart, and stability/CDI metrics.
 */

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  LineChart, Line, ScatterChart, Scatter, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import { getJourney, type JourneyData } from "@/lib/api";
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

function emotionColor(emotion: string): string {
  return EMOTION_COLORS[emotion.toLowerCase()] ?? "#6b7280";
}

export default function JourneyPage() {
  const router = useRouter();
  const [data, setData] = useState<JourneyData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    getJourney()
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [router]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <div className="animate-pulse text-center space-y-2">
          <div className="text-4xl">🛤️</div>
          <p>Loading journey…</p>
        </div>
      </div>
    );
  }

  if (!data || data.total_points === 0) {
    return (
      <div className="flex items-center justify-center h-full text-gray-400">
        <div className="text-center space-y-3">
          <div className="text-5xl">🛤️</div>
          <h2 className="text-xl font-semibold text-gray-200">No journey data yet</h2>
          <p className="text-sm max-w-xs">
            Start chatting to build your emotional journey timeline.
          </p>
        </div>
      </div>
    );
  }

  // Format journey points for the trend line
  const trendData = data.journey_points.map((p, i) => ({
    idx: i + 1,
    risk: p.risk_score,
    emotion: p.emotion,
    confidence: Math.round(p.confidence * 100),
    is_high_risk: p.is_high_risk,
    time: new Date(p.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
  }));

  // Format heatmap: scatter by hour
  const heatmapData = data.heatmap.map((c) => ({
    hour: c.hour,
    intensity: c.intensity,
    emotion: c.emotion,
  }));

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-100">Emotional Journey</h1>
        <p className="text-sm text-gray-400 mt-1">
          Your last {data.total_points} recorded emotional moment{data.total_points !== 1 ? "s" : ""}.
        </p>
      </div>

      {/* Stability + CDI + moving average */}
      <MoodTrendExtended
        movingAverage={data.moving_average}
        stabilityIndex={data.stability_index}
        volatilityLabel={data.volatility_label}
        cdiScore={data.cdi_score}
        cdiLevel={data.cdi_level}
      />

      {/* Emotion journey trend line */}
      <div className="rounded-xl border border-glass-border bg-glass p-4 backdrop-blur-sm">
        <h2 className="text-sm font-semibold text-gray-300 mb-4">Emotion Risk Over Time</h2>
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
            <XAxis dataKey="time" tick={{ fill: "#6b7280", fontSize: 10 }} />
            <YAxis domain={[0, 1]} tick={{ fill: "#6b7280", fontSize: 10 }} />
            <Tooltip
              contentStyle={{
                background: "rgba(17,24,39,0.95)",
                border: "1px solid rgba(255,255,255,0.12)",
                borderRadius: 8,
                color: "#f3f4f6",
                fontSize: 12,
              }}
              // eslint-disable-next-line @typescript-eslint/no-explicit-any
              formatter={(v: any, _: any, props: any) => [
                `${typeof v === "number" ? v.toFixed(3) : v} (${props.payload?.emotion ?? ""})`,
                "Risk",
              ]}
            />
            <Line
              type="monotone"
              dataKey="risk"
              stroke="#818cf8"
              strokeWidth={2}
              dot={(props) => {
                const { cx, cy, payload } = props;
                return (
                  <circle
                    key={`dot-${payload.idx}`}
                    cx={cx}
                    cy={cy}
                    r={5}
                    fill={payload.is_high_risk ? "#ef4444" : emotionColor(payload.emotion)}
                    stroke="none"
                  />
                );
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Heatmap — emotion intensity by hour of day */}
      {heatmapData.length > 0 && (
        <div className="rounded-xl border border-glass-border bg-glass p-4 backdrop-blur-sm">
          <h2 className="text-sm font-semibold text-gray-300 mb-4">
            Emotion Intensity Heatmap (by hour)
          </h2>
          <ResponsiveContainer width="100%" height={200}>
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis
                type="number"
                dataKey="hour"
                name="Hour"
                domain={[0, 23]}
                tick={{ fill: "#6b7280", fontSize: 10 }}
                tickFormatter={(v) => `${v}:00`}
              />
              <YAxis
                type="number"
                dataKey="intensity"
                name="Intensity"
                domain={[0, 1]}
                tick={{ fill: "#6b7280", fontSize: 10 }}
              />
              <Tooltip
                contentStyle={{
                  background: "rgba(17,24,39,0.95)",
                  border: "1px solid rgba(255,255,255,0.12)",
                  borderRadius: 8,
                  color: "#f3f4f6",
                  fontSize: 12,
                }}
                cursor={{ strokeDasharray: "3 3" }}
              />
              <Scatter name="Emotions" data={heatmapData}>
                {heatmapData.map((entry, i) => (
                  <Cell
                    key={`cell-${i}`}
                    fill={emotionColor(entry.emotion)}
                    opacity={0.6 + entry.intensity * 0.4}
                  />
                ))}
              </Scatter>
            </ScatterChart>
          </ResponsiveContainer>
          <p className="text-xs text-gray-600 mt-2">
            Each dot represents an emotion detected at that hour. Larger opacity = higher intensity.
          </p>
        </div>
      )}
    </div>
  );
}
