"use client";

import React from 'react';
import { Layers, MapPin, CheckCircle, AlertTriangle, Globe } from 'lucide-react';
import { FallbackLevelResult } from '@/types';

interface SourcingHierarchyVisualizerProps {
  levels: FallbackLevelResult[];
  activeLevel?: number;
  onSelectLevel?: (level: number) => void;
}

export const SourcingHierarchyVisualizer: React.FC<SourcingHierarchyVisualizerProps> = ({
  levels,
  activeLevel,
  onSelectLevel
}) => {
  return (
    <div className="w-full bg-stone-50 border border-arch-border rounded-2xl p-4 my-6">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Layers className="w-4 h-4 text-arch-terracotta" />
          <h4 className="text-xs font-semibold uppercase tracking-wider text-arch-charcoal">
            Hierarchical Regional Fallback Pipeline (7 Levels)
          </h4>
        </div>
        <span className="text-xs text-stone-500">
          Prioritizes Local Vicinity &rarr; Regional &rarr; Pan-India &rarr; Global
        </span>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
        {levels.map((lvl) => {
          const count = lvl.suppliers.length;
          const isSelected = activeLevel === lvl.level;
          const hasResults = count > 0;

          return (
            <div
              key={lvl.level}
              onClick={() => onSelectLevel && onSelectLevel(lvl.level)}
              className={`p-2.5 rounded-xl border text-center transition-all cursor-pointer ${
                isSelected
                  ? 'bg-arch-terracotta text-white border-arch-terracotta shadow-md'
                  : hasResults
                  ? 'bg-white hover:bg-stone-100 border-arch-border text-arch-charcoal'
                  : 'bg-stone-100/60 border-stone-200 text-stone-400 opacity-60'
              }`}
            >
              <div className="text-xs font-bold tracking-widest uppercase mb-1 opacity-80">
                {lvl.level === 7 ? 'Global' : `Level ${lvl.level}`}
              </div>
              <div className={`text-base font-bold font-serif leading-none mb-1 ${isSelected ? 'text-white' : hasResults ? 'text-arch-terracotta' : 'text-stone-400'}`}>
                {count} {count === 1 ? 'Supplier' : 'Suppliers'}
              </div>
              <div className={`text-xs truncate leading-tight ${isSelected ? 'text-white/90' : 'text-stone-500'}`} title={lvl.radius_desc}>
                {lvl.level_name}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
