"use client";

import React from "react";
import { usePathname } from "next/navigation";
import { BRAND } from "@/lib/brandConfig";

export const Footer: React.FC = () => {
  const pathname = usePathname();

  // Hide footer on discovery homepage ('/') for clean infinite-scroll discovery
  if (pathname === '/') {
    return null;
  }

  return (
    <footer className="bg-white dark:bg-arch-dark-card border-t border-arch-border dark:border-arch-dark-border py-12 mt-20 text-secondary text-arch-muted dark:text-arch-dark-muted transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8">
        <div className="space-y-3">
          <span className="font-serif text-heading font-bold text-arch-charcoal dark:text-stone-100 block">
            {BRAND.name}
          </span>
          <p className="text-secondary text-arch-muted dark:text-arch-dark-muted leading-relaxed">
            {BRAND.tagline}. Bridging design references, architectural specimens, official catalogs, and regional vendor discovery.
          </p>
        </div>
        <div>
          <h5 className="font-semibold text-arch-charcoal dark:text-stone-200 mb-3 uppercase tracking-wider text-xs">
            Regional Sourcing Hierarchy
          </h5>
          <ul className="space-y-2 text-secondary">
            <li>Immediate Vicinity (&lt;25 km)</li>
            <li>Extended Local (50 km)</li>
            <li>Regional Hubs (100 km)</li>
            <li>State-wide Distribution</li>
            <li>Pan-India Freight Logistics</li>
            <li>International Exporters</li>
          </ul>
        </div>
        <div>
          <h5 className="font-semibold text-arch-charcoal dark:text-stone-200 mb-3 uppercase tracking-wider text-xs">
            Supported Sources
          </h5>
          <ul className="space-y-2 text-secondary">
            <li>Pinterest Inspiration</li>
            <li>Instagram Design Walkthroughs</li>
            <li>YouTube Project Videos</li>
            <li>Reddit Architecture Discussions</li>
            <li>Google Shopping &amp; Business Vendors</li>
          </ul>
        </div>
        <div>
          <h5 className="font-semibold text-arch-charcoal dark:text-stone-200 mb-3 uppercase tracking-wider text-xs">
            Verification Standards
          </h5>
          <p className="text-secondary text-arch-muted dark:text-arch-dark-muted leading-relaxed">
            {BRAND.name} clearly distinguishes visual inspiration from confirmed commercial products. Contact details and specifications are sourced from verified public documentation.
          </p>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-10 pt-6 border-t border-arch-border dark:border-arch-dark-border flex flex-col sm:flex-row items-center justify-between text-secondary text-arch-muted dark:text-arch-dark-muted">
        <p>&copy; {new Date().getFullYear()} {BRAND.name}. All rights reserved.</p>
        <p className="mt-2 sm:mt-0 font-medium">Architectural Specification &amp; Sourcing System</p>
      </div>
    </footer>
  );
};
