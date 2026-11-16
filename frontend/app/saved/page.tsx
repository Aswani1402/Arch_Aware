"use client";

import React, { useState, useEffect, useMemo } from 'react';
import Link from 'next/link';
import {
  Bookmark, Layers, Building2, Package, ArrowRight, Trash2,
  Play, ExternalLink, Compass, ArrowLeft, Image as ImageIcon, MapPin
} from 'lucide-react';
import { SavedItem, Reference } from '@/types';
import { getSavedItems, toggleSavedItem, hasAuthToken } from '@/lib/api';
import { FullScreenReelModal } from '@/components/FullScreenReelModal';
import { ContextualDetailsDrawer } from '@/components/ContextualDetailsDrawer';

function resolveDisplayVerification(status?: string | null, isPotential?: boolean): {
  category: 'VERIFIED' | 'UNVERIFIED' | 'POTENTIAL' | 'UNKNOWN';
  label: string;
  badgeClass: string;
} {
  const norm = (status || '').toUpperCase().trim();
  if (isPotential || norm === 'POTENTIAL' || norm === 'POTENTIAL_GOOGLE_PLACE') {
    return {
      category: 'POTENTIAL',
      label: 'Potential',
      badgeClass: 'bg-amber-950/70 text-amber-300 border-amber-700/70',
    };
  }
  if (
    norm === 'VERIFIED' ||
    norm === 'VERIFIED_EXACT' ||
    norm === 'MANUFACTURER_CONFIRMED' ||
    norm === 'SUPPLIER_CONFIRMED'
  ) {
    return {
      category: 'VERIFIED',
      label: 'Verified',
      badgeClass: 'bg-emerald-950/70 text-emerald-300 border-emerald-700/70',
    };
  }
  if (norm === 'UNVERIFIED') {
    return {
      category: 'UNVERIFIED',
      label: 'Unverified',
      badgeClass: 'bg-stone-800 text-stone-300 border-stone-700',
    };
  }
  return {
    category: 'UNKNOWN',
    label: 'Unknown',
    badgeClass: 'bg-slate-900 text-slate-300 border-slate-700',
  };
}

