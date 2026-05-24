"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Sparkles, Check, Send, ChevronDown, Loader2, Gauge } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";
import { EmptyState } from "@/components/ui/EmptyState";
import { apiClient, type NegotiationMessage } from "@/lib/api";
import { flowState } from "@/lib/flowState";

type ChatMsg = { id: number; from: "ai" | "user"; text: string; points?: string[] };

type PageState =
  | { status: "no-evaluation" }
  | { status: "creating" }
  | { status: "active"; sessionId: number; round: number; maxRounds: number }
  | { status: "completed"; sessionId: number }
  | { status: "error"; message: string };

export default function NegotiationPage() {
  const router = useRouter();
  const vehicle = flowState.getVehicle();
  const evaluation = flowState.getEvaluation();

  const askingPrice = vehicle?.price ?? 0;
  const [state, setState] = useState<PageState>({ status: "no-evaluation" });
  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [currentOffer, setCurrentOffer] = useState(0);
  const [savings, setSavings] = useState(0);
  const [suggestedNext, setSuggestedNext] = useState(0);
  const bottomRef = useRef<HTMLDivElement>(null);

  const appendMsg = useCallback((msg: ChatMsg) => {
    setMessages((prev) => [...prev, msg]);
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    if (!vehicle || !evaluation) {
      setState({ status: "no-evaluation" });
      return;
    }

    const cached = flowState.getNegotiation();
    if (cached) {
      setState({ status: "active", sessionId: cached.sessionId, round: 1, maxRounds: 5 });
      setCurrentOffer(cached.initialAskingPrice);
      setSavings(cached.savings ?? 0);
      // Reload messages from session
      apiClient.getNegotiationSession(cached.sessionId).then((session) => {
        const mapped: ChatMsg[] = session.messages.map((m: NegotiationMessage) => ({
          id: m.id,
          from: m.role === "user" ? "user" : "ai",
          text: m.content,
        }));
        setMessages(mapped);
        const s = session.status === "completed" ? "completed" : "active";
        setState(s === "completed"
          ? { status: "completed", sessionId: cached.sessionId }
          : { status: "active", sessionId: cached.sessionId, round: session.current_round, maxRounds: session.max_rounds });
      }).catch(() => { /* use cached state */ });
      return;
    }

    // Create new session
    setState({ status: "creating" });
    const targetPrice = Math.round(askingPrice * 0.93);

    apiClient.createNegotiation({
      deal_id: evaluation.dealId,
      user_target_price: targetPrice,
      strategy: "collaborative",
    }).then((resp) => {
      flowState.setNegotiation({
        sessionId: resp.session_id,
        dealId: evaluation.dealId,
        initialAskingPrice: askingPrice,
        savings: 0,
      });
      setCurrentOffer(askingPrice);
      setSuggestedNext(targetPrice);
      setState({ status: "active", sessionId: resp.session_id, round: resp.current_round, maxRounds: 5 });
      appendMsg({ id: Date.now(), from: "ai", text: resp.agent_message });
    }).catch((err) => {
      setState({ status: "error", message: err instanceof Error ? err.message : "Failed to start negotiation." });
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function sendChat() {
    if (!input.trim() || sending || state.status !== "active") return;
    const text = input.trim();
    setInput("");
    setSending(true);
    appendMsg({ id: Date.now(), from: "user", text });

    try {
      const resp = await apiClient.sendChatMessage(state.sessionId, { message: text });
      appendMsg({ id: Date.now() + 1, from: "ai", text: resp.agent_message.content });
    } catch {
      appendMsg({ id: Date.now() + 1, from: "ai", text: "Sorry, something went wrong. Please try again." });
    } finally {
      setSending(false);
    }
  }

  async function counter(offerAmount: number) {
    if (sending || state.status !== "active") return;
    setSending(true);
    appendMsg({ id: Date.now(), from: "user", text: `Counter offer: $${offerAmount.toLocaleString()}` });

    try {
      const resp = await apiClient.processNextRound(state.sessionId, {
        user_action: "counter",
        counter_offer: offerAmount,
      });

      setCurrentOffer(offerAmount);
      const saved = askingPrice - offerAmount;
      setSavings(saved > 0 ? saved : 0);
      if (resp.metadata.suggested_price) setSuggestedNext(resp.metadata.suggested_price);
      setState({ status: resp.status === "completed" ? "completed" : "active", sessionId: state.sessionId, round: resp.current_round, maxRounds: 5 });
      appendMsg({ id: Date.now() + 1, from: "ai", text: resp.agent_message });
    } catch {
      appendMsg({ id: Date.now() + 1, from: "ai", text: "Counter offer failed. Please try again." });
    } finally {
      setSending(false);
    }
  }

  async function accept() {
    if (sending || state.status !== "active") return;
    setSending(true);
    try {
      const resp = await apiClient.processNextRound(state.sessionId, { user_action: "confirm" });
      const saved = askingPrice - currentOffer;
      const neg = flowState.getNegotiation();
      if (neg) {
        flowState.setNegotiation({ ...neg, finalPrice: currentOffer, savings: saved > 0 ? saved : 0 });
      }
      setSavings(saved > 0 ? saved : 0);
      appendMsg({ id: Date.now(), from: "ai", text: resp.agent_message });
      setState({ status: "completed", sessionId: state.sessionId });
    } catch {
      appendMsg({ id: Date.now(), from: "ai", text: "Failed to confirm. Please try again." });
    } finally {
      setSending(false);
    }
  }

  if (state.status === "no-evaluation") {
    return (
      <AppShell>
        <div className="bg-white border border-slate-200 rounded-xl mt-2">
          <EmptyState
            icon={<Gauge size={28} />}
            title="No evaluation completed yet."
            body="Run an AI evaluation on a vehicle first. We need the deal score and analysis to start an effective negotiation."
            cta="Go to evaluation"
            onCta={() => router.push("/dashboard/evaluation")}
          />
        </div>
      </AppShell>
    );
  }

  if (state.status === "creating") {
    return (
      <AppShell>
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
          <Loader2 size={32} className="text-blue-600 animate-spin" />
          <div className="text-[15px] font-medium text-slate-600">Setting up your AI negotiation coach…</div>
        </div>
      </AppShell>
    );
  }

  if (state.status === "error") {
    return (
      <AppShell>
        <div className="bg-white border border-red-200 rounded-xl p-6 text-center">
          <div className="font-semibold text-red-700">{state.message}</div>
          <button onClick={() => router.push("/dashboard/evaluation")} className="mt-4 text-sm font-semibold text-blue-700">
            Back to evaluation
          </button>
        </div>
      </AppShell>
    );
  }

  const isCompleted = state.status === "completed";
  const round = state.status === "active" || state.status === "completed" ? (state as { round: number }).round : 0;
  const maxRounds = state.status === "active" || state.status === "completed" ? (state as { maxRounds: number }).maxRounds : 5;

  const headerRight = (
    <>
      <div className="flex items-center gap-1.5 text-[13px] font-medium text-slate-600">
        <span className={`w-2 h-2 rounded-full ${isCompleted ? "bg-slate-400" : "bg-green-500"}`} />
        {isCompleted ? "Deal closed" : "Active · AI coach ready"}
      </div>
      {isCompleted ? (
        <button
          onClick={() => router.push("/dashboard/summary")}
          className="h-8 px-3.5 rounded-lg bg-blue-600 text-white text-sm font-semibold flex items-center gap-1.5 hover:bg-blue-700 transition-colors"
        >
          View summary <Check size={14} />
        </button>
      ) : (
        <button
          onClick={accept}
          disabled={sending}
          className="h-8 px-3.5 rounded-lg bg-green-600 text-white text-sm font-semibold flex items-center gap-1.5 hover:bg-green-700 disabled:opacity-60 transition-colors"
        >
          <Check size={14} /> Close deal at ${currentOffer.toLocaleString()}
        </button>
      )}
    </>
  );

  return (
    <AppShell headerRight={headerRight}>
      <div className="grid grid-cols-[320px_1fr] gap-5" style={{ height: "calc(100vh - 60px - 48px)" }}>
        {/* Sidebar */}
        <aside className="flex flex-col gap-4 overflow-auto">
          <div className="bg-white border border-slate-200 rounded-2xl p-4">
            <div className="flex items-center gap-3">
              <div className="w-14 h-10 rounded-md bg-slate-100 flex items-center justify-center shrink-0">
                <VehicleIcon />
              </div>
              <div className="flex-1 min-w-0">
                <div className="text-[13px] font-semibold text-navy-900 truncate">
                  {vehicle?.year} {vehicle?.make} {vehicle?.model}
                </div>
                <div className="text-[12px] text-slate-500 mt-0.5 tabular-nums">{vehicle?.mileage?.toLocaleString()} mi</div>
              </div>
            </div>
            <div className="flex justify-between mt-3.5 pt-3.5 border-t border-slate-200">
              <div>
                <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">Round</div>
                <div className="text-[22px] font-bold text-navy-900 tabular-nums mt-1">
                  {round}<span className="text-slate-400 text-sm">/{maxRounds}</span>
                </div>
              </div>
              <div className="text-right">
                <div className="text-[11px] font-semibold uppercase tracking-wider text-green-700">Saved</div>
                <div className="text-[22px] font-bold text-green-600 tabular-nums mt-1">+${savings.toLocaleString()}</div>
              </div>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-4">
            <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 mb-3">Position</div>
            <PriceRow label="Asking price" value={`$${askingPrice.toLocaleString()}`} tone="muted" />
            <PriceRow label="Your current offer" value={`$${currentOffer.toLocaleString()}`} tone="brand" />
            {suggestedNext > 0 && suggestedNext !== currentOffer && (
              <PriceRow label="AI suggested next" value={`$${suggestedNext.toLocaleString()}`} tone="ai" />
            )}
            {evaluation && (
              <PriceRow label="Deal score" value={`${evaluation.overallScore.toFixed(1)}/10`} tone="muted" />
            )}
          </div>

          <div className="bg-blue-50 border border-blue-100 rounded-xl p-3.5">
            <div className="flex gap-2.5">
              <Sparkles size={16} className="text-blue-700 shrink-0 mt-0.5" />
              <div className="text-[12px] leading-relaxed text-slate-700">
                <strong className="text-blue-700">Coach tip:</strong>{" "}
                {savings === 0
                  ? "Start with a reasonable counter below asking. Dealers expect 2–3 rounds."
                  : `You've saved $${savings.toLocaleString()} so far. Keep negotiating or close at the current price.`}
              </div>
            </div>
          </div>
        </aside>

        {/* Chat */}
        <div className="bg-white border border-slate-200 rounded-2xl flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-3.5">
            {messages.length === 0 && (
              <div className="flex items-center justify-center h-full text-slate-400 text-sm">
                No messages yet.
              </div>
            )}
            {messages.map((m) =>
              m.from === "ai" ? <AIBubble key={m.id} {...m} /> : <UserBubble key={m.id} text={m.text} />
            )}
            {sending && (
              <div className="flex gap-2.5 items-center text-slate-400 text-sm">
                <Loader2 size={14} className="animate-spin" /> Genie is thinking…
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {!isCompleted && (
            <>
              <div className="px-4 py-2.5 border-t border-slate-200 flex gap-2 flex-wrap">
                <button
                  onClick={accept}
                  disabled={sending}
                  className="h-8 px-3 rounded-lg bg-green-600 text-white text-[13px] font-semibold flex items-center gap-1.5 hover:bg-green-700 disabled:opacity-60 transition-colors"
                >
                  <Check size={13} /> Accept at ${currentOffer.toLocaleString()}
                </button>
                {suggestedNext > 0 && suggestedNext !== currentOffer && (
                  <button
                    onClick={() => counter(suggestedNext)}
                    disabled={sending}
                    className="h-8 px-3 rounded-lg border border-slate-300 bg-white text-navy-900 text-[13px] font-semibold hover:bg-slate-50 disabled:opacity-60 transition-colors"
                  >
                    Counter at ${suggestedNext.toLocaleString()}
                  </button>
                )}
                <div className="ml-auto text-[12px] text-slate-500 flex items-center">
                  Powered by Genie
                </div>
              </div>

              <div className="p-3 border-t border-slate-200 bg-white flex gap-2.5">
                <input
                  className="flex-1 h-10 px-3.5 border border-slate-300 rounded-lg text-sm text-navy-900 placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20 transition-all"
                  placeholder="Type a message or ask Genie for advice…"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && sendChat()}
                  disabled={sending}
                />
                <button
                  onClick={sendChat}
                  disabled={sending || !input.trim()}
                  className="w-10 h-10 rounded-lg bg-blue-600 text-white flex items-center justify-center hover:bg-blue-700 disabled:opacity-60 transition-colors shrink-0"
                >
                  <Send size={16} />
                </button>
              </div>
            </>
          )}

          {isCompleted && (
            <div className="p-5 border-t border-slate-200 bg-green-50 text-center">
              <div className="text-[15px] font-semibold text-green-800">Deal closed!</div>
              <div className="text-sm text-green-700 mt-1">Final price: ${currentOffer.toLocaleString()} · Saved: ${savings.toLocaleString()}</div>
              <button onClick={() => router.push("/dashboard/summary")} className="mt-3 h-9 px-5 rounded-lg bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition-colors">
                View deal summary
              </button>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}

function PriceRow({ label, value, tone }: { label: string; value: string; tone: "muted" | "brand" | "ai" }) {
  const colorMap = { muted: "text-slate-700", brand: "font-bold text-navy-900", ai: "text-blue-700" };
  return (
    <div className="flex justify-between items-center py-1.5">
      <span className="text-[13px] text-slate-500">{label}</span>
      <span className={`text-[14px] font-semibold tabular-nums ${colorMap[tone]}`}>{value}</span>
    </div>
  );
}

function AIBubble({ text, points }: ChatMsg) {
  const [open, setOpen] = useState(false);
  return (
    <div className="flex gap-2.5 items-start max-w-[78%]">
      <div className="w-8 h-8 rounded-lg bg-navy-900 flex items-center justify-center shrink-0">
        <Sparkles size={15} className="text-blue-300" />
      </div>
      <div className="bg-blue-50 border border-blue-100 rounded-xl rounded-tl-sm px-3.5 py-3">
        <div className="text-[10px] font-semibold text-blue-700 uppercase tracking-wider mb-1.5">Genie · AI coach</div>
        <div className="text-[14px] leading-relaxed text-navy-900">{text}</div>
        {points && points.length > 0 && (
          <>
            <button onClick={() => setOpen((o) => !o)} className="mt-2 flex items-center gap-1 text-[12px] font-semibold text-blue-700 hover:opacity-80">
              {open ? "Hide reasoning" : "See reasoning"}
              <ChevronDown size={12} className="transition-transform duration-200" style={{ transform: open ? "rotate(180deg)" : "" }} />
            </button>
            {open && (
              <div className="mt-2 p-2.5 bg-white rounded-lg border border-blue-100">
                <ul className="flex flex-col gap-1">
                  {points.map((p, i) => (
                    <li key={i} className="flex gap-1.5 text-[13px] leading-relaxed text-slate-700">
                      <span className="text-slate-400">•</span>{p}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

function UserBubble({ text }: { text: string }) {
  return (
    <div className="flex justify-end">
      <div className="bg-blue-600 text-white rounded-xl rounded-tr-sm px-3.5 py-2.5 max-w-[70%] text-[14px] leading-relaxed">
        {text}
      </div>
    </div>
  );
}

function VehicleIcon() {
  return (
    <svg width="40" height="20" viewBox="0 0 40 20" fill="none" className="text-slate-300">
      <rect x="2" y="6" width="36" height="11" rx="2" fill="currentColor" opacity="0.5" />
      <rect x="8" y="2" width="24" height="9" rx="2" fill="currentColor" opacity="0.35" />
      <circle cx="10" cy="17" r="3.5" fill="currentColor" opacity="0.6" />
      <circle cx="30" cy="17" r="3.5" fill="currentColor" opacity="0.6" />
    </svg>
  );
}
