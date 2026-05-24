"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Bookmark,
  ArrowRight,
  Check,
  Shield,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  ChevronDown,
  Building,
  Search,
  Loader2,
} from "lucide-react";
import { ScoreGauge } from "@/components/ui/ScoreGauge";
import { scoreTier, scoreTextColor, scoreBgColor } from "@/components/ui/ScoreBadge";
import { Tag } from "@/components/ui/Tag";
import { EmptyState } from "@/components/ui/EmptyState";
import { AppShell } from "@/components/layout/AppShell";
import { apiClient } from "@/lib/api";
import { flowState, type FlowVehicle, type FlowEvaluation } from "@/lib/flowState";
import { useAuth } from "@/lib/auth";

type PageState =
  | { status: "no-vehicle" }
  | { status: "running"; step: number; stepLabel: string }
  | { status: "done"; vehicle: FlowVehicle; evaluation: FlowEvaluation }
  | { status: "error"; message: string };

const STEP_LABELS = [
  "Assessing vehicle condition…",
  "Analyzing price fairness…",
  "Evaluating financing options…",
  "Assessing risk factors…",
  "Computing overall score…",
];

function getNum(obj: unknown, key: string, fallback = 0): number {
  if (obj && typeof obj === "object" && key in (obj as object)) {
    const v = (obj as Record<string, unknown>)[key];
    if (typeof v === "number") return v;
  }
  return fallback;
}

function getStrArr(obj: unknown, key: string): string[] {
  if (obj && typeof obj === "object" && key in (obj as object)) {
    const v = (obj as Record<string, unknown>)[key];
    if (Array.isArray(v)) return v.filter((s): s is string => typeof s === "string");
  }
  return [];
}

function getStr(obj: unknown, key: string, fallback = ""): string {
  if (obj && typeof obj === "object" && key in (obj as object)) {
    const v = (obj as Record<string, unknown>)[key];
    if (typeof v === "string") return v;
  }
  return fallback;
}

