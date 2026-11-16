"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Layers, Search, Building2, ChevronRight, CheckCircle2,
  Sparkles, Filter, ExternalLink, ArrowRight, ShieldCheck, MapPin,
  Film, ShoppingBag, MessageSquare, Store, X, Phone, Star, DollarSign
} from 'lucide-react';
import { Category } from '@/types';
import {
  getCategories,
  searchSocialCrawlInstagram,
  searchSocialCrawlYouTube,
  searchSocialCrawlReddit,
  searchSocialCrawlBusinesses,
  searchSocialCrawlShopping
} from '@/lib/api';
import { SourceBadge } from '@/components/SourceBadge';

// 17 Dedicated Material Categories
const DEDICATED_MATERIAL_CATEGORIES = [
  { id: "bricks", name: "Bricks", query: "clay bricks fly ash bricks AAC blocks masonry", icon: "🧱", section: "Structural" },
  { id: "cement", name: "Cement", query: "cement concrete ready mix concrete mortar", icon: "🏗️", section: "Structural" },
  { id: "tmt-steel", name: "TMT and steel", query: "TMT bars reinforcement steel structural steel beams", icon: "🔩", section: "Structural" },
  { id: "pipes", name: "Pipes", query: "PVC CPVC UPVC HDPE drainage water supply pipes", icon: "🚿", section: "Plumbing" },
  { id: "tiles", name: "Tiles", query: "ceramic tiles vitrified tiles porcelain floor wall tiles", icon: "🔲", section: "Finishes" },
  { id: "marble-granite", name: "Marble and granite", query: "marble granite quartz sandstone natural stone flooring", icon: "🏛️", section: "Finishes" },
  { id: "wood-timber", name: "Wood and timber", query: "timber teak wood plywood MDF veneers wood flooring", icon: "🪵", section: "Woodwork" },
  { id: "doors-windows", name: "Doors and windows", query: "wooden main doors aluminium windows UPVC sliding glass doors", icon: "🚪", section: "Openings" },
  { id: "glass-aluminium", name: "Glass and aluminium", query: "toughened glass structural glazing aluminium profiles facade", icon: "🪟", section: "Glazing" },
  { id: "paints-finishes", name: "Paints and finishes", query: "exterior weather paints interior emulsions textures microcement", icon: "🎨", section: "Finishes" },
  { id: "electrical-products", name: "Electrical products", query: "modular switches copper cables distribution boards smart switches", icon: "⚡", section: "Electrical" },
  { id: "plumbing-products", name: "Plumbing products", query: "plumbing valves pumps water tanks drainage fittings", icon: "🔧", section: "Plumbing" },
  { id: "lighting", name: "Lighting", query: "architectural LED lights downlights chandeliers spotlights landscape lighting", icon: "💡", section: "Electrical" },
  { id: "sanitaryware", name: "Sanitaryware", query: "wall hung toilets wash basins faucets showers mixers bathtubs", icon: "🛁", section: "Plumbing" },
  { id: "hardware", name: "Hardware", query: "door handles concealed hinges mortise smart locks drawer channels", icon: "🔑", section: "Hardware" },
  { id: "furniture", name: "Furniture", query: "modern sofas dining tables beds recliners modular wardrobe", icon: "🛋️", section: "Interiors" },
  { id: "decorative-products", name: "Decorative products", query: "architectural wall decor sculptures mirrors artefacts pottery rugs", icon: "🏺", section: "Decor" },
];

// 14 Architectural Material Taxonomy Sections (MasterFormat A-N)
const TAXONOMY_SECTIONS = [
  { code: "ALL", name: "All 14 Sections" },
  { code: "A", name: "A. Structural & Construction" },
  { code: "B", name: "B. Building Envelope & Roofing" },
  { code: "C", name: "C. Doors, Windows & Glazing" },
  { code: "D", name: "D. Interior Finishes & Surfaces" },
  { code: "E", name: "E. Woodwork & Joinery" },
  { code: "F", name: "F. Ceiling & Partition Systems" },
  { code: "G", name: "G. Plumbing & Sanitaryware" },
  { code: "H", name: "H. Electrical & Lighting" },
  { code: "I", name: "I. HVAC & Indoor Comfort" },
  { code: "J", name: "J. Fire Protection & Safety" },
  { code: "K", name: "K. Metal & Facade Detailing" },
  { code: "L", name: "L. Sustainable & Alternative" },
  { code: "M", name: "M. Landscape & External Works" },
  { code: "N", name: "N. Specialty Products" },
];

