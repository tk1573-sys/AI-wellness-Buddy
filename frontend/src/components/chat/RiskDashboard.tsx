/**
 * RiskDashboard — compact right-panel widget for the chat split layout.
 *
 * Displays the current session's risk summary: high-risk message count,
 * escalation status, and the most recent escalation message if present.
 */

"use client";

import { AlertTriangle, ShieldAlert, ShieldCheck } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  isHighRisk?: boolean;
  escalationMessage?: string | null;
}

interface RiskDashboardProps {
  messages: Message[];
}

export function RiskDashboard({ messages }: RiskDashboardProps) {
  const highRiskCount = messages.filter((m) => m.isHighRisk).length;
  const latestEscalation = [...messages]
    .reverse()
    .find((m) => m.escalationMessage)?.escalationMessage ?? null;
  const isEscalated = highRiskCount > 0;

  return (
    <div className="rounded-xl border border-glass-border bg-gray-900/60 backdrop-blur-sm p-4 space-y-3">
      <div className="flex items-center gap-2">
        {isEscalated ? (
          <ShieldAlert className="w-4 h-4 text-red-400 flex-shrink-0" />
        ) : (
          <ShieldCheck className="w-4 h-4 text-green-400 flex-shrink-0" />
        )}
        <span className="text-xs font-semibold text-gray-300 uppercase tracking-wide">
          Risk Dashboard
        </span>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">High-risk messages</span>
        <span
          className={`text-sm font-bold ${
            highRiskCount > 0 ? "text-red-400" : "text-green-400"
          }`}
        >
          {highRiskCount}
        </span>
      </div>

      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-500">Session status</span>
        <span
          className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
            isEscalated
              ? "bg-red-900/40 text-red-300 border border-red-700/40"
              : "bg-green-900/40 text-green-300 border border-green-700/40"
          }`}
        >
          {isEscalated ? "Elevated" : "Stable"}
        </span>
      </div>

      {latestEscalation && (
        <div className="flex items-start gap-2 rounded-lg border border-red-700/30 bg-red-900/20 px-3 py-2">
          <AlertTriangle className="w-3.5 h-3.5 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-xs text-red-300 leading-relaxed">{latestEscalation}</p>
        </div>
      )}
    </div>
  );
}
