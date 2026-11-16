"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Layers, Store, Bookmark, Building2, Menu, X, ChevronDown, Sparkles, User as UserIcon, LogIn, LogOut, Compass
} from 'lucide-react';
import { BRAND } from '@/lib/brandConfig';
import { useNavigation } from '@/lib/navigationContext';
import { useAuth } from '@/lib/authContext';
import { LocationSelector } from './LocationSelector';
import { ThemeToggle } from './ThemeToggle';

export const Navbar: React.FC = () => {
  const pathname = usePathname();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const {
    keywordExplorerOpen,
    savedDrawerOpen,
    openSavedInspiration,
    savedInspirationCount,
    savedVendorsCount,
  } = useNavigation();

  // Automatically close mobile menu whenever a drawer opens or pathname changes
  useEffect(() => {
    if (savedDrawerOpen || keywordExplorerOpen) {
      setMobileMenuOpen(false);
    }
  }, [savedDrawerOpen, keywordExplorerOpen]);

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  return (
    <header className="sticky top-0 z-40 w-full bg-white/95 dark:bg-arch-dark-bg/95 backdrop-blur-md border-b border-arch-border dark:border-arch-dark-border transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          {/* 1. Application Logo & Name */}
          <Link
            href="/"
            className="flex items-center gap-2.5 group shrink-0"
            aria-label={`${BRAND.name} Home`}
          >
            <div className="w-9 h-9 rounded-xl bg-arch-dark dark:bg-arch-terracotta text-white flex items-center justify-center font-serif font-bold text-lg tracking-tight group-hover:bg-arch-terracotta dark:group-hover:bg-orange-600 transition-colors shadow-xs">
              {BRAND.logoLetter}
            </div>
            <span className="font-serif text-2xl font-bold tracking-tight text-arch-charcoal dark:text-stone-100 leading-none">
              {BRAND.name}
            </span>
          </Link>

          {/* Desktop Navigation Items: Explore, Vendors, Saved */}
          <nav className="hidden lg:flex items-center gap-2">
            {/* 1. Explore */}
            <Link
              href="/"
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-body-base font-medium transition-all ${
                pathname === '/' && !keywordExplorerOpen
                  ? 'bg-stone-100 dark:bg-arch-dark-surface text-arch-charcoal dark:text-stone-100 font-semibold shadow-xs'
                  : 'text-arch-charcoal dark:text-arch-dark-text hover:bg-stone-100 dark:hover:bg-arch-dark-surface'
              }`}
              title="Explore architectural inspiration"
            >
              <Compass className="w-4 h-4 text-arch-terracotta dark:text-arch-dark-terracotta" />
              <span>Explore</span>
            </Link>

            {/* 2. Vendors */}
            <Link
              href="/sourcing"
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-body-base font-medium transition-all ${
                pathname === '/sourcing' || pathname === '/suppliers'
                  ? 'bg-stone-100 dark:bg-arch-dark-surface text-arch-charcoal dark:text-stone-100 font-semibold shadow-xs'
                  : 'text-arch-charcoal dark:text-arch-dark-text hover:bg-stone-100 dark:hover:bg-arch-dark-surface'
              }`}
              title="Discover regional suppliers and verified trade vendors"
            >
              <Store className="w-4 h-4 text-blue-500" />
              <span>Vendors</span>
            </Link>

            {/* 3. Saved (Single Entry) */}
            <button
              onClick={() => {
                if (pathname === '/saved') {
                  // already on saved page
                } else {
                  openSavedInspiration();
                }
              }}
              type="button"
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-xl text-body-base font-medium transition-all ${
                savedDrawerOpen || pathname === '/saved'
                  ? 'bg-stone-100 dark:bg-arch-dark-surface text-arch-charcoal dark:text-stone-100 font-semibold shadow-xs'
                  : 'text-arch-charcoal dark:text-arch-dark-text hover:bg-stone-100 dark:hover:bg-arch-dark-surface'
              }`}
              title="View your saved items"
            >
              <Bookmark className="w-4 h-4 text-rose-500" />
              <span>Saved</span>
              {(savedInspirationCount + savedVendorsCount) > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-rose-500/10 dark:bg-rose-500/20 text-rose-600 dark:text-rose-300 text-xs font-semibold">
                  {savedInspirationCount + savedVendorsCount}
                </span>
              )}
            </button>
          </nav>

          {/* Right Controls: Location, Theme Toggle, and Account/Sign-in */}
          <div className="flex items-center gap-2.5 shrink-0">
            {/* Location */}
            <LocationSelector />

            {/* Light/Dark Theme toggle */}
            <ThemeToggle />

            {/* Account / Sign-In Indicator */}
            {user ? (
              <div className="hidden sm:flex items-center gap-1.5 pl-2 border-l border-arch-border dark:border-arch-dark-border">
                <Link
                  href="/admin"
                  className="flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold bg-stone-100 hover:bg-stone-200 dark:bg-arch-dark-surface dark:hover:bg-stone-800 text-arch-charcoal dark:text-stone-200 transition-colors"
                  title={`Signed in as ${user.email}`}
                >
                  <div className="w-5 h-5 rounded-full bg-arch-terracotta text-white flex items-center justify-center text-xs font-bold uppercase">
                    {user.email ? user.email[0] : 'U'}
                  </div>
                  <span className="hidden xl:inline max-w-[110px] truncate">{user.email}</span>
                </Link>
                <button
                  onClick={logout}
                  className="p-1.5 text-stone-400 hover:text-arch-charcoal dark:hover:text-stone-200 rounded-lg transition-colors"
                  title="Sign Out"
                  aria-label="Sign Out"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <Link
                href="/login"
                className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-stone-100 hover:bg-stone-200 dark:bg-arch-dark-surface dark:hover:bg-stone-800 text-arch-charcoal dark:text-stone-200 border border-arch-border dark:border-arch-dark-border transition-colors ml-1"
              >
                <LogIn className="w-3.5 h-3.5 text-arch-terracotta" />
                <span>Sign In</span>
              </Link>
            )}

            {/* Mobile Hamburger Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              type="button"
              className="lg:hidden p-2 rounded-xl text-arch-charcoal dark:text-arch-dark-text bg-stone-100 dark:bg-arch-dark-surface hover:bg-stone-200 dark:hover:bg-stone-800 transition-colors"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden py-4 border-t border-arch-border dark:border-arch-dark-border space-y-2 animate-in fade-in duration-150">
            <Link
              href="/"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full flex items-center justify-between px-4 py-3 rounded-xl text-body-base font-medium text-arch-charcoal dark:text-arch-dark-text bg-stone-50 dark:bg-arch-dark-surface"
            >
              <span className="flex items-center gap-2.5">
                <Compass className="w-4 h-4 text-arch-terracotta" />
                Explore
              </span>
              <span className="text-secondary text-arch-muted">Inspiration</span>
            </Link>

            <Link
              href="/sourcing"
              onClick={() => setMobileMenuOpen(false)}
              className="w-full flex items-center justify-between px-4 py-3 rounded-xl text-body-base font-medium text-arch-charcoal dark:text-arch-dark-text bg-stone-50 dark:bg-arch-dark-surface"
            >
              <span className="flex items-center gap-2.5">
                <Store className="w-4 h-4 text-blue-500" />
                Vendors
              </span>
              <span className="text-secondary text-arch-muted">Suppliers</span>
            </Link>

            <button
              onClick={() => {
                setMobileMenuOpen(false);
                setTimeout(() => openSavedInspiration(), 50);
              }}
              className="w-full flex items-center justify-between px-4 py-3 rounded-xl text-body-base font-medium text-arch-charcoal dark:text-arch-dark-text bg-stone-50 dark:bg-arch-dark-surface"
            >
              <span className="flex items-center gap-2.5">
                <Bookmark className="w-4 h-4 text-rose-500" />
                Saved
              </span>
              {(savedInspirationCount + savedVendorsCount) > 0 && (
                <span className="px-2 py-0.5 rounded-full bg-rose-500/10 text-rose-600 text-xs font-semibold">
                  {savedInspirationCount + savedVendorsCount}
                </span>
              )}
            </button>

            {user ? (
              <div className="pt-2 border-t border-arch-border dark:border-arch-dark-border flex items-center justify-between px-4 py-2">
                <Link
                  href="/admin"
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-2 text-xs font-medium text-arch-charcoal dark:text-stone-200"
                >
                  <div className="w-6 h-6 rounded-full bg-arch-terracotta text-white flex items-center justify-center text-xs font-bold uppercase">
                    {user.email ? user.email[0] : 'U'}
                  </div>
                  <span className="truncate max-w-[200px]">{user.email}</span>
                </Link>
                <button
                  onClick={() => {
                    logout();
                    setMobileMenuOpen(false);
                  }}
                  className="text-xs text-rose-600 dark:text-rose-400 font-semibold"
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <Link
                href="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-arch-terracotta text-white shadow-xs"
              >
                <LogIn className="w-3.5 h-3.5" />
                <span>Sign In / Register</span>
              </Link>
            )}
          </div>
        )}
      </div>
    </header>
  );
};
