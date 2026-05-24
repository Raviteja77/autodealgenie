"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Gauge, AlertTriangle } from "lucide-react";
import { useAuth } from "@/lib/auth";

export default function SignupPage() {
  const router = useRouter();
  const { signup } = useAuth();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    setLoading(true);

    try {
      await signup(email, username, password);
      router.push("/dashboard/search");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Sign up failed. Please try again."
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
        <h1 className="text-[24px] font-bold text-navy-900 tracking-tight">Create your account.</h1>
        <p className="mt-1.5 text-sm text-slate-500 leading-relaxed">
          It takes 30 seconds and you&apos;ll start scoring deals immediately.
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
            <label className="text-[13px] font-medium text-navy-900">Username</label>
            <input
              type="text"
              placeholder="johndoe"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              minLength={3}
              className="h-11 px-3.5 border border-slate-300 rounded-lg text-sm text-navy-900 bg-white placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20 transition-all"
            />
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-[13px] font-medium text-navy-900">Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              className="h-11 px-3.5 border border-slate-300 rounded-lg text-sm text-navy-900 bg-white placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20 transition-all"
            />
            <p className="text-[11px] text-slate-400">Min 8 chars, must include uppercase, lowercase, and a number.</p>
          </div>
          <div className="flex flex-col gap-1.5">
            <label className="text-[13px] font-medium text-navy-900">Confirm password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="h-11 px-3.5 border border-slate-300 rounded-lg text-sm text-navy-900 bg-white placeholder:text-slate-400 focus:outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-600/20 transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="mt-2.5 h-[52px] rounded-lg bg-blue-600 text-white font-semibold text-[15px] hover:bg-blue-700 disabled:opacity-60 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <div className="mt-5 pt-5 border-t border-slate-200 text-center text-sm text-slate-600">
          Already have an account?{" "}
          <Link href="/auth/login" className="text-blue-700 font-semibold hover:opacity-80">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}
