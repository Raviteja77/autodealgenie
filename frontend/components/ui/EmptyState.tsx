import { type ReactNode } from "react";

interface EmptyStateProps {
  icon: ReactNode;
  title: string;
  body: string;
  cta?: string;
  onCta?: () => void;
}

export function EmptyState({ icon, title, body, cta, onCta }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center px-8 py-16 text-center">
      <div className="w-16 h-16 rounded-xl bg-slate-100 text-slate-500 flex items-center justify-center">
        {icon}
      </div>
      <h3 className="mt-4 text-lg font-semibold text-navy-900">{title}</h3>
      <p className="mt-1.5 text-sm text-slate-500 max-w-sm leading-relaxed">{body}</p>
      {cta && (
        <button
          onClick={onCta}
          className="mt-5 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition-colors"
        >
          {cta}
        </button>
      )}
    </div>
  );
}
