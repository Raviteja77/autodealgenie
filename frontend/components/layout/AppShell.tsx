"use client";

import { type ReactNode, useState, useRef, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  List,
  Search,
  Car,
  Gauge,
  MessageSquare,
  CheckCircle,
  LogOut,
  ChevronUp,
} from "lucide-react";
import { cn } from "@/lib/utils/cn";
import { useAuth } from "@/lib/auth";

const NAV_ITEMS = [
  { key: "deals",       label: "My deals",    icon: List,          href: "/deals" },
  { key: "search",      label: "New search",  icon: Search,        href: "/dashboard/search" },
  { key: "results",     label: "Results",     icon: Car,           href: "/dashboard/results" },
  { key: "evaluation",  label: "Evaluation",  icon: Gauge,         href: "/dashboard/evaluation" },
  { key: "negotiation", label: "Negotiation", icon: MessageSquare, href: "/dashboard/negotiation" },
  { key: "summary",     label: "Summary",     icon: CheckCircle,   href: "/dashboard/summary" },
];

interface AppShellProps {
  children: ReactNode;
  headerRight?: ReactNode;
  headerTitle?: string;
}

export function AppShell({ children, headerRight, headerTitle }: AppShellProps) {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  const displayName = user?.full_name || user?.username || "User";
  const initials = displayName
    .split(" ")
    .map((w) => w[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  const activeKey = NAV_ITEMS.find((n) => pathname.startsWith(n.href))?.key ?? "deals";

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-60 bg-white border-r border-slate-200 flex flex-col sticky top-0 h-screen shrink-0">
        <Link
          href="/deals"
          className="flex items-center gap-2.5 px-5 py-5 pb-4"
        >
          <div className="w-8 h-8 rounded-lg bg-navy-900 flex items-center justify-center shrink-0">
            <Gauge size={16} className="text-blue-400" />
          </div>
          <span className="font-bold text-[15px] tracking-tight text-navy-900">
            AutoDealGenie
          </span>
        </Link>

        <nav className="px-3 flex flex-col gap-0.5 flex-1">
          {NAV_ITEMS.map(({ key, label, icon: Icon, href }) => {
            const isActive = key === activeKey;
            return (
              <Link
                key={key}
                href={href}
                className={cn(
                  "flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-colors",
                  isActive
                    ? "bg-slate-100 font-semibold text-navy-900"
                    : "font-medium text-slate-600 hover:bg-slate-50"
                )}
              >
                <Icon
                  size={18}
                  className={isActive ? "text-blue-600" : "text-slate-500"}
                />
                {label}
              </Link>
            );
          })}
        </nav>

        {/* User footer */}
        <div className="p-4 border-t border-slate-200 mt-auto relative" ref={menuRef}>
          {menuOpen && (
            <div className="absolute bottom-full left-3 right-3 mb-1 bg-white border border-slate-200 rounded-lg shadow-lg py-1 z-50">
              <button
                onClick={() => { setMenuOpen(false); logout(); }}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
              >
                <LogOut size={15} />
                Sign out
              </button>
            </div>
          )}

          <button
            onClick={() => setMenuOpen((o) => !o)}
            className="w-full flex items-center gap-2.5 rounded-lg hover:bg-slate-50 transition-colors p-1 -m-1"
          >
            <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-xs font-semibold shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0 text-left">
              <div className="text-[13px] font-semibold text-navy-900 truncate">{displayName}</div>
              <div className="text-[11px] text-slate-500 truncate">{user?.email ?? ""}</div>
            </div>
            <ChevronUp
              size={15}
              className={cn("text-slate-400 shrink-0 transition-transform", !menuOpen && "rotate-180")}
            />
          </button>
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Topbar */}
        <header className="h-[60px] bg-white border-b border-slate-200 flex items-center justify-between px-7 sticky top-0 z-30">
          <span className="text-base font-semibold text-navy-900">
            {headerTitle ?? NAV_ITEMS.find((n) => n.key === activeKey)?.label ?? "Dashboard"}
          </span>
          {headerRight && (
            <div className="flex items-center gap-2.5">{headerRight}</div>
          )}
        </header>

        <div className="flex-1 p-7 pb-20">{children}</div>
      </main>
    </div>
  );
}
