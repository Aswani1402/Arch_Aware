"use client";

import React from 'react';
import { Youtube, ExternalLink, Bookmark, Instagram, Globe, MessageSquare, ShoppingBag, Store } from 'lucide-react';
import { BRAND, getSourceLabel } from '@/lib/brandConfig';

interface SourceBadgeProps {
  platform: string;
  sourceUrl?: string;
  creatorName?: string;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({
  platform,
  sourceUrl,
  creatorName,
  className = "",
  size = "md"
}) => {
  const getBadgeDetails = () => {
    const key = (platform || "").toLowerCase().trim();

    switch (key) {
      case 'youtube':
        return {
          icon: <Youtube className="w-3.5 h-3.5 text-red-600 dark:text-red-400" />,
          label: BRAND.sourceLabels.youtube,
          lightBg: 'bg-red-50 text-red-900 border-red-200',
          darkBg: 'dark:bg-red-950/60 dark:text-red-300 dark:border-red-900/60'
        };
      case 'reddit':
        return {
          icon: <MessageSquare className="w-3.5 h-3.5 text-orange-600 dark:text-orange-400" />,
          label: BRAND.sourceLabels.reddit,
          lightBg: 'bg-orange-50 text-orange-900 border-orange-200',
          darkBg: 'dark:bg-orange-950/60 dark:text-orange-300 dark:border-orange-900/60'
        };
      case 'pinterest':
        return {
          icon: <Bookmark className="w-3.5 h-3.5 text-rose-600 dark:text-rose-400" />,
          label: BRAND.sourceLabels.pinterest,
          lightBg: 'bg-rose-50 text-rose-900 border-rose-200',
          darkBg: 'dark:bg-rose-950/60 dark:text-rose-300 dark:border-rose-900/60'
        };
      case 'instagram':
        return {
          icon: <Instagram className="w-3.5 h-3.5 text-pink-600 dark:text-pink-400" />,
          label: BRAND.sourceLabels.instagram, // "Instagram" - clean source name
          lightBg: 'bg-pink-50 text-pink-900 border-pink-200',
          darkBg: 'dark:bg-pink-950/60 dark:text-pink-300 dark:border-pink-900/60'
        };
      case 'x':
      case 'twitter':
        return {
          icon: (
            <svg className="w-3 h-3 fill-current text-stone-800 dark:text-stone-200" viewBox="0 0 24 24">
              <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z" />
            </svg>
          ),
          label: BRAND.sourceLabels.x,
          lightBg: 'bg-stone-100 text-stone-900 border-stone-300',
          darkBg: 'dark:bg-stone-900 dark:text-stone-200 dark:border-stone-700'
        };
      case 'shopping':
      case 'google_shopping':
      case 'google-shopping':
        return {
          icon: <ShoppingBag className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />,
          label: BRAND.sourceLabels.shopping,
          lightBg: 'bg-emerald-50 text-emerald-900 border-emerald-200',
          darkBg: 'dark:bg-emerald-950/60 dark:text-emerald-300 dark:border-emerald-900/60'
        };
      case 'search':
      case 'google_search':
      case 'google-search':
        return {
          icon: <Globe className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />,
          label: BRAND.sourceLabels.search,
          lightBg: 'bg-sky-50 text-sky-900 border-sky-200',
          darkBg: 'dark:bg-sky-950/60 dark:text-sky-300 dark:border-sky-900/60'
        };
      case 'google_places':
      case 'google-places':
        return {
          icon: <Store className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />,
          label: BRAND.sourceLabels.google_places || 'Google Places',
          lightBg: 'bg-indigo-50 text-indigo-900 border-indigo-200',
          darkBg: 'dark:bg-indigo-950/60 dark:text-indigo-300 dark:border-indigo-900/60'
        };
      case 'google_business':
      case 'google-business':
      case 'suppliers':
      case 'supplier':
      case 'vendors':
      case 'vendor':
        return {
          icon: <Store className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />,
          label: BRAND.sourceLabels.suppliers, // "Supply Vendors"
          lightBg: 'bg-blue-50 text-blue-900 border-blue-200',
          darkBg: 'dark:bg-blue-950/60 dark:text-blue-300 dark:border-blue-900/60'
        };
      default:
        return {
          icon: <Globe className="w-3.5 h-3.5 text-stone-600 dark:text-stone-400" />,
          label: getSourceLabel(platform),
          lightBg: 'bg-stone-50 text-stone-800 border-stone-200',
          darkBg: 'dark:bg-stone-900 dark:text-stone-300 dark:border-stone-800'
        };
    }
  };

  const { icon, label, lightBg, darkBg } = getBadgeDetails();

  const content = (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-secondary font-medium border ${lightBg} ${darkBg} shadow-2xs backdrop-blur-xs transition-colors ${className}`}>
      {icon}
      <span className="truncate max-w-[140px]">{creatorName || label}</span>
      {sourceUrl && <ExternalLink className="w-3 h-3 opacity-60 ml-0.5 shrink-0" />}
    </span>
  );

  if (sourceUrl) {
    return (
      <a
        href={sourceUrl}
        target="_blank"
        rel="noopener noreferrer"
        onClick={(e) => e.stopPropagation()}
        className="inline-block hover:opacity-90 transition-opacity"
        title={`View on ${label}`}
      >
        {content}
      </a>
    );
  }

  return content;
};
