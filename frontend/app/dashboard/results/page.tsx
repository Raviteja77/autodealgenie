"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Heart, Search, AlertTriangle } from "lucide-react";
import { ScoreBadge } from "@/components/ui/ScoreBadge";
import { EmptyState } from "@/components/ui/EmptyState";
import { AppShell } from "@/components/layout/AppShell";
import { apiClient, type VehicleRecommendation } from "@/lib/api";
import { MOCK_SEARCH_RESPONSE } from "@/lib/mock/mockData";
import { flowState } from "@/lib/flowState";

const IS_DEMO = process.env.NEXT_PUBLIC_USE_MOCK === "true";

type SortKey = "score" | "price_asc" | "price_desc" | "days";

function sortVehicles(vehicles: VehicleRecommendation[], sort: SortKey) {
  return [...vehicles].sort((a, b) => {
    if (sort === "score") return (b.recommendation_score ?? 0) - (a.recommendation_score ?? 0);
    if (sort === "price_asc") return (a.price ?? 0) - (b.price ?? 0);
    if (sort === "price_desc") return (b.price ?? 0) - (a.price ?? 0);
    if (sort === "days") return (a.days_on_market ?? 999) - (b.days_on_market ?? 999);
    return 0;
  });
}

function ResultsContent() {
  const router = useRouter();
  const params = useSearchParams();
  const [vehicles, setVehicles] = useState<VehicleRecommendation[]>([]);
  const [totalFound, setTotalFound] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [favorites, setFavorites] = useState<Record<string, boolean>>({});
  const [compare, setCompare] = useState<Record<string, boolean>>({});
  const [sort, setSort] = useState<SortKey>("score");

  const make = params.get("make") ?? "";
  const model = params.get("model") ?? "";
  const yearMin = params.get("yearMin");
  const yearMax = params.get("yearMax");
  const maxMileage = params.get("maxMileage");
  const maxPrice = params.get("maxPrice");
  const condition = params.get("condition");

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        if (IS_DEMO) {
          await new Promise((r) => setTimeout(r, 800)); // simulate network
          setVehicles(MOCK_SEARCH_RESPONSE.top_vehicles);
          setTotalFound(MOCK_SEARCH_RESPONSE.total_found);
        } else {
          const res = await apiClient.searchCars({
            make: make || undefined,
            model: model || undefined,
            year_min: yearMin ? parseInt(yearMin) : undefined,
            year_max: yearMax ? parseInt(yearMax) : undefined,
            mileage_max: maxMileage ? parseInt(maxMileage) : undefined,
            budget_max: maxPrice ? parseInt(maxPrice) : undefined,
            user_priorities: condition || undefined,
          });
          setVehicles(res.top_vehicles);
          setTotalFound(res.total_found);
        }
      } catch (err) {
        setError(
          err instanceof Error
            ? err.message
            : "Search is temporarily unavailable. Please try again."
        );
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [make, model, yearMin, yearMax, maxMileage, maxPrice, condition]);

  const sorted = sortVehicles(vehicles, sort);
  const compareCount = Object.values(compare).filter(Boolean).length;

  const headerRight = (
    <select
      className={selCls}
      value={sort}
      onChange={(e) => setSort(e.target.value as SortKey)}
      style={{ width: 170 }}
    >
      <option value="score">Sort: Best match</option>
      <option value="price_asc">Price: low → high</option>
      <option value="price_desc">Price: high → low</option>
      <option value="days">Newest listing</option>
    </select>
  );

  const searchLabel = [
    make || "Any make",
    model,
    yearMin && yearMax ? `${yearMin}–${yearMax}` : null,
    maxPrice ? `under $${parseInt(maxPrice).toLocaleString()}` : null,
  ]
    .filter(Boolean)
    .join(" · ");

  return (
    <AppShell headerRight={headerRight}>
      <div className="grid grid-cols-[260px_1fr] gap-6">
        {/* Filter sidebar */}
        <aside className="self-start sticky top-[84px]">
          <div className="bg-white border border-slate-200 rounded-xl p-5">
            <div className="flex justify-between items-center">
              <h3 className="text-sm font-semibold text-navy-900">Filters</h3>
              <button
                onClick={() => router.push("/dashboard/search")}
                className="text-xs font-semibold text-blue-700 hover:opacity-80"
              >
                New search
              </button>
            </div>
            <div className="mt-4 pt-3.5 border-t border-slate-200">
              <div className="text-[12px] font-semibold uppercase tracking-wider text-navy-900 mb-2">
                Score filter
              </div>
              <FilterGroup label="">
                <CheckRow defaultChecked>Great (8.5+)</CheckRow>
                <CheckRow defaultChecked>Good (7–8.4)</CheckRow>
                <CheckRow>Fair (5–6.9)</CheckRow>
              </FilterGroup>
            </div>
            {IS_DEMO && (
              <div className="mt-4 pt-3.5 border-t border-slate-200">
                <div className="text-[11px] text-amber-700 bg-amber-50 rounded-lg px-3 py-2 font-medium">
                  Demo mode — showing sample listings
                </div>
              </div>
            )}
          </div>
        </aside>

        {/* Main */}
        <div>
          <div className="flex justify-between items-end mb-4">
            <div>
              <h1 className="text-[22px] font-bold text-navy-900 tracking-tight">
                {loading
                  ? "Scanning listings…"
                  : error
                  ? "Search failed"
                  : vehicles.length === 0
                  ? "No matches yet"
                  : `${totalFound} listings, scored for you`}
              </h1>
              <p className="text-[13px] text-slate-500 mt-1">{searchLabel}</p>
            </div>
          </div>

          {loading && <ResultsSkeleton />}

          {!loading && error && (
            <div className="bg-white border border-red-200 rounded-xl p-6 flex gap-3 items-start">
              <AlertTriangle size={18} className="text-red-600 mt-0.5 shrink-0" />
              <div>
                <div className="font-semibold text-red-700">Search unavailable</div>
                <div className="text-sm text-slate-600 mt-1">{error}</div>
                <button
                  onClick={() => router.push("/dashboard/search")}
                  className="mt-3 text-sm font-semibold text-blue-700 hover:opacity-80"
                >
                  Go back and try again
                </button>
              </div>
            </div>
          )}

          {!loading && !error && vehicles.length === 0 && (
            <div className="bg-white border border-slate-200 rounded-xl">
              <EmptyState
                icon={<Search size={28} />}
                title="No cars matched these criteria."
                body="Try widening your year range or raising your max price. We'll keep scanning new listings."
                cta="Adjust search"
              />
            </div>
          )}

          {!loading && !error && sorted.length > 0 && (
            <div className="grid grid-cols-2 gap-4">
              {sorted.map((v) => {
                const key = v.vin ?? `${v.make}-${v.model}-${v.year}`;
                return (
                  <VehicleCard
                    key={key}
                    v={v}
                    fav={!!favorites[key]}
                    onFav={() => setFavorites((f) => ({ ...f, [key]: !f[key] }))}
                    cmp={!!compare[key]}
                    onCmp={() => setCompare((c) => ({ ...c, [key]: !c[key] }))}
                    onEvaluate={() => {
                      flowState.setVehicle({
                        vin: v.vin,
                        make: v.make,
                        model: v.model,
                        year: v.year,
                        mileage: v.mileage,
                        price: v.price,
                        msrp: v.msrp,
                        trim: v.trim,
                        location: v.location,
                        dealer_name: v.dealer_name,
                        recommendation_score: v.recommendation_score,
                        recommendation_summary: v.recommendation_summary,
                      });
                      // Clear stale evaluation/negotiation from a previous flow
                      sessionStorage.removeItem("adg_evaluation");
                      sessionStorage.removeItem("adg_negotiation");
                      router.push("/dashboard/evaluation");
                    }}
                  />
                );
              })}
            </div>
          )}
        </div>
      </div>

      {/* Comparison bar */}
      {compareCount >= 2 && (
        <div
          className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-navy-900 text-white px-5 py-3 rounded-xl flex items-center gap-4 z-40"
          style={{ boxShadow: "0 24px 48px -12px rgba(15,22,41,0.4)" }}
        >
          <span className="text-sm font-medium">{compareCount} cars selected</span>
          <button className="h-8 px-4 rounded-lg bg-white text-navy-900 text-sm font-semibold hover:bg-slate-100 transition-colors">
            Compare side-by-side
          </button>
          <button
            onClick={() => setCompare({})}
            className="text-slate-400 text-sm hover:text-slate-200 transition-colors"
          >
            Clear
          </button>
        </div>
      )}
    </AppShell>
  );
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<AppShell><ResultsSkeleton /></AppShell>}>
      <ResultsContent />
    </Suspense>
  );
}

