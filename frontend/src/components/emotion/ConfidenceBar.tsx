/**
 * ConfidenceBar — horizontal bar visualising confidence/uncertainty scores.
 */

interface ConfidenceBarProps {
  confidence: number;  // 0–1
  label?: string;
}

export function ConfidenceBar({ confidence, label = "Confidence" }: ConfidenceBarProps) {
  const pct = Math.round(confidence * 100);
  const color =
    pct >= 75 ? "bg-green-500" :
    pct >= 50 ? "bg-yellow-500" :
                "bg-red-500";

  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>{label}</span>
          <span>{pct}%</span>
        </div>
      )}
      <div className="w-full h-1.5 rounded-full bg-white/10">
        <div
          className={`h-full rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
