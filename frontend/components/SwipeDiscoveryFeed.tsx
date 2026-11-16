"use client";

import React, { useState, useEffect, useCallback, useRef } from 'react';
import Link from 'next/link';
import {
  ChevronUp, ChevronDown, Bookmark, Share2, Layers, FileText,
  ExternalLink, Building2, MapPin, Phone, Globe, ShieldCheck,
  CheckCircle2, AlertCircle, Compass, ArrowRight, Eye, RefreshCw,
  ImageOff, Sparkles, Tag, MessageSquare, Mail, PhoneCall,
  Check, Info, ChevronRight, Award, HelpCircle
} from 'lucide-react';
import {
  Reference,
  InspirationMaterial,
  Product,
  HierarchicalSourcingResponse,
  SourcingSupplierResult,
  SourcingTierResult
} from '@/types';
import { SourceBadge } from './SourceBadge';
import { VerificationBadge } from './VerificationBadge';
import { QuotationModal } from './QuotationModal';
import {
  getReferenceDetail,
  getProductDetail,
  searchSourcing,
  toggleSavedItem,
  getSavedItems,
  hasAuthToken
} from '@/lib/api';
import { useAuth } from '@/lib/authContext';

interface SwipeDiscoveryFeedProps {
  references: Reference[];
  onLoadMore?: () => void;
  hasMore?: boolean;
  onOpenDetails?: (ref: Reference) => void;
  onOpenSaveModal?: (item: any) => void;
  onSelectCategory?: (category: string) => void;
}

