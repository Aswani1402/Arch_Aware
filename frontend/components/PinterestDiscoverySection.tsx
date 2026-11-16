"use client";

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import {
  Search, ExternalLink, Bookmark, Check, AlertCircle, RefreshCw,
  Sparkles, Layers, ShieldAlert, ArrowRight, Info, DollarSign, Eye, Play, Video
} from 'lucide-react';
import {
  PinterestItem,
  PinterestSearchResponse,
  searchPinterest,
  savePinterestPin,
  getPinterestStatus,
  getPinterestCategories
} from '@/lib/api';

interface PinterestDiscoverySectionProps {
  onOpenDetails?: (pin: PinterestItem) => void;
  className?: string;
}

export const PinterestDiscoverySection: React.FC<PinterestDiscoverySectionProps> = ({
  onOpenDetails,
  className = ""
}) => {
  // API & Category state
  const [categories, setCategories] = useState<Array<{ id: string; name: string; query: string; section: string; description: string }>>([]);
  const [selectedCategoryId, setSelectedCategoryId] = useState<string | null>(null);
  const [selectedSection, setSelectedSection] = useState<string>("ALL");
  const [apiStatus, setApiStatus] = useState<{ configured: boolean; message: string } | null>(null);

  // Search input and query
  const [queryInput, setQueryInput] = useState<string>("Indian and Kerala Architecture");
  const [activeSearchedQuery, setActiveSearchedQuery] = useState<string>("");
  const [dryRunMode, setDryRunMode] = useState<boolean>(false);

  // Results & Pagination state
  const [items, setItems] = useState<PinterestItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [loadingMore, setLoadingMore] = useState<boolean>(false);
  const [hasMore, setHasMore] = useState<boolean>(false);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [dryRunDetails, setDryRunDetails] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [hasSearchedOnce, setHasSearchedOnce] = useState<boolean>(false);

  // Saved pins map (pin_id or source_url -> boolean)
  const [savedMap, setSavedMap] = useState<Record<string, boolean>>({});
  const [savedNotice, setSavedNotice] = useState<string | null>(null);

  // Load status and categories on mount (NO automatic search on page load to preserve credits!)
  useEffect(() => {
    getPinterestStatus()
      .then(res => setApiStatus({ configured: res.configured, message: res.message }))
      .catch(() => setApiStatus({ configured: false, message: "Could not reach backend status endpoint." }));

    getPinterestCategories()
      .then(res => {
        if (res && res.categories) {
          setCategories(res.categories);
        }
      })
      .catch(err => console.error("Error loading Pinterest categories", err));
  }, []);

  // Sections list for filtering categories
  const sections = ["ALL", "Typologies", "Envelopes", "Interiors", "Spaces", "Materials", "Finishes", "Circulation", "Services", "Landscape", "Craftsmanship", "Products", "Sustainability", "Regional"];

  const filteredCategories = selectedSection === "ALL"
    ? categories
    : categories.filter(c => c.section.toLowerCase() === selectedSection.toLowerCase());

  // Execute explicit user-triggered search (never called automatically on page load)
  const handleTriggerSearch = async (searchTerm: string, isDryRun: boolean = false) => {
    const term = searchTerm.trim();
    if (!term) return;

    setLoading(true);
    setErrorMessage(null);
    setDryRunDetails(null);
    setHasSearchedOnce(true);
    setActiveSearchedQuery(term);

    try {
      const res: PinterestSearchResponse = await searchPinterest({
        query: term,
        dry_run: isDryRun,
        relevance: "score",
        trim: false
      });

      if (res.dry_run) {
        setDryRunDetails(res.dry_run_details || { message: "Dry-run succeeded. 0 credits charged." });
        setItems([]);
        setHasMore(false);
        setNextCursor(null);
      } else {
        setItems(res.items || []);
        setHasMore(Boolean(res.has_more));
        setNextCursor(res.next_cursor || null);
      }
    } catch (err: any) {
      console.error("Pinterest search failed", err);
      setErrorMessage(err.message || "Failed to search Pinterest via SocialCrawl API.");
      setItems([]);
      setHasMore(false);
      setNextCursor(null);
    } finally {
      setLoading(false);
    }
  };

  // Explicit user-triggered pagination ("Load More" button only)
  const handleLoadMore = async () => {
    if (!nextCursor || loadingMore || !activeSearchedQuery) return;

    setLoadingMore(true);
    setErrorMessage(null);

    try {
      const res: PinterestSearchResponse = await searchPinterest({
        query: activeSearchedQuery,
        cursor: nextCursor,
        relevance: "score",
        trim: false
      });

      setItems(prev => [...prev, ...(res.items || [])]);
      setHasMore(Boolean(res.has_more));
      setNextCursor(res.next_cursor || null);
    } catch (err: any) {
      console.error("Failed to load more Pinterest items", err);
      setErrorMessage(err.message || "Failed to paginate next page.");
    } finally {
      setLoadingMore(false);
    }
  };

  // Toggle Save Pinterest Pin to user moodboard / database
  const handleToggleSave = async (pin: PinterestItem) => {
    const key = pin.pin_id || pin.source_url || pin.id;
    const isCurrentlySaved = Boolean(savedMap[key]);

    // Optimistic UI update
    setSavedMap(prev => ({ ...prev, [key]: !isCurrentlySaved }));

    try {
      const res = await savePinterestPin({
        pin_id: pin.pin_id,
        title: pin.title,
        description: pin.description,
        image_url: pin.image_url,
        source_url: pin.source_url,
        creator_name: pin.creator_name,
        creator_url: pin.creator_url,
        material_tags: activeSearchedQuery,
        project_collection: "Pinterest Inspiration"
      });

      setSavedMap(prev => ({ ...prev, [key]: res.saved }));
      setSavedNotice(res.saved ? "Saved to your Moodboard collection!" : "Removed from saved collection.");
      setTimeout(() => setSavedNotice(null), 3000);
    } catch (err: any) {
      console.error("Error saving Pinterest pin", err);
      // Revert optimistic update
      setSavedMap(prev => ({ ...prev, [key]: isCurrentlySaved }));
      setSavedNotice("Failed to update saved collection.");
      setTimeout(() => setSavedNotice(null), 3000);
    }
  };

  // Helper for dynamic masonry aspect ratio
  const getAspectRatioClass = (idx: number) => {
    const mod = idx % 4;
    switch (mod) {
      case 0: return "aspect-[3/4]";
      case 1: return "aspect-[4/5]";
      case 2: return "aspect-[1/1]";
      default: return "aspect-[2/3]";
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Editorial Header & Sourcing Attribution Banner */}
      <div className="bg-stone-900/90 border border-stone-800 rounded-3xl p-6 sm:p-8 backdrop-blur-md relative overflow-hidden shadow-xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-rose-600/10 rounded-full blur-3xl pointer-events-none" />

        <div className="relative z-10 space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <span className="px-3 py-1 rounded-full bg-rose-600/20 text-rose-400 border border-rose-500/30 text-xs font-semibold flex items-center gap-1.5 shadow-xs">
                <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse" />
                SocialCrawl Pinterest Search API
              </span>
              <span className="px-2.5 py-1 rounded-full bg-stone-800 text-stone-300 text-xs font-mono border border-stone-700">
                Live Inspiration
              </span>
            </div>

            {/* API Status Pill */}
            {apiStatus && (
              <div className={`text-xs px-3 py-1 rounded-full flex items-center gap-1.5 border ${
                apiStatus.configured
                  ? 'bg-emerald-950/40 text-emerald-300 border-emerald-800/60'
                  : 'bg-amber-950/40 text-amber-300 border-amber-800/60'
              }`}>
                <span className={`w-1.5 h-1.5 rounded-full ${apiStatus.configured ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                <span>{apiStatus.configured ? "API Key Configured" : "API Key Pending (SOCIALCRAWL_API_KEY)"}</span>
              </div>
            )}
          </div>

          <div className="max-w-3xl">
            <h2 className="text-2xl sm:text-3xl font-serif font-bold text-white tracking-tight">
              Curated Architectural Inspiration from Pinterest
            </h2>
            <p className="mt-2 text-stone-300 text-xs sm:text-sm leading-relaxed">
              Explore authentic architectural pins across 28 specialized design categories including Indian and Kerala Architecture, facades, masonry, joinery, and sustainable construction techniques.
            </p>
          </div>

          {/* Attribution & Data Integrity Notice */}
          <div className="p-3.5 rounded-2xl bg-stone-950/80 border border-stone-800/90 text-xs text-stone-400 space-y-1">
            <div className="flex items-center gap-1.5 text-stone-200 font-semibold">
              <Info className="w-3.5 h-3.5 text-amber-500 shrink-0" />
              <span>Attribution & Visual Integrity Notice</span>
            </div>
            <p>
              Pinterest items are external visual references provided via SocialCrawl. Sourced pins remain the property of their respective creators and are provided for architectural inspiration only. Pinterest pins do not establish verified commercial availability, pricing, manufacturer guarantees, or technical specifications.
            </p>
          </div>
        </div>
      </div>

      {/* Saved Toast Notice */}
      {savedNotice && (
        <div className="fixed bottom-6 right-6 z-50 bg-stone-900 border border-amber-500/50 text-amber-300 px-4 py-2.5 rounded-2xl shadow-2xl text-xs flex items-center gap-2 animate-bounce">
          <Check className="w-4 h-4 text-amber-400" />
          <span>{savedNotice}</span>
        </div>
      )}

      {/* Search Bar & Request Safety Controls */}
      <div className="bg-stone-900/80 border border-stone-800/80 rounded-2xl p-4 sm:p-5 space-y-4">
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
          {/* Main Keyword Input */}
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-stone-400 absolute left-4 top-3.5 pointer-events-none" />
            <input
              type="text"
              placeholder="Search Kerala architecture, terracotta jaali, cantilever staircases, teak woodwork..."
              value={queryInput}
              onChange={(e) => setQueryInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  handleTriggerSearch(queryInput, dryRunMode);
                }
              }}
              className="w-full pl-11 pr-4 py-2.5 bg-stone-950 border border-stone-800 rounded-xl text-stone-100 placeholder:text-stone-500 text-xs sm:text-sm focus:outline-none focus:border-amber-500/70 transition-colors"
            />
          </div>

          {/* Dry Run Toggle */}
          <button
            type="button"
            onClick={() => setDryRunMode(!dryRunMode)}
            className={`px-3 py-2.5 rounded-xl text-xs font-semibold flex items-center justify-center gap-1.5 transition-all border ${
              dryRunMode
                ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 shadow-xs'
                : 'bg-stone-950 text-stone-400 border-stone-800 hover:text-stone-200'
            }`}
            title="Perform dry-run price check without charging SocialCrawl credits"
          >
            <DollarSign className="w-3.5 h-3.5" />
            <span>Dry-Run Check</span>
          </button>

          {/* Explicit Search Action Button */}
          <button
            type="button"
            onClick={() => handleTriggerSearch(queryInput, dryRunMode)}
            disabled={loading || !queryInput.trim()}
            className="px-6 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-500 disabled:opacity-50 text-white font-semibold text-xs sm:text-sm flex items-center justify-center gap-2 shadow-lg hover:shadow-rose-600/30 transition-all active:scale-95"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Searching...</span>
              </>
            ) : dryRunMode ? (
              <>
                <Eye className="w-4 h-4" />
                <span>Check Dry-Run Price</span>
              </>
            ) : (
              <>
                <Search className="w-4 h-4" />
                <span>Search Pinterest</span>
              </>
            )}
          </button>
        </div>

        {/* Section Filters for Categories */}
        <div className="space-y-2 pt-2 border-t border-stone-800/60">
          <div className="flex items-center justify-between text-xs text-stone-400">
            <span className="font-semibold text-stone-300">Browse 28 Focused Architectural Categories:</span>
            <span>Click any category to search its focused query</span>
          </div>

          <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none pb-1">
            {sections.map((sec) => (
              <button
                key={sec}
                type="button"
                onClick={() => setSelectedSection(sec)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition-colors ${
                  selectedSection === sec
                    ? 'bg-stone-700 text-white font-bold'
                    : 'bg-stone-950 text-stone-400 hover:text-stone-200'
                }`}
              >
                {sec}
              </button>
            ))}
          </div>

          {/* Focused Category Chips */}
          <div className="flex flex-wrap gap-1.5 max-h-40 overflow-y-auto pr-1">
            {filteredCategories.map((cat) => {
              const isSelected = selectedCategoryId === cat.id;
              return (
                <button
                  key={cat.id}
                  type="button"
                  onClick={() => {
                    setSelectedCategoryId(cat.id);
                    setQueryInput(cat.query);
                    handleTriggerSearch(cat.query, dryRunMode);
                  }}
                  className={`px-3 py-1.5 rounded-xl text-xs font-medium transition-all text-left flex items-center gap-1.5 border ${
                    isSelected
                      ? 'bg-amber-500 text-stone-950 border-amber-500 font-bold shadow-xs'
                      : 'bg-stone-950/70 text-stone-300 border-stone-800/80 hover:border-amber-500/40 hover:text-white'
                  }`}
                  title={`${cat.name}: ${cat.description}`}
                >
                  <Sparkles className={`w-3 h-3 ${isSelected ? 'text-stone-950' : 'text-amber-500/70'}`} />
                  <span>{cat.name}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Dry Run Notice / Details Card */}
      {dryRunDetails && (
        <div className="p-4 rounded-2xl bg-amber-950/30 border border-amber-600/40 text-amber-200 text-xs space-y-2">
          <div className="flex items-center gap-2 font-semibold text-amber-300">
            <DollarSign className="w-4 h-4 text-amber-400" />
            <span>Dry-Run Mode Price Estimate (No credits charged)</span>
          </div>
          <p className="text-stone-300 text-xs">
            The dry-run request verified API authentication and pricing. To fetch live architectural pins, toggle &ldquo;Dry-Run Check&rdquo; off and click &ldquo;Search Pinterest&rdquo;.
          </p>
          <pre className="p-3 rounded-xl bg-stone-950 font-mono text-xs text-amber-400 overflow-x-auto border border-stone-800">
            {JSON.stringify(dryRunDetails, null, 2)}
          </pre>
        </div>
      )}

      {/* Error State Banner */}
      {errorMessage && (
        <div className="p-4 rounded-2xl bg-rose-950/50 border border-rose-800 text-rose-200 text-xs flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <strong className="block text-rose-300 font-semibold">Search Request Notice</strong>
            <span>{errorMessage}</span>
            {!apiStatus?.configured && (
              <p className="mt-1 text-xs text-stone-400">
                To enable live searches, configure the <code className="text-amber-400">SOCIALCRAWL_API_KEY</code> environment variable in your backend environment.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Initial Welcome State (Before any search is made) */}
      {!hasSearchedOnce && !loading && (
        <div className="py-16 text-center space-y-3 bg-stone-900/40 border border-stone-800/60 rounded-3xl p-8">
          <div className="w-14 h-14 rounded-full bg-rose-600/10 border border-rose-500/30 flex items-center justify-center mx-auto text-rose-400 shadow-md">
            <Sparkles className="w-6 h-6" />
          </div>
          <h3 className="font-serif text-lg font-bold text-stone-200">
            Select a Category or Enter a Keyword to Discover Pinterest Inspiration
          </h3>
          <p className="text-xs text-stone-400 max-w-lg mx-auto leading-relaxed">
            In accordance with request safety standards, searches are triggered exclusively on your explicit request. Choose from Indian and Kerala Architecture, facades, finishes, or custom keywords above.
          </p>
          <button
            type="button"
            onClick={() => handleTriggerSearch(queryInput, false)}
            className="mt-3 px-5 py-2.5 rounded-full bg-stone-800 hover:bg-stone-700 text-amber-400 font-semibold text-xs border border-stone-700 inline-flex items-center gap-1.5 shadow-sm transition-all"
          >
            <span>Search &ldquo;{queryInput}&rdquo;</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>
      )}

      {/* Loading Skeletons */}
      {loading && (
        <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-4 space-y-4">
          {[360, 280, 420, 320, 390, 300, 340, 400].map((h, i) => (
            <div
              key={i}
              style={{ height: `${h}px` }}
              className="break-inside-avoid rounded-2xl bg-stone-900 border border-stone-800/80 animate-pulse"
            />
          ))}
        </div>
      )}

      {/* Empty State after search */}
      {hasSearchedOnce && !loading && items.length === 0 && !dryRunDetails && !errorMessage && (
        <div className="py-20 text-center space-y-3 bg-stone-900/40 border border-stone-800 rounded-3xl p-8">
          <Layers className="w-10 h-10 text-stone-600 mx-auto" />
          <h3 className="font-serif text-base font-bold text-stone-200">
            No Pinterest pins found for &ldquo;{activeSearchedQuery}&rdquo;
          </h3>
          <p className="text-xs text-stone-400 max-w-md mx-auto">
            Try a broader keyword or select one of the 28 curated categories such as Bricks and Blocks, Stone and Marble, or Living Rooms.
          </p>
        </div>
      )}

      {/* Results Masonry Grid */}
      {!loading && items.length > 0 && (
        <div className="space-y-8">
          <div className="flex items-center justify-between text-xs text-stone-400 px-1">
            <span>
              Showing <strong className="text-stone-200">{items.length}</strong> Pinterest visual inspiration references for &ldquo;{activeSearchedQuery}&rdquo;
            </span>
            <span className="text-xs text-stone-500 font-mono">
              Source: SocialCrawl API
            </span>
          </div>

          <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-4 space-y-4">
            {items.map((pin, index) => {
              const key = pin.pin_id || pin.source_url || pin.id;
              const isSaved = Boolean(savedMap[key]);
              const aspectClass = getAspectRatioClass(index);

              return (
                <div
                  key={key || index}
                  className="break-inside-avoid group relative rounded-2xl overflow-hidden bg-stone-900 border border-stone-800/80 hover:border-rose-500/40 transition-all duration-300 shadow-sm hover:shadow-2xl flex flex-col"
                >
                  {/* Pin Image Container */}
                  <div className={`relative w-full ${aspectClass} overflow-hidden bg-stone-950`}>
                    <img
                      src={pin.image_url}
                      alt={pin.title || `Pinterest Inspiration ${index + 1}`}
                      loading={index < 4 ? "eager" : "lazy"}
                      onError={(e) => {
                        // Safe architectural placeholder if CDN image fails
                        e.currentTarget.src = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80";
                      }}
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    />

                    {/* Top Overlay Attribution Badges */}
                    <div className="absolute top-2.5 left-2.5 right-2.5 flex items-center justify-between pointer-events-none">
                      {/* Pinterest Source Label */}
                      <span className="px-2 py-0.5 rounded-full text-xs font-semibold tracking-wide bg-rose-600/90 text-white backdrop-blur-md shadow-sm pointer-events-auto flex items-center gap-1">
                        <span>Pinterest Pin</span>
                      </span>

                      {/* Video or Inspiration Ref Badge */}
                      {pin.is_video ? (
                        <span className="px-2 py-0.5 rounded-full bg-amber-500/90 backdrop-blur-md text-stone-950 text-xs font-bold pointer-events-auto flex items-center gap-1 shadow-sm">
                          <Play className="w-2.5 h-2.5 fill-current" />
                          <span>{pin.video_duration || "Video"}</span>
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-full bg-stone-950/80 backdrop-blur-md text-stone-300 text-xs font-mono pointer-events-auto border border-stone-800">
                          Inspiration Ref
                        </span>
                      )}
                    </div>

                    {/* Bottom Action Bar on Hover */}
                    <div className="absolute inset-0 bg-gradient-to-t from-stone-950/95 via-stone-950/30 to-transparent opacity-0 sm:group-hover:opacity-100 transition-opacity duration-200 flex flex-col justify-end p-3 pointer-events-none">
                      <div className="flex items-center justify-between pt-2">
                        {/* Save to Moodboard Button */}
                        <button
                          type="button"
                          onClick={(e) => {
                            e.stopPropagation();
                            handleToggleSave(pin);
                          }}
                          className={`px-3 py-1.5 rounded-full text-xs font-semibold flex items-center gap-1.5 backdrop-blur-md transition-all pointer-events-auto active:scale-95 ${
                            isSaved
                              ? 'bg-amber-500 text-stone-950 shadow-md font-bold'
                              : 'bg-stone-900/90 text-stone-200 hover:text-amber-400 hover:bg-stone-800'
                          }`}
                          title={isSaved ? "Saved to Moodboard (Click to remove)" : "Save to Moodboard"}
                        >
                          <Bookmark className={`w-3.5 h-3.5 ${isSaved ? 'fill-current' : ''}`} />
                          <span>{isSaved ? "Saved" : "Save"}</span>
                        </button>

                        {/* Open Original Pinterest Pin Link */}
                        <a
                          href={pin.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          onClick={(e) => e.stopPropagation()}
                          className="px-3 py-1.5 rounded-full bg-stone-900/90 hover:bg-rose-600 text-stone-200 hover:text-white text-xs font-semibold flex items-center gap-1.5 shadow-lg border border-stone-700/80 transition-all pointer-events-auto active:scale-95"
                          title="View original Pinterest pin"
                        >
                          <span>Visit Pin</span>
                          <ExternalLink className="w-3.5 h-3.5" />
                        </a>
                      </div>
                    </div>
                  </div>

                  {/* Card Content & Metadata */}
                  <div className="p-3.5 space-y-1.5 bg-stone-900 flex-1 flex flex-col justify-between">
                    <div>
                      {/* Title: Display only if available (never invent fake titles) */}
                      {pin.title ? (
                        <h4 className="font-semibold text-stone-100 text-xs sm:text-sm leading-snug line-clamp-2 group-hover:text-amber-400 transition-colors">
                          {pin.title}
                        </h4>
                      ) : (
                        <span className="text-xs text-stone-500 italic block">
                          Visual Reference Pin
                        </span>
                      )}

                      {/* Description: Display only if available */}
                      {pin.description && (
                        <p className="text-xs text-stone-400 line-clamp-2 mt-1 leading-relaxed">
                          {pin.description}
                        </p>
                      )}
                    </div>

                    <div className="pt-2 border-t border-stone-800/60 space-y-1.5">
                      {/* Creator Information: Display only if available */}
                      <div className="flex items-center justify-between text-xs text-stone-400">
                        {pin.creator_name ? (
                          pin.creator_url ? (
                            <a
                              href={pin.creator_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="truncate text-stone-300 hover:text-rose-400 transition-colors max-w-[70%]"
                              title={`Creator: ${pin.creator_name}`}
                            >
                              By: {pin.creator_name}
                            </a>
                          ) : (
                            <span className="truncate text-stone-300 max-w-[70%]">
                              By: {pin.creator_name}
                            </span>
                          )
                        ) : (
                          <span className="text-stone-500 text-xs">
                            Pinterest Creator
                          </span>
                        )}

                        <span className="text-xs text-rose-400/90 font-medium">
                          Pinterest
                        </span>
                      </div>

                      {/* Mobile Action Controls */}
                      <div className="flex sm:hidden items-center justify-between pt-1">
                        <button
                          type="button"
                          onClick={() => handleToggleSave(pin)}
                          className={`px-2.5 py-1 rounded-lg text-xs font-semibold flex items-center gap-1 transition-colors ${
                            isSaved
                              ? 'bg-amber-500 text-stone-950 font-bold'
                              : 'bg-stone-800 text-stone-300 hover:text-amber-400'
                          }`}
                        >
                          <Bookmark className={`w-3 h-3 ${isSaved ? 'fill-current' : ''}`} />
                          <span>{isSaved ? "Saved" : "Save"}</span>
                        </button>

                        <a
                          href={pin.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="px-2.5 py-1 rounded-lg bg-stone-800 text-rose-400 hover:bg-stone-700 text-xs font-semibold flex items-center gap-1"
                        >
                          <span>Visit Pin</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Load More Pagination (Only with explicit user click, no automatic pagination) */}
          {hasMore && (
            <div className="flex justify-center pt-4 pb-10">
              <button
                type="button"
                onClick={handleLoadMore}
                disabled={loadingMore}
                className="px-6 py-2.5 rounded-full bg-stone-800 hover:bg-stone-700 disabled:opacity-50 text-stone-200 text-xs sm:text-sm font-semibold border border-stone-700 shadow-md transition-all active:scale-95 flex items-center gap-2"
              >
                {loadingMore ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin text-amber-500" />
                    <span>Loading more Pinterest pins...</span>
                  </>
                ) : (
                  <>
                    <span>Load More Pinterest Inspiration</span>
                    <ArrowRight className="w-4 h-4 text-amber-500" />
                  </>
                )}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
