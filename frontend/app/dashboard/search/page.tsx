"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, AlertTriangle, Sparkles } from "lucide-react";
import { AppShell } from "@/components/layout/AppShell";

interface SearchForm {
  make: string;
  model: string;
  yearMin: string;
  yearMax: string;
  maxMileage: string;
  condition: string;
  maxPrice: string;
  paymentMethod: "cash" | "financing";
  creditScore: string;
  downPayment: string;
  loanTerm: string;
}

export default function SearchPage() {
  const router = useRouter();
  const [form, setForm] = useState<SearchForm>({
    make: "",
    model: "",
    yearMin: "2018",
    yearMax: "2024",
    maxMileage: "",
    condition: "",
    maxPrice: "",
    paymentMethod: "financing",
    creditScore: "good",
    downPayment: "",
    loanTerm: "60",
  });
  const [priceError, setPriceError] = useState(false);

  function set<K extends keyof SearchForm>(key: K, value: SearchForm[K]) {
    setForm((f) => ({ ...f, [key]: value }));
    if (key === "maxPrice" && value) setPriceError(false);
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!form.maxPrice.trim()) {
      setPriceError(true);
      return;
    }

    const params = new URLSearchParams();
    if (form.make) params.set("make", form.make);
    if (form.model) params.set("model", form.model);
    if (form.yearMin) params.set("yearMin", form.yearMin);
    if (form.yearMax) params.set("yearMax", form.yearMax);
    if (form.maxMileage) params.set("maxMileage", form.maxMileage.replace(/,/g, ""));
    if (form.condition) params.set("condition", form.condition);
    params.set("maxPrice", form.maxPrice.replace(/[$,]/g, ""));
    params.set("paymentMethod", form.paymentMethod);
    if (form.paymentMethod === "financing") {
      params.set("creditScore", form.creditScore);
      if (form.downPayment) params.set("downPayment", form.downPayment.replace(/[$,]/g, ""));
      params.set("loanTerm", form.loanTerm);
    }

    router.push(`/dashboard/results?${params.toString()}`);
  }

  return (
    <AppShell>
      <div className="max-w-[760px] mx-auto">
        {/* Header */}
        <div className="mb-7">
          <h1 className="text-[28px] font-bold text-navy-900 tracking-tight">
            What kind of car are you looking for?
          </h1>
          <p className="mt-2 text-[15px] leading-relaxed text-slate-500">
            We&apos;ll score every matching listing and surface the best deals first. You can refine later.
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="bg-white border border-slate-200 rounded-xl p-7">
            {/* Vehicle section */}
            <div className="text-[11px] font-semibold uppercase tracking-widest text-slate-500">Vehicle</div>
            <div className="grid grid-cols-2 gap-3.5 mt-3">
              <Field label="Make">
                <select
                  className={selectCls}
                  value={form.make}
                  onChange={(e) => set("make", e.target.value)}
                >
                  <option value="">Any make</option>
                  <option value="Honda">Honda</option>
                  <option value="Toyota">Toyota</option>
                  <option value="Mazda">Mazda</option>
                  <option value="Subaru">Subaru</option>
                  <option value="Hyundai">Hyundai</option>
                  <option value="Ford">Ford</option>
                  <option value="Chevrolet">Chevrolet</option>
                  <option value="BMW">BMW</option>
                  <option value="Mercedes-Benz">Mercedes-Benz</option>
                  <option value="Volkswagen">Volkswagen</option>
                  <option value="Kia">Kia</option>
                  <option value="Nissan">Nissan</option>
                </select>
              </Field>
              <Field label="Model">
                <input
                  className={inputCls}
                  placeholder="e.g. Civic, Corolla"
                  value={form.model}
                  onChange={(e) => set("model", e.target.value)}
                />
              </Field>
              <Field label="Year (min)">
                <select
                  className={selectCls}
                  value={form.yearMin}
                  onChange={(e) => set("yearMin", e.target.value)}
                >
                  {[2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022].map((y) => (
                    <option key={y} value={y}>{y}</option>
                  ))}
                </select>
              </Field>
              <Field label="Year (max)">
                <select
                  className={selectCls}
                  value={form.yearMax}
                  onChange={(e) => set("yearMax", e.target.value)}
                >
                  {[2024, 2023, 2022, 2021, 2020, 2019].map((y) => (
                    <option key={y} value={y}>{y}</option>
                  ))}
                </select>
              </Field>
              <Field label="Max mileage">
                <input
                  className={inputCls}
                  placeholder="e.g. 60,000"
                  value={form.maxMileage}
                  onChange={(e) => set("maxMileage", e.target.value)}
                />
              </Field>
              <Field label="Condition">
                <select
                  className={selectCls}
                  value={form.condition}
                  onChange={(e) => set("condition", e.target.value)}
                >
                  <option value="">Any</option>
                  <option value="Excellent">Excellent</option>
                  <option value="Good">Good</option>
                  <option value="Fair">Fair</option>
                </select>
              </Field>
            </div>

            {/* Budget section */}
            <div className="text-[11px] font-semibold uppercase tracking-widest text-slate-500 mt-7">Budget</div>
            <div className="grid grid-cols-2 gap-3.5 mt-3">
              <Field label="Max price">
                <input
                  className={`${inputCls} ${priceError ? "border-red-600 focus:ring-red-600/20 focus:border-red-600" : ""}`}
                  placeholder="$22,000"
                  value={form.maxPrice}
                  onChange={(e) => set("maxPrice", e.target.value)}
                />
                {priceError && (
                  <div className="flex items-center gap-1.5 text-xs text-red-600 font-medium mt-1">
                    <AlertTriangle size={12} /> Enter a max price to continue.
                  </div>
                )}
              </Field>
              <Field label="Payment method">
                <div className="flex gap-2">
                  <PillButton
                    active={form.paymentMethod === "cash"}
                    onClick={() => set("paymentMethod", "cash")}
                  >
                    Cash
                  </PillButton>
                  <PillButton
                    active={form.paymentMethod === "financing"}
                    onClick={() => set("paymentMethod", "financing")}
                  >
                    Financing
                  </PillButton>
                </div>
              </Field>
            </div>

            {/* Financing section */}
            {form.paymentMethod === "financing" && (
              <>
                <div className="text-[11px] font-semibold uppercase tracking-widest text-slate-500 mt-7">Financing</div>
                <div className="grid grid-cols-3 gap-3.5 mt-3">
                  <Field label="Credit score">
                    <select
                      className={selectCls}
                      value={form.creditScore}
                      onChange={(e) => set("creditScore", e.target.value)}
                    >
                      <option value="excellent">Excellent (740+)</option>
                      <option value="good">Good (670–739)</option>
                      <option value="fair">Fair (580–669)</option>
                    </select>
                  </Field>
                  <Field label="Down payment">
                    <input
                      className={inputCls}
                      placeholder="$3,500"
                      value={form.downPayment}
                      onChange={(e) => set("downPayment", e.target.value)}
                    />
                  </Field>
                  <Field label="Preferred term">
                    <select
                      className={selectCls}
                      value={form.loanTerm}
                      onChange={(e) => set("loanTerm", e.target.value)}
                    >
                      <option value="48">48 months</option>
                      <option value="60">60 months</option>
                      <option value="72">72 months</option>
                    </select>
                  </Field>
                </div>
              </>
            )}

            {/* Actions */}
            <div className="mt-8 pt-5 border-t border-slate-200 flex justify-end">
              <button
                type="submit"
                className="h-[46px] px-6 rounded-lg bg-blue-600 text-white font-semibold text-[15px] hover:bg-blue-700 transition-colors flex items-center gap-2"
              >
                Find my car <ArrowRight size={16} />
              </button>
            </div>
          </div>
        </form>

        {/* Tip */}
        <div className="mt-5 p-4 bg-blue-50 rounded-xl flex gap-3 items-start">
          <Sparkles size={18} className="text-blue-700 mt-0.5 shrink-0" />
          <div className="text-[13px] leading-relaxed text-slate-700">
            <strong className="text-blue-700">Tip:</strong> the broader your search, the more comparisons we can run. You can save a search and return any time.
          </div>
        </div>
      </div>
    </AppShell>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-[13px] font-medium text-navy-900">{label}</label>
      {children}
    </div>
  );
}

function PillButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex-1 h-10 rounded-lg border text-[13px] font-semibold transition-all ${
        active
          ? "border-blue-600 bg-blue-50 text-blue-700"
          : "border-slate-300 bg-white text-slate-600 hover:bg-slate-50"
      }`}
    >
      {children}
    </button>
  );
}

const inputCls =
  "h-10 px-3 border border-slate-300 rounded-lg text-sm text-navy-900 bg-white placeholder:text-slate-400 w-full focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20 transition-all";

const selectCls =
  "h-10 px-3 pr-8 border border-slate-300 rounded-lg text-sm text-navy-900 bg-white w-full focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20 transition-all appearance-none";