export default function MaterialsCataloguePage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [activeSection, setActiveSection] = useState<string>("ALL");

  // Selected Dedicated Material Hub for deep 4-source discovery
  const [selectedMaterial, setSelectedMaterial] = useState<typeof DEDICATED_MATERIAL_CATEGORIES[0] | null>(null);
  const [activeTab, setActiveTab] = useState<'inspiration' | 'products' | 'reviews' | 'suppliers'>('inspiration');

  // Discovery results state
  const [discoveryLoading, setDiscoveryLoading] = useState<boolean>(false);
  const [inspirationItems, setInspirationItems] = useState<any[]>([]);
  const [shoppingItems, setShoppingItems] = useState<any[]>([]);
  const [redditItems, setRedditItems] = useState<any[]>([]);
  const [businessItems, setBusinessItems] = useState<any[]>([]);
  const [discoveryError, setDiscoveryError] = useState<string | null>(null);

  // In-memory cache to prevent duplicate SocialCrawl requests and conserve credits
  const [materialCache, setMaterialCache] = useState<Record<string, any>>({});

  useEffect(() => {
    getCategories()
      .then((cats) => {
        setCategories(cats);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to fetch categories", err);
        setLoading(false);
      });
  }, []);

  // When a dedicated material is selected or tab changed, load data on demand
  useEffect(() => {
    if (!selectedMaterial) return;

    const cacheKey = `${selectedMaterial.id}-${activeTab}`;
    if (materialCache[cacheKey]) {
      // Use cached results (free, zero API credits)
      if (activeTab === 'inspiration') setInspirationItems(materialCache[cacheKey]);
      if (activeTab === 'products') setShoppingItems(materialCache[cacheKey]);
      if (activeTab === 'reviews') setRedditItems(materialCache[cacheKey]);
      if (activeTab === 'suppliers') setBusinessItems(materialCache[cacheKey]);
      return;
    }

    setDiscoveryLoading(true);
    setDiscoveryError(null);

    const query = selectedMaterial.query;

    if (activeTab === 'inspiration') {
      // Fetch Instagram Reels and YouTube walkthroughs
      Promise.allSettled([
        searchSocialCrawlInstagram({ query, max_pages: 1 }),
        searchSocialCrawlYouTube({ query, max_pages: 1 }),
      ]).then(([igRes, ytRes]) => {
        const igItems = igRes.status === 'fulfilled' && igRes.value.items ? igRes.value.items : [];
        const ytItems = ytRes.status === 'fulfilled' && ytRes.value.items ? ytRes.value.items : [];
        const combined = [...igItems, ...ytItems];
        setInspirationItems(combined);
        setMaterialCache(prev => ({ ...prev, [cacheKey]: combined }));
        setDiscoveryLoading(false);
      }).catch(err => {
        setDiscoveryError("Failed to load inspiration items.");
        setDiscoveryLoading(false);
      });
    } else if (activeTab === 'products') {
      // Fetch Google Shopping products
      searchSocialCrawlShopping({ query })
        .then(res => {
          const items = res.items || [];
          setShoppingItems(items);
          setMaterialCache(prev => ({ ...prev, [cacheKey]: items }));
          setDiscoveryLoading(false);
        })
        .catch(err => {
          setDiscoveryError("Failed to load Google Shopping products.");
          setDiscoveryLoading(false);
        });
    } else if (activeTab === 'reviews') {
      // Fetch Reddit community reviews
      searchSocialCrawlReddit({ query, max_pages: 1 })
        .then(res => {
          const items = res.items || [];
          setRedditItems(items);
          setMaterialCache(prev => ({ ...prev, [cacheKey]: items }));
          setDiscoveryLoading(false);
        })
        .catch(err => {
          setDiscoveryError("Failed to load Reddit discussions.");
          setDiscoveryLoading(false);
        });
    } else if (activeTab === 'suppliers') {
      // Fetch Google Business suppliers without forcing a hardcoded city
      searchSocialCrawlBusinesses({ query, location: "India" })
        .then(res => {
          const items = res.items || [];
          setBusinessItems(items);
          setMaterialCache(prev => ({ ...prev, [cacheKey]: items }));
          setDiscoveryLoading(false);
        })
        .catch(err => {
          setDiscoveryError("Failed to load Google Business suppliers.");
          setDiscoveryLoading(false);
        });
    }
  }, [selectedMaterial, activeTab]);

  // Filter categories
  const filteredCategories = categories.filter((cat) => {
    const matchesSection = activeSection === "ALL" || cat.section_code === activeSection;
    const matchesSearch =
      !searchQuery.trim() ||
      cat.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (cat.description && cat.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (cat.subcategories && cat.subcategories.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (cat.typical_applications && cat.typical_applications.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (cat.standards_compliance && cat.standards_compliance.toLowerCase().includes(searchQuery.toLowerCase()));

    return matchesSection && matchesSearch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
      {/* Editorial Header */}
      <div className="max-w-3xl">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-arch-terracotta/10 text-arch-terracotta border border-arch-terracotta/20 mb-3">
          <Layers className="w-3.5 h-3.5" />
          Hierarchical Architectural Materials Discovery
        </span>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal tracking-tight">
          Materials & Building Systems Taxonomy
        </h1>
        <p className="mt-2 text-sm text-stone-600 leading-relaxed font-sans">
          Explore architectural construction materials across 4 perspectives: Inspiration (Reels/Videos), Products (Google Shopping), Reviews (Reddit), and Suppliers (Google Business).
        </p>
      </div>

      {/* 1. 17 DEDICATED MATERIAL CATEGORIES SECTION */}
      <div className="bg-stone-900 rounded-3xl p-6 border border-stone-800 text-stone-100 shadow-xl space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-amber-400">
              Dedicated Material Discovery Hubs
            </span>
            <h2 className="font-serif text-xl font-bold text-white mt-0.5">
              Select a Material to Explore Across 4 SocialCrawl Sources
            </h2>
          </div>
          {selectedMaterial && (
            <button
              onClick={() => setSelectedMaterial(null)}
              className="text-xs text-stone-400 hover:text-white flex items-center gap-1 bg-stone-800 px-3 py-1.5 rounded-full border border-stone-700 transition-colors"
            >
              <X className="w-3.5 h-3.5" />
              <span>Close Material Explorer</span>
            </button>
          )}
        </div>

        {/* 17 Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto scrollbar-none pb-2 pt-1">
          {DEDICATED_MATERIAL_CATEGORIES.map((mat) => {
            const isSelected = selectedMaterial?.id === mat.id;
            return (
              <button
                key={mat.id}
                onClick={() => setSelectedMaterial(isSelected ? null : mat)}
                className={`px-3.5 py-2 rounded-2xl text-xs font-semibold flex items-center gap-2 whitespace-nowrap transition-all shrink-0 ${
                  isSelected
                    ? 'bg-amber-500 text-stone-950 shadow-md font-bold scale-105'
                    : 'bg-stone-800/90 hover:bg-stone-750 text-stone-200 border border-stone-700/80 hover:border-amber-500/40'
                }`}
              >
                <span>{mat.icon}</span>
                <span>{mat.name}</span>
              </button>
            );
          })}
        </div>

        {/* 2. DEDICATED MATERIAL 4-SOURCE RESEARCH PANEL */}
        {selectedMaterial && (
          <div className="mt-4 pt-5 border-t border-stone-800 space-y-5 animate-in fade-in duration-300">
            {/* Material Header & 4 Tabs */}
            <div className="flex flex-wrap items-center justify-between gap-3 bg-stone-950/60 p-3 rounded-2xl border border-stone-800/80">
              <div className="flex items-center gap-2.5">
                <span className="text-2xl">{selectedMaterial.icon}</span>
                <div>
                  <h3 className="font-serif text-lg font-bold text-white">
                    {selectedMaterial.name} Discovery Hub
                  </h3>
                  <p className="text-xs text-stone-400">
                    Query: <span className="font-mono text-amber-300">&ldquo;{selectedMaterial.query}&rdquo;</span>
                  </p>
                </div>
              </div>

              {/* 4 Source Perspective Tabs */}
              <div className="flex items-center p-1 rounded-xl bg-stone-900 border border-stone-800 text-xs">
                <button
                  type="button"
                  onClick={() => setActiveTab('inspiration')}
                  className={`px-3 py-1.5 rounded-lg font-semibold flex items-center gap-1.5 transition-all ${
                    activeTab === 'inspiration'
                      ? 'bg-gradient-to-r from-pink-600 to-purple-600 text-white shadow-xs'
                      : 'text-stone-400 hover:text-stone-200'
                  }`}
                >
                  <Film className="w-3.5 h-3.5" />
                  <span>Inspiration</span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('products')}
                  className={`px-3 py-1.5 rounded-lg font-semibold flex items-center gap-1.5 transition-all ${
                    activeTab === 'products'
                      ? 'bg-emerald-600 text-white shadow-xs'
                      : 'text-stone-400 hover:text-stone-200'
                  }`}
                >
                  <ShoppingBag className="w-3.5 h-3.5" />
                  <span>Products</span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('reviews')}
                  className={`px-3 py-1.5 rounded-lg font-semibold flex items-center gap-1.5 transition-all ${
                    activeTab === 'reviews'
                      ? 'bg-orange-600 text-white shadow-xs'
                      : 'text-stone-400 hover:text-stone-200'
                  }`}
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  <span>Reviews</span>
                </button>

                <button
                  type="button"
                  onClick={() => setActiveTab('suppliers')}
                  className={`px-3 py-1.5 rounded-lg font-semibold flex items-center gap-1.5 transition-all ${
                    activeTab === 'suppliers'
                      ? 'bg-blue-600 text-white shadow-xs'
                      : 'text-stone-400 hover:text-stone-200'
                  }`}
                >
                  <Store className="w-3.5 h-3.5" />
                  <span>Suppliers</span>
                </button>
              </div>
            </div>

            {/* Loading Indicator */}
            {discoveryLoading && (
              <div className="py-12 text-center text-stone-400 space-y-2">
                <div className="w-6 h-6 border-2 border-amber-500 border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-xs">Fetching verified {selectedMaterial.name} data via SocialCrawl...</p>
              </div>
            )}

            {/* Error Banner */}
            {discoveryError && (
              <div className="p-3 rounded-xl bg-rose-950/50 border border-rose-800 text-rose-200 text-xs">
                {discoveryError}
              </div>
            )}

            {/* TAB 1: INSPIRATION (Instagram Reels & YouTube) */}
            {!discoveryLoading && activeTab === 'inspiration' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {inspirationItems.length > 0 ? (
                  inspirationItems.map((item, idx) => (
                    <div key={item.id || idx} className="bg-stone-950 rounded-2xl border border-stone-800 overflow-hidden flex flex-col justify-between group hover:border-amber-500/50 transition-all">
                      <div className="relative aspect-4/5 bg-stone-900 overflow-hidden">
                        {item.image_url ? (
                          <img referrerPolicy="no-referrer"
                            src={item.image_url}
                            alt={item.title || "Inspiration"}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-stone-600">
                            <Film className="w-8 h-8" />
                          </div>
                        )}
                        <div className="absolute top-2 left-2">
                          <SourceBadge platform={item.source_platform || "instagram"} size="sm" />
                        </div>
                        {item.video_duration && (
                          <span className="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-black/80 text-xs text-white font-mono">
                            {item.video_duration}
                          </span>
                        )}
                      </div>
                      <div className="p-3 space-y-2 flex-1 flex flex-col justify-between">
                        <div>
                          <h4 className="text-xs font-semibold text-stone-200 line-clamp-2 leading-snug">
                            {item.title}
                          </h4>
                          {item.creator_name && (
                            <p className="text-xs text-stone-400 mt-1">
                              by {item.creator_name}
                            </p>
                          )}
                        </div>
                        {item.source_url && (
                          <a
                            href={item.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-amber-400 hover:text-amber-300 pt-2 border-t border-stone-800/80"
                          >
                            <span>Open Source</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="col-span-full py-8 text-center text-stone-500 text-xs">
                    No inspiration posts found for {selectedMaterial.name}.
                  </div>
                )}
              </div>
            )}

            {/* TAB 2: PRODUCT DISCOVERY (Google Shopping) */}
            {!discoveryLoading && activeTab === 'products' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {shoppingItems.length > 0 ? (
                  shoppingItems.map((prod, idx) => (
                    <div key={prod.id || idx} className="bg-stone-950 rounded-2xl border border-stone-800 p-4 flex flex-col justify-between hover:border-emerald-500/50 transition-all">
                      <div className="space-y-3">
                        <div className="relative aspect-4/3 rounded-xl bg-stone-900 overflow-hidden flex items-center justify-center">
                          {prod.image_url ? (
                            <img referrerPolicy="no-referrer"
                              src={prod.image_url}
                              alt={prod.title || prod.product_name}
                              className="w-full h-full object-contain"
                            />
                          ) : (
                            <ShoppingBag className="w-8 h-8 text-stone-600" />
                          )}
                          <div className="absolute top-2 left-2">
                            <SourceBadge platform="google_shopping" size="sm" />
                          </div>
                        </div>

                        <div>
                          <span className="text-xs text-stone-400 uppercase font-semibold block">
                            {prod.merchant || prod.brand || "Material Supplier"}
                          </span>
                          <h4 className="text-xs font-bold text-stone-100 line-clamp-2 mt-0.5">
                            {prod.title || prod.product_name}
                          </h4>
                          {prod.description && (
                            <p className="text-xs text-stone-400 line-clamp-2 mt-1">
                              {prod.description}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="pt-3 mt-3 border-t border-stone-800 flex items-center justify-between text-xs">
                        <span className="font-serif font-bold text-emerald-400 text-sm">
                          {prod.price_display || (prod.price ? `₹${prod.price.toLocaleString()}` : "Price on Enquiry")}
                        </span>
                        {prod.product_url && (
                          <a
                            href={prod.product_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-stone-300 hover:text-white bg-stone-850 px-2.5 py-1 rounded-lg border border-stone-700"
                          >
                            <span>View Product</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="col-span-full py-8 text-center text-stone-500 text-xs">
                    No Google Shopping products found for {selectedMaterial.name}.
                  </div>
                )}
              </div>
            )}

            {/* TAB 3: REVIEWS & DISCUSSIONS (Reddit) */}
            {!discoveryLoading && activeTab === 'reviews' && (
              <div className="space-y-3">
                {redditItems.length > 0 ? (
                  redditItems.map((post, idx) => (
                    <div key={post.id || idx} className="bg-stone-950 rounded-2xl border border-stone-800 p-4 hover:border-orange-500/50 transition-all space-y-2">
                      <div className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2 text-xs">
                          <SourceBadge platform="reddit" size="sm" />
                          <span className="font-semibold text-orange-400">{post.subreddit || "r/architecture"}</span>
                          <span className="text-stone-500">•</span>
                          <span className="text-stone-400">Posted by {post.creator_name || "Community Member"}</span>
                        </div>
                        {post.upvotes !== undefined && (
                          <span className="text-xs font-mono text-stone-400">
                            ▲ {post.upvotes} upvotes
                          </span>
                        )}
                      </div>

                      <h4 className="text-xs font-bold text-stone-100">
                        {post.title}
                      </h4>

                      {post.description && (
                        <p className="text-xs text-stone-400 line-clamp-3 leading-relaxed">
                          {post.description}
                        </p>
                      )}

                      {post.source_url && (
                        <a
                          href={post.source_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-xs text-orange-400 hover:text-orange-300 pt-1"
                        >
                          <span>Read Discussion Thread on Reddit</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="py-8 text-center text-stone-500 text-xs">
                    No Reddit discussion threads found for {selectedMaterial.name}.
                  </div>
                )}
              </div>
            )}

            {/* TAB 4: SUPPLIERS (Google Business) */}
            {!discoveryLoading && activeTab === 'suppliers' && (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {businessItems.length > 0 ? (
                  businessItems.map((biz, idx) => (
                    <div key={biz.id || idx} className="bg-stone-950 rounded-2xl border border-stone-800 p-4 flex flex-col justify-between hover:border-blue-500/50 transition-all space-y-3">
                      <div>
                        <div className="flex items-start justify-between gap-2 mb-2">
                          <SourceBadge platform="google_business" size="sm" />
                          {biz.verified && (
                            <span className="inline-flex items-center gap-1 text-xs text-emerald-400 font-semibold bg-emerald-950/60 px-2 py-0.5 rounded-full border border-emerald-800">
                              <CheckCircle2 className="w-3 h-3" />
                              <span>Verified</span>
                            </span>
                          )}
                        </div>

                        <h4 className="text-sm font-serif font-bold text-stone-100">
                          {biz.name}
                        </h4>
                        <span className="text-xs text-stone-400 block mt-0.5">
                          {biz.category || "Building Materials Supplier"}
                        </span>

                        {biz.rating && (
                          <div className="flex items-center gap-1 text-xs text-amber-400 mt-2">
                            <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                            <span className="font-bold">{biz.rating}</span>
                            {biz.review_count && (
                              <span className="text-stone-500 text-xs">({biz.review_count} reviews)</span>
                            )}
                          </div>
                        )}

                        {biz.address && (
                          <div className="flex items-start gap-1.5 text-xs text-stone-400 mt-2">
                            <MapPin className="w-3.5 h-3.5 text-stone-500 shrink-0 mt-0.5" />
                            <span className="line-clamp-2">{biz.address}</span>
                          </div>
                        )}

                        {biz.phone && (
                          <div className="flex items-center gap-1.5 text-xs text-stone-300 mt-1">
                            <Phone className="w-3.5 h-3.5 text-stone-500 shrink-0" />
                            <span className="font-mono">{biz.phone}</span>
                          </div>
                        )}
                      </div>

                      <div className="pt-3 border-t border-stone-800/80 flex items-center justify-between text-xs">
                        {biz.google_maps_url ? (
                          <a
                            href={biz.google_maps_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-xs text-blue-400 hover:text-blue-300"
                          >
                            <span>Google Maps</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        ) : <span />}

                        <Link
                          href={`/sourcing?q=${encodeURIComponent(biz.name)}`}
                          className="px-2.5 py-1 rounded bg-stone-850 hover:bg-stone-800 text-stone-300 text-xs border border-stone-700"
                        >
                          Find in Sourcing
                        </Link>
                      </div>
                    </div>
                  ))
                ) : (
                  <div className="col-span-full py-8 text-center text-stone-500 text-xs">
                    No Google Business suppliers found for {selectedMaterial.name}.
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* 2. FULL 14-SECTION ARCHITECTURAL TAXONOMY SECTION */}
      <div className="space-y-6">
        <div className="border-b border-arch-border pb-3 flex items-center justify-between">
          <div>
            <h2 className="font-serif text-2xl font-bold text-arch-charcoal">
              Full 14-Section Architectural MasterFormat Catalogue
            </h2>
            <p className="text-xs text-stone-500 mt-0.5">
              Browse materials by building classification, compliance standards, and specifications.
            </p>
          </div>
        </div>

        {/* Search & Section Navigation Toolbar */}
        <div className="bg-white rounded-3xl border border-arch-border p-5 shadow-2xs space-y-4">
          {/* Search Bar */}
          <div className="relative max-w-xl">
            <Search className="w-4 h-4 text-stone-400 absolute left-4 top-3.5 pointer-events-none" />
            <input
              type="text"
              placeholder="Search material type, subcategory (e.g. Laterite, AAC, TMT, Limewash, Terrazzo)..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-11 pr-4 py-2.5 rounded-2xl border border-stone-200 bg-stone-50 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-arch-terracotta/30 focus:border-arch-terracotta transition-all"
            />
          </div>

          {/* Section Filter Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none pb-1">
            {TAXONOMY_SECTIONS.map((sec) => (
              <button
                key={sec.code}
                onClick={() => setActiveSection(sec.code)}
                className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                  activeSection === sec.code
                    ? 'bg-arch-dark text-white shadow-xs'
                    : 'bg-stone-50 hover:bg-stone-100 text-stone-600 border border-stone-200'
                }`}
              >
                {sec.name}
              </button>
            ))}
          </div>
        </div>

        {/* Category Results Count */}
        <div className="flex items-center justify-between text-xs text-stone-500 font-medium px-1">
          <span>Showing <strong>{filteredCategories.length}</strong> material categories in catalogue</span>
          {activeSection !== "ALL" && (
            <button
              onClick={() => setActiveSection("ALL")}
              className="text-arch-terracotta hover:underline font-semibold"
            >
              Show All Sections
            </button>
          )}
        </div>

        {/* Catalogue Cards Grid */}
        {loading ? (
          <div className="py-20 text-center text-stone-400 font-serif">
            <div className="w-8 h-8 border-2 border-arch-terracotta border-t-transparent rounded-full animate-spin mx-auto mb-2" />
            <p className="text-xs">Loading material taxonomy...</p>
          </div>
        ) : filteredCategories.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCategories.map((cat) => {
              const subcats = cat.subcategories
                ? cat.subcategories.split(',').map((s) => s.trim())
                : [];

              return (
                <div
                  key={cat.id}
                  className="bg-white rounded-2xl border border-arch-border hover:border-arch-terracotta/40 hover:shadow-lg transition-all duration-300 p-6 flex flex-col justify-between space-y-4"
                >
                  <div className="space-y-3">
                    {/* Section Badge */}
                    <div className="flex items-center justify-between gap-2">
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-stone-100 text-stone-700 font-mono">
                        Section {cat.section_code || "Taxonomy"}
                      </span>
                      <span className="text-xs text-stone-400 uppercase tracking-wider font-semibold">
                        {cat.section_name || "Architecture"}
                      </span>
                    </div>

                    {/* Category Name */}
                    <h3 className="font-serif text-xl font-bold text-arch-charcoal leading-snug">
                      <Link
                        href={`/materials/${cat.slug}`}
                        className="hover:text-arch-terracotta transition-colors"
                      >
                        {cat.name}
                      </Link>
                    </h3>

                    {/* Description */}
                    {cat.description && (
                      <p className="text-xs text-stone-600 line-clamp-3 leading-relaxed">
                        {cat.description}
                      </p>
                    )}

                    {/* Subcategories */}
                    {subcats.length > 0 && (
                      <div className="space-y-1 pt-1">
                        <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block">
                          Included Product Types & Subcategories:
                        </span>
                        <div className="flex flex-wrap gap-1">
                          {subcats.slice(0, 4).map((sub) => (
                            <span
                              key={sub}
                              className="text-xs px-2 py-0.5 rounded-md bg-stone-50 text-stone-700 font-medium border border-stone-200/60"
                            >
                              {sub}
                            </span>
                          ))}
                          {subcats.length > 4 && (
                            <span className="text-xs px-1.5 py-0.5 rounded-md bg-stone-100 text-stone-500 font-mono">
                              +{subcats.length - 4} more
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Standards Compliance */}
                    {cat.standards_compliance && (
                      <div className="text-xs text-stone-500 pt-1 flex items-center gap-1.5">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                        <span className="truncate">Standards: <strong className="text-stone-700 font-mono text-xs">{cat.standards_compliance}</strong></span>
                      </div>
                    )}
                  </div>

                  {/* Footer Actions */}
                  <div className="pt-4 border-t border-stone-100 flex items-center justify-between text-xs">
                    <Link
                      href={`/materials/${cat.slug}`}
                      className="inline-flex items-center gap-1 text-xs font-semibold text-arch-charcoal hover:text-arch-terracotta transition-colors"
                    >
                      <span>View Specifications</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </Link>

                    <Link
                      href={`/sourcing?category=${encodeURIComponent(cat.slug)}`}
                      className="px-2.5 py-1 rounded-lg bg-stone-100 hover:bg-arch-terracotta hover:text-white text-stone-700 font-medium transition-colors text-xs"
                    >
                      Find Suppliers
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div className="py-16 text-center bg-white rounded-3xl border border-arch-border p-8">
            <Layers className="w-10 h-10 text-stone-300 mx-auto mb-3" />
            <h3 className="font-serif text-xl font-bold text-arch-charcoal">No material categories found</h3>
            <p className="mt-2 text-xs text-stone-500 max-w-sm mx-auto">
              Try adjusting your search query or select another section.
            </p>
            <button
              onClick={() => {
                setSearchQuery("");
                setActiveSection("ALL");
              }}
              className="mt-4 px-4 py-2 bg-arch-dark text-white rounded-xl text-xs font-semibold hover:bg-arch-terracotta transition-colors"
            >
              Clear Filters
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
