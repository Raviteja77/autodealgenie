"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Download, ArrowRight, Check, MessageSquare, Loader2 } from "lucide-react";
import { ScoreGauge } from "@/components/ui/ScoreGauge";
import { EmptyState } from "@/components/ui/EmptyState";
import { AppShell } from "@/components/layout/AppShell";
import { apiClient, type NegotiationSession, type NegotiationMessage } from "@/lib/api";
import { flowState } from "@/lib/flowState";

type PageState =
  | { status: "no-negotiation" }
  | { status: "loading" }
  | { status: "done"; session: NegotiationSession }
  | { status: "error"; message: string };

export default function SummaryPage() {
  const router = useRouter();
  const [state, setState] = useState<PageState>({ status: "loading" });

  const vehicle = flowState.getVehicle();
  const evaluation = flowState.getEvaluation();
  const negotiation = flowState.getNegotiation();

  useEffect(() => {
    if (!negotiation) {
      setState({ status: "no-negotiation" });
      return;
    }
    apiClient.getNegotiationSession(negotiation.sessionId)
      .then((session) => setState({ status: "done", session }))
      .catch((err) => setState({ status: "error", message: err instanceof Error ? err.message : "Failed to load summary." }));
  }, []);

  const headerRight = (
    <>
      <button
        onClick={() => router.push("/dashboard/search")}
        className="h-8 px-3.5 rounded-lg bg-blue-600 text-white text-sm font-semibold flex items-center gap-1.5 hover:bg-blue-700 transition-colors"
      >
        Search another car
      </button>
    </>
  );

  if (state.status === "no-negotiation") {
    return (
      <AppShell headerRight={headerRight}>
        <div className="bg-white border border-slate-200 rounded-xl mt-2">
          <EmptyState
            icon={<MessageSquare size={28} />}
            title="No negotiation completed yet."
            body="Complete a deal evaluation and then negotiate with the AI coach. Your final deal summary will appear here."
            cta="Start negotiation"
            onCta={() => router.push("/dashboard/negotiation")}
          />
        </div>
      </AppShell>
    );
  }

  if (state.status === "loading") {
    return (
      <AppShell headerRight={headerRight}>
        <div className="flex items-center justify-center min-h-[400px]">
          <Loader2 size={28} className="text-blue-600 animate-spin" />
        </div>
      </AppShell>
    );
  }

  if (state.status === "error") {
    return (
      <AppShell headerRight={headerRight}>
        <div className="bg-white border border-red-200 rounded-xl p-6 text-center">
          <div className="font-semibold text-red-700">{state.message}</div>
        </div>
      </AppShell>
    );
  }

  const session = state.session;
  const finalPrice = negotiation?.finalPrice ?? vehicle?.price ?? 0;
  const askingPrice = negotiation?.initialAskingPrice ?? vehicle?.price ?? 0;
  const totalSavings = askingPrice - finalPrice;
  const dealScore = evaluation?.overallScore ?? 0;

  // Build negotiation arc from messages
  const agentMessages = session.messages.filter((m: NegotiationMessage) => m.role === "agent");
  const userMessages = session.messages.filter((m: NegotiationMessage) => m.role === "user");

  return (
    <AppShell headerRight={headerRight}>
      {/* Hero */}
      <div className="bg-white border border-slate-200 rounded-2xl p-8 overflow-hidden relative">
        <div className="grid grid-cols-[1fr_auto] gap-6 items-start">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-green-100 text-green-800 text-[12px] font-semibold">
              <Check size={12} /> Negotiation complete
            </div>
            <h1 className="mt-4 text-[32px] font-bold text-navy-900 tracking-tight leading-tight">
              {vehicle ? `${vehicle.year} ${vehicle.make} ${vehicle.model}${vehicle.trim ? ` ${vehicle.trim}` : ""}` : "Your deal is done."}
            </h1>
            <p className="mt-2 text-[15px] leading-relaxed text-slate-600 max-w-[520px]">
              {session.current_round} round{session.current_round !== 1 ? "s" : ""} of negotiation completed.
            </p>
            <div className="flex gap-8 mt-6">
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Final price</div>
                <div className="text-[36px] font-bold text-navy-900 tabular-nums mt-2 tracking-tight">
                  ${finalPrice.toLocaleString()}
                </div>
                {askingPrice > 0 && (
                  <div className="text-[13px] font-medium text-slate-500 tabular-nums mt-1.5">
                    was ${askingPrice.toLocaleString()} asking
                  </div>
                )}
              </div>
              {totalSavings > 0 && (
                <div>
                  <div className="text-[11px] font-semibold uppercase tracking-wider text-green-700">You saved</div>
                  <div className="text-[36px] font-bold text-green-600 tabular-nums mt-2 tracking-tight">
                    +${totalSavings.toLocaleString()}
                  </div>
                  <div className="text-[13px] font-medium text-green-700 mt-1.5">
                    {Math.round((totalSavings / askingPrice) * 100)}% below asking
                  </div>
                </div>
              )}
            </div>
          </div>
          {dealScore > 0 && <ScoreGauge score={dealScore} size={180} />}
        </div>
      </div>

      {/* Conversation summary */}
      {session.messages.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl p-6 mt-5">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Negotiation recap</div>
          <h3 className="text-[18px] font-semibold text-navy-900 mt-1.5">
            {session.current_round} round{session.current_round !== 1 ? "s" : ""} · {userMessages.length} messages from you · {agentMessages.length} from Genie
          </h3>
          <div className="mt-4 flex flex-col gap-2.5 max-h-[280px] overflow-y-auto">
            {session.messages.slice(0, 10).map((m: NegotiationMessage) => (
              <div
                key={m.id}
                className={`p-3 rounded-xl text-[13px] leading-relaxed ${
                  m.role === "user"
                    ? "bg-blue-600 text-white self-end ml-8"
                    : "bg-slate-50 text-slate-700 border border-slate-200 mr-8"
                }`}
              >
                {m.role === "agent" && (
                  <div className="text-[10px] font-semibold text-blue-600 uppercase tracking-wider mb-1">Genie</div>
                )}
                {m.content.slice(0, 200)}{m.content.length > 200 ? "…" : ""}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Deal details */}
      <div className="grid grid-cols-2 gap-4 mt-5">
        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Vehicle</div>
          <div className="mt-2.5">
            <div className="text-[18px] font-bold text-navy-900">
              {vehicle ? `${vehicle.year} ${vehicle.make} ${vehicle.model}` : "—"}
            </div>
            <div className="text-[13px] text-slate-500 mt-0.5">
              {vehicle?.mileage?.toLocaleString()} mi{vehicle?.location ? ` · ${vehicle.location}` : ""}
            </div>
          </div>
          {dealScore > 0 && (
            <div className="mt-4 p-4 bg-slate-50 rounded-xl">
              <BreakdownRow label="AI deal score" value={`${dealScore.toFixed(1)}/10`} />
              <BreakdownRow label="Asking price" value={`$${askingPrice.toLocaleString()}`} />
              <BreakdownRow label="Final price" value={`$${finalPrice.toLocaleString()}`} bold />
              {totalSavings > 0 && (
                <>
                  <div className="h-px bg-slate-200 my-3" />
                  <BreakdownRow label="Total savings" value={`+$${totalSavings.toLocaleString()}`} big />
                </>
              )}
            </div>
          )}
        </div>

        <div className="bg-white border border-slate-200 rounded-xl p-6">
          <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Next steps</div>
          <ul className="mt-4 flex flex-col gap-3">
            {[
              "Arrange a pre-purchase inspection",
              "Confirm financing with your chosen lender",
              "Review title, registration, and fee breakdown",
              "Get insurance coverage before taking delivery",
            ].map((step, i) => (
              <li key={i} className="flex items-start gap-2.5 text-[14px] text-slate-700">
                <div className="w-5 h-5 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-[11px] font-bold shrink-0 mt-0.5">
                  {i + 1}
                </div>
                {step}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* CTAs */}
      <div className="flex justify-end gap-2.5 mt-6">
        <button
          onClick={() => router.push("/dashboard/search")}
          className="h-10 px-5 rounded-lg bg-blue-600 text-white text-sm font-semibold flex items-center gap-2 hover:bg-blue-700 transition-colors"
        >
          Search another car <ArrowRight size={14} />
        </button>
      </div>
    </AppShell>
  );
}

function BreakdownRow({ label, value, bold, big }: { label: string; value: string; bold?: boolean; big?: boolean }) {
  return (
    <div className="flex justify-between items-center py-1">
      <span className="text-[13px] text-slate-600">{label}</span>
      <span className={`tabular-nums ${big ? "text-[18px] font-bold text-blue-700" : bold ? "text-[14px] font-bold text-navy-900" : "text-[14px] font-semibold text-navy-900"}`}>
        {value}
      </span>
    </div>
  );
}
