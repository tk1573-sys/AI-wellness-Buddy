/**
 * RiskDashboard — right-panel widget displaying risk level, model confidence,
 * escalation alerts, and safety notice for the current session.
 */

"use client";

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
          ℹ️ If you&apos;re in crisis, please contact emergency services or a mental health professional immediately.
        </p>
      </div>
    </div>
  );
}
