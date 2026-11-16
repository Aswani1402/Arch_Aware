"use client";

import React, { useEffect, useState } from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '@/lib/themeContext';

export const ThemeToggle: React.FC<{ className?: string }> = ({ className = "" }) => {
  const { theme, toggleTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className={`w-9 h-9 rounded-xl bg-stone-100 dark:bg-arch-dark-surface border border-arch-border dark:border-arch-dark-border ${className}`} />
    );
  }

  const isDark = theme === 'dark';

  return (
    <button
      onClick={toggleTheme}
      type="button"
      className={`relative p-2 rounded-xl text-arch-charcoal dark:text-arch-dark-text bg-stone-100 hover:bg-stone-200/80 dark:bg-arch-dark-surface dark:hover:bg-stone-800 border border-arch-border dark:border-arch-dark-border transition-all duration-200 shadow-xs flex items-center justify-center ${className}`}
      title={isDark ? "Switch to Light Theme" : "Switch to Dark Theme"}
      aria-label="Toggle Theme"
    >
      {isDark ? (
        <Sun className="w-4 h-4 text-amber-400 transition-transform hover:rotate-45" />
      ) : (
        <Moon className="w-4 h-4 text-stone-600 transition-transform hover:-rotate-12" />
      )}
    </button>
  );
};

