"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Plus, Trash2, Filter, Car, Loader2 } from "lucide-react";
import { StatusBadge } from "@/components/ui/StatusBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { AppShell } from "@/components/layout/AppShell";
import { apiClient, type Deal } from "@/lib/api";

export default function DealsPage() {
  const router = useRouter();
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    apiClient.getDeals()
      .then((data) => setDeals(data))
      .catch((err) => setError(err instanceof Error ? err.message : "Failed to load deals."))
      .finally(() => setLoading(false));
  }, []);

  const filtered = statusFilter === "all"
    ? deals
    : deals.filter((d) => d.status === statusFilter);

  const headerRight = (
    <button
      onClick={() => router.push("/dashboard/search")}
      className="h-8 px-3 rounded-lg bg-blue-600 text-white text-sm font-semibold flex items-center gap-1.5 hover:bg-blue-700 transition-colors"
    >
      <Plus size={14} /> New search
    </button>
  );

  return (
    <AppShell headerRight={headerRight}>
      {loading ? (
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 size={28} className="text-blue-600 animate-spin" />
        </div>
      ) : error ? (
        <div className="bg-white border border-red-200 rounded-xl p-6 text-center">
          <div className="font-semibold text-red-700">{error}</div>
        </div>
      ) : deals.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-xl mt-2">
          <EmptyState
            icon={<Car size={28} />}
            title="No deals yet."
            body="Run a search and we'll start scoring listings for you. You can save and revisit any deal at any time."
            cta="Start your first search"
            onCta={() => router.push("/dashboard/search")}
          />
        </div>
      ) : (
        <>
          <div className="grid grid-cols-4 gap-3.5">
            <StatCard label="Total deals" value={String(deals.length)} delta="All time" tone="default" />
            <StatCard label="In progress" value={String(deals.filter((d) => d.status === "in_progress").length)} delta="Active negotiations" tone="default" />
            <StatCard label="Completed" value={String(deals.filter((d) => d.status === "completed").length)} delta="Closed deals" tone="default" />
            <StatCard
              label="Total asking value"
              value={`$${deals.reduce((s, d) => s + d.asking_price, 0).toLocaleString()}`}
              delta="Across all deals"
              tone="green"
            />
          </div>

          <div className="bg-white border border-slate-200 rounded-xl mt-5 overflow-hidden">
            <div className="flex items-center justify-between px-5 py-4 border-b border-slate-200">
              <h3 className="text-base font-semibold text-navy-900">Your deals</h3>
              <div className="flex gap-2">
                <select
                  className="h-8 px-2 text-xs border border-slate-300 rounded-lg bg-white text-navy-900 focus:outline-none focus:border-blue-600"
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                >
                  <option value="all">All statuses</option>
                  <option value="in_progress">In progress</option>
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                  <option value="cancelled">Cancelled</option>
                </select>
                <button className="h-8 px-3 rounded-lg text-sm font-semibold text-navy-900 hover:bg-slate-100 flex items-center gap-1.5 transition-colors">
                  <Filter size={14} /> Filter
                </button>
              </div>
            </div>

            {filtered.length === 0 ? (
              <div className="py-12 text-center text-slate-500 text-sm">No deals match this filter.</div>
            ) : (
              <table className="w-full border-collapse">
                <thead>
                  <tr className="bg-slate-50">
                    <Th>Vehicle</Th>
                    <Th>Started</Th>
                    <Th>Status</Th>
                    <Th align="right">Asking</Th>
                    <Th align="right">Actions</Th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((d) => (
                    <tr key={d.id} className="border-t border-slate-200">
                      <Td>
                        <div className="flex items-center gap-3">
                          <div className="w-[60px] h-11 rounded-lg bg-slate-100 overflow-hidden flex items-center justify-center shrink-0">
                            <VehicleIcon />
                          </div>
                          <div>
                            <div className="text-[14px] font-semibold text-navy-900">
                              {d.vehicle_year} {d.vehicle_make} {d.vehicle_model}
                            </div>
                            <div className="text-[12px] text-slate-500 tabular-nums mt-0.5">
                              {d.vehicle_mileage.toLocaleString()} mi · ${d.asking_price.toLocaleString()}
                            </div>
                          </div>
                        </div>
                      </Td>
                      <Td>
                        <span className="text-[13px] text-slate-600 tabular-nums">
                          {new Date(d.created_at).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                        </span>
                      </Td>
                      <Td>
                        <StatusBadge status={toDisplayStatus(d.status) as "Pending" | "In progress" | "Completed" | "Cancelled"} />
                      </Td>
                      <Td align="right">
                        <span className="text-[14px] font-semibold text-navy-900 tabular-nums">${d.asking_price.toLocaleString()}</span>
                      </Td>
                      <Td align="right">
                        <div className="inline-flex gap-1.5">
                          {d.status === "in_progress" && (
                            <button
                              onClick={() => router.push("/dashboard/negotiation")}
                              className="h-7 px-2.5 rounded-md bg-blue-600 text-white text-xs font-semibold hover:bg-blue-700 transition-colors"
                            >
                              Continue
                            </button>
                          )}
                          {d.status === "completed" && (
                            <button
                              onClick={() => router.push("/dashboard/summary")}
                              className="h-7 px-2.5 rounded-md border border-slate-300 bg-white text-xs font-semibold text-navy-900 hover:bg-slate-50 transition-colors"
                            >
                              View summary
                            </button>
                          )}
                          {d.status === "pending" && (
                            <button
                              onClick={() => router.push("/dashboard/evaluation")}
                              className="h-7 px-2.5 rounded-md border border-slate-300 bg-white text-xs font-semibold text-navy-900 hover:bg-slate-50 transition-colors"
                            >
                              Evaluate
                            </button>
                          )}
                          <button
                            aria-label="Delete"
                            onClick={() => setDeals((prev) => prev.filter((x) => x.id !== d.id))}
                            className="h-7 w-7 rounded-md text-slate-500 hover:bg-slate-100 flex items-center justify-center transition-colors"
                          >
                            <Trash2 size={13} />
                          </button>
                        </div>
                      </Td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </>
      )}
    </AppShell>
  );
}

function toDisplayStatus(s: string): string {
  return ({ in_progress: "In progress", pending: "Pending", completed: "Completed", cancelled: "Cancelled" } as Record<string, string>)[s] ?? s;
}

function StatCard({ label, value, delta, tone }: { label: string; value: string; delta: string; tone: "default" | "green" }) {
  const isGreen = tone === "green";
  return (
    <div className={`p-4 rounded-xl border ${isGreen ? "bg-green-50 border-green-200" : "bg-white border-slate-200"}`}>
      <div className={`text-[11px] font-semibold uppercase tracking-wider ${isGreen ? "text-green-700" : "text-slate-500"}`}>{label}</div>
      <div className={`text-[28px] font-bold tabular-nums leading-tight mt-2 ${isGreen ? "text-green-700" : "text-navy-900"}`}>{value}</div>
      <div className={`text-[12px] font-medium tabular-nums mt-1.5 ${isGreen ? "text-green-700" : "text-slate-500"}`}>{delta}</div>
    </div>
  );
}

function Th({ children, align = "left" }: { children: React.ReactNode; align?: "left" | "center" | "right" }) {
  return (
    <th className="px-4 py-2.5 text-[11px] font-semibold text-slate-500 uppercase tracking-wider" style={{ textAlign: align }}>
      {children}
    </th>
  );
}

function Td({ children, align = "left" }: { children: React.ReactNode; align?: "left" | "center" | "right" }) {
  return <td className="px-4 py-3.5 align-middle" style={{ textAlign: align }}>{children}</td>;
}

function VehicleIcon() {
  return (
    <svg width="36" height="18" viewBox="0 0 36 18" fill="none" className="text-slate-300">
      <rect x="1" y="6" width="34" height="10" rx="2" fill="currentColor" opacity="0.5" />
      <rect x="6" y="2" width="24" height="8" rx="2" fill="currentColor" opacity="0.35" />
      <circle cx="9" cy="16" r="2.5" fill="currentColor" opacity="0.6" />
      <circle cx="27" cy="16" r="2.5" fill="currentColor" opacity="0.6" />
    </svg>
  );
}
