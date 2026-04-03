/**
 * MoodTrendExtended — extended dashboard card showing:
 *  - Moving-average risk line chart
 *  - Stability index metric
 *  - CDI (Clinical Distress Index) gauge
 */

"use client";

import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import type { MovingAveragePoint } from "@/lib/api";

interface MoodTrendExtendedProps {
  movingAverage: MovingAveragePoint[];
  stabilityIndex: number;
  volatilityLabel: string;
  cdiScore: number;
  cdiLevel: string;
}

const CDI_COLORS: Record<string, string> = {
  low: "text-green-400",
  moderate: "text-yellow-400",
  high: "text-orange-400",
  critical: "text-red-400",
};

const STABILITY_COLORS = (idx: number) =>
  idx >= 0.7 ? "text-green-400" : idx >= 0.4 ? "text-yellow-400" : "text-red-400";

export function MoodTrendExtended({
  movingAverage,
  stabilityIndex,
  volatilityLabel,
  cdiScore,
  cdiLevel,
}: MoodTrendExtendedProps) {
  return (
    <div className="space-y-4">
      {/* Stability + CDI metrics row */}
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-xl border border-glass-border bg-glass p-3 backdrop-blur-sm space-y-1">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Stability Index</p>
          <p className={`text-xl font-bold ${STABILITY_COLORS(stabilityIndex)}`}>
            {stabilityIndex.toFixed(2)}
          </p>
          <p className="text-xs text-gray-600 capitalize">{volatilityLabel} volatility</p>
        </div>
        <div className="rounded-xl border border-glass-border bg-glass p-3 backdrop-blur-sm space-y-1">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Clinical Distress</p>
          <p className={`text-xl font-bold ${CDI_COLORS[cdiLevel] ?? "text-gray-100"}`}>
            {(cdiScore * 100).toFixed(0)}%
          </p>
          <p className={`text-xs capitalize ${CDI_COLORS[cdiLevel] ?? "text-gray-600"}`}>
            {cdiLevel} distress
          </p>
        </div>
      </div>

      {/* Moving average line chart */}
      {movingAverage.length > 1 && (
        <div className="rounded-xl border border-glass-border bg-glass p-4 backdrop-blur-sm">
          <h2 className="text-sm font-semibold text-gray-300 mb-3">
            Risk Trend (3-point moving average)
          </h2>
          <ResponsiveContainer width="100%" height={160}>
            <LineChart data={movingAverage}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="index" tick={{ fill: "#6b7280", fontSize: 10 }} />
              <YAxis domain={[0, 1]} tick={{ fill: "#6b7280", fontSize: 10 }} />
              <Tooltip
                contentStyle={{
                  background: "rgba(17,24,39,0.95)",
                  border: "1px solid rgba(255,255,255,0.12)",
                  borderRadius: 8,
                  color: "#f3f4f6",
                  fontSize: 12,
                }}
                formatter={(v: unknown) => [
                  typeof v === "number" ? v.toFixed(3) : String(v),
                  "Avg Risk",
                ] as [string, string]}
              />
              <Line
                type="monotone"
                dataKey="avg_risk"
                stroke="#f59e0b"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
