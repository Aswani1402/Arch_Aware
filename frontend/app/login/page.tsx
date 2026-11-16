"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Shield, User, Building2, Lock, ArrowLeft } from 'lucide-react';
import { useAuth } from '@/lib/authContext';
import { fetchApi } from '@/lib/api';
import { BRAND } from '@/lib/brandConfig';

export default function LoginPage() {
  const router = useRouter();
  const { login } = useAuth();
  const [email, setEmail] = useState("architect@studio.com");
  const [password, setPassword] = useState("password123");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await fetchApi<any>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      });
      login(res.access_token, res.user);
      router.push('/');
    } catch (err: any) {
      setError(err.message || "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const setRoleDemo = (roleEmail: string, rolePass: string) => {
    setEmail(roleEmail);
    setPassword(rolePass);
  };

  return (
    <div className="max-w-md mx-auto px-4 py-16 space-y-6">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-stone-600 hover:text-arch-terracotta transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Feed</span>
      </Link>

      <div className="bg-white rounded-3xl border border-arch-border p-8 shadow-sm">
        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-xl bg-arch-dark text-white font-serif font-bold text-2xl flex items-center justify-center mx-auto mb-3">
            {BRAND.logoLetter}
          </div>
          <h1 className="font-serif text-2xl font-bold text-arch-charcoal">
            {BRAND.name} Portal
          </h1>
          <p className="text-xs text-stone-500 mt-1">
            Access your architectural moodboards or manage verified vendor catalogs
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-xl">
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-4 text-xs">
          <div>
            <label className="block font-medium text-stone-700 mb-1">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
            />
          </div>

          <div>
            <label className="block font-medium text-stone-700 mb-1">Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-xl bg-arch-terracotta hover:bg-arch-terracotta-dark text-white font-semibold text-xs transition-colors shadow-md disabled:opacity-50"
          >
            {loading ? "Signing In..." : "Sign In"}
          </button>
        </form>

        {/* Demo Fast-Switch Buttons */}
        <div className="mt-6 pt-6 border-t border-arch-border text-center">
          <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block mb-2">
            Instant Demo Role Accounts
          </span>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => setRoleDemo("architect@studio.com", "password123")}
              className="p-2 rounded-lg bg-stone-50 hover:bg-stone-100 border border-stone-200 text-xs font-medium text-stone-700"
            >
              Architect
            </button>
            <button
              onClick={() => setRoleDemo("supplier@malabarpaints.com", "supplier123")}
              className="p-2 rounded-lg bg-stone-50 hover:bg-stone-100 border border-stone-200 text-xs font-medium text-stone-700"
            >
              Supplier
            </button>
            <button
              onClick={() => setRoleDemo("admin@architect.ai", "adminpassword123")}
              className="p-2 rounded-lg bg-stone-50 hover:bg-stone-100 border border-stone-200 text-xs font-medium text-stone-700"
            >
              Admin Curator
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
