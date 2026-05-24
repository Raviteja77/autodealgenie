"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Gauge, AlertTriangle } from "lucide-react";
import { useAuth } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email, password);
      router.push("/dashboard/search");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "The email or password is incorrect."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="w-full max-w-[440px]">
      <div
        className="bg-white rounded-2xl p-8"
        style={{ boxShadow: "0 24px 64px -16px rgba(15,22,41,0.18)" }}
      >
        <div className="w-9 h-9 rounded-lg bg-navy-900 flex items-center justify-center mb-4">
          <Gauge size={16} className="text-blue-400" />
        </div>
        <h1 className="text-[24px] font-bold text-navy-900 tracking-tight">Welcome back.</h1>
        <p className="mt-1.5 text-sm text-slate-500 leading-relaxed">
          Sign in to keep evaluating deals and continue negotiations.
        </p>

        {error && (
          <div className="mt-5 p-3 bg-red-50 border border-red-100 rounded-lg flex items-center gap-2 text-red-700 text-sm font-medium">
            <AlertTriangle size={16} />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-5 flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-[13px] font-medium text-navy-900">Email</label>
            <input
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="h-11 px-3.5 border border-slate-300 rounded-lg text-sm text-navy-900 bg-white placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20 transition-all"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label className="text-[13px] font-medium text-navy-900 flex justify-between">
              <span>Password</span>
              <Link href="/auth/forgot-password" className="text-blue-700 font-medium hover:opacity-80">
                Forgot password?
              </Link>
            </label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className={`h-11 px-3.5 border rounded-lg text-sm text-navy-900 bg-white placeholder:text-slate-400 focus:outline-none transition-all ${
                error
                  ? "border-red-600 focus:ring-2 focus:ring-red-600/20"
                  : "border-slate-300 focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20"
              }`}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-2.5 h-[52px] rounded-lg bg-blue-600 text-white font-semibold text-[15px] hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Signing in…" : "Sign in"}
          </button>
        </form>

        <div className="mt-5 pt-5 border-t border-slate-200 text-center text-sm text-slate-600">
          Don&apos;t have an account?{" "}
          <Link href="/auth/signup" className="text-blue-700 font-semibold hover:opacity-80">
            Sign up
          </Link>
        </div>
      </div>
    </div>
  );
}