function VehicleCard({
  v,
  fav,
  onFav,
  cmp,
  onCmp,
  onEvaluate,
}: {
  v: VehicleRecommendation;
  fav: boolean;
  onFav: () => void;
  cmp: boolean;
  onCmp: () => void;
  onEvaluate: () => void;
}) {
  const score = v.recommendation_score ?? 0;
  const delta = v.msrp != null && v.price != null ? v.msrp - v.price : null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl overflow-hidden flex flex-col">
      <div className="relative">
        <VehicleThumb />
        <div
          className="absolute top-2.5 right-2.5 bg-white rounded-full flex items-center gap-1.5 pl-2.5 pr-1 py-1"
          style={{ boxShadow: "0 2px 8px rgba(15,22,41,0.12)" }}
        >
          <span className="text-[10px] font-semibold text-slate-600 uppercase tracking-wider">Deal</span>
          <ScoreBadge score={score} size="sm" />
        </div>
        <button
          onClick={onFav}
          aria-label="Favorite"
          className="absolute top-2.5 left-2.5 w-8 h-8 rounded-full bg-white/95 flex items-center justify-center hover:bg-white transition-colors"
          style={{ boxShadow: "0 1px 4px rgba(0,0,0,0.1)" }}
        >
          <Heart size={15} className={fav ? "text-red-600 fill-red-600" : "text-navy-900"} />
        </button>
      </div>

      <div className="p-3.5 flex flex-col gap-2.5 flex-1">
        <div className="flex justify-between items-start">
          <div>
            <div className="text-[14px] font-semibold text-navy-900">
              {v.year} {v.make} {v.model} {v.trim}
            </div>
            <div className="text-[12px] text-slate-500 mt-0.5 tabular-nums">
              {v.mileage?.toLocaleString()} mi
              {v.location ? ` · ${v.location}` : ""}
            </div>
          </div>
          <div className="text-right">
            <div className="text-[16px] font-bold text-navy-900 tabular-nums">
              ${v.price?.toLocaleString() ?? "—"}
            </div>
            {delta != null && (
              <div
                className={`text-[11px] font-medium mt-0.5 tabular-nums ${
                  delta >= 0 ? "text-green-600" : "text-amber-600"
                }`}
              >
                {delta >= 0
                  ? `$${delta.toLocaleString()} under FMV`
                  : `$${Math.abs(delta).toLocaleString()} over FMV`}
              </div>
            )}
          </div>
        </div>

        {v.recommendation_summary && (
          <div className="p-2.5 bg-blue-50 rounded-lg text-[12px] leading-relaxed text-slate-700">
            <span className="font-semibold text-blue-700">Why this car? </span>
            {v.recommendation_summary}
          </div>
        )}

        {v.highlights && v.highlights.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {v.highlights.map((h) => (
              <span
                key={h}
                className="text-[11px] font-medium px-2 py-0.5 bg-slate-100 text-slate-600 rounded-full"
              >
                {h}
              </span>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2.5 mt-auto">
          <button
            onClick={onEvaluate}
            className="flex-1 h-8 rounded-lg bg-blue-600 text-white text-[13px] font-semibold hover:bg-blue-700 transition-colors"
          >
            Evaluate deal
          </button>
          <label className="flex items-center gap-1.5 text-[12px] font-medium text-slate-600 cursor-pointer shrink-0">
            <input type="checkbox" checked={cmp} onChange={onCmp} className="m-0" />
            Compare
          </label>
        </div>
      </div>
    </div>
  );
}

function VehicleThumb() {
  return (
    <div className="h-[150px] bg-slate-100 flex items-center justify-center">
      <svg width="120" height="60" viewBox="0 0 120 60" fill="none" className="text-slate-300">
        <rect x="10" y="20" width="100" height="30" rx="6" fill="currentColor" opacity="0.5" />
        <rect x="25" y="10" width="70" height="24" rx="4" fill="currentColor" opacity="0.35" />
        <circle cx="30" cy="50" r="10" fill="currentColor" opacity="0.6" />
        <circle cx="90" cy="50" r="10" fill="currentColor" opacity="0.6" />
      </svg>
    </div>
  );
}

function ResultsSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="skel h-[150px] rounded-none" />
          <div className="p-3.5 flex flex-col gap-2.5">
            <div className="skel h-4 w-3/5" />
            <div className="skel h-3 w-2/5" />
            <div className="skel h-14 w-full" />
            <div className="skel h-8 w-full" />
          </div>
        </div>
      ))}
    </div>
  );
}

function FilterGroup({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      {label && (
        <div className="text-[12px] font-semibold uppercase tracking-wider text-navy-900 mb-2">{label}</div>
      )}
      <div className="flex flex-col gap-2">{children}</div>
    </div>
  );
}

function CheckRow({
  children,
  defaultChecked,
}: {
  children: React.ReactNode;
  defaultChecked?: boolean;
}) {
  return (
    <label className="flex items-center gap-2 text-[13px] text-slate-700 cursor-pointer">
      <input type="checkbox" defaultChecked={defaultChecked} className="m-0" />
      {children}
    </label>
  );
}

const selCls =
  "h-8 px-2 text-xs border border-slate-300 rounded-lg bg-white text-navy-900 focus:outline-none focus:border-blue-600";