export const SwipeDiscoveryFeed: React.FC<SwipeDiscoveryFeedProps> = ({
  references,
  onLoadMore,
  hasMore = false,
  onOpenDetails,
  onOpenSaveModal,
  onSelectCategory,
}) => {
  const { location } = useAuth();
  const [activeIndex, setActiveIndex] = useState(0);
  const [activeReferenceDetail, setActiveReferenceDetail] = useState<Reference | null>(null);
  const [selectedMaterialIndex, setSelectedMaterialIndex] = useState(0);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [sourcingData, setSourcingData] = useState<HierarchicalSourcingResponse | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [sourcingLoading, setSourcingLoading] = useState(false);
  const [savedReferenceIds, setSavedReferenceIds] = useState<Set<number>>(new Set());
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [activeQuotation, setActiveQuotation] = useState<{ product: any; supplier: any } | null>(null);
  const [isDescExpanded, setIsDescExpanded] = useState(false);
  const [expandedTiers, setExpandedTiers] = useState<Record<number, boolean>>({
    1: true,
    2: true,
    3: false,
    4: false,
    5: false,
  });

  // Scroll container and card refs for swipe/scroll detection
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const cardRefs = useRef<(HTMLDivElement | null)[]>([]);
  const isUserScrolling = useRef(false);
  const touchStartY = useRef<number | null>(null);
  const touchStartTime = useRef<number>(0);
  const lastWheelTime = useRef<number>(0);

  // Cache fetched reference details to avoid refetching on scroll
  const refDetailCache = useRef<Map<number, Reference>>(new Map<number, Reference>());
  const sourcingCache = useRef<Map<string, HierarchicalSourcingResponse>>(new Map<string, HierarchicalSourcingResponse>());

  const currentRef = references[activeIndex] || null;

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // Preload upcoming images
  useEffect(() => {
    if (references.length === 0) return;
    const preloadIndices = [activeIndex + 1, activeIndex + 2];
    preloadIndices.forEach((idx) => {
      if (idx < references.length) {
        const item = references[idx];
        const imgUrl = item.inspiration_image_url || item.thumbnail_url || item.media_url;
        if (imgUrl && typeof window !== 'undefined') {
          const img = new Image();
          img.src = imgUrl;
        }
      }
    });
  }, [activeIndex, references]);

  // Load saved references
  useEffect(() => {
    if (!hasAuthToken()) return;
    getSavedItems()
      .then((items) => {
        const savedIds = new Set<number>();
        items.forEach((item) => {
          if (item.item_type === 'reference' && item.reference_id) {
            savedIds.add(item.reference_id);
          }
        });
        setSavedReferenceIds(savedIds);
      })
      .catch(() => {});
  }, []);

  // Set up IntersectionObserver on card elements to synchronize active reference with scroll
  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container || cardRefs.current.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && entry.intersectionRatio >= 0.55) {
            const index = Number(entry.target.getAttribute('data-index'));
            if (!isNaN(index) && index !== activeIndex) {
              setActiveIndex(index);
              setIsDescExpanded(false);
              setSelectedMaterialIndex(0);
            }
          }
        });
      },
      {
        root: container,
        threshold: [0.55],
      }
    );

    cardRefs.current.forEach((el) => {
      if (el) observer.observe(el);
    });

    return () => observer.disconnect();
  }, [references.length, activeIndex]);

  // Programmatic scroll to card index
  const scrollToCard = useCallback((index: number) => {
    if (index < 0 || index >= references.length) return;
    const targetCard = cardRefs.current[index];
    if (targetCard && scrollContainerRef.current) {
      isUserScrolling.current = true;
      targetCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      setActiveIndex(index);
      setIsDescExpanded(false);
      setSelectedMaterialIndex(0);
      setTimeout(() => {
        isUserScrolling.current = false;
      }, 500);
    }
  }, [references.length]);

  // Keyboard controls: ArrowUp and ArrowDown
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }
      if (e.key === 'ArrowUp' || e.key === 'k') {
        e.preventDefault();
        scrollToCard(activeIndex - 1);
      } else if (e.key === 'ArrowDown' || e.key === 'j' || e.key === ' ') {
        e.preventDefault();
        if (activeIndex < references.length - 1) {
          scrollToCard(activeIndex + 1);
        } else if (hasMore && onLoadMore) {
          onLoadMore();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeIndex, references.length, hasMore, onLoadMore, scrollToCard]);

  // Touch Swipe Handlers for Mobile (Swipe Up to Next, Swipe Down to Prev)
  const handleTouchStart = (e: React.TouchEvent) => {
    touchStartY.current = e.touches[0].clientY;
    touchStartTime.current = Date.now();
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (touchStartY.current === null) return;
    const touchEndY = e.changedTouches[0].clientY;
    const deltaY = touchStartY.current - touchEndY;
    const duration = Date.now() - touchStartTime.current;
    touchStartY.current = null;

    // Fast swipe or delta > 45px
    if (Math.abs(deltaY) > 45 && duration < 600) {
      if (deltaY > 0 && activeIndex < references.length - 1) {
        // Swipe Up -> Next Inspiration
        scrollToCard(activeIndex + 1);
      } else if (deltaY < 0 && activeIndex > 0) {
        // Swipe Down -> Previous Inspiration
        scrollToCard(activeIndex - 1);
      }
    }
  };

  // Desktop Mouse Wheel handling over central container
  const handleWheel = (e: React.WheelEvent) => {
    const now = Date.now();
    if (now - lastWheelTime.current < 400) return; // Debounce rapid wheel events

    if (Math.abs(e.deltaY) > 35) {
      if (e.deltaY > 0 && activeIndex < references.length - 1) {
        lastWheelTime.current = now;
        scrollToCard(activeIndex + 1);
      } else if (e.deltaY < 0 && activeIndex > 0) {
        lastWheelTime.current = now;
        scrollToCard(activeIndex - 1);
      }
    }
  };

  // Fetch full Reference detail (including identified materials) whenever activeReference changes
  useEffect(() => {
    if (!currentRef) return;
    const refId = currentRef.id;

    if (refDetailCache.current.has(refId)) {
      const cached = refDetailCache.current.get(refId)!;
      setActiveReferenceDetail(cached);
      return;
    }

    setDetailLoading(true);
    getReferenceDetail(refId.toString())
      .then((detail: Reference) => {
        setActiveReferenceDetail(detail);
        refDetailCache.current.set(refId, detail);
      })
      .catch((err) => {
        console.error("Failed to load reference detail", err);
        setActiveReferenceDetail(currentRef);
      })
      .finally(() => {
        setDetailLoading(false);
      });
  }, [currentRef?.id]);

  // Identified materials list for active reference
  const materialsList: InspirationMaterial[] = activeReferenceDetail?.materials || [];
  const activeMaterial: InspirationMaterial | null = materialsList[selectedMaterialIndex] || null;

  // When active material changes, fetch product detail (if confirmed product) and trigger 5-Tier supplier sourcing
  useEffect(() => {
    if (!activeMaterial && materialsList.length === 0) {
      setSelectedProduct(null);
      setSourcingData(null);
      return;
    }

    const mat = activeMaterial || materialsList[0];
    if (!mat) return;

    // Load commercial product detail if product_id is linked
    if (mat.product_id) {
      getProductDetail(mat.product_id.toString())
        .then((p: Product) => setSelectedProduct(p))
        .catch(() => setSelectedProduct(null));
    } else {
      setSelectedProduct(null);
    }

    // Trigger Hierarchical 5-Tier Sourcing for THIS MATERIAL SPECIFICALLY
    const cacheKey = `${mat.id}_${mat.name}_${mat.product_id || 0}_${location.city}`;
    if (sourcingCache.current.has(cacheKey)) {
      setSourcingData(sourcingCache.current.get(cacheKey)!);
      return;
    }

    setSourcingLoading(true);
    searchSourcing({
      city: location.city || undefined,
      state: location.state || undefined,
      product_id: mat.product_id || undefined,
      category: mat.category_slug || undefined,
      q: mat.name,
    })
      .then((res: HierarchicalSourcingResponse) => {
        setSourcingData(res);
        sourcingCache.current.set(cacheKey, res);
      })
      .catch((err) => {
        console.error("Failed to search material sourcing", err);
        setSourcingData(null);
      })
      .finally(() => {
        setSourcingLoading(false);
      });
  }, [activeMaterial?.id, activeReferenceDetail?.id, location.city, location.state]);

  // Handle Save / Bookmark
  const handleSaveToggle = async () => {
    if (!currentRef) return;
    try {
      const res = await toggleSavedItem({
        item_type: 'reference',
        reference_id: currentRef.id,
        project_collection: 'Architect Board',
      });
      setSavedReferenceIds((prev) => {
        const next = new Set(prev);
        if (res.saved) {
          next.add(currentRef.id);
          showToast('Added to Saved Moodboards');
        } else {
          next.delete(currentRef.id);
          showToast('Removed from Saved Moodboards');
        }
        return next;
      });
    } catch (e) {
      showToast('Please sign in to save materials');
    }
  };

  // Handle Share
  const handleShare = () => {
    if (typeof window !== 'undefined') {
      const url = `${window.location.origin}/reference/${currentRef?.slug || currentRef?.id}`;
      navigator.clipboard.writeText(url);
      showToast('Architectural reference link copied!');
    }
  };

  const toggleTier = (tierId: number) => {
    setExpandedTiers((prev) => ({ ...prev, [tierId]: !prev[tierId] }));
  };

  if (!currentRef) {
    return (
      <div className="py-20 text-center bg-white rounded-3xl border border-arch-border p-8">
        <Compass className="w-12 h-12 text-stone-300 mx-auto mb-3" />
        <h3 className="font-serif text-2xl font-bold text-arch-charcoal">No architectural inspirations found</h3>
        <p className="mt-2 text-xs text-stone-500">Try broadening your regional, style, or material filters.</p>
      </div>
    );
  }

  const isCurrentSaved = savedReferenceIds.has(currentRef.id);

  // Group suppliers into 5 Tiers from sourcingData
  const tiers: SourcingTierResult[] = sourcingData?.tiers || [
    { tier_id: 1, tier_name: "Tier 1 — Local", geographic_scope: "City / District", description: location.city ? `Suppliers and verified stockists in ${location.city} and immediate radius` : "Select a location in the navigation bar to see immediate local suppliers", suppliers: sourcingData?.tier1_suppliers || [] },
    { tier_id: 2, tier_name: "Tier 2 — Nearby", geographic_scope: "Surrounding Districts & Borders", description: "Adjacent regional districts and nearby state trading hubs", suppliers: sourcingData?.tier2_suppliers || [] },
    { tier_id: 3, tier_name: "Tier 3 — South India", geographic_scope: "Kerala, Tamil Nadu, Karnataka & AP", description: "South Indian trade centers, stone quarries, and architectural distributors", suppliers: sourcingData?.tier3_suppliers || [] },
    { tier_id: 4, tier_name: "Tier 4 — India", geographic_scope: "Pan-India National Distribution", description: "National manufacturers, authorized direct depots, and national freight carriers", suppliers: sourcingData?.tier4_suppliers || [] },
    { tier_id: 5, tier_name: "Tier 5 — International", geographic_scope: "Global Exporters & Importers", description: "Worldwide manufacturers and direct architectural exporters", suppliers: sourcingData?.tier5_suppliers || [] },
  ];

  const totalSuppliersCount = sourcingData?.total_suppliers_found ?? tiers.reduce((acc, t) => acc + t.suppliers.length, 0);

  return (
    <div className="space-y-4">
      {/* Toast Feedback */}
      {toastMessage && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-2 bg-stone-900 text-white rounded-full text-xs font-semibold shadow-2xl border border-arch-terracotta/40 animate-in fade-in slide-in-from-bottom-3 duration-200">
          {toastMessage}
        </div>
      )}

      {/* Swipe Navigation Instructions Hint */}
      <div className="flex items-center justify-between px-2 text-xs text-stone-400">
        <div className="flex items-center gap-1.5 font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          <span>Swipe-First Discovery Active: Wheel, trackpad, or swipe up/down to explore references</span>
        </div>
        <div className="flex items-center gap-3">
          <span>Inspiration <strong>{activeIndex + 1}</strong> of <strong>{references.length}</strong></span>
          <span className="hidden sm:inline font-mono">Use ↑ / ↓ Keys</span>
        </div>
      </div>

      {/* Main Dual-Column Layout: Central Swipe Viewport (Left/Center) + Synchronized Sourcing Panel (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* ===================================================================
            CENTRAL INSPIRATION AREA: PRIMARY VERTICAL SCROLL CONTAINER (7 Cols)
            - Touch swipe up/down
            - Mouse wheel / trackpad scroll
            - Intelligent aspect ratio preservation (portrait and landscape)
            - Auto-syncs right sourcing panel without page reload
           =================================================================== */}
        <div className="lg:col-span-7 flex flex-col items-center">
          <div
            ref={scrollContainerRef}
            onTouchStart={handleTouchStart}
            onTouchEnd={handleTouchEnd}
            onWheel={handleWheel}
            className="w-full max-w-xl h-[760px] max-h-[82vh] bg-stone-950 rounded-3xl overflow-y-auto snap-y snap-mandatory relative shadow-2xl border border-stone-800 scrollbar-none"
            style={{ scrollSnapType: 'y mandatory', WebkitOverflowScrolling: 'touch' }}
          >
            {references.map((ref, idx) => {
              const isYouTube = ref.source_platform === 'youtube' && Boolean(ref.video_embed_id);
              const imgUrl = ref.inspiration_image_url || ref.thumbnail_url || ref.media_url || "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80";
              const isActive = idx === activeIndex;

              return (
                <div
                  key={ref.id}
                  data-index={idx}
                  ref={(el) => { cardRefs.current[idx] = el; }}
                  className="w-full h-full snap-start snap-always relative shrink-0 flex flex-col justify-between overflow-hidden"
                  style={{ height: '100%', scrollSnapAlign: 'start' }}
                >
                  {/* Background Presentation Layer:
                      To preserve landscape architectural photographs without forced 9:16 cropping,
                      we render an ambient blurred backdrop behind the sharp, aspect-preserved photo */}
                  <div className="absolute inset-0 z-0 overflow-hidden bg-stone-950 flex items-center justify-center">
                    {isYouTube ? (
                      <div className="w-full h-full relative bg-black flex items-center justify-center">
                        <iframe
                          src={`https://www.youtube.com/embed/${ref.video_embed_id}?autoplay=${isActive ? '1' : '0'}&mute=1&loop=1&playlist=${ref.video_embed_id}&enablejsapi=1&rel=0&modestbranding=1`}
                          title={ref.title}
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                          allowFullScreen
                          className="w-full h-full object-cover"
                        />
                        <div className="absolute top-3 right-16 z-10 px-2 py-1 rounded-md bg-black/75 backdrop-blur-md text-xs text-stone-200 pointer-events-none border border-white/10">
                          Official YouTube Video Walkthrough
                        </div>
                      </div>
                    ) : (ref.source_platform === 'instagram' && (ref.media_url?.includes('.mp4') || (ref as any).video_url?.includes('.mp4'))) ? (
                      <div className="w-full h-full relative bg-black flex items-center justify-center">
                        <video
                          src={(ref as any).video_url || ref.media_url}
                          poster={imgUrl}
                          autoPlay={isActive}
                          muted
                          loop
                          playsInline
                          controls
                          className="w-full h-full object-contain z-10"
                        />
                        <div
                          className="absolute inset-0 bg-cover bg-center filter blur-3xl scale-125 opacity-30 z-0 pointer-events-none"
                          style={{ backgroundImage: `url(${imgUrl})` }}
                        />
                        <div className="absolute top-3 right-16 z-20 px-2 py-1 rounded-md bg-black/75 backdrop-blur-md text-xs text-pink-300 pointer-events-none border border-pink-500/30">
                          Instagram Architectural Reel
                        </div>
                      </div>
                    ) : (
                      <>
                        {/* Ambient blurred backdrop fills the container */}
                        <div
                          className="absolute inset-0 scale-125 blur-3xl opacity-40 bg-center bg-cover pointer-events-none transition-all duration-700"
                          style={{ backgroundImage: `url(${imgUrl})` }}
                        />

                        {/* Foreground Architectural Photograph: Uncropped with Natural Aspect Ratio */}
                        <img
                          src={imgUrl}
                          alt={ref.title}
                          loading={idx <= 2 ? "eager" : "lazy"}
                          className="relative z-1 max-h-full max-w-full object-contain mx-auto drop-shadow-2xl transition-transform duration-500"
                        />

                        {/* Gradient Scrim for Legible Top and Bottom Typography */}
                        <div className="absolute inset-0 z-2 bg-gradient-to-t from-black/95 via-black/30 to-black/75 pointer-events-none" />
                      </>
                    )}
                  </div>

                  {/* Top Overlay Bar */}
                  <div className="relative z-10 p-4 sm:p-5 flex items-center justify-between text-xs pointer-events-auto">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30 backdrop-blur-md capitalize">
                        {ref.content_type?.replace(/_/g, ' ') || 'Architectural Project'}
                      </span>
                      <SourceBadge
                        platform={ref.source_platform}
                        sourceUrl={ref.source_url}
                        creatorName={ref.creator_name}
                        className="bg-black/60 text-white border-white/20 backdrop-blur-md shadow-sm"
                      />
                      {(ref.region || ref.country) && (
                        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-black/50 text-stone-200 border border-white/15 backdrop-blur-md">
                          <MapPin className="w-3 h-3 text-arch-terracotta" />
                          <span>{ref.region ? `${ref.region}, ` : ''}{ref.country || 'Global'}</span>
                        </span>
                      )}
                      {ref.architectural_style && (
                        <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-arch-terracotta/80 text-white backdrop-blur-md">
                          {ref.architectural_style}
                        </span>
                      )}
                    </div>

                    {/* Active Card Index Badge */}
                    <div className="px-2.5 py-1 rounded-full text-xs font-mono font-bold bg-black/60 text-stone-200 border border-white/15 backdrop-blur-md">
                      {idx + 1} / {references.length}
                    </div>
                  </div>

                  {/* Right-Side Floating Actions */}
                  <div className="absolute right-3.5 bottom-28 z-20 flex flex-col items-center gap-3 pointer-events-auto">
                    {/* Save to Moodboard */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (onOpenSaveModal) {
                          onOpenSaveModal({
                            id: ref.id,
                            title: ref.title,
                            imageUrl: ref.inspiration_image_url || ref.thumbnail_url,
                            type: ref.content_type
                          });
                        } else {
                          handleSaveToggle();
                        }
                      }}
                      className={`p-3 rounded-full backdrop-blur-md transition-all transform active:scale-90 shadow-xl ${
                        isCurrentSaved && isActive
                          ? 'bg-amber-500 text-stone-950 ring-2 ring-amber-500/50'
                          : 'bg-black/60 hover:bg-black/80 text-white border border-white/20'
                      }`}
                      title="Save to board"
                    >
                      <Bookmark className={`w-5 h-5 ${isCurrentSaved && isActive ? 'fill-current' : ''}`} />
                    </button>
                    <span className="text-xs font-semibold text-white/90 drop-shadow -mt-2">
                      {isCurrentSaved && isActive ? 'Saved' : 'Save'}
                    </span>

                    {/* Details & Materials Trigger */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        if (onOpenDetails) {
                          onOpenDetails(ref);
                        }
                      }}
                      className="p-3 rounded-full bg-black/60 hover:bg-amber-500 hover:text-stone-950 text-white border border-white/20 backdrop-blur-md transition-all transform active:scale-90 shadow-xl"
                      title="View full specifications & materials"
                    >
                      <FileText className="w-5 h-5" />
                    </button>
                    <span className="text-xs font-semibold text-white/90 drop-shadow -mt-2">
                      Details
                    </span>

                    {/* Share Action */}
                    <button
                      onClick={handleShare}
                      className="p-3 rounded-full bg-black/60 hover:bg-black/80 text-white border border-white/20 backdrop-blur-md transition-all transform active:scale-90 shadow-xl"
                      title="Copy reference link"
                    >
                      <Share2 className="w-5 h-5" />
                    </button>
                    <span className="text-xs font-semibold text-white/90 drop-shadow -mt-2">
                      Share
                    </span>

                    {/* Visual Swipe Up / Down Stepper Micro-Pills */}
                    <div className="mt-2 flex flex-col gap-1 bg-black/40 backdrop-blur-md p-1 rounded-full border border-white/10">
                      <button
                        onClick={() => scrollToCard(idx - 1)}
                        disabled={idx === 0}
                        className="p-1 text-stone-300 hover:text-white disabled:opacity-30 transition-colors"
                        title="Scroll to previous card"
                      >
                        <ChevronUp className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => scrollToCard(idx + 1)}
                        disabled={idx >= references.length - 1}
                        className="p-1 text-stone-300 hover:text-white disabled:opacity-30 transition-colors"
                        title="Scroll to next card"
                      >
                        <ChevronDown className="w-4 h-4" />
                      </button>
                    </div>
                  </div>

                  {/* Bottom Content Area on Inspiration Card */}
                  <div className="relative z-10 p-5 sm:p-6 text-white pointer-events-auto bg-gradient-to-t from-black/98 via-black/85 to-transparent pt-12">
                    <div className="flex flex-wrap items-center gap-2 mb-2 text-xs">
                      {ref.project_type && (
                        <span className="px-2 py-0.5 rounded-full bg-white/20 text-stone-200 text-xs font-bold uppercase tracking-wider">
                          {ref.project_type}
                        </span>
                      )}
                      {ref.architecture_era && (
                        <span className="px-2 py-0.5 rounded-full bg-stone-800 text-stone-300 text-xs font-medium border border-white/10">
                          {ref.architecture_era}
                        </span>
                      )}
                      {ref.architect_name && (
                        <span className="text-stone-300 text-xs">
                          Design: <strong>{ref.architect_name}</strong>
                        </span>
                      )}
                    </div>

                    {/* Title */}
                    <h2 className="font-serif text-xl sm:text-2xl font-bold leading-tight drop-shadow-md text-white">
                      {ref.title}
                    </h2>

                    {/* Project Description */}
                    {ref.description && (
                      <div className="mt-2 text-xs text-stone-300 leading-relaxed max-w-lg">
                        <p className={isDescExpanded ? "" : "line-clamp-2"}>
                          {ref.description}
                        </p>
                        {ref.description.length > 120 && (
                          <button
                            onClick={() => setIsDescExpanded(!isDescExpanded)}
                            className="text-arch-terracotta hover:underline text-xs font-semibold mt-1"
                          >
                            {isDescExpanded ? "Show less" : "Read more"}
                          </button>
                        )}
                      </div>
                    )}

                    {/* Material Tags */}
                    {ref.material_tags && (
                      <div className="mt-3 flex flex-wrap gap-1.5">
                        {ref.material_tags.split(',').slice(0, 4).map((tag) => (
                          <button
                            key={tag}
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              if (onSelectCategory) {
                                onSelectCategory(tag.trim().toLowerCase().replace(/\s+/g, '-'));
                              }
                            }}
                            className="text-xs px-2 py-0.5 rounded-md bg-white/15 hover:bg-white/30 text-stone-200 border border-white/10 backdrop-blur-sm font-mono cursor-pointer transition-colors"
                          >
                            #{tag.trim()}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Swipe Indicator Progress Bar */}
          <div className="w-full max-w-xl mt-3 flex items-center gap-2 px-1">
            <div className="flex-1 h-1 bg-stone-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-arch-terracotta transition-all duration-300 rounded-full"
                style={{ width: `${((activeIndex + 1) / references.length) * 100}%` }}
              />
            </div>
            <span className="text-xs text-stone-400 font-mono">
              {activeIndex + 1} / {references.length}
            </span>
          </div>
        </div>

        {/* ===================================================================
            RIGHT COLUMN: COMPLETE SOURCING PANEL (~5 Cols)
            Organized strictly per user specification:
            1. Selected Architectural Inspiration (attribution, region, style)
            2. Materials Used (identified materials breakdown with provenance)
            3. Original Manufacturer (official brand, verified product spec, catalog)
            4. Available Suppliers (5-Tier Hierarchical Sourcing: Local, Nearby,
               South India, India, International with verified direct contacts)
           =================================================================== */}
        <div className="lg:col-span-5 sticky top-20 space-y-5">
          <div className="bg-white rounded-3xl border border-arch-border p-6 shadow-sm space-y-6 max-h-[85vh] overflow-y-auto scrollbar-thin">

            {/* 1. SELECTED ARCHITECTURAL INSPIRATION HEADER */}
            <div className="pb-4 border-b border-arch-border space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
                  Selected Architectural Inspiration
                </span>
                <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-stone-100 text-stone-700 border border-stone-200">
                  {currentRef.source_platform}
                </span>
              </div>

              <h3 className="font-serif text-xl sm:text-2xl font-bold text-arch-charcoal leading-snug">
                {currentRef.title}
              </h3>

              <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-stone-600">
                {currentRef.architect_name && (
                  <div>
                    Architect: <strong className="text-arch-charcoal">{currentRef.architect_name}</strong>
                  </div>
                )}
                {(currentRef.country || currentRef.region) && (
                  <div>
                    Region: <strong className="text-arch-charcoal">{currentRef.region ? `${currentRef.region}, ` : ''}{currentRef.country}</strong>
                  </div>
                )}
                {currentRef.architectural_style && (
                  <div>
                    Style: <strong className="text-arch-terracotta">{currentRef.architectural_style}</strong>
                  </div>
                )}
              </div>

              {currentRef.source_url && (
                <div className="pt-1">
                  <a
                    href={currentRef.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-stone-500 hover:text-arch-terracotta font-medium transition-colors"
                  >
                    <span>View original project publication</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              )}
            </div>

            {/* 2. MATERIALS USED BREAKDOWN (IDENTIFIED FOR ACTIVE INSPIRATION) */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta block">
                    Identified Materials Breakdown
                  </span>
                  <h4 className="font-serif text-lg font-bold text-arch-charcoal">
                    Materials Used ({materialsList.length})
                  </h4>
                </div>
                <span className="text-xs text-stone-400">
                  Click a material to source suppliers
                </span>
              </div>

              {detailLoading ? (
                <div className="py-8 text-center text-stone-400 font-serif text-xs space-y-1">
                  <RefreshCw className="w-5 h-5 animate-spin mx-auto text-arch-terracotta mb-1" />
                  <p>Analyzing architectural finishes & specifications...</p>
                </div>
              ) : materialsList.length > 0 ? (
                <div className="space-y-2.5">
                  {materialsList.map((mat, mIdx) => {
                    const isSelected = mIdx === selectedMaterialIndex;

                    return (
                      <div
                        key={mat.id || mIdx}
                        onClick={() => setSelectedMaterialIndex(mIdx)}
                        className={`p-3 rounded-2xl cursor-pointer transition-all border text-left ${
                          isSelected
                            ? 'bg-arch-cream/40 border-arch-terracotta ring-1 ring-arch-terracotta shadow-xs'
                            : 'bg-stone-50 hover:bg-stone-100/80 border-stone-200'
                        }`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="space-y-1 flex-1">
                            <div className="flex items-center gap-2">
                              <span className="text-xs font-bold uppercase tracking-wider text-stone-500 font-mono">
                                {mat.element_location || mat.material_category}
                              </span>
                              {/* Provenance Badge */}
                              {mat.identification_type === 'confirmed_product' ? (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300">
                                  <CheckCircle2 className="w-3 h-3 text-emerald-700" />
                                  <span>Confirmed Product</span>
                                </span>
                              ) : mat.identification_type === 'architect_documented' ? (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-300">
                                  <FileText className="w-3 h-3 text-blue-700" />
                                  <span>Architect Documented</span>
                                </span>
                              ) : (
                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-300">
                                  <Sparkles className="w-3 h-3 text-amber-700" />
                                  <span>Visually Inferred ({Math.round((mat.confidence_score || 0.85) * 100)}%)</span>
                                </span>
                              )}
                            </div>

                            <div className="font-serif text-sm font-bold text-arch-charcoal">
                              {mat.name || mat.material_name}
                            </div>

                            {mat.notes && (
                              <p className="text-xs text-stone-600 leading-relaxed">
                                {mat.notes}
                              </p>
                            )}

                            {mat.compatible_alternatives && (
                              <div className="text-xs text-stone-500 pt-0.5">
                                <span className="font-semibold text-stone-600">Compatible Alternatives:</span> {mat.compatible_alternatives}
                              </div>
                            )}
                          </div>

                          {/* Material Detail Crop Image if available */}
                          {mat.detail_image_url && (
                            <div className="w-16 h-16 rounded-xl overflow-hidden bg-stone-200 border border-stone-300 shrink-0">
                              <img
                                src={mat.detail_image_url}
                                alt={mat.name}
                                className="w-full h-full object-cover"
                              />
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="p-3 bg-stone-50 rounded-2xl text-xs text-stone-600 space-y-1">
                  <p className="font-medium text-arch-charcoal">Reference Craft Materials</p>
                  <p className="text-xs text-stone-500">
                    {currentRef.material_tags || currentRef.category_name || "Regional architectural finishes"}
                  </p>
                </div>
              )}
            </div>

            {/* 3. ORIGINAL MANUFACTURER & PRODUCT SPECIFICATIONS */}
            <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200 space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta block">
                    Original Manufacturer & Product
                  </span>
                  <h4 className="font-serif text-base font-bold text-arch-charcoal">
                    {selectedProduct?.manufacturer?.name || activeMaterial?.product?.manufacturer_name || (activeMaterial?.identification_type === 'confirmed_product' ? "Commercial Manufacturer" : "Material Craft Specification")}
                  </h4>
                </div>
                {selectedProduct && (
                  <span className="text-xs font-semibold text-stone-500">
                    Origin: <strong>{selectedProduct.country_of_manufacture || selectedProduct.manufacturer?.country || "India"}</strong>
                  </span>
                )}
              </div>

              {selectedProduct ? (
                <div className="space-y-3">
                  <div className="text-xs text-stone-700">
                    Product: <strong>{selectedProduct.name}</strong>
                    {selectedProduct.sku_code && (
                      <span className="ml-2 font-mono text-stone-500 text-xs">({selectedProduct.sku_code})</span>
                    )}
                  </div>

                  {/* Isolated Manufacturer Product Image (Strictly Decoupled from Inspiration Photo) */}
                  {selectedProduct.image_url && (
                    <div className="p-2.5 bg-white rounded-xl border border-stone-200 space-y-1.5">
                      <div className="flex items-center justify-between text-xs text-stone-500 font-semibold">
                        <span className="text-arch-terracotta">Verified Commercial Product Photo</span>
                        <span>Isolated Technical Spec</span>
                      </div>
                      <div className="aspect-[16/9] w-full overflow-hidden rounded-lg bg-stone-100 border border-stone-200">
                        <img
                          src={selectedProduct.image_url}
                          alt={selectedProduct.name}
                          className="w-full h-full object-cover"
                        />
                      </div>
                    </div>
                  )}

                  {/* Specifications Grid */}
                  <div className="grid grid-cols-2 gap-2 text-xs p-2.5 bg-white rounded-xl border border-stone-200">
                    <div>
                      <span className="text-stone-400 block text-xs uppercase font-bold">Material Composition</span>
                      <span className="font-semibold text-arch-charcoal block truncate">{selectedProduct.material_type || selectedProduct.finish || "Standard Architectural Spec"}</span>
                    </div>
                    <div>
                      <span className="text-stone-400 block text-xs uppercase font-bold">Dimensions / Finish</span>
                      <span className="font-semibold text-arch-charcoal block truncate">{selectedProduct.dimensions || selectedProduct.finish || "Modular Dimension"}</span>
                    </div>
                  </div>

                  {/* Manufacturer Official Links */}
                  <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
                    {selectedProduct.manufacturer?.official_website && (
                      <a
                        href={selectedProduct.manufacturer.official_website}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-white border border-stone-200 text-xs font-medium text-stone-700 hover:text-arch-terracotta transition-colors shadow-2xs"
                      >
                        <Globe className="w-3 h-3 text-stone-400" />
                        <span>Brand Website</span>
                        <ExternalLink className="w-2.5 h-2.5 text-stone-400" />
                      </a>
                    )}
                    {selectedProduct.manufacturer?.official_catalog_url && (
                      <a
                        href={selectedProduct.manufacturer.official_catalog_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-xs font-semibold text-emerald-900 hover:bg-emerald-100 transition-colors shadow-2xs"
                      >
                        <FileText className="w-3 h-3 text-emerald-700" />
                        <span>Official Catalog</span>
                        <ExternalLink className="w-2.5 h-2.5 text-emerald-700" />
                      </a>
                    )}
                  </div>
                </div>
              ) : (
                <div className="p-3 bg-white rounded-xl border border-stone-200 text-xs text-stone-600 space-y-1">
                  <div className="flex items-center gap-1.5 text-stone-700 font-semibold">
                    <Info className="w-3.5 h-3.5 text-arch-terracotta" />
                    <span>Vernacular & Documented Craft Material</span>
                  </div>
                  <p className="text-xs text-stone-500 leading-relaxed">
                    This material is sourced directly from regional quarries, timber yards, or artisan fabricators rather than a single corporate conglomerate. Verified suppliers for this specification are organized below.
                  </p>
                </div>
              )}
            </div>

            {/* 4. AVAILABLE SUPPLIERS (HIERARCHICAL 5-TIER GLOBAL SOURCING) */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta block">
                    Hierarchical Global Sourcing
                  </span>
                  <h4 className="font-serif text-lg font-bold text-arch-charcoal">
                    Available Suppliers ({totalSuppliersCount})
                  </h4>
                </div>
                <span className="text-xs text-stone-400">
                  Target: {location.city || 'Pan-India'}
                </span>
              </div>

              {sourcingLoading ? (
                <div className="py-8 text-center text-stone-400 font-serif text-xs space-y-2">
                  <RefreshCw className="w-5 h-5 animate-spin mx-auto text-arch-terracotta" />
                  <p>Searching verified supplier tiers from {location.city || 'Pan-India'} to Global Trade Hubs...</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {tiers.map((tier) => {
                    const isExpanded = expandedTiers[tier.tier_id] ?? (tier.tier_id <= 2);
                    const supCount = tier.suppliers.length;

                    return (
                      <div
                        key={tier.tier_id}
                        className="rounded-2xl border border-stone-200 overflow-hidden bg-white shadow-2xs transition-all"
                      >
                        {/* Tier Accordion Header */}
                        <button
                          onClick={() => toggleTier(tier.tier_id)}
                          className="w-full p-3.5 flex items-center justify-between bg-stone-50/70 hover:bg-stone-100 transition-colors text-left"
                        >
                          <div className="space-y-0.5">
                            <div className="flex items-center gap-2">
                              <span className="font-serif font-bold text-sm text-arch-charcoal">
                                {tier.tier_name}
                              </span>
                              <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                                supCount > 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-stone-200 text-stone-600'
                              }`}>
                                {supCount} {supCount === 1 ? 'Supplier' : 'Suppliers'}
                              </span>
                            </div>
                            <p className="text-xs text-stone-500">
                              {tier.description}
                            </p>
                          </div>

                          <ChevronDown className={`w-4 h-4 text-stone-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`} />
                        </button>

                        {/* Tier Content: Suppliers List */}
                        {isExpanded && (
                          <div className="p-3 space-y-3 bg-white border-t border-stone-100">
                            {supCount > 0 ? (
                              supCount > 0 && tier.suppliers.map((sup) => (
                                <div
                                  key={sup.supplier_id}
                                  className="p-3.5 rounded-xl border border-stone-200 hover:border-arch-terracotta/40 transition-all space-y-2.5 bg-stone-50/40"
                                >
                                  {/* Supplier Header */}
                                  <div className="flex items-start justify-between gap-2">
                                    <div>
                                      <Link
                                        href={`/supplier/${sup.supplier_id}`}
                                        className="font-serif text-sm font-bold text-arch-charcoal hover:text-arch-terracotta transition-colors block"
                                      >
                                        {sup.supplier_name}
                                      </Link>
                                      <div className="text-xs text-stone-500 flex items-center gap-1.5 mt-0.5">
                                        <MapPin className="w-3 h-3 text-arch-terracotta shrink-0" />
                                        <span>{sup.address || `${sup.city}, ${sup.state}, ${sup.country}`}</span>
                                      </div>
                                      {sup.contact_person && (
                                        <div className="text-xs text-stone-500 mt-0.5">
                                          Contact Person: <strong className="text-stone-700">{sup.contact_person}</strong>
                                        </div>
                                      )}
                                    </div>

                                    {/* Verification Status Badge */}
                                    <VerificationBadge status={sup.verification_status} isPotential={sup.is_potential} />
                                  </div>

                                  {/* Coverage & Brands */}
                                  {(sup.brands_distributed || sup.delivery_areas) && (
                                    <div className="text-xs text-stone-500 space-y-0.5 pt-1 border-t border-stone-200/60 font-mono">
                                      {sup.brands_distributed && (
                                        <div>Brands: <span className="text-stone-700">{sup.brands_distributed}</span></div>
                                      )}
                                      {sup.delivery_areas && (
                                        <div>Service Scope: <span className="text-stone-700">{sup.delivery_areas}</span></div>
                                      )}
                                    </div>
                                  )}

                                  {/* Working Contact Actions */}
                                  <div className="pt-2 border-t border-stone-200/60 flex flex-wrap items-center justify-between gap-2 text-xs">
                                    <div className="flex flex-wrap items-center gap-1.5">
                                      {/* Phone Call Action */}
                                      {sup.phone ? (
                                        <a
                                          href={`tel:${sup.phone}`}
                                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-900 font-semibold text-xs border border-emerald-200 transition-colors"
                                          title={`Call ${sup.phone}`}
                                        >
                                          <PhoneCall className="w-3 h-3 text-emerald-700" />
                                          <span>{sup.phone}</span>
                                        </a>
                                      ) : (
                                        <span className="text-xs text-stone-400 italic">Contact unlisted</span>
                                      )}

                                      {/* WhatsApp Action */}
                                      {sup.whatsapp && (
                                        <a
                                          href={`https://wa.me/${sup.whatsapp.replace(/[^0-9]/g, '')}`}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-green-500 hover:bg-green-600 text-white font-semibold text-xs shadow-2xs transition-colors"
                                          title={`Chat on WhatsApp (${sup.whatsapp})`}
                                        >
                                          <MessageSquare className="w-3 h-3" />
                                          <span>WhatsApp</span>
                                        </a>
                                      )}

                                      {/* Email Action */}
                                      {sup.email && (
                                        <a
                                          href={`mailto:${sup.email}`}
                                          className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-700 text-xs border border-stone-200 transition-colors"
                                          title={`Email ${sup.email}`}
                                        >
                                          <Mail className="w-3 h-3 text-stone-500" />
                                          <span className="hidden sm:inline">{sup.email}</span>
                                        </a>
                                      )}

                                      {/* Google Maps Search Action (Free External Link) */}
                                      {sup.google_maps_url && (
                                        <a
                                          href={sup.google_maps_url}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-700 text-xs border border-stone-200 transition-colors"
                                          title="Open Showroom Location in Google Maps"
                                        >
                                          <MapPin className="w-3 h-3 text-red-500" />
                                          <span>Maps</span>
                                        </a>
                                      )}

                                      {/* Website Action */}
                                      {sup.website && (
                                        <a
                                          href={sup.website}
                                          target="_blank"
                                          rel="noopener noreferrer"
                                          className="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-700 text-xs border border-stone-200 transition-colors"
                                          title="Visit Official Website"
                                        >
                                          <Globe className="w-3 h-3 text-stone-500" />
                                          <span>Web</span>
                                        </a>
                                      )}
                                    </div>

                                    {/* Request Quotation Action */}
                                    <button
                                      onClick={() => setActiveQuotation({ product: selectedProduct || { id: 0, name: activeMaterial?.name || "Architectural Material" }, supplier: sup })}
                                      className="px-3 py-1 rounded-lg bg-arch-terracotta hover:bg-arch-terracotta-dark text-white font-semibold text-xs transition-colors shadow-2xs"
                                    >
                                      Request Quote
                                    </button>
                                  </div>
                                </div>
                              ))
                            ) : (
                              <div className="py-3 px-2 text-center text-xs text-stone-400 italic">
                                No suppliers identified in this geographic tier for the selected specification. Expanding to broader tiers.
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>

          </div>
        </div>
      </div>

      {/* Quotation Inquiry Modal */}
      {activeQuotation && (
        <QuotationModal
          isOpen={true}
          onClose={() => setActiveQuotation(null)}
          product={activeQuotation.product}
          supplier={activeQuotation.supplier}
        />
      )}
    </div>
  );
};
