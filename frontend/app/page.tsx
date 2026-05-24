import Link from "next/link";
import {
  Search,
  Gauge,
  MessageSquare,
  ArrowRight,
  Check,
  Sparkles,
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white font-sans">
      {/* Top Nav */}
      <header
        className="sticky top-0 z-50 border-b border-slate-200"
        style={{ background: "rgba(255,255,255,0.92)", backdropFilter: "blur(8px)" }}
      >
        <div className="max-w-[1200px] mx-auto px-6 flex items-center justify-between h-[68px]">
          <Link href="/" className="flex items-center gap-2.5">
            <div className="w-[34px] h-[34px] rounded-lg bg-navy-900 flex items-center justify-center">
              <Gauge size={18} className="text-blue-400" />
            </div>
            <span className="font-bold text-[18px] tracking-tight text-navy-900">AutoDealGenie</span>
          </Link>
          <nav className="hidden md:flex items-center gap-8">
            {[
              { label: "How it works", href: "#how" },
              { label: "Features", href: "#features" },
              { label: "Trust", href: "#trust" },
            ].map(({ label, href }) => (
              <a key={label} href={href} className="text-sm font-medium text-slate-700 hover:text-navy-900 transition-colors">
                {label}
              </a>
            ))}
          </nav>
          <div className="flex items-center gap-2.5">
            <Link
              href="/auth/login"
              className="h-9 px-3.5 rounded-lg text-sm font-semibold text-navy-900 hover:bg-slate-100 transition-colors flex items-center"
            >
              Sign in
            </Link>
            <Link
              href="/auth/signup"
              className="h-9 px-3.5 rounded-lg text-sm font-semibold bg-blue-600 text-white hover:bg-blue-700 transition-colors flex items-center"
            >
              Start free
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section
        className="relative overflow-hidden"
        style={{ background: "linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)" }}
      >
        <div className="max-w-[1200px] mx-auto px-6 py-[88px] grid grid-cols-1 md:grid-cols-2 gap-14 items-center">
          <div>
            <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 text-xs font-semibold uppercase tracking-wider px-3 py-1.5 rounded-full mb-5">
              <Sparkles size={14} />
              AI-powered buying assistant
            </div>
            <h1 className="text-[52px] font-bold leading-[1.05] tracking-tight text-navy-900 max-w-[540px]">
              Buy your next car with{" "}
              <span className="text-blue-600">confidence</span> — not pressure.
            </h1>
            <p className="mt-5 text-lg leading-relaxed text-slate-600 max-w-[500px]">
              AutoDealGenie evaluates every listing with a 1–10 deal score, then
              coaches you through the negotiation. No dealer tricks, no inflated
              quotes.
            </p>
            <div className="flex items-center gap-3 mt-8">
              <Link
                href="/dashboard/search"
                className="h-[52px] px-7 rounded-lg bg-blue-600 text-white font-semibold text-[15px] hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                Start car search <ArrowRight size={16} />
              </Link>
              <a
                href="#how"
                className="h-[52px] px-7 rounded-lg text-navy-900 font-semibold text-[15px] hover:bg-slate-100 transition-colors flex items-center"
              >
                See how it works
              </a>
            </div>
            <div className="flex items-center gap-6 mt-7 text-sm text-slate-500">
              {["Free to use", "No spam to your phone", "Cancel anytime"].map((t) => (
                <span key={t} className="flex items-center gap-1.5">
                  <Check size={14} className="text-green-600" /> {t}
                </span>
              ))}
            </div>
          </div>

          {/* Hero preview cards */}
          <div className="relative h-[440px] hidden md:block">
            {/* Back card — vehicle listing */}
            <div
              className="absolute top-6 right-0 w-[380px] bg-white rounded-2xl border border-slate-200 overflow-hidden"
              style={{ boxShadow: "0 24px 64px -16px rgba(15,22,41,0.18)" }}
            >
              <div className="h-40 bg-slate-100 relative">
                <div className="absolute inset-0 flex items-center justify-center text-slate-300">
                  <svg width="120" height="60" viewBox="0 0 120 60" fill="none">
                    <rect x="10" y="20" width="100" height="30" rx="6" fill="currentColor" opacity="0.4"/>
                    <rect x="25" y="10" width="70" height="24" rx="4" fill="currentColor" opacity="0.3"/>
                    <circle cx="30" cy="50" r="10" fill="currentColor" opacity="0.5"/>
                    <circle cx="90" cy="50" r="10" fill="currentColor" opacity="0.5"/>
                  </svg>
                </div>
                <div
                  className="absolute top-3 right-3 bg-white rounded-full flex items-center gap-2 pl-3 pr-1 py-1"
                  style={{ boxShadow: "0 4px 12px rgba(15,22,41,0.15)" }}
                >
                  <span className="text-[10px] font-semibold text-slate-600 uppercase tracking-wider">Deal</span>
                  <div className="w-[30px] h-[30px] rounded-full bg-green-500 text-white flex items-center justify-center font-bold text-[13px] tabular-nums">8.4</div>
                </div>
              </div>
              <div className="p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-semibold text-[16px] text-navy-900">2021 Honda Civic LX</div>
                    <div className="text-sm text-slate-500 mt-0.5 tabular-nums">47,000 mi · Sedan</div>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-[20px] text-navy-900 tabular-nums">$19,550</div>
                    <div className="text-[11px] font-medium text-green-600 mt-1">$650 under FMV</div>
                  </div>
                </div>
                <div className="mt-3 p-2.5 bg-blue-50 rounded-lg text-[13px] leading-relaxed text-slate-700">
                  <span className="font-semibold text-blue-700">Why this car?</span> Clean history, fair price for the year, financing in your range.
                </div>
              </div>
            </div>

            {/* Front card — AI coach */}
            <div
              className="absolute bottom-0 left-0 w-[300px] rounded-2xl p-5 text-white"
              style={{ background: "#0F1629", boxShadow: "0 20px 48px -12px rgba(15,22,41,0.4)" }}
            >
              <div className="flex items-center gap-2 text-blue-300 text-[11px] font-semibold uppercase tracking-wider">
                <Sparkles size={14} /> Genie · live coach
              </div>
              <div className="mt-2.5 text-[15px] font-medium leading-relaxed">
                Counter at <span className="text-blue-300">$18,400</span>. Comps in your area sit $500 lower.
              </div>
              <div className="mt-3.5 pt-3 border-t border-white/10 flex justify-between">
                <div>
                  <div className="text-[11px] text-slate-400 uppercase tracking-wider">Savings</div>
                  <div className="font-bold text-[22px] text-green-400 tabular-nums mt-1">+$1,150</div>
                </div>
                <div>
                  <div className="text-[11px] text-slate-400 uppercase tracking-wider">Round</div>
                  <div className="font-bold text-[22px] text-white tabular-nums mt-1">3<span className="text-slate-500 text-sm">/5</span></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Social proof strip */}
      <section className="bg-navy-900 py-14">
        <div className="max-w-[1200px] mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { num: "$18.4M", label: "Saved by members in negotiation" },
            { num: "47,200", label: "Deals closed with a Genie score" },
            { num: "1.8M",   label: "Listings scored every day" },
            { num: "8.1/10", label: "Average deal score on accepted offers" },
          ].map((s, i) => (
            <div
              key={i}
              className={i > 0 ? "pl-6 border-l border-white/10" : ""}
            >
              <div className="text-[36px] font-bold text-white tabular-nums tracking-tight leading-tight">{s.num}</div>
              <div className="text-sm text-slate-400 mt-1.5">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Value props */}
      <section className="py-20" id="features">
        <div className="max-w-[1200px] mx-auto px-6">
          <div className="max-w-xl">
            <div className="text-xs font-semibold uppercase tracking-widest text-blue-700">What you get</div>
            <h2 className="mt-3 text-[40px] font-bold tracking-tight text-navy-900 leading-tight">
              Three tools that replace a dealer&apos;s playbook.
            </h2>
          </div>
          <div className="mt-10 grid md:grid-cols-3 gap-5">
            {[
              {
                icon: <Search size={22} />,
                title: "AI-ranked search",
                body: "Every listing is scored against fair market data the moment it appears. The best deals float to the top, automatically.",
                stat: "1.8M+ listings scanned daily",
              },
              {
                icon: <Gauge size={22} />,
                title: "Transparent deal scoring",
                body: "A 1–10 score with the reasoning shown: condition, price fairness, financing, risk. No mystery, no marketing fluff.",
                stat: "5-step evaluation",
              },
              {
                icon: <MessageSquare size={22} />,
                title: "Negotiation coach",
                body: "Practice with our AI, then take real counter-offers to the dealer. We tell you what to say and when to walk.",
                stat: "$2,840 avg member savings",
              },
            ].map((item, i) => (
              <div
                key={i}
                className="p-7 bg-white border border-slate-200 rounded-2xl flex flex-col gap-4"
              >
                <div className="w-11 h-11 rounded-xl bg-blue-50 text-blue-700 flex items-center justify-center">
                  {item.icon}
                </div>
                <div>
                  <h3 className="text-[20px] font-semibold text-navy-900">{item.title}</h3>
                  <p className="mt-2 text-[15px] leading-relaxed text-slate-600">{item.body}</p>
                </div>
                <div className="mt-auto pt-4 border-t border-slate-200 text-[13px] font-semibold text-navy-900 tabular-nums">
                  {item.stat}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-20 bg-slate-50" id="how">
        <div className="max-w-[1200px] mx-auto px-6">
          <div className="flex justify-between items-end mb-12 flex-wrap gap-6">
            <div className="max-w-xl">
              <div className="text-xs font-semibold uppercase tracking-widest text-blue-700">How it works</div>
              <h2 className="mt-3 text-[40px] font-bold tracking-tight text-navy-900 leading-tight">
                From &ldquo;I need a car&rdquo; to &ldquo;I bought a car&rdquo; in four steps.
              </h2>
            </div>
            <Link
              href="/dashboard/search"
              className="flex items-center gap-2 text-blue-700 text-sm font-semibold hover:opacity-80 transition-opacity"
            >
              See a sample deal <ArrowRight size={14} />
            </Link>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 relative">
            {[
              { n: "01", t: "Search",    d: "Tell us what you want. We rank listings by fair-market score in seconds." },
              { n: "02", t: "Evaluate",  d: "A 1–10 deal score with reasoning for condition, price, financing, and risk." },
              { n: "03", t: "Negotiate", d: "Our coach drafts counter-offers in real time. You stay in control." },
              { n: "04", t: "Save",      d: "Embedded lender and insurance matches close out the deal in one place." },
            ].map((s, i) => (
              <div key={i} className="relative">
                <div className="w-12 h-12 rounded-full bg-navy-900 text-white flex items-center justify-center text-sm font-bold relative z-10 border-4 border-slate-50">
                  {s.n}
                </div>
                <div className="mt-5">
                  <h3 className="text-[20px] font-semibold text-navy-900">{s.t}</h3>
                  <p className="mt-1.5 text-sm leading-relaxed text-slate-600 max-w-[240px]">{s.d}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Trust section */}
      <section className="py-20 bg-white" id="trust">
        <div className="max-w-[1200px] mx-auto px-6">
          <div className="text-center mb-12">
            <div className="text-xs font-semibold uppercase tracking-widest text-blue-700">Why trust us</div>
            <h2 className="mt-3 text-[40px] font-bold tracking-tight text-navy-900 leading-tight">
              Built for buyers, not dealerships.
            </h2>
            <p className="mt-4 text-[17px] text-slate-600 max-w-[540px] mx-auto leading-relaxed">
              We don&apos;t take commissions from dealers. Our AI scores every listing the same way
              regardless of who&apos;s selling it.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6 mb-14">
            {[
              {
                quote: "Saved $2,200 off a Civic that had been sitting on the lot for 3 weeks. The Genie told me exactly what to say.",
                name: "Marcus T.",
                location: "San Jose, CA",
                savings: "$2,200 saved",
              },
              {
                quote: "I was going to accept the dealer's first offer. Genie showed me it was $1,800 over fair market. Counter worked.",
                name: "Priya M.",
                location: "Austin, TX",
                savings: "$1,800 saved",
              },
              {
                quote: "The deal score on my Outback was 7.8. Everything matched up — clean history, fair price. Bought with zero regret.",
                name: "Jordan L.",
                location: "Seattle, WA",
                savings: "Deal score 7.8/10",
              },
            ].map((t, i) => (
              <div
                key={i}
                className="p-6 bg-slate-50 border border-slate-200 rounded-2xl flex flex-col gap-4"
              >
                <p className="text-[15px] leading-relaxed text-slate-700 flex-1">
                  &ldquo;{t.quote}&rdquo;
                </p>
                <div className="flex items-center justify-between pt-3 border-t border-slate-200">
                  <div>
                    <div className="text-[14px] font-semibold text-navy-900">{t.name}</div>
                    <div className="text-[12px] text-slate-500 mt-0.5">{t.location}</div>
                  </div>
                  <div className="text-[13px] font-semibold text-green-700 bg-green-50 px-2.5 py-1 rounded-full">
                    {t.savings}
                  </div>
                </div>
              </div>
            ))}
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 p-8 bg-slate-50 rounded-2xl border border-slate-200">
            {[
              { label: "No dealer kickbacks", desc: "We earn nothing from dealer relationships." },
              { label: "Data-backed scores", desc: "Fair market value from 1.8M daily listings." },
              { label: "Your data is private", desc: "We never sell your search history." },
              { label: "Free to use", desc: "No hidden fees. No credit card required." },
            ].map((item, i) => (
              <div key={i} className={i > 0 ? "pl-6 border-l border-slate-200" : ""}>
                <div className="text-[15px] font-semibold text-navy-900">{item.label}</div>
                <div className="text-[13px] text-slate-500 mt-1 leading-relaxed">{item.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-navy-900 text-white">
        <div className="max-w-[1200px] mx-auto px-6 py-16 border-b border-white/10 flex justify-between items-center flex-wrap gap-8">
          <div>
            <h2 className="text-[36px] font-bold tracking-tight leading-tight">Stop overpaying for cars.</h2>
            <p className="mt-2.5 text-base leading-relaxed text-slate-400 max-w-[480px]">
              Make your next car purchase the easy one. Free to start, no credit check, no spam.
            </p>
          </div>
          <Link
            href="/auth/signup"
            className="h-[52px] px-7 rounded-lg bg-white text-navy-900 font-semibold text-[15px] hover:bg-slate-100 transition-colors flex items-center gap-2"
          >
            Create an account <ArrowRight size={16} />
          </Link>
        </div>
        <div className="max-w-[1200px] mx-auto px-6 py-8 flex justify-between items-center flex-wrap gap-6">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-md bg-navy-700 flex items-center justify-center">
              <Gauge size={14} className="text-blue-400" />
            </div>
            <span className="font-semibold text-sm">AutoDealGenie</span>
            <span className="text-slate-500 text-[13px] ml-2">© 2026</span>
          </div>
          <div className="flex gap-7">
            {["Privacy", "Terms", "Lender disclosures", "Contact"].map((l) => (
              <a key={l} href="#" className="text-[13px] text-slate-400 hover:text-slate-300 transition-colors">
                {l}
              </a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}
