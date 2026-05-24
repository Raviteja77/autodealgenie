"use client";

import { scoreTextColor } from "./ScoreBadge";

interface ScoreGaugeProps {
  score: number;
  size?: number;
}

export function ScoreGauge({ score, size = 160 }: ScoreGaugeProps) {
  const r = size * 0.42;
  const c = 2 * Math.PI * r;
  const fill = (score / 10) * c;

  const strokeColor =
    score >= 7 ? "#10B981" : score >= 5 ? "#F59E0B" : "#DC2626";

  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke="#E2E8F0"
          strokeWidth={size * 0.08}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          stroke={strokeColor}
          strokeWidth={size * 0.08}
          strokeDasharray={`${fill} ${c}`}
          transform={`rotate(-90 ${size / 2} ${size / 2})`}
          strokeLinecap="round"
          className="gauge-arc"
        />
      </svg>
      <div
        style={{ position: "absolute", inset: 0 }}
        className="flex flex-col items-center justify-center"
      >
        <span
          className={`font-bold tabular-nums text-navy-900 ${scoreTextColor(score)}`}
          style={{ fontSize: size * 0.26, lineHeight: 1 }}
        >
          {score.toFixed(1)}
        </span>
        <span
          className="text-slate-500 font-medium tracking-widest uppercase"
          style={{ fontSize: size * 0.075, marginTop: 4 }}
        >
          out of 10
        </span>
      </div>
    </div>
  );
}
