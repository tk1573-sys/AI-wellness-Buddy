/**
<<<<<<< HEAD
 * RiskDashboard — displays risk level, alerts, and escalation indicators.
=======
 * RiskDashboard — compact right-panel widget for the chat split layout.
 *
 * Displays the current session's risk summary: high-risk message count,
 * escalation status, and the most recent escalation message if present.
>>>>>>> 4362f5eb8d9a4933237299b50fce9fb5d12654d1
 */

"use client";

<<<<<<< HEAD
interface RiskDashboardProps {
  isLoading?: boolean;
  isHighRisk?: boolean;
  escalationMessage?: string | null;
  riskScore?: number;
  confidenceScore?: number;
}

export function RiskDashboard({
  isLoading = false,
  isHighRisk = false,
  escalationMessage = null,
  riskScore = 0,
  confidenceScore = 0,
}: RiskDashboardProps) {
  if (isLoading) {
    return (
      <div className="rounded-xl border border-slate-600/60 bg-slate-900/85 backdrop-blur-sm p-4 space-y-3">
        <h3 className="text-xs font-semibold text-slate-100 uppercase tracking-wide">
          Risk Assessment
        </h3>
        <div className="space-y-2">
          <div className="h-10 bg-slate-700/70 rounded animate-pulse" />
          <div className="h-6 bg-slate-700/70 rounded animate-pulse" />
        </div>
      </div>
    );
  }

  const riskLevel = riskScore >= 0.85 ? "Critical" : riskScore >= 0.7 ? "High" : riskScore >= 0.4 ? "Medium" : "Low";
  const riskColor =
    riskScore >= 0.85
      ? "from-rose-700 to-red-600"
      : riskScore >= 0.7
      ? "from-red-600 to-red-500"
      : riskScore >= 0.4
      ? "from-amber-600 to-amber-500"
      : "from-emerald-600 to-green-500";

  const riskBgColor =
    riskScore >= 0.85
      ? "bg-rose-950/70 border border-rose-400/60"
      : riskScore >= 0.7
      ? "bg-red-950/70 border border-red-400/60"
      : riskScore >= 0.4
      ? "bg-amber-950/70 border border-amber-400/60"
      : "bg-emerald-950/70 border border-emerald-400/60";

  const riskTextColor =
    riskScore >= 0.85
      ? "text-rose-100"
      : riskScore >= 0.7
      ? "text-red-100"
      : riskScore >= 0.4
      ? "text-amber-100"
      : "text-emerald-100";

  return (
    <div className="rounded-xl border border-slate-600/60 bg-slate-900/85 backdrop-blur-sm p-4 space-y-4">
      <h3 className="text-xs font-semibold text-slate-100 uppercase tracking-wide">
        🛡️ Risk Assessment
      </h3>

      {/* Risk Score Gauge */}
      <div className={`rounded-lg ${riskBgColor} p-3`}>
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-slate-200">Risk Level</span>
          <span className={`text-sm font-semibold ${riskTextColor}`}>{riskLevel}</span>
        </div>
        <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
          <div
            className={`h-full bg-gradient-to-r ${riskColor}`}
            style={{
              width: `${Math.round(riskScore * 100)}%`,
              transition: "width 0.3s ease-out",
            }}
          />
        </div>
        <div className="text-xs text-slate-200 mt-1">
          {Math.round(riskScore * 100)}% risk detected
        </div>
      </div>

      {/* Confidence Score */}
      <div className="rounded-lg bg-slate-800/65 border border-slate-600/60 p-3">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-slate-300">Model Confidence</span>
          <span className="text-xs font-semibold text-slate-100">
            {Math.round(confidenceScore * 100)}%
          </span>
        </div>
        <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-blue-400"
            style={{
              width: `${Math.round(confidenceScore * 100)}%`,
              transition: "width 0.3s ease-out",
            }}
          />
        </div>
      </div>

      {/* High-Risk Alert */}
      {isHighRisk && escalationMessage && (
        <div className="rounded-lg border border-red-400/70 bg-red-950/75 p-3 space-y-1">
          <div className="flex items-start gap-2">
            <span className="text-lg flex-shrink-0">🆘</span>
            <div>
              <div className="text-xs font-semibold text-red-100 mb-0.5">
                High-Risk Alert
              </div>
              <div className="text-xs text-red-50 leading-relaxed">
                {escalationMessage}
              </div>
            </div>
          </div>
        </div>
      )}

      {!isHighRisk && riskScore <= 0 && (
        <div className="rounded-lg border border-slate-600/60 bg-slate-800/65 p-3">
          <p className="text-xs text-slate-300 leading-relaxed">
            Risk analysis is not available yet. Continue chatting to generate risk signals.
          </p>
        </div>
      )}

      {/* Safety Notice */}
      <div className="rounded-lg bg-slate-800/65 border border-slate-600/60 p-3">
        <p className="text-xs text-slate-300 leading-relaxed">
          ℹ️ If you're in crisis, please contact emergency services or a mental health professional immediately.
        </p>
      </div>
=======
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
>>>>>>> 4362f5eb8d9a4933237299b50fce9fb5d12654d1
    </div>
  );
}
