import { cn } from "@/lib/utils/cn";

type Status = "Pending" | "In progress" | "Completed" | "Cancelled";

const STATUS_STYLES: Record<Status, { bg: string; fg: string }> = {
  Pending:      { bg: "bg-slate-100",  fg: "text-slate-700" },
  "In progress":{ bg: "bg-blue-50",   fg: "text-blue-700"  },
  Completed:    { bg: "bg-green-50",  fg: "text-green-700" },
  Cancelled:    { bg: "bg-red-50",    fg: "text-red-700"   },
};

interface StatusBadgeProps {
  status: Status;
  className?: string;
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const styles = STATUS_STYLES[status] ?? STATUS_STYLES.Pending;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold whitespace-nowrap",
        styles.bg,
        styles.fg,
        className
      )}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {status}
    </span>
  );
}
