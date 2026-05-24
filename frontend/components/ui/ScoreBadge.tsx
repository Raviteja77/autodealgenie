import { cn } from "@/lib/utils/cn";

function scoreColor(score: number): string {
  if (score >= 7) return "bg-green-500";
  if (score >= 5) return "bg-amber-500";
  return "bg-red-600";
}

interface ScoreBadgeProps {
  score: number;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function ScoreBadge({ score, size = "md", className }: ScoreBadgeProps) {
  const sizeClasses = {
    sm: "w-7 h-7 text-xs",
    md: "w-8 h-8 text-sm",
    lg: "w-10 h-10 text-base",
  };
  return (
    <div
      className={cn(
        "rounded-full flex items-center justify-center font-bold text-white tabular-nums shrink-0",
        scoreColor(score),
        sizeClasses[size],
        className
      )}
    >
      {score.toFixed(1)}
    </div>
  );
}

export function scoreTier(score: number): string {
  if (score >= 8.5) return "Great";
  if (score >= 7)   return "Good";
  if (score >= 5)   return "Fair";
  return "Poor";
}

export function scoreTextColor(score: number): string {
  if (score >= 7) return "text-green-500";
  if (score >= 5) return "text-amber-500";
  return "text-red-600";
}

export function scoreBgColor(score: number): string {
  if (score >= 7) return "bg-green-500";
  if (score >= 5) return "bg-amber-500";
  return "bg-red-600";
}
