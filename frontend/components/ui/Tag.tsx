import { cn } from "@/lib/utils/cn";

type Tone = "neutral" | "blue" | "green";

const TONE_STYLES: Record<Tone, string> = {
  neutral: "bg-white text-slate-600 border-slate-200",
  blue:    "bg-blue-50 text-blue-700 border-blue-100",
  green:   "bg-green-50 text-green-700 border-green-100",
};

interface TagProps {
  children: React.ReactNode;
  tone?: Tone;
  className?: string;
}

export function Tag({ children, tone = "neutral", className }: TagProps) {
  return (
    <span
      className={cn(
        "inline-flex px-2 py-0.5 rounded-full text-[11px] font-semibold border",
        TONE_STYLES[tone],
        className
      )}
    >
      {children}
    </span>
  );
}
