"use client";

import React, { useState, useEffect, useCallback, useMemo, useRef, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  Layers, MapPin, Store, AlertCircle, RefreshCw, X, Sparkles
} from 'lucide-react';
import { Reference, FeedResponse } from '@/types';
import { PinterestMasonryFeed } from '@/components/PinterestMasonryFeed';
import { FullScreenReelModal } from '@/components/FullScreenReelModal';
import { ContextualDetailsDrawer } from '@/components/ContextualDetailsDrawer';
import { KeywordExplorerPanel } from '@/components/KeywordExplorerPanel';
import { discoverySearch, getFeed, getSavedItems, hasAuthToken, toggleSavedItem } from '@/lib/api';
import { useAuth } from '@/lib/authContext';
import { useNavigation } from '@/lib/navigationContext';

type SourceFilter = 'all' | 'pinterest' | 'instagram' | 'youtube' | 'shopping' | 'reddit';

interface SourceStatusSummary {
  source_name: string;
  status: string;
  result_count?: number;
  error_message?: string | null;
}

function extractYoutubeVideoId(url?: string): string | undefined {
  if (!url) return undefined;
  const match = url.match(/(?:v=|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
  return match?.[1];
}

function mapDiscoveryItemToReference(item: any, idx: number): Reference {
  const sourceUrl = item.original_url || item.canonical_url || '';
  const sourcePlatform = item.source || 'google_search';
  const syntheticId = typeof item.id === 'number' && item.id > 0 ? item.id : -(idx + 10000);
  const metaSrc = item.source_metadata || {};
  const priceLabel =
    item.price != null
      ? `${item.currency ? `${item.currency} ` : ''}${item.price}`
      : undefined;
  const cleanPhone = typeof item.phone === 'string' ? item.phone.replace(/[^\d+]/g, '') : undefined;
  const sellerVal =
    (typeof metaSrc.seller === 'string' && metaSrc.seller.trim() ? metaSrc.seller.trim() : undefined) ||
    (sourcePlatform === 'google_shopping' && typeof item.creator_name === 'string' && item.creator_name.trim()
      ? item.creator_name.trim()
      : undefined);
  const hasListingDetails = Boolean(
    priceLabel ||
      item.address ||
      cleanPhone ||
      item.website ||
      sellerVal ||
      metaSrc.brand ||
      metaSrc.availability ||
      metaSrc.rating != null
  );
  const metaPayload = hasListingDetails
    ? JSON.stringify({
        price_label: priceLabel,
        price: item.price ?? undefined,
        currency: item.currency || undefined,
        seller: sellerVal,
        brand: metaSrc.brand || undefined,
        availability: metaSrc.availability || undefined,
        rating: metaSrc.rating ?? undefined,
        reviews_count: metaSrc.reviews_count ?? undefined,
        address: item.address || item.location,
        clean_phone: cleanPhone || undefined,
        directions_url: sourceUrl || undefined,
        website: item.website || undefined,
      })
    : undefined;

  return {
    id: syntheticId,
    title: item.title || 'Architectural Discovery Result',
    slug: `discovery-${sourcePlatform}-${Math.abs(syntheticId)}`,
    source_platform: sourcePlatform,
    source_url: sourceUrl,
    creator_name: item.creator_name || undefined,
    creator_url: item.creator_url || undefined,
    thumbnail_url: item.thumbnail_url || item.image_url || undefined,
    media_url: item.video_url || item.image_url || undefined,
    video_embed_id: sourcePlatform === 'youtube' ? extractYoutubeVideoId(item.video_url || sourceUrl) : undefined,
    category_id: item.category_id ?? undefined,
    category_name: item.category || undefined,
    material_tags: Array.isArray(item.matched_keywords) && item.matched_keywords.length > 0
      ? item.matched_keywords.join(', ')
      : item.subcategory || item.category || undefined,
    location_context: item.location || item.address || undefined,
    content_type: item.content_type || 'architectural_project',
    verification_status: item.verification_status || 'UNVERIFIED',
    description: item.description || undefined,
    inspiration_image_url: item.image_url || item.thumbnail_url || undefined,
    inspiration_source_url: sourceUrl || undefined,
    manufacturer_name: item.source_attribution || undefined,
    colors_and_finishes: metaPayload,
    retrieval_method: 'live_discovery_api',
    provenance: item.provenance || 'live_discovery',
    inspiration_relevance_tier: item.inspiration_relevance_tier || 'EXACT_METADATA_MATCH',
    media_status: item.media_status || (item.image_url || item.thumbnail_url || item.video_url ? 'MEDIA_READY' : 'MEDIA_UNUSABLE'),
    matched_products_count: 0,
    created_at: item.retrieval_timestamp || new Date().toISOString(),
  };
}

function mapSourceFilterToDiscovery(filter: SourceFilter): string | undefined {
  switch (filter) {
    case 'all':
      return 'all';
    case 'shopping':
      return 'google_shopping';
    default:
      return filter;
  }
}

function interleaveByProvider(items: Reference[]): Reference[] {
  const buckets: Record<string, Reference[]> = {};
  items.forEach(item => {
    const p = item.source_platform || 'other';
    if (!buckets[p]) buckets[p] = [];
    buckets[p].push(item);
  });
  const keys = Object.keys(buckets);
  const result: Reference[] = [];
  let max = 0;
  keys.forEach(k => {
    if (buckets[k].length > max) max = buckets[k].length;
  });
  for (let i = 0; i < max; i++) {
    for (const k of keys) {
      if (i < buckets[k].length) {
        result.push(buckets[k][i]);
      }
    }
  }
  return result;
}

function HomeFeedContent() {
  const searchParams = useSearchParams();
  const { location } = useAuth();
  const {
    keywordExplorerOpen,
    setKeywordExplorerOpen,
    refreshSavedCounts,
  } = useNavigation();

  // Active filters and state
  const [sourceFilter, setSourceFilter] = useState<SourceFilter>('all');
  const [references, setReferences] = useState<Reference[]>([]);
  const [page, setPage] = useState<number>(1);
  const [hasMore, setHasMore] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(true);
  const [apiError, setApiError] = useState<string | null>(null);
  const [errorClass, setErrorClass] = useState<'credits_exhausted' | 'rate_limit' | 'timeout' | 'auth_failure' | 'general' | null>(null);
  const [discoveryStatuses, setDiscoveryStatuses] = useState<Record<string, SourceStatusSummary>>({});

  // Keyword Explorer state
  const [activeKeyword, setActiveKeyword] = useState<string>("");
  const [activeCategory, setActiveCategory] = useState<string>("");
  const [activeSubcategory, setActiveSubcategory] = useState<string>("");

  // Modals and Drawers
  const [activeDrawerReference, setActiveDrawerReference] = useState<Reference | null>(null);
  const [reelModalOpen, setReelModalOpen] = useState<boolean>(false);
  const [activeReelIndex, setActiveReelIndex] = useState<number>(0);

  // Saved Items map
  const [savedMap, setSavedMap] = useState<Record<number, boolean>>({});

  // Fetch sequence tracking & scroll preservation
  const fetchSeqRef = useRef<number>(0);
  const scrollPosRef = useRef<number>(0);

  const openDrawerPreservingScroll = useCallback((ref: Reference) => {
    if (typeof window !== 'undefined') scrollPosRef.current = window.scrollY;
    setActiveDrawerReference(ref);
  }, []);

  const closeDrawerRestoringScroll = useCallback(() => {
    setActiveDrawerReference(null);
    if (typeof window !== 'undefined') {
      requestAnimationFrame(() => window.scrollTo({ top: scrollPosRef.current }));
    }
  }, []);

  const openReelPreservingScroll = useCallback((index: number) => {
    if (typeof window !== 'undefined') scrollPosRef.current = window.scrollY;
    setActiveReelIndex(index);
    setReelModalOpen(true);
  }, []);

  const closeReelRestoringScroll = useCallback(() => {
    setReelModalOpen(false);
    if (typeof window !== 'undefined') {
      requestAnimationFrame(() => window.scrollTo({ top: scrollPosRef.current }));
    }
  }, []);

  // Load saved items from database only when authenticated
  const loadSavedState = useCallback(() => {
    if (!hasAuthToken()) {
      setSavedMap({});
      return;
    }
    getSavedItems()
      .then((items: any[]) => {
        if (Array.isArray(items)) {
          const map: Record<number, boolean> = {};
          items.forEach(item => {
            if (item.item_type === 'reference' && item.reference_id) {
              map[item.reference_id] = true;
            }
          });
          setSavedMap(map);
          refreshSavedCounts();
        }
      })
      .catch(() => {});
  }, [refreshSavedCounts]);

  useEffect(() => {
    loadSavedState();
  }, [loadSavedState]);

  // Handle cross-route URL parameters
  useEffect(() => {
    const openKw = searchParams.get('openKeywords');
    if (openKw === 'true') {
      setKeywordExplorerOpen(true);
    }
    const qParam = searchParams.get('q');
    if (qParam && qParam.trim() && qParam !== activeKeyword) {
      setActiveKeyword(qParam.trim());
      setPage(1);
    }
    const sourceParam = searchParams.get('source');
    if (sourceParam && ['all', 'pinterest', 'instagram', 'youtube', 'shopping', 'reddit'].includes(sourceParam)) {
      setSourceFilter(sourceParam as SourceFilter);
      setPage(1);
    }
    const itemParam = searchParams.get('item');
    if (itemParam && references.length > 0) {
      const targetId = Number(itemParam);
      const foundIdx = references.findIndex(r => r.id === targetId);
      if (foundIdx !== -1 && (!reelModalOpen || activeReelIndex !== foundIdx)) {
        setActiveReelIndex(foundIdx);
        setReelModalOpen(true);
      }
    }
  }, [searchParams, setKeywordExplorerOpen, activeKeyword, references, reelModalOpen, activeReelIndex]);

  // Fetch feed items combining local curated DB (/api/feed) and live unified discovery (/api/discovery/search)
  const loadFeed = useCallback(async (
    pageNum: number,
    isInitial: boolean = false,
    queryTerm?: string,
    currentSourceFilter?: SourceFilter,
    categoryParam?: string,
    subcategoryParam?: string
  ) => {
    const currentSeq = ++fetchSeqRef.current;
    setLoading(true);
    setApiError(null);
    setErrorClass(null);

    try {
      const q = (queryTerm !== undefined ? queryTerm : activeKeyword).trim();
      const activeFilter = currentSourceFilter !== undefined ? currentSourceFilter : sourceFilter;
      const platformParam = activeFilter === 'all' ? undefined : (activeFilter === 'shopping' ? 'google_shopping' : activeFilter);
      const discoverySources = mapSourceFilterToDiscovery(activeFilter);

      const shouldRunDiscovery = Boolean(q) && Boolean(discoverySources);

      let feedRes: FeedResponse | null = null;
      let discoveryRes: any = null;
      let feedErr: any = null;
      let discoveryErr: any = null;

      if (shouldRunDiscovery) {
        const [feedOutcome, discoveryOutcome] = await Promise.allSettled([
          getFeed({
            page: pageNum,
            page_size: 30,
            q: q || undefined,
            platform: platformParam,
          }),
            discoverySearch({
              q,
              sources: discoverySources,
              tab: 'all',
              page: pageNum,
              page_size: 30,
              category: categoryParam !== undefined ? (categoryParam || undefined) : (activeCategory || undefined),
              subcategory: subcategoryParam !== undefined ? (subcategoryParam || undefined) : (activeSubcategory || undefined),
              material: q || undefined,
              city: location.city || undefined,
              district: location.district || location.city || undefined,
              state: location.state || undefined,
              lat: location.lat,
              lng: location.lon,
            }),
        ]);
        if (feedOutcome.status === 'fulfilled') feedRes = feedOutcome.value;
        else feedErr = feedOutcome.reason;
        if (discoveryOutcome.status === 'fulfilled') discoveryRes = discoveryOutcome.value;
        else discoveryErr = discoveryOutcome.reason;
      } else {
        try {
          feedRes = await getFeed({
            page: pageNum,
            page_size: 30,
            q: q || undefined,
            platform: platformParam,
          });
        } catch (err) {
          feedErr = err;
        }
      }

      if (currentSeq !== fetchSeqRef.current) return;

      if (!feedRes && !discoveryRes) {
        const errMessage = (discoveryErr?.message || feedErr?.message || 'Failed to load architectural discovery feed.').toLowerCase();
        if (errMessage.includes('credit') || errMessage.includes('quota') || discoveryErr?.status === 402 || discoveryErr?.status === 429) {
          setErrorClass('credits_exhausted');
        } else if (errMessage.includes('timeout') || errMessage.includes('timed out')) {
          setErrorClass('timeout');
        } else if (errMessage.includes('auth') || discoveryErr?.status === 401 || discoveryErr?.status === 403) {
          setErrorClass('auth_failure');
        } else {
          setErrorClass('general');
        }
        throw feedErr || discoveryErr || new Error('Failed to load architectural discovery feed.');
      }

      if (discoveryRes?.source_statuses) {
        setDiscoveryStatuses(discoveryRes.source_statuses);
      } else if (pageNum === 1 && !shouldRunDiscovery) {
        setDiscoveryStatuses({});
      }

      const mappedDiscovery: Reference[] = Array.isArray(discoveryRes?.results)
        ? discoveryRes.results.map((item: any, idx: number) => mapDiscoveryItemToReference(item, idx))
        : [];
      const feedItems: Reference[] = Array.isArray(feedRes?.items) ? feedRes.items : [];

      // Interleave providers if on 'all' tab so no single provider floods the feed
      const rawCombined = [...mappedDiscovery, ...feedItems];
      const orderedItems = activeFilter === 'all' ? interleaveByProvider(rawCombined) : rawCombined;

      // Deduplicate items
      const makeDedupeKey = (ref: Reference) => {
        const u = (ref.source_url || '').toLowerCase().trim();
        const t = (ref.title || '').toLowerCase().trim();
        return u || t ? `${u}::${t}` : '';
      };

      const combinedItems: Reference[] = [];
      const seenKeys = new Set<string>();
      orderedItems.forEach(ref => {
        const key = makeDedupeKey(ref);
        if (key && seenKeys.has(key)) return;
        if (key) seenKeys.add(key);
        combinedItems.push(ref);
      });

      if (isInitial) {
        setReferences(combinedItems);
      } else {
        setReferences(prev => {
          const existingIds = new Set(prev.map(item => item.id));
          const existingKeys = new Set(prev.map(makeDedupeKey).filter(Boolean));
          const newItems = combinedItems.filter(item => {
            if (existingIds.has(item.id)) return false;
            const key = makeDedupeKey(item);
            if (key && existingKeys.has(key)) return false;
            if (key) existingKeys.add(key);
            return true;
          });
          return [...prev, ...newItems];
        });
      }
      setHasMore(Boolean(feedRes?.has_more || discoveryRes?.pagination?.has_more));
    } catch (err: any) {
      if (currentSeq !== fetchSeqRef.current) return;
      setApiError(err.message || "Failed to load architectural discovery feed.");
    } finally {
      if (currentSeq === fetchSeqRef.current) {
        setLoading(false);
      }
    }
  }, [activeKeyword, activeCategory, activeSubcategory, sourceFilter, location.city, location.state]);

  // Initial load or when active keyword changes
  useEffect(() => {
    setPage(1);
    loadFeed(1, true, activeKeyword, sourceFilter, activeCategory, activeSubcategory);
  }, [activeKeyword, sourceFilter, activeCategory, activeSubcategory, loadFeed]);

  // Source filter switcher
  const handleSourceFilterChange = (newSource: SourceFilter) => {
    setSourceFilter(newSource);
    setPage(1);
  };

  // Keyword selection from the Keyword Explorer
  const handleSelectKeyword = (
    keyword: string,
    groupName?: string,
    category?: string,
    subcategory?: string
  ) => {
    const cleanKw = keyword.trim();
    if (!cleanKw) return;

    setReferences([]);
    setLoading(true);
    setApiError(null);
    setErrorClass(null);

    setActiveKeyword(cleanKw);
    setActiveCategory(category || groupName || "");
    setActiveSubcategory(subcategory || "");
    setPage(1);
    setKeywordExplorerOpen(false);
    loadFeed(1, true, cleanKw, sourceFilter, category, subcategory);
  };

  const handleClearKeyword = () => {
    setReferences([]);
    setLoading(true);
    setActiveKeyword("");
    setActiveCategory("");
    setActiveSubcategory("");
    setDiscoveryStatuses({});
    setPage(1);
    loadFeed(1, true, "", sourceFilter, "", "");
  };

  const handleLoadMore = () => {
    if (!loading && hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      loadFeed(nextPage, false, activeKeyword, sourceFilter, activeCategory, activeSubcategory);
    }
  };

  // Persistent Save toggle
  const handleSaveToggle = async (ref: Reference) => {
    if (!hasAuthToken()) {
      alert('Sign in to save architectural references.');
      return;
    }
    const isCurrentlySaved = Boolean(savedMap[ref.id]);
    setSavedMap(prev => ({ ...prev, [ref.id]: !isCurrentlySaved }));

    try {
      const res = await toggleSavedItem({
        item_type: 'reference',
        reference_id: ref.id,
        project_collection: 'Moodboard'
      });
      setSavedMap(prev => ({ ...prev, [ref.id]: res.saved }));
      refreshSavedCounts();
    } catch {
      setSavedMap(prev => ({ ...prev, [ref.id]: isCurrentlySaved }));
    }
  };

  // Calculate per-tab counts
  const tabCounts = useMemo(() => {
    const counts: Record<string, number> = {
      all: references.length,
      pinterest: references.filter(r => r.source_platform === 'pinterest').length,
      instagram: references.filter(r => r.source_platform === 'instagram').length,
      youtube: references.filter(r => r.source_platform === 'youtube').length,
      shopping: references.filter(r => r.source_platform === 'google_shopping').length,
      reddit: references.filter(r => r.source_platform === 'reddit').length,
    };
    for (const [k, v] of Object.entries(discoveryStatuses)) {
      const key = k === 'google_shopping' ? 'shopping' : k;
      if (v?.result_count != null && counts[key] !== undefined) {
        counts[key] = Math.max(counts[key], v.result_count);
      }
    }
    return counts;
  }, [references, discoveryStatuses]);

  // Display references filtered by active tab
  const displayedReferences = useMemo(() => {
    if (sourceFilter === 'all') return references;
    if (sourceFilter === 'shopping') {
      return references.filter(r => r.source_platform === 'google_shopping');
    }
    return references.filter(r => r.source_platform === sourceFilter);
  }, [references, sourceFilter]);

  const sourceTabs: Array<{ id: SourceFilter; label: string }> = [
    { id: 'all', label: 'All' },
    { id: 'pinterest', label: 'Pinterest' },
    { id: 'instagram', label: 'Instagram' },
    { id: 'youtube', label: 'YouTube' },
    { id: 'shopping', label: 'Shopping' },
    { id: 'reddit', label: 'Reddit' },
  ];

  return (
    <div className="min-h-screen bg-arch-bg dark:bg-arch-dark-bg text-arch-charcoal dark:text-arch-dark-text flex flex-col font-sans transition-colors duration-200">
      
      {/* 1. KEYWORD EXPLORER PANEL */}
      <KeywordExplorerPanel
        isOpen={keywordExplorerOpen}
        onClose={() => setKeywordExplorerOpen(false)}
        onSelectKeyword={handleSelectKeyword}
        selectedKeyword={activeKeyword}
      />

      {/* 2. ONE CONTEXT BAR (SINGLE ROW): selected material - Category > Subcategory - location, with buttons "Change" and "Find vendors" */}
      <section className="sticky top-16 z-30 w-full bg-white/95 dark:bg-arch-dark-bg/95 backdrop-blur-md border-b border-arch-border dark:border-arch-dark-border py-2.5 px-4 sm:px-6 lg:px-8 transition-colors">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4 text-secondary">
          
          {/* Left: Selected material (Category > Subcategory > Material) */}
          <div className="flex items-center gap-2 min-w-0">
            <Layers className="w-4 h-4 text-arch-terracotta shrink-0" />
            <div className="flex items-center gap-1.5 truncate">
              {activeKeyword ? (
                <>
                  <span className="text-arch-muted dark:text-arch-dark-muted truncate">
                    {activeCategory ? `${activeCategory} > ` : ''}
                    {activeSubcategory ? `${activeSubcategory} > ` : ''}
                  </span>
                  <span className="font-semibold text-arch-charcoal dark:text-stone-100 truncate">
                    {activeKeyword}
                  </span>
                </>
              ) : (
                <span className="font-semibold text-arch-charcoal dark:text-stone-100">
                  All Architectural Materials
                </span>
              )}
            </div>
            <button
              onClick={() => setKeywordExplorerOpen(true)}
              type="button"
              className="px-2.5 py-1 rounded-lg text-xs font-semibold bg-stone-100 hover:bg-stone-200 dark:bg-arch-dark-surface dark:hover:bg-stone-800 text-arch-charcoal dark:text-stone-200 border border-arch-border dark:border-arch-dark-border transition-colors cursor-pointer shrink-0 ml-1"
              title="Open Keyword Explorer"
            >
              Change
            </button>
            {activeKeyword && (
              <button
                onClick={handleClearKeyword}
                type="button"
                className="p-1 rounded-lg text-arch-muted hover:text-arch-charcoal dark:hover:text-stone-100 transition-colors"
                title="Clear selected material"
                aria-label="Clear selected material"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Right: Location & Find vendors button */}
          <div className="flex items-center gap-3 shrink-0">
            <div className="flex items-center gap-1.5 text-secondary text-arch-muted dark:text-arch-dark-muted hidden sm:flex">
              <MapPin className="w-4 h-4 text-arch-terracotta shrink-0" />
              <span className="font-medium text-arch-charcoal dark:text-stone-200 truncate max-w-[180px]">
                {location.city || "All India"}, {location.state || "India"}
              </span>
            </div>

            <Link
              href={`/sourcing${activeKeyword ? `?q=${encodeURIComponent(activeKeyword)}` : ''}${location.city ? `&city=${encodeURIComponent(location.city)}` : ''}`}
              className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-arch-terracotta hover:bg-arch-terracotta-dark text-white text-secondary font-semibold transition-all shadow-xs shrink-0"
              title={`Find verified trade suppliers for ${activeKeyword || 'materials'}`}
            >
              <Store className="w-4 h-4" />
              <span>Find vendors</span>
            </Link>
          </div>

        </div>
      </section>

      {/* 3. ONE ROW OF SOURCE TABS: All, Pinterest, Instagram, YouTube, Shopping, Reddit, with per-tab result counts */}
      <section className="w-full bg-arch-bg dark:bg-arch-dark-bg border-b border-arch-border/50 dark:border-arch-dark-border/50 px-4 sm:px-6 lg:px-8 py-3">
        <div className="max-w-7xl mx-auto flex items-center gap-2 overflow-x-auto scrollbar-none">
          {sourceTabs.map((tab) => {
            const isActive = sourceFilter === tab.id;
            const count = tabCounts[tab.id] ?? 0;
            return (
              <button
                key={tab.id}
                onClick={() => handleSourceFilterChange(tab.id)}
                type="button"
                className={`px-3.5 py-1.5 rounded-xl text-secondary transition-all flex items-center gap-1.5 shrink-0 cursor-pointer ${
                  isActive
                    ? 'bg-arch-charcoal text-white dark:bg-stone-100 dark:text-arch-dark-bg font-semibold shadow-xs'
                    : 'bg-stone-100 hover:bg-stone-200 dark:bg-arch-dark-surface dark:hover:bg-stone-800 text-arch-muted dark:text-arch-dark-muted hover:text-arch-charcoal dark:hover:text-stone-100 font-medium'
                }`}
              >
                <span>{tab.label}</span>
                <span className={`text-xs px-1.5 py-0.5 rounded-full ${
                  isActive
                    ? 'bg-white/20 dark:bg-black/20 text-white dark:text-arch-dark-bg'
                    : 'bg-stone-200/70 dark:bg-stone-700/60 text-stone-600 dark:text-stone-300'
                }`}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </section>

      {/* 4. MAIN FULL-WIDTH MASONRY FEED (4-5 columns on wide desktop) */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        {/* Loading State */}
        {loading && references.length === 0 ? (
          <div className="py-28 flex flex-col items-center justify-center text-arch-muted dark:text-arch-dark-muted">
            <div className="w-10 h-10 border-3 border-arch-terracotta border-t-transparent rounded-full animate-spin mb-4" />
            <p className="font-serif font-semibold text-heading text-arch-charcoal dark:text-stone-200">
              Discovering architectural specifications...
            </p>
            <p className="text-secondary text-arch-muted dark:text-arch-dark-muted mt-1.5">
              Querying Pinterest, Instagram, YouTube, Shopping, Reddit and design catalogs
            </p>
          </div>
        ) : errorClass === 'credits_exhausted' ? (
          /* Designed Screen: Credits Exhausted */
          <div className="py-24 text-center px-4 max-w-lg mx-auto">
            <div className="w-16 h-16 rounded-2xl bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 flex items-center justify-center mx-auto text-amber-600 mb-4">
              <Sparkles className="w-8 h-8" />
            </div>
            <h3 className="text-heading font-serif font-bold text-arch-charcoal dark:text-stone-100 mb-2">
              Discovery API Credits Exhausted
            </h3>
            <p className="text-body-base text-arch-muted dark:text-arch-dark-muted mb-6 leading-relaxed">
              The live search provider has reached its credit allowance for this session. Curated architectural catalog specifications remain fully accessible.
            </p>
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={() => setKeywordExplorerOpen(true)}
                className="px-5 py-2.5 rounded-xl bg-arch-terracotta text-white font-semibold text-body-base hover:bg-arch-terracotta-dark transition-colors shadow-xs cursor-pointer"
              >
                Browse 6,319 Catalog Materials
              </button>
            </div>
          </div>
        ) : apiError && displayedReferences.length === 0 ? (
          /* Designed Screen: Error State */
          <div className="py-24 text-center px-4 max-w-lg mx-auto">
            <div className="w-16 h-16 rounded-2xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-900/60 flex items-center justify-center mx-auto text-red-500 mb-4">
              <AlertCircle className="w-8 h-8" />
            </div>
            <h3 className="text-heading font-serif font-bold text-arch-charcoal dark:text-stone-100 mb-2">
              Unable to Load Discovery Feed
            </h3>
            <p className="text-body-base text-arch-muted dark:text-arch-dark-muted mb-6 leading-relaxed">
              {apiError}
            </p>
            <button
              onClick={() => loadFeed(1, true, activeKeyword, sourceFilter, activeCategory, activeSubcategory)}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-arch-charcoal dark:bg-stone-100 text-white dark:text-stone-900 font-semibold text-body-base hover:opacity-90 transition-opacity shadow-xs cursor-pointer"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Retry Search</span>
            </button>
          </div>
        ) : displayedReferences.length === 0 ? (
          /* Designed Screen: Empty Results */
          <div className="py-24 text-center px-4 max-w-lg mx-auto">
            <div className="w-16 h-16 rounded-2xl bg-stone-100 dark:bg-arch-dark-surface flex items-center justify-center mx-auto text-arch-terracotta mb-4">
              <Layers className="w-8 h-8" />
            </div>
            <h3 className="text-heading font-serif font-bold text-arch-charcoal dark:text-stone-100 mb-2">
              {sourceFilter !== 'all'
                ? `No results in ${sourceTabs.find(t => t.id === sourceFilter)?.label}`
                : "No architectural specimens found"}
            </h3>
            <p className="text-body-base text-arch-muted dark:text-arch-dark-muted mb-6 leading-relaxed">
              {sourceFilter !== 'all'
                ? `There are no specimens for "${activeKeyword || 'this material'}" under this source tab. Switch to All Sources or explore other materials.`
                : `No visual references were returned for "${activeKeyword}". Try browsing the material catalogue across 10 physical construction categories.`}
            </p>
            <div className="flex items-center justify-center gap-3">
              {sourceFilter !== 'all' && (
                <button
                  onClick={() => setSourceFilter('all')}
                  className="px-5 py-2.5 rounded-xl bg-arch-terracotta text-white font-semibold text-body-base hover:bg-arch-terracotta-dark transition-colors shadow-xs cursor-pointer"
                >
                  View All Sources
                </button>
              )}
              <button
                onClick={() => setKeywordExplorerOpen(true)}
                className="px-5 py-2.5 rounded-xl text-body-base font-semibold bg-stone-100 hover:bg-stone-200 dark:bg-arch-dark-surface dark:hover:bg-stone-800 text-arch-charcoal dark:text-stone-200 border border-arch-border dark:border-arch-dark-border transition-colors shadow-xs cursor-pointer"
              >
                Open Material Explorer
              </button>
            </div>
          </div>
        ) : (
          /* Masonry Feed */
          <PinterestMasonryFeed
            references={displayedReferences}
            onOpenDetails={openDrawerPreservingScroll}
            onSaveToggle={handleSaveToggle}
            onSelectCard={(ref, index) => {
              openReelPreservingScroll(index);
            }}
            isSavedMap={savedMap}
            onLoadMore={handleLoadMore}
            hasMore={hasMore}
            loading={loading}
          />
        )}
      </main>

      {/* 5. CONTEXTUAL DETAIL DRAWER */}
      <ContextualDetailsDrawer
        isOpen={Boolean(activeDrawerReference)}
        onClose={closeDrawerRestoringScroll}
        reference={activeDrawerReference}
      />

      {/* 6. FULL SCREEN REEL / VIDEO MODAL */}
      {reelModalOpen && (
        <FullScreenReelModal
          isOpen={reelModalOpen}
          initialIndex={activeReelIndex}
          references={displayedReferences}
          onClose={closeReelRestoringScroll}
          onOpenDetails={(ref) => {
            setReelModalOpen(false);
            openDrawerPreservingScroll(ref);
          }}
          onSaveToggle={handleSaveToggle}
          isSavedMap={savedMap}
          onLoadMore={handleLoadMore}
        />
      )}
    </div>
  );
}

export default function HomePage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-arch-bg dark:bg-arch-dark-bg" />}>
      <HomeFeedContent />
    </Suspense>
  );
}