export default function EvaluationPage() {
  const router = useRouter();
  const { user } = useAuth();
  const [state, setState] = useState<PageState>({ status: "no-vehicle" });
  const [lendersOpen, setLendersOpen] = useState(true);

  useEffect(() => {
    const vehicle = flowState.getVehicle();
    if (!vehicle || !vehicle.price) {
      setState({ status: "no-vehicle" });
      return;
    }

    const cached = flowState.getEvaluation();
    if (cached) {
      setState({ status: "done", vehicle, evaluation: cached });
      return;
    }

    runEvaluation(vehicle);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function runEvaluation(vehicle: FlowVehicle) {
    if (!user) return;

    try {
      setState({ status: "running", step: 0, stepLabel: "Creating deal…" });

      const deal = await apiClient.createDeal({
        customer_name: user.full_name || user.username,
        customer_email: user.email,
        vehicle_make: vehicle.make ?? "Unknown",
        vehicle_model: vehicle.model ?? "Unknown",
        vehicle_year: vehicle.year ?? new Date().getFullYear(),
        vehicle_mileage: vehicle.mileage ?? 0,
        vehicle_vin: vehicle.vin ?? "UNKNOWN",
        asking_price: vehicle.price ?? 0,
      });

      // Run all 5 pipeline steps. Pre-supply financing + condition answers so
      // the backend never pauses to ask questions.
      const initialAnswers: Record<string, string | number> = {
        vin: vehicle.vin ?? "UNKNOWN",
        condition_description: "good",
        financing_type: "loan",
        interest_rate: 6.5,
      };

      let lastResult = null;
      let evaluationId = 0;

      for (let i = 0; i < 7; i++) {
        setState({ status: "running", step: Math.min(i, 4), stepLabel: STEP_LABELS[Math.min(i, 4)] });

        const result = await apiClient.startEvaluation(deal.id, {
          answers: i === 0 ? initialAnswers : undefined,
        });

        lastResult = result;
        evaluationId = result.evaluation_id;

        if (result.status === "completed") break;
        if (result.status === "awaiting_input") {
          // Shouldn't happen with pre-supplied answers, but break to avoid looping
          break;
        }
      }

      if (!lastResult || !lastResult.result_json) {
        setState({ status: "error", message: "Evaluation completed but no results were returned." });
        return;
      }

      const rj = lastResult.result_json as Record<string, unknown>;
      const finalStep = (rj.final as Record<string, unknown> | undefined)?.assessment as Record<string, unknown> | undefined;
      const overallScore = getNum(finalStep, "overall_score", 5.0);

      const evaluation: FlowEvaluation = {
        dealId: deal.id,
        evaluationId,
        overallScore,
        resultJson: rj,
      };

      flowState.setEvaluation(evaluation);
      setState({ status: "done", vehicle, evaluation });
    } catch (err) {
      setState({
        status: "error",
        message: err instanceof Error ? err.message : "Evaluation failed. Please try again.",
      });
    }
  }

  if (state.status === "no-vehicle") {
    return (
      <AppShell>
        <div className="bg-white border border-slate-200 rounded-xl mt-2">
          <EmptyState
            icon={<Search size={28} />}
            title="No vehicle selected."
            body="Go to search, find a car you're interested in, and click 'Evaluate deal' to run the AI analysis."
            cta="Go to search"
            onCta={() => router.push("/dashboard/search")}
          />
        </div>
      </AppShell>
    );
  }

  if (state.status === "running") {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-6">
          <div className="w-16 h-16 rounded-2xl bg-blue-50 flex items-center justify-center">
            <Loader2 size={28} className="text-blue-600 animate-spin" />
          </div>
          <div className="text-center">
            <div className="text-[18px] font-semibold text-navy-900">Running 5-step AI evaluation</div>
            <div className="text-[14px] text-slate-500 mt-1">{state.stepLabel}</div>
          </div>
          <div className="flex gap-2">
            {STEP_LABELS.map((_, i) => (
              <div
                key={i}
                className={`w-2.5 h-2.5 rounded-full transition-colors ${
                  i <= state.step ? "bg-blue-600" : "bg-slate-200"
                }`}
              />
            ))}
          </div>
        </div>
      </AppShell>
    );
  }

  if (state.status === "error") {
    return (
      <AppShell>
        <div className="bg-white border border-red-200 rounded-xl p-6 flex gap-3 items-start">
          <AlertTriangle size={18} className="text-red-600 mt-0.5 shrink-0" />
          <div>
            <div className="font-semibold text-red-700">Evaluation failed</div>
            <div className="text-sm text-slate-600 mt-1">{state.message}</div>
            <button
              onClick={() => {
                const vehicle = flowState.getVehicle();
                if (vehicle) runEvaluation(vehicle);
              }}
              className="mt-3 text-sm font-semibold text-blue-700 hover:opacity-80"
            >
              Retry
            </button>
          </div>
        </div>
      </AppShell>
    );
  }

  // Done — render with real data
  const { vehicle, evaluation } = state;
  const rj = evaluation.resultJson;

  const conditionStep = (rj.vehicle_condition as Record<string, unknown> | undefined)?.assessment as Record<string, unknown> | undefined;
  const priceStep = (rj.price as Record<string, unknown> | undefined)?.assessment as Record<string, unknown> | undefined;
  const financingStep = (rj.financing as Record<string, unknown> | undefined)?.assessment as Record<string, unknown> | undefined;
  const riskStep = (rj.risk as Record<string, unknown> | undefined)?.assessment as Record<string, unknown> | undefined;
  const finalStep = (rj.final as Record<string, unknown> | undefined)?.assessment as Record<string, unknown> | undefined;

  const conditionScore = getNum(conditionStep, "condition_score", 7.0);
  const priceScore = getNum(priceStep, "score", 5.0);
  const fairValue = getNum(priceStep, "fair_value", vehicle.price ?? 0);
  const financingScore = getNum(financingStep, "affordability_score", 7.0);
  const riskScore = getNum(riskStep, "risk_score", 5.0);
  const overallScore = evaluation.overallScore;
  const recommendation = getStr(finalStep, "recommendation", "Analysis complete.");

  const conditionNotes = getStrArr(conditionStep, "condition_notes");
  const priceInsights = getStrArr(priceStep, "insights");
  const priceTalkingPoints = getStrArr(priceStep, "talking_points");
  const financingNotes = getStrArr(financingStep, "affordability_notes");
  const monthlyPayment = getNum(financingStep, "monthly_payment", 0);

  const askingPrice = vehicle.price ?? 0;
  const delta = fairValue - askingPrice;

  const PIPELINE_STEPS = [
    { label: "Condition", score: conditionScore },
    { label: "Price", score: priceScore },
    { label: "Financing", score: financingScore },
    { label: "Risk", score: riskScore },
    { label: "Overall", score: overallScore },
  ];

  const SUBSCORES = [
    {
      icon: Shield,
      label: "Vehicle condition",
      score: conditionScore,
      insights: conditionNotes.length > 0 ? conditionNotes : ["Condition assessed based on mileage and vehicle data"],
    },
    {
      icon: DollarSign,
      label: "Price fairness",
      score: priceScore,
      insights: priceInsights.length > 0 ? priceInsights : [`Fair market value estimated at $${fairValue.toLocaleString()}`],
    },
    {
      icon: TrendingUp,
      label: "Financing estimate",
      score: financingScore,
      insights: financingNotes.length > 0 ? financingNotes : [
        monthlyPayment > 0 ? `Est. monthly payment ~$${Math.round(monthlyPayment).toLocaleString()} (60-month, 6.5% APR)` : "Financing estimate based on standard loan terms",
      ],
    },
    {
      icon: AlertTriangle,
      label: "Risk assessment",
      score: riskScore,
      insights: [`Risk score: ${riskScore.toFixed(1)}/10`, `${vehicle.mileage?.toLocaleString()} mi — ${riskScore >= 7 ? "within normal range" : "monitor maintenance closely"}`],
    },
  ];

  return (
    <AppShell>
      {/* Sticky vehicle summary */}
      <div className="sticky top-[60px] z-20 bg-slate-50 -mx-7 mb-6 px-7 py-5 border-b border-slate-200">
        <div className="bg-white border border-slate-200 rounded-xl p-4 flex items-center gap-4">
          <VehicleThumb className="w-[88px] h-16 rounded-lg shrink-0" />
          <div className="flex-1">
            <div className="text-base font-semibold text-navy-900">
              {vehicle.year} {vehicle.make} {vehicle.model} {vehicle.trim}
            </div>
            <div className="text-[13px] text-slate-500 mt-0.5 tabular-nums">
              {vehicle.mileage?.toLocaleString()} mi{vehicle.location ? ` · ${vehicle.location}` : ""}
            </div>
          </div>
          <div className="text-right mr-2">
            <div className="text-[20px] font-bold text-navy-900 tabular-nums">${askingPrice.toLocaleString()}</div>
            {delta !== 0 && (
              <div className={`text-[12px] font-medium mt-1 tabular-nums ${delta >= 0 ? "text-green-600" : "text-amber-600"}`}>
                {delta >= 0 ? `$${delta.toLocaleString()} under FMV` : `$${Math.abs(delta).toLocaleString()} over FMV`}
              </div>
            )}
          </div>
          <div className="flex gap-2">
            <button className="h-9 px-3.5 rounded-lg border border-slate-300 bg-white text-navy-900 text-sm font-semibold flex items-center gap-1.5 hover:bg-slate-50 transition-colors">
              <Bookmark size={13} /> Save
            </button>
            <button
              onClick={() => router.push("/dashboard/negotiation")}
              className="h-9 px-3.5 rounded-lg bg-blue-600 text-white text-sm font-semibold flex items-center gap-1.5 hover:bg-blue-700 transition-colors"
            >
              Start negotiation <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Pipeline */}
      <div className="bg-white border border-slate-200 rounded-xl p-7">
        <div className="text-[11px] font-semibold uppercase tracking-widest text-slate-500">5-step AI evaluation</div>
        <div className="flex items-center justify-between mt-4">
          {PIPELINE_STEPS.map((step, i) => (
            <div key={i} className="flex items-center flex-1">
              <div className="flex flex-col items-center gap-2 min-w-[80px]">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white ${scoreBgColor(step.score)}`}>
                  <Check size={20} />
                </div>
                <span className="text-[13px] font-semibold text-navy-900">{step.label}</span>
                <span className={`text-sm font-bold tabular-nums ${scoreTextColor(step.score)}`}>
                  {step.score.toFixed(1)}
                </span>
              </div>
              {i < PIPELINE_STEPS.length - 1 && (
                <div className="flex-1 h-0.5 bg-green-500 mb-8 mx-1" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Score + subscores */}
      <div className="grid grid-cols-[320px_1fr] gap-5 mt-5">
        <div className="bg-white border border-slate-200 rounded-2xl p-7 text-center">
          <div className="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Overall deal score</div>
          <div className="mt-4 flex justify-center">
            <ScoreGauge score={overallScore} size={200} />
          </div>
          <div
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-white text-[13px] font-semibold mt-4"
            style={{ background: overallScore >= 7 ? "#10B981" : overallScore >= 5 ? "#F59E0B" : "#EF4444" }}
          >
            <Check size={14} /> {scoreTier(overallScore)} deal
          </div>
          <div className="mt-4 p-3.5 bg-slate-50 rounded-xl text-[13px] leading-relaxed text-slate-700 text-left">
            <strong className="text-navy-900">Bottom line: </strong>{recommendation}
          </div>
          {priceTalkingPoints.length > 0 && (
            <div className="mt-3.5 p-3.5 bg-blue-50 rounded-xl text-left">
              <div className="text-[11px] font-semibold uppercase tracking-wider text-blue-700 mb-2">Negotiation tips</div>
              <ul className="flex flex-col gap-1.5">
                {priceTalkingPoints.slice(0, 3).map((tip, i) => (
                  <li key={i} className="flex gap-1.5 text-[12px] leading-relaxed text-slate-700">
                    <span className="text-blue-400">•</span>{tip}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="flex flex-col gap-5">
          {fairValue > 0 && (
            <div className="bg-white border border-slate-200 rounded-xl p-5">
              <div className="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Price fairness</div>
              <PriceBar asking={askingPrice} fmv={fairValue} />
            </div>
          )}

          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            {SUBSCORES.map((row, i) => {
              const Icon = row.icon;
              return (
                <div key={i} className={`p-4 flex gap-4 ${i < SUBSCORES.length - 1 ? "border-b border-slate-200" : ""}`}>
                  <div className="w-10 h-10 rounded-xl bg-slate-100 text-navy-900 flex items-center justify-center shrink-0">
                    <Icon size={18} />
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between items-center">
                      <span className="text-[14px] font-semibold text-navy-900">{row.label}</span>
                      <span className={`text-base font-bold tabular-nums ${scoreTextColor(row.score)}`}>
                        {row.score.toFixed(1)}<span className="text-slate-400 text-xs">/10</span>
                      </span>
                    </div>
                    <ul className="mt-2 flex flex-col gap-1">
                      {row.insights.map((it, j) => (
                        <li key={j} className="flex gap-2 text-[13px] leading-relaxed text-slate-600">
                          <span className="text-slate-400">•</span>{it}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Lenders */}
      <LenderSection dealId={evaluation.dealId} evaluationId={evaluation.evaluationId} open={lendersOpen} onToggle={() => setLendersOpen((o) => !o)} />
    </AppShell>
  );
}

function LenderSection({ dealId, evaluationId, open, onToggle }: { dealId: number; evaluationId: number; open: boolean; onToggle: () => void }) {
  const [lenders, setLenders] = useState<import("@/lib/api").LenderMatch[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!open || lenders.length > 0) return;
    setLoading(true);
    apiClient.getEvaluationLenders(dealId, evaluationId)
      .then((r) => setLenders(r.recommendations.slice(0, 3)))
      .catch(() => setLenders([]))
      .finally(() => setLoading(false));
  }, [open, dealId, evaluationId, lenders.length]);

  return (
    <Collapsible title="Lender recommendations" meta="Based on your vehicle and loan amount" open={open} onToggle={onToggle}>
      {loading && <div className="text-sm text-slate-500 py-2">Loading lender recommendations…</div>}
      {!loading && lenders.length === 0 && (
        <div className="text-sm text-slate-500 py-2">No lender recommendations available for this vehicle.</div>
      )}
      {!loading && lenders.length > 0 && (
        <div className="grid grid-cols-3 gap-3.5">
          {lenders.map((l, i) => (
            <div key={i} className="border border-slate-200 rounded-xl p-4 bg-white">
              <div className="flex justify-between items-start">
                <div>
                  <div className="text-[14px] font-semibold text-navy-900">{l.lender.name}</div>
                  <div className="text-[12px] text-slate-500 mt-0.5">Auto Loan</div>
                </div>
                {l.rank === 1 && <Tag tone="blue">Best match</Tag>}
              </div>
              <div className="flex gap-4 mt-3.5">
                <div>
                  <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">APR range</div>
                  <div className="text-base font-bold text-navy-900 tabular-nums mt-0.5">
                    {l.lender.apr_range_min}–{l.lender.apr_range_max}%
                  </div>
                </div>
                <div>
                  <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Est. monthly</div>
                  <div className="text-base font-bold text-navy-900 tabular-nums mt-0.5">${Math.round(l.estimated_monthly_payment)}</div>
                </div>
              </div>
              <div className="text-[11px] text-slate-500 mt-2 leading-relaxed">{l.recommendation_reason.slice(0, 80)}{l.recommendation_reason.length > 80 ? "…" : ""}</div>
              <button className="w-full mt-3.5 h-8 rounded-lg border border-slate-300 bg-white text-sm font-semibold text-navy-900 hover:bg-slate-50 transition-colors">
                Pre-qualify
              </button>
            </div>
          ))}
        </div>
      )}
    </Collapsible>
  );
}

function PriceBar({ asking, fmv }: { asking: number; fmv: number }) {
  const min = Math.min(asking, fmv) * 0.9;
  const max = Math.max(asking, fmv) * 1.1;
  const range = max - min || 1;
  const askingPct = ((asking - min) / range) * 100;
  const fmvPct = ((fmv - min) / range) * 100;
  const delta = fmv - asking;

  return (
    <div className="mt-3.5">
      <div className="flex justify-between mb-3.5">
        <div>
          <div className="text-[22px] font-bold text-navy-900 tabular-nums">${asking.toLocaleString()}</div>
          <div className="text-[11px] font-medium uppercase tracking-wider text-slate-500 mt-1">Asking price</div>
        </div>
        <div className="text-right">
          <div className={`text-[22px] font-bold tabular-nums ${delta >= 0 ? "text-green-600" : "text-amber-600"}`}>
            {delta >= 0 ? "−" : "+"}${Math.abs(delta).toLocaleString()}
          </div>
          <div className={`text-[11px] font-medium uppercase tracking-wider mt-1 ${delta >= 0 ? "text-green-700" : "text-amber-700"}`}>
            {delta >= 0 ? "Below fair market" : "Above fair market"}
          </div>
        </div>
      </div>
      <div className="relative h-14">
        <div className="absolute inset-x-0 top-[22px] h-2 bg-slate-100 rounded-full" />
        <div className="absolute top-[14px] w-0.5 h-6 bg-slate-500" style={{ left: `${fmvPct}%`, transform: "translateX(-50%)" }} />
        <div className="absolute top-11 text-[11px] font-medium text-slate-600 whitespace-nowrap" style={{ left: `${fmvPct}%`, transform: "translateX(-50%)" }}>
          FMV ${fmv.toLocaleString()}
        </div>
        <div
          className="absolute top-[16px] w-[18px] h-[18px] bg-white border-[3px] border-blue-600 rounded-full"
          style={{ left: `${askingPct}%`, transform: "translateX(-50%)", boxShadow: "0 2px 6px rgba(37,99,235,0.35)" }}
        />
        <div className="absolute top-11 text-[11px] font-semibold text-blue-700 whitespace-nowrap" style={{ left: `${askingPct}%`, transform: "translateX(-50%)" }}>
          Asking
        </div>
      </div>
    </div>
  );
}

function Collapsible({ title, meta, open, onToggle, children }: { title: string; meta: string; open: boolean; onToggle: () => void; children: React.ReactNode }) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl mt-4 overflow-hidden">
      <button onClick={onToggle} className="w-full flex items-center justify-between px-5 py-4 bg-transparent hover:bg-slate-50 transition-colors">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-700 flex items-center justify-center">
            <Building size={16} />
          </div>
          <div className="text-left">
            <div className="text-[15px] font-semibold text-navy-900">{title}</div>
            <div className="text-[12px] text-slate-500 mt-0.5">{meta}</div>
          </div>
        </div>
        <ChevronDown size={18} className="text-slate-500 transition-transform duration-200" style={{ transform: open ? "rotate(180deg)" : "rotate(0deg)" }} />
      </button>
      {open && <div className="px-5 pb-5">{children}</div>}
    </div>
  );
}

function VehicleThumb({ className = "" }: { className?: string }) {
  return (
    <div className={`bg-slate-100 flex items-center justify-center ${className}`}>
      <svg width="80" height="40" viewBox="0 0 80 40" fill="none" className="text-slate-300">
        <rect x="5" y="12" width="70" height="22" rx="4" fill="currentColor" opacity="0.5" />
        <rect x="15" y="5" width="50" height="18" rx="3" fill="currentColor" opacity="0.35" />
        <circle cx="20" cy="34" r="7" fill="currentColor" opacity="0.6" />
        <circle cx="60" cy="34" r="7" fill="currentColor" opacity="0.6" />
      </svg>
    </div>
  );
}
