"use client";

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  Building2, Search, SlidersHorizontal, Filter, X, MapPin,
  Layers, ArrowRight, User, Compass, Sparkles
} from 'lucide-react';
import { Reference, Category, FeedResponse, FeedFilters } from '@/types';
import { FeedCard } from '@/components/FeedCard';
import { ReferenceModal } from '@/components/ReferenceModal';
import { getFeed, getCategories, getFeedFilters } from '@/lib/api';

export default function ProjectsDirectoryPage() {
  const [references, setReferences] = useState<Reference[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [feedFilters, setFeedFilters] = useState<FeedFilters | null>(null);

  // Filter state
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedCountry, setSelectedCountry] = useState<string>("");
  const [selectedRegion, setSelectedRegion] = useState<string>("");
  const [selectedStyle, setSelectedStyle] = useState<string>("");
  const [selectedProjectType, setSelectedProjectType] = useState<string>("");
  const [selectedEra, setSelectedEra] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("");

  const [loading, setLoading] = useState<boolean>(true);
  const [page, setPage] = useState<number>(1);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [activeReferenceId, setActiveReferenceId] = useState<number | string | null>(null);

  useEffect(() => {
    getCategories().then(setCategories).catch(() => {});
    getFeedFilters().then(setFeedFilters).catch(() => {});
  }, []);

  const loadProjects = useCallback(async (pageNum: number, isInitial: boolean = false) => {
    setLoading(true);
    try {
      const res: FeedResponse = await getFeed({
        page: pageNum,
        page_size: 18,
        q: searchQuery,
        category: selectedCategory,
        country: selectedCountry || undefined,
        region: selectedRegion || undefined,
        style: selectedStyle || undefined,
        project_type: selectedProjectType || undefined,
        era: selectedEra || undefined,
      });

      if (isInitial) {
        setReferences(res.items);
      } else {
        setReferences((prev) => [...prev, ...res.items]);
      }
      setHasMore(res.has_more);
    } catch (err) {
      console.error("Failed to load projects", err);
    } finally {
      setLoading(false);
    }
  }, [
    searchQuery,
    selectedCategory,
    selectedCountry,
    selectedRegion,
    selectedStyle,
    selectedProjectType,
    selectedEra,
  ]);

  useEffect(() => {
    setPage(1);
    loadProjects(1, true);
  }, [loadProjects]);

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      loadProjects(nextPage, false);
    }
  };

  const resetFilters = () => {
    setSearchQuery("");
    setSelectedCountry("");
    setSelectedRegion("");
    setSelectedStyle("");
    setSelectedProjectType("");
    setSelectedEra("");
    setSelectedCategory("");
  };

  const hasActiveFilters = Boolean(
    selectedCountry || selectedRegion || selectedStyle || selectedProjectType || selectedEra || selectedCategory || searchQuery
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Editorial Header */}
      <div className="max-w-3xl">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-arch-terracotta/10 text-arch-terracotta border border-arch-terracotta/20 mb-3">
          <Building2 className="w-3.5 h-3.5" />
          Global & Regional Architectural Projects Archive
        </span>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal tracking-tight">
          Architectural Projects Archive
        </h1>
        <p className="mt-2 text-sm text-stone-600 leading-relaxed font-sans">
          Discover verified architectural built work from Kerala, Tamil Nadu, across India, and worldwide. Inspect design systems, building typologies, and the exact material assemblies specified by architects.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-3xl border border-arch-border p-5 shadow-2xs space-y-4">
        {/* Search */}
        <div className="relative max-w-2xl">
          <Search className="w-4 h-4 text-stone-400 absolute left-4 top-3.5 pointer-events-none" />
          <input
            type="text"
            placeholder="Search projects by name, architect, style (e.g. Nalukettu, Brutalism), location, or material..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-2.5 rounded-2xl border border-stone-200 bg-stone-50 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-arch-terracotta/30 focus:border-arch-terracotta transition-all"
          />
        </div>

        {/* Dynamic Filters Row */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2.5 text-xs pt-1">
          {/* Country */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-400 mb-1">
              Country
            </label>
            <select
              value={selectedCountry}
              onChange={(e) => {
                setSelectedCountry(e.target.value);
                setSelectedRegion("");
              }}
              className="w-full px-2.5 py-1.5 rounded-xl border border-stone-200 bg-stone-50 text-stone-700 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-arch-terracotta"
            >
              <option value="">All Countries</option>
              {feedFilters?.countries.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>

          {/* Region / State */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-400 mb-1">
              State / Region
            </label>
            <select
              value={selectedRegion}
              onChange={(e) => setSelectedRegion(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded-xl border border-stone-200 bg-stone-50 text-stone-700 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-arch-terracotta"
            >
              <option value="">All Regions</option>
              {feedFilters?.regions.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>

          {/* Style */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-400 mb-1">
              Architectural Style
            </label>
            <select
              value={selectedStyle}
              onChange={(e) => setSelectedStyle(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded-xl border border-stone-200 bg-stone-50 text-stone-700 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-arch-terracotta"
            >
              <option value="">All Styles</option>
              {feedFilters?.styles.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          {/* Building Type */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-400 mb-1">
              Typology
            </label>
            <select
              value={selectedProjectType}
              onChange={(e) => setSelectedProjectType(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded-xl border border-stone-200 bg-stone-50 text-stone-700 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-arch-terracotta"
            >
              <option value="">All Typologies</option>
              {feedFilters?.project_types.map((pt) => (
                <option key={pt} value={pt}>{pt}</option>
              ))}
            </select>
          </div>

          {/* Era */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-400 mb-1">
              Period / Era
            </label>
            <select
              value={selectedEra}
              onChange={(e) => setSelectedEra(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded-xl border border-stone-200 bg-stone-50 text-stone-700 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-arch-terracotta"
            >
              <option value="">All Eras</option>
              {feedFilters?.eras.map((era) => (
                <option key={era} value={era}>{era}</option>
              ))}
            </select>
          </div>

          {/* Material */}
          <div>
            <label className="block text-xs font-bold uppercase tracking-wider text-stone-400 mb-1">
              Material Focus
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-2.5 py-1.5 rounded-xl border border-stone-200 bg-stone-50 text-stone-700 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-arch-terracotta"
            >
              <option value="">All Materials</option>
              {categories.map((cat) => (
                <option key={cat.slug} value={cat.slug}>{cat.name}</option>
              ))}
            </select>
          </div>
        </div>

        {hasActiveFilters && (
          <div className="pt-2 flex justify-end">
            <button
              onClick={resetFilters}
              className="text-xs text-arch-terracotta hover:underline font-semibold"
            >
              Clear All Project Filters
            </button>
          </div>
        )}
      </div>

      {/* Grid of Architectural Projects */}
      {loading && references.length === 0 ? (
        <div className="py-20 text-center text-stone-400 font-serif">
          <div className="w-8 h-8 border-2 border-arch-terracotta border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-xs">Loading architectural project archive...</p>
        </div>
      ) : references.length > 0 ? (
        <div className="space-y-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {references.map((ref) => (
              <FeedCard
                key={ref.id}
                reference={ref}
                onSelect={(r) => setActiveReferenceId(r.id)}
              />
            ))}
          </div>

          {hasMore && (
            <div className="text-center pt-4">
              <button
                onClick={handleLoadMore}
                disabled={loading}
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full bg-white hover:bg-stone-50 text-arch-charcoal text-xs font-semibold border border-arch-border shadow-xs transition-all disabled:opacity-50"
              >
                {loading ? "Loading more projects..." : "Load More Projects"}
              </button>
            </div>
          )}

          <ReferenceModal
            referenceId={activeReferenceId}
            onClose={() => setActiveReferenceId(null)}
          />
        </div>
      ) : (
        <div className="py-16 text-center bg-white rounded-3xl border border-arch-border p-8">
          <Building2 className="w-10 h-10 text-stone-300 mx-auto mb-3" />
          <h3 className="font-serif text-xl font-bold text-arch-charcoal">No architectural projects found</h3>
          <p className="mt-2 text-xs text-stone-500 max-w-sm mx-auto">
            Try adjusting your search criteria or resetting filters to browse all projects.
          </p>
          <button
            onClick={resetFilters}
            className="mt-4 px-4 py-2 bg-arch-dark text-white rounded-xl text-xs font-semibold hover:bg-arch-terracotta transition-colors"
          >
            Reset All Filters
          </button>
        </div>
      )}
    </div>
  );
}
