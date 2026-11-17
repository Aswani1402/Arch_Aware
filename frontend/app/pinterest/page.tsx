"use client";

import React from 'react';
import Link from 'next/link';
import { ArrowLeft, Compass, Bookmark, Sparkles } from 'lucide-react';
import { PinterestDiscoverySection } from '@/components/PinterestDiscoverySection';

export default function PinterestInspirationPage() {
  return (
    <div className="min-h-screen bg-stone-950 text-stone-100 flex flex-col">
      {/* Top Header */}
      <header className="sticky top-0 z-30 bg-stone-950/90 backdrop-blur-md border-b border-stone-800/80 px-4 sm:px-6 py-3.5 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="p-1.5 rounded-lg bg-stone-900 text-stone-400 hover:text-white hover:bg-stone-850 transition-colors"
              title="Return to Arch_Aware Home"
            >
              <ArrowLeft className="w-4 h-4" />
            </Link>

            <span className="font-serif text-sm sm:text-base font-bold tracking-tight text-white uppercase">
              Arch_Aware
            </span>

            <span className="text-stone-600">/</span>

            <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-rose-600/10 border border-rose-500/20 text-rose-400 text-xs font-semibold">
              <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
              <span>Pinterest Inspiration</span>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <Link
              href="/"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-stone-900 hover:bg-stone-800 border border-stone-800 text-stone-300 hover:text-amber-400 text-xs font-medium transition-colors"
            >
              <Compass className="w-3.5 h-3.5 text-amber-500" />
              <span>Main Discovery</span>
            </Link>

            <Link
              href="/saved"
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-stone-900 hover:bg-stone-800 border border-stone-800 text-stone-300 hover:text-amber-400 text-xs font-medium transition-colors"
            >
              <Bookmark className="w-3.5 h-3.5 text-amber-500" />
              <span>Saved Boards</span>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6">
        <PinterestDiscoverySection />
      </main>
    </div>
  );
}
