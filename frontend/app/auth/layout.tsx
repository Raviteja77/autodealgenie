import { type ReactNode } from "react";
import Link from "next/link";
import { Gauge } from "lucide-react";

export default function AuthLayout({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
      <header className="h-16 bg-white border-b border-slate-200 flex items-center px-6">
        <Link href="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-navy-900 flex items-center justify-center">
            <Gauge size={16} className="text-blue-400" />
          </div>
          <span className="font-bold text-[17px] tracking-tight text-navy-900">AutoDealGenie</span>
        </Link>
      </header>
      <div className="flex-1 flex items-center justify-center p-5">
        {children}
      </div>
    </div>
  );
}