export default function SavedPage() {
  const [savedItems, setSavedItems] = useState<SavedItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [requiresAuth, setRequiresAuth] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'reference' | 'product' | 'supplier'>('all');

  // Full Screen Reel Modal state for saved items
  const [reelModalOpen, setReelModalOpen] = useState(false);
  const [activeReelIndex, setActiveReelIndex] = useState(0);

  // Contextual Details Drawer state
  const [activeDrawerReference, setActiveDrawerReference] = useState<Reference | null>(null);

  const fetchItems = () => {
    if (!hasAuthToken()) {
      setSavedItems([]);
      setRequiresAuth(true);
      setLoading(false);
      return;
    }
    setRequiresAuth(false);
    setLoading(true);
    getSavedItems()
      .then(res => {
        setSavedItems(res || []);
        setLoading(false);
      })
      .catch((err) => {
        if (!hasAuthToken()) {
          setRequiresAuth(true);
        } else {
          console.error("Error fetching saved items:", err);
        }
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchItems();
  }, []);

  const handleRemove = async (item: SavedItem) => {
    try {
      await toggleSavedItem({
        item_type: item.item_type,
        reference_id: item.reference_id,
        product_id: item.product_id,
        supplier_id: item.supplier_id
      });
      // Immediately filter out removed item
      setSavedItems(prev => prev.filter(i => i.id !== item.id));
    } catch (e) {
      console.error("Error removing saved item:", e);
    }
  };

  // Convert saved reference items to Reference[] list for FullScreenReelModal
  const savedReferences: Reference[] = useMemo(() => {
    return savedItems
      .filter(i => i.item_type === 'reference' && i.item_data)
      .map(i => {
        const d = i.item_data;
        return {
          id: d.id || i.reference_id || i.id,
          title: d.title || 'Architectural Inspiration',
          slug: d.slug || `ref-${i.id}`,
          source_platform: d.source_platform || 'curated',
          source_url: d.source_url || '#',
          creator_name: d.creator_name || d.architect_name || 'Architectural Creator',
          creator_url: d.creator_url,
          thumbnail_url: d.thumbnail_url,
          media_url: d.media_url || d.thumbnail_url,
          inspiration_image_url: d.inspiration_image_url || d.thumbnail_url,
          inspiration_source_url: d.inspiration_source_url || d.source_url,
          video_embed_id: d.video_embed_id,
          video_duration: d.video_duration,
          is_short: Boolean(d.is_short),
          source_domain: d.source_domain,
          category_name: d.category_name,
          material_tags: d.material_tags,
          location_context: d.location_context,
          image_attribution: d.image_attribution,
          colors_and_finishes: d.colors_and_finishes,
          content_type: d.content_type || (d.video_embed_id ? 'youtube_walkthrough' : 'architectural_project'),
          description: d.description,
          matched_products_count: d.matched_products_count || 0,
          product_match_status: d.product_match_status || 'unidentified',
          verification_status: d.verification_status || 'UNKNOWN'
        } as Reference;
      });
  }, [savedItems]);

  const savedMap = useMemo(() => {
    const map: Record<number, boolean> = {};
    savedItems.forEach(i => {
      if (i.reference_id) map[i.reference_id] = true;
    });
    return map;
  }, [savedItems]);

  const handleOpenReel = (refId: number) => {
    const idx = savedReferences.findIndex(r => r.id === refId);
    if (idx !== -1) {
      setActiveReelIndex(idx);
      setReelModalOpen(true);
    }
  };

  const filteredItems = savedItems.filter(item => {
    if (activeTab === 'all') return true;
    return item.item_type === activeTab;
  });

  return (
    <div className="min-h-screen bg-arch-bg dark:bg-arch-dark-bg text-arch-charcoal dark:text-stone-100 flex flex-col font-sans transition-colors">
      {/* Sticky Top Header Bar */}
      <header className="sticky top-0 z-30 bg-white/90 dark:bg-arch-dark-surface/90 backdrop-blur-md border-b border-arch-border dark:border-arch-dark-border px-4 sm:px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Link
              href="/"
              className="p-1.5 rounded-lg bg-stone-100 hover:bg-stone-200 dark:bg-arch-dark-card dark:hover:bg-stone-800 text-arch-charcoal dark:text-stone-300 transition-colors flex items-center gap-1.5 text-xs font-medium border border-arch-border dark:border-arch-dark-border"
            >
              <ArrowLeft className="w-4 h-4 text-amber-500" />
              <span>Back to Discovery</span>
            </Link>

            <span className="font-serif text-sm sm:text-base font-bold text-arch-charcoal dark:text-stone-100 uppercase tracking-tight">
              Saved <span className="text-amber-500 font-sans text-xs">Moodboard</span>
            </span>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-mono font-medium">
              {savedItems.length} Saved {savedItems.length === 1 ? 'Item' : 'Items'}
            </span>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        {/* Title & Description */}
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <Bookmark className="w-3.5 h-3.5 fill-current" />
            <span>Curated Architectural Inspiration & Sourcing Specs</span>
          </div>
          <h1 className="font-serif text-2xl sm:text-3xl font-bold text-arch-charcoal dark:text-stone-100">
            Saved References & Materials
          </h1>
          <p className="text-xs text-stone-400 max-w-2xl">
            Your collection of architectural designs, video walkthroughs, and material specifications. Click any visual item to open the full-screen swiper.
          </p>
        </div>

        {/* Tab Filter */}
        <div className="flex items-center gap-2 border-b border-stone-800 pb-3 text-xs font-medium overflow-x-auto">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3.5 py-1.5 rounded-full transition-all ${activeTab === 'all'
                ? 'bg-amber-500 text-stone-950 font-bold shadow-xs'
                : 'bg-stone-100 dark:bg-arch-dark-surface text-stone-600 dark:text-stone-300 hover:bg-stone-200 dark:hover:bg-stone-800 border border-arch-border dark:border-arch-dark-border'
              }`}
          >
            All Items ({savedItems.length})
          </button>
          <button
            onClick={() => setActiveTab('reference')}
            className={`px-3.5 py-1.5 rounded-full transition-all flex items-center gap-1.5 ${activeTab === 'reference'
                ? 'bg-amber-500 text-stone-950 font-bold shadow-xs'
                : 'bg-stone-100 dark:bg-arch-dark-surface text-stone-600 dark:text-stone-300 hover:bg-stone-200 dark:hover:bg-stone-800 border border-arch-border dark:border-arch-dark-border'
              }`}
          >
            <Compass className="w-3.5 h-3.5" />
            <span>Visual References ({savedItems.filter(i => i.item_type === 'reference').length})</span>
          </button>
          <button
            onClick={() => setActiveTab('product')}
            className={`px-3.5 py-1.5 rounded-full transition-all flex items-center gap-1.5 ${activeTab === 'product'
                ? 'bg-amber-500 text-stone-950 font-bold shadow-xs'
                : 'bg-stone-100 dark:bg-arch-dark-surface text-stone-600 dark:text-stone-300 hover:bg-stone-200 dark:hover:bg-stone-800 border border-arch-border dark:border-arch-dark-border'
              }`}
          >
            <Package className="w-3.5 h-3.5" />
            <span>Products ({savedItems.filter(i => i.item_type === 'product').length})</span>
          </button>
          <button
            onClick={() => setActiveTab('supplier')}
            className={`px-3.5 py-1.5 rounded-full transition-all flex items-center gap-1.5 ${activeTab === 'supplier'
                ? 'bg-amber-500 text-stone-950 font-bold shadow-xs'
                : 'bg-stone-100 dark:bg-arch-dark-surface text-stone-600 dark:text-stone-300 hover:bg-stone-200 dark:hover:bg-stone-800 border border-arch-border dark:border-arch-dark-border'
              }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>Suppliers ({savedItems.filter(i => i.item_type === 'supplier').length})</span>
          </button>
        </div>

        {/* Content Loading State */}
        {loading && (
          <div className="py-24 text-center text-stone-500 space-y-2">
            <div className="w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs">Loading saved moodboards...</p>
          </div>
        )}

        {/* Empty / Unauthenticated State */}
        {!loading && requiresAuth && (
          <div className="py-20 text-center rounded-3xl bg-stone-900/50 border border-stone-800/80 p-8 space-y-3 max-w-lg mx-auto">
            <Bookmark className="w-10 h-10 text-amber-400 mx-auto" />
            <h3 className="font-serif text-lg font-bold text-stone-200">
              Sign in to view your saved collection
            </h3>
            <p className="text-xs text-stone-400">
              Your saved architectural inspiration, specifications, and supplier contacts are linked to your MATERIQ account.
            </p>
            <Link
              href="/login"
              className="inline-flex items-center gap-1.5 px-5 py-2.5 bg-amber-500 text-stone-950 font-bold text-xs rounded-full hover:bg-amber-400 transition-colors shadow-md"
            >
              <span>Sign In</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        )}

        {/* Empty State (Authenticated) */}
        {!loading && !requiresAuth && filteredItems.length === 0 && (
          <div className="py-20 text-center rounded-3xl bg-stone-900/50 border border-stone-800/80 p-8 space-y-3 max-w-lg mx-auto">
            <Bookmark className="w-10 h-10 text-stone-600 mx-auto" />
            <h3 className="font-serif text-lg font-bold text-stone-200">
              No saved items in this view
            </h3>
            <p className="text-xs text-stone-400">
              Browse the discovery feed and tap &ldquo;Save&rdquo; on any architectural photo, Short, or video walkthrough to collect them here.
            </p>
            <Link
              href="/"
              className="inline-flex items-center gap-1.5 px-4 py-2 bg-amber-500 text-stone-950 font-bold text-xs rounded-full hover:bg-amber-400 transition-colors shadow-md"
            >
              <span>Explore Architectural Discovery</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        )}

        {/* 1. MASONRY LAYOUT FOR SAVED VISUAL REFERENCES */}
        {!loading && !requiresAuth && (activeTab === 'all' || activeTab === 'reference') && (
          <div className="space-y-4">
            {activeTab === 'all' && savedItems.some(i => i.item_type === 'reference') && (
              <h2 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                <Compass className="w-3.5 h-3.5" />
                <span>Visual References & Walkthroughs</span>
              </h2>
            )}

            <div className="columns-1 sm:columns-2 md:columns-3 lg:columns-4 gap-4 space-y-4">
              {filteredItems
                .filter(item => item.item_type === 'reference' && item.item_data)
                .map((item) => {
                  const d = item.item_data;
                  const isVideo = Boolean(d.video_embed_id);
                  const imageUrl = d.inspiration_image_url || d.thumbnail_url || d.media_url;

                  return (
                    <div
                      key={item.id}
                      onClick={() => handleOpenReel(d.id || item.reference_id)}
                      className="break-inside-avoid group relative rounded-2xl overflow-hidden bg-white dark:bg-arch-dark-card border border-arch-border dark:border-arch-dark-border hover:border-arch-terracotta/40 shadow-card hover:shadow-xl transition-all duration-300 cursor-pointer flex flex-col"
                    >
                      {/* Media Image Container */}
                      <div className="relative aspect-[4/3] w-full overflow-hidden bg-stone-950">
                        <img referrerPolicy="no-referrer"
                          src={imageUrl || ""}
                          alt={d.title}
                          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                          loading="lazy"
                        />

                        {/* Top Badges */}
                        <div className="absolute top-2.5 left-2.5 right-2.5 flex items-center justify-between pointer-events-none">
                          {/* Media Type Indicator */}
                          {isVideo ? (
                            <span className="px-2 py-0.5 rounded-full bg-black/80 backdrop-blur-md text-xs font-bold text-white flex items-center gap-1">
                              <Play className="w-2.5 h-2.5 fill-current text-rose-400" />
                              <span>{d.is_short ? 'Short' : (d.video_duration || 'Video')}</span>
                            </span>
                          ) : (
                            <span className="px-2 py-0.5 rounded-full bg-stone-900/90 border border-stone-700 text-stone-300 text-xs font-semibold flex items-center gap-1">
                              <ImageIcon className="w-2.5 h-2.5 text-amber-400" />
                              <span>Image</span>
                            </span>
                          )}

                          {/* Unsave Button */}
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRemove(item);
                            }}
                            className="p-1.5 rounded-full bg-black/60 hover:bg-rose-600/90 text-stone-300 hover:text-white backdrop-blur-md transition-colors pointer-events-auto"
                            title="Remove from saved"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </div>

                      {/* Card Meta Content */}
                      <div className="p-3.5 space-y-1.5 bg-white/95 dark:bg-arch-dark-card/95 flex-1 flex flex-col justify-between">
                        <div className="space-y-1">
                          <div className="flex items-center justify-between gap-2 pb-1">
                            <span className="text-xs font-mono uppercase text-stone-400">
                              {d.source_platform || 'curated'}
                            </span>
                            {(() => {
                              const badge = resolveDisplayVerification(d.verification_status, false);
                              return (
                                <span
                                  data-verification-state={badge.category}
                                  className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${badge.badgeClass}`}
                                >
                                  {badge.label}
                                </span>
                              );
                            })()}
                          </div>
                          <h3 className="font-serif font-bold text-arch-charcoal dark:text-stone-100 text-xs sm:text-sm leading-snug line-clamp-2 group-hover:text-arch-terracotta transition-colors">
                            {d.title}
                          </h3>

                          <div className="flex items-center justify-between text-xs text-stone-400 pt-0.5">
                            <span className="truncate text-stone-300 text-xs">
                              {d.architect_name || d.creator_name || "Architectural Source"}
                            </span>
                            {d.source_domain && (
                              <span className="text-xs font-mono text-stone-500">
                                {d.source_domain}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Bottom Actions */}
                        <div className="pt-2 border-t border-stone-800/80 flex items-center justify-between text-xs">
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              const refObj = savedReferences.find(r => r.id === (d.id || item.reference_id));
                              if (refObj) setActiveDrawerReference(refObj);
                            }}
                            className="text-amber-400 hover:text-amber-300 text-xs font-semibold flex items-center gap-1"
                          >
                            <Layers className="w-3 h-3" />
                            <span>More Details</span>
                          </button>

                          <span className="text-xs text-stone-500 font-mono">
                            Tap to view reel &uarr;&darr;
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        )}

        {/* 2. GRID LAYOUT FOR SAVED PRODUCTS & SUPPLIERS */}
        {!loading && !requiresAuth && (activeTab === 'all' || activeTab === 'product' || activeTab === 'supplier') && (
          <div className="space-y-4 pt-4">
            {activeTab === 'all' && savedItems.some(i => i.item_type === 'product' || i.item_type === 'supplier') && (
              <h2 className="text-xs font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1.5">
                <Package className="w-3.5 h-3.5" />
                <span>Saved Products & Trade Suppliers</span>
              </h2>
            )}

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredItems
                .filter(item => item.item_type === 'product' || item.item_type === 'supplier')
                .map((item) => {
                  const d = item.item_data || {};
                  return (
                    <div
                      key={item.id}
                      className="bg-white dark:bg-arch-dark-card rounded-2xl border border-arch-border dark:border-arch-dark-border p-4 hover:border-arch-terracotta/40 shadow-card transition-all flex flex-col justify-between space-y-3"
                    >
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-xs text-stone-500 gap-2">
                          <div className="flex items-center gap-2">
                            <span className="uppercase text-xs font-bold text-amber-400">
                              {item.item_type}
                            </span>
                            {(() => {
                              const badge = resolveDisplayVerification(d.verification_status, Boolean(d.is_potential));
                              return (
                                <span
                                  data-verification-state={badge.category}
                                  className={`px-2 py-0.5 rounded-full text-xs font-semibold border ${badge.badgeClass}`}
                                >
                                  {badge.label}
                                </span>
                              );
                            })()}
                          </div>
                          <button
                            onClick={() => handleRemove(item)}
                            className="p-1 text-stone-500 hover:text-rose-400 transition-colors"
                            title="Remove"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>

                        {d.image_url && (
                          <div className="relative aspect-video rounded-xl overflow-hidden bg-stone-950 mb-2">
                            <img referrerPolicy="no-referrer"
                              src={d.image_url}
                              alt={d.name}
                              className="w-full h-full object-cover"
                            />
                          </div>
                        )}

                        <h3 className="font-semibold text-stone-100 text-sm line-clamp-1">
                          {d.name}
                        </h3>

                        {d.material_type && (
                          <p className="text-xs text-stone-400">
                            {d.material_type} &bull; {d.manufacturer_name}
                          </p>
                        )}

                        {d.city && (
                          <p className="text-xs text-stone-400 flex items-center gap-1">
                            <MapPin className="w-3 h-3 text-stone-500" />
                            <span>{d.city}, {d.state}</span>
                          </p>
                        )}
                      </div>

                      <div className="pt-2 border-t border-stone-800 flex items-center justify-between text-xs">
                        {item.item_type === 'product' && item.product_id && (
                          <Link
                            href={`/product/${item.product_id}`}
                            className="text-amber-400 hover:underline font-semibold"
                          >
                            View Product & Vendors &rarr;
                          </Link>
                        )}
                        {item.item_type === 'supplier' && item.supplier_id && (
                          <Link
                            href={`/supplier/${item.supplier_id}`}
                            className="text-amber-400 hover:underline font-semibold"
                          >
                            View Supplier Catalog &rarr;
                          </Link>
                        )}
                      </div>
                    </div>
                  );
                })}
            </div>
          </div>
        )}
      </main>

      {/* Full Screen Vertical Swiper for Saved Media */}
      {reelModalOpen && savedReferences.length > 0 && (
        <FullScreenReelModal
          isOpen={reelModalOpen}
          initialIndex={activeReelIndex}
          references={savedReferences}
          onClose={() => setReelModalOpen(false)}
          onOpenDetails={(ref) => setActiveDrawerReference(ref)}
          onSaveToggle={(ref) => {
            const item = savedItems.find(i => i.reference_id === ref.id);
            if (item) handleRemove(item);
          }}
          isSavedMap={savedMap}
        />
      )}

      {/* Contextual Details Drawer */}
      {activeDrawerReference && (
        <ContextualDetailsDrawer
          isOpen={Boolean(activeDrawerReference)}
          onClose={() => setActiveDrawerReference(null)}
          reference={activeDrawerReference}
        />
      )}
    </div>
  );
}
