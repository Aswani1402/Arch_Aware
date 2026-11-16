"use client";

import React, { useState, useEffect, Suspense } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import {
  Search, MapPin, Navigation, Layers, Building2, Phone, Globe,
  ExternalLink, CheckCircle2, AlertCircle, Filter, ArrowRight,
  ShoppingBag, Store, Star, DollarSign, Package, ShieldCheck, Bookmark
} from 'lucide-react';
import { HierarchicalSourcingResponse, SourcingSupplierResult } from '@/types';
import { SourcingHierarchyVisualizer } from '@/components/SourcingHierarchyVisualizer';
import { VerificationBadge } from '@/components/VerificationBadge';
import { QuotationModal } from '@/components/QuotationModal';
import { SourceBadge } from '@/components/SourceBadge';
import { searchSourcing, getSocialCrawlSuppliers, searchGooglePlaces, getSavedItems, toggleSavedItem, hasAuthToken } from '@/lib/api';
import { useAuth } from '@/lib/authContext';
import { useNavigation } from '@/lib/navigationContext';

type SourcingEntityType = 'all' | 'products' | 'manufacturers' | 'dealers' | 'distributors' | 'showrooms' | 'suppliers';

function SourcingContent() {
  const searchParams = useSearchParams();
  const initialQ = searchParams.get('q') || "";
  const initialProductId = searchParams.get('product_id') ? parseInt(searchParams.get('product_id')!) : undefined;
  const initialCategory = searchParams.get('category') || undefined;

  const { location } = useAuth();
  const { refreshSavedCounts } = useNavigation();
  const [query, setQuery] = useState(initialQ);
  const [selectedRadius, setSelectedRadius] = useState<number>(25);
  const [sourcingData, setSourcingData] = useState<HierarchicalSourcingResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [activeLevelFilter, setActiveLevelFilter] = useState<number | undefined>(undefined);
  const [activeQuotation, setActiveQuotation] = useState<{ product: any; supplier: any } | null>(null);
  const [savedVendorsMap, setSavedVendorsMap] = useState<Record<number, boolean>>({});
  const [savingId, setSavingId] = useState<number | null>(null);

  useEffect(() => {
    if (!hasAuthToken()) return;
    getSavedItems()
      .then((items: any[]) => {
        if (Array.isArray(items)) {
          const map: Record<number, boolean> = {};
          items.forEach(i => {
            if (i.item_type === 'supplier' && i.supplier_id) {
              map[i.supplier_id] = true;
            }
          });
          setSavedVendorsMap(map);
        }
      })
      .catch(() => {});
  }, []);

  const handleToggleSaveVendor = async (supplierId: number, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!hasAuthToken()) {
      alert('Please sign in to save vendors to your Trade Directory.');
      return;
    }
    if (savingId === supplierId) return;
    setSavingId(supplierId);
    try {
      const res = await toggleSavedItem({
        item_type: 'supplier',
        supplier_id: supplierId,
        project_collection: 'Verified Trade Directory'
      });
      setSavedVendorsMap(prev => ({
        ...prev,
        [supplierId]: Boolean(res.saved)
      }));
      refreshSavedCounts();
    } catch (err) {
      console.error("Failed to toggle save vendor", err);
    } finally {
      setSavingId(null);
    }
  };

  // Entity Type Filter: Products, Manufacturers, Dealers, Distributors, Showrooms, Suppliers
  const [entityType, setEntityType] = useState<SourcingEntityType>('all');

  // SocialCrawl Google Business & Google Shopping Live Data
  const [socialCrawlData, setSocialCrawlData] = useState<{
    businesses: any[];
    products: any[];
    businesses_count: number;
    products_count: number;
  } | null>(null);
  const [socialCrawlLoading, setSocialCrawlLoading] = useState<boolean>(false);

  const executeSearch = async (searchTerm?: string, radius?: number) => {
    const qTerm = searchTerm !== undefined ? searchTerm : query;
    setLoading(true);
    setSocialCrawlLoading(true);

    try {
      const res = await searchSourcing({
        q: qTerm || undefined,
        product_id: initialProductId,
        category: initialCategory,
        city: location.city,
        state: location.state,
        lat: location.lat,
        lon: location.lon,
        radius: radius || selectedRadius
      });
      setSourcingData(res);
      setActiveLevelFilter(undefined);
    } catch (err) {
      console.error("Sourcing search failed", err);
    } finally {
      setLoading(false);
    }

    // Also fetch live SocialCrawl Google Business & Google Shopping data + Google Places if query exists
    if (qTerm && qTerm.trim().length > 0) {
      try {
        const formattedLoc = location.city ? `${location.city}, ${location.state || "India"}, India` : "India";
        const [scSettled, placesSettled] = await Promise.allSettled([
          getSocialCrawlSuppliers({
            q: qTerm.trim(),
            location: formattedLoc,
            lat: location.lat,
            lon: location.lon,
            dry_run: false
          }),
          searchGooglePlaces({
            material: qTerm.trim(),
            city: location.city,
            lat: location.lat || undefined,
            lon: location.lon || undefined,
            radius_km: radius || selectedRadius
          })
        ]);

        let combinedBusinesses: any[] = [];
        let combinedProducts: any[] = [];

        if (scSettled.status === "fulfilled" && scSettled.value) {
          combinedBusinesses = [...(scSettled.value.businesses || [])];
          combinedProducts = [...(scSettled.value.products || [])];
        }

        if (placesSettled.status === "fulfilled" && placesSettled.value && Array.isArray(placesSettled.value.places)) {
          const existingBizNames = new Set(
            combinedBusinesses.map((b: any) => (b.name || "").toLowerCase().replace(/[^a-z0-9]/g, ''))
          );
          placesSettled.value.places.forEach((p: any) => {
            const normName = (p.name || "").toLowerCase().replace(/[^a-z0-9]/g, '');
            if (normName && !existingBizNames.has(normName)) {
              existingBizNames.add(normName);
              combinedBusinesses.push({
                id: p.google_place_id || `place-${Math.random()}`,
                name: p.name,
                category: p.category || "Building Material Supplier",
                address: p.address,
                phone: p.phone,
                whatsapp: p.whatsapp,
                rating: p.rating,
                reviews_count: p.reviews_count || p.user_ratings_total,
                maps_url: p.google_maps_url,
                distance_km: p.distance_km,
                distance_display: p.distance_display,
                source_platform: "google_places",
                verified: false,
                is_potential: true
              });
            }
          });
        }

        setSocialCrawlData({
          businesses: combinedBusinesses,
          products: combinedProducts,
          businesses_count: combinedBusinesses.length,
          products_count: combinedProducts.length
        });
      } catch (err) {
        console.error("Discovered suppliers search failed", err);
      } finally {
        setSocialCrawlLoading(false);
      }
    } else {
      setSocialCrawlLoading(false);
    }
  };

  useEffect(() => {
    executeSearch();
  }, [location.city, location.state]);

  useEffect(() => {
    const qParam = searchParams.get('q');
    if (qParam !== null && qParam !== query) {
      setQuery(qParam);
      executeSearch(qParam);
    }
  }, [searchParams]);

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeSearch();
  };

  // Helper to filter suppliers by entity type
  const filterSupplierByEntityType = (sup: SourcingSupplierResult) => {
    if (entityType === 'all') return true;
    const bType = (sup.business_type || '').toLowerCase();
    if (entityType === 'manufacturers') return bType.includes('manufacturer') || bType.includes('producer');
    if (entityType === 'dealers') return bType.includes('dealer') || bType.includes('retailer');
    if (entityType === 'distributors') return bType.includes('distributor') || bType.includes('wholesaler');
    if (entityType === 'showrooms') return bType.includes('showroom') || bType.includes('experience');
    if (entityType === 'suppliers') return bType.includes('supplier') || bType.includes('yard') || bType.includes('contractor');
    return true;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Page Title & Sourcing Header */}
      <div className="max-w-3xl">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-arch-terracotta/10 text-arch-terracotta border border-arch-terracotta/20 mb-3">
          <Layers className="w-3.5 h-3.5" />
          <span>7-Tier Regional & International Sourcing Fallback</span>
        </div>
        <h1 className="font-serif text-3xl sm:text-4xl lg:text-5xl font-bold text-arch-charcoal tracking-tight">
          Location-Based Supplier & Material Discovery
        </h1>
        <p className="mt-3 text-sm text-stone-600 leading-relaxed font-sans">
          Discover verified local manufacturers, dealers, showrooms, and global specialty suppliers. Integrated with Google Business local directories and Google Shopping product pricing via SocialCrawl.
        </p>
      </div>

      {/* Sourcing Search Control Bar */}
      <div className="bg-white p-5 rounded-3xl border border-arch-border shadow-sm space-y-4">
        <form onSubmit={handleFormSubmit} className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
          <div className="md:col-span-5 relative">
            <Search className="w-4 h-4 text-stone-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search material, brand, supplier (e.g. Laterite, AAC blocks, TMT steel, Kajaria, Kohler)..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-arch-border text-xs focus:ring-1 focus:ring-arch-terracotta outline-none bg-stone-50"
            />
          </div>

          <div className="md:col-span-4 flex items-center gap-2">
            <div className="relative w-full">
              <MapPin className="w-4 h-4 text-arch-terracotta absolute left-3 top-3" />
              <input
                type="text"
                readOnly
                value={location.city ? `Origin: ${location.city}, ${location.state || "India"}` : "Origin: All India (Select in header)"}
                className="w-full pl-9 pr-3 py-2.5 rounded-xl border border-arch-border text-xs bg-stone-100 text-stone-700 font-medium cursor-not-allowed"
                title="Change location in the navigation bar"
              />
            </div>
          </div>

          <div className="md:col-span-3 flex items-center gap-2">
            <select
              value={selectedRadius}
              onChange={(e) => {
                const r = parseFloat(e.target.value);
                setSelectedRadius(r);
                executeSearch(query, r);
              }}
              className="w-full px-3 py-2.5 rounded-xl border border-arch-border text-xs bg-stone-50 font-medium outline-none focus:ring-1 focus:ring-arch-terracotta"
            >
              <option value="25">Initial: 25 km Radius</option>
              <option value="50">Initial: 50 km Radius</option>
              <option value="100">Initial: 100 km Radius</option>
            </select>

            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2.5 rounded-xl bg-arch-dark hover:bg-arch-terracotta text-white font-semibold text-xs transition-colors shrink-0 shadow-sm"
            >
              {loading ? "Searching..." : "Search"}
            </button>
          </div>
        </form>

        {/* ENTITY TYPE SWITCHER: Products, Manufacturers, Dealers, Distributors, Showrooms, Suppliers */}
        <div className="pt-3 border-t border-stone-100 flex items-center gap-1.5 overflow-x-auto scrollbar-none">
          <span className="text-xs font-bold uppercase tracking-wider text-stone-400 mr-2 shrink-0">
            Switch Entity:
          </span>

          <button
            type="button"
            onClick={() => setEntityType('all')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              entityType === 'all'
                ? 'bg-arch-dark text-white shadow-xs'
                : 'bg-stone-100 hover:bg-stone-200 text-stone-600'
            }`}
          >
            All Sourcing
          </button>

          <button
            type="button"
            onClick={() => setEntityType('products')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap flex items-center gap-1.5 transition-all ${
              entityType === 'products'
                ? 'bg-emerald-600 text-white shadow-xs'
                : 'bg-stone-100 hover:bg-stone-200 text-stone-600'
            }`}
          >
            <ShoppingBag className="w-3.5 h-3.5" />
            <span>Products</span>
            {socialCrawlData?.products_count ? (
              <span className="px-1.5 py-0.2 rounded-full bg-white/20 text-xs font-mono">
                {socialCrawlData.products_count}
              </span>
            ) : null}
          </button>

          <button
            type="button"
            onClick={() => setEntityType('manufacturers')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              entityType === 'manufacturers'
                ? 'bg-arch-dark text-white shadow-xs'
                : 'bg-stone-100 hover:bg-stone-200 text-stone-600'
            }`}
          >
            Manufacturers
          </button>

          <button
            type="button"
            onClick={() => setEntityType('dealers')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              entityType === 'dealers'
                ? 'bg-arch-dark text-white shadow-xs'
                : 'bg-stone-100 hover:bg-stone-200 text-stone-600'
            }`}
          >
            Dealers
          </button>

          <button
            type="button"
            onClick={() => setEntityType('distributors')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              entityType === 'distributors'
                ? 'bg-arch-dark text-white shadow-xs'
                : 'bg-stone-100 hover:bg-stone-200 text-stone-600'
            }`}
          >
            Distributors
          </button>

          <button
            type="button"
            onClick={() => setEntityType('showrooms')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
              entityType === 'showrooms'
                ? 'bg-arch-dark text-white shadow-xs'
                : 'bg-stone-100 hover:bg-stone-200 text-stone-600'
            }`}
          >
            Showrooms
          </button>

          <button
            type="button"
            onClick={() => setEntityType('suppliers')}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap flex items-center gap-1.5 transition-all ${
              entityType === 'suppliers'
                ? 'bg-blue-600 text-white shadow-xs'
                : 'bg-stone-100 hover:bg-stone-200 text-stone-600'
            }`}
          >
            <Store className="w-3.5 h-3.5" />
            <span>Suppliers</span>
            {socialCrawlData?.businesses_count ? (
              <span className="px-1.5 py-0.2 rounded-full bg-white/20 text-xs font-mono">
                {socialCrawlData.businesses_count}
              </span>
            ) : null}
          </button>
        </div>
      </div>

      {/* SECTION 1: GOOGLE SHOPPING PRODUCTS (WHEN PRODUCTS TAB SELECTED OR SEARCHED) */}
      {(entityType === 'products' || (entityType === 'all' && socialCrawlData && socialCrawlData.products.length > 0)) && (
        <div className="bg-white rounded-3xl border border-arch-border p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-stone-100">
            <div className="flex items-center gap-2">
              <SourceBadge platform="google_shopping" size="md" />
              <h2 className="font-serif text-xl font-bold text-arch-charcoal">
                Google Shopping Products & Price Discovery
              </h2>
            </div>
            {socialCrawlData?.products_count ? (
              <span className="text-xs font-semibold text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                {socialCrawlData.products_count} Products Found
              </span>
            ) : null}
          </div>

          {socialCrawlLoading ? (
            <div className="py-8 text-center text-xs text-stone-500">
              Loading verified Google Shopping prices...
            </div>
          ) : socialCrawlData && socialCrawlData.products.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {socialCrawlData.products.map((prod, idx) => (
                <div key={prod.id || idx} className="rounded-2xl border border-stone-200 p-4 bg-stone-50 flex flex-col justify-between hover:border-emerald-500/60 transition-all space-y-3">
                  <div className="space-y-2">
                    <div className="relative aspect-4/3 rounded-xl bg-white overflow-hidden flex items-center justify-center border border-stone-100">
                      {prod.image_url ? (
                        <img referrerPolicy="no-referrer"
                          src={prod.image_url}
                          alt={prod.title || prod.product_name}
                          className="w-full h-full object-contain p-2"
                        />
                      ) : (
                        <ShoppingBag className="w-8 h-8 text-stone-300" />
                      )}
                    </div>

                    <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block truncate">
                      {prod.merchant || prod.brand || "Supplier"}
                    </span>
                    <h4 className="text-xs font-bold text-arch-charcoal line-clamp-2">
                      {prod.title || prod.product_name}
                    </h4>
                  </div>

                  <div className="pt-2 border-t border-stone-200/80 flex items-center justify-between">
                    <span className="font-serif font-bold text-emerald-700 text-sm">
                      {prod.price_display || (prod.price ? `₹${prod.price.toLocaleString()}` : "Quote")}
                    </span>

                    {prod.product_url && (
                      <a
                        href={prod.product_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 text-xs font-semibold text-arch-terracotta hover:underline"
                      >
                        <span>Buy Link</span>
                        <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-stone-500 py-4 text-center">
              Search a material name (e.g. &ldquo;Laterite&rdquo;, &ldquo;TMT steel&rdquo;, &ldquo;Kajaria tiles&rdquo;) to see live Google Shopping prices.
            </p>
          )}
        </div>
      )}

      {/* SECTION 2: GOOGLE BUSINESS SUPPLIERS (WHEN SUPPLIERS TAB SELECTED OR SEARCHED) */}
      {(entityType === 'suppliers' || (entityType === 'all' && socialCrawlData && socialCrawlData.businesses.length > 0)) && (
        <div className="bg-white rounded-3xl border border-arch-border p-6 shadow-sm space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-stone-100">
            <div className="flex items-center gap-2">
              <SourceBadge platform="google_business" size="md" />
              <h2 className="font-serif text-xl font-bold text-arch-charcoal">
                Google Business Local Suppliers & Dealers
              </h2>
            </div>
            {socialCrawlData?.businesses_count ? (
              <span className="text-xs font-semibold text-blue-700 bg-blue-50 px-2.5 py-1 rounded-full border border-blue-200">
                {socialCrawlData.businesses_count} Verified Listings
              </span>
            ) : null}
          </div>

          {(() => {
            const existingDbNames = new Set(
              sourcingData?.levels_traversed?.flatMap(l => l.suppliers.map(s => (s.supplier_name || "").toLowerCase().replace(/[^a-z0-9]/g, ''))) || []
            );
            const uniqueDiscovered = (socialCrawlData?.businesses || []).filter(biz => {
              const norm = (biz.name || "").toLowerCase().replace(/[^a-z0-9]/g, '');
              return norm && !existingDbNames.has(norm);
            });

            if (uniqueDiscovered.length === 0) return null;

            return (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {uniqueDiscovered.map((biz, idx) => {
                  const revCount = biz.reviews_count ?? biz.review_count ?? biz.user_ratings_total;
                  const mapsUrl = biz.maps_url || biz.google_maps_url;
                  // Only provide direct WhatsApp link if WhatsApp availability is established by the provider
                  const waUrl = biz.whatsapp
                    ? (biz.whatsapp.startsWith('http') ? biz.whatsapp : `https://wa.me/${biz.whatsapp.replace(/[^0-9]/g, '')}`)
                    : null;

                  return (
                    <div key={biz.id || idx} className="rounded-2xl border border-stone-200 p-5 bg-stone-50 flex flex-col justify-between hover:border-blue-500/60 transition-all space-y-3">
                      <div>
                        <div className="flex items-start justify-between gap-2 mb-1.5">
                          <span className="text-xs font-bold uppercase tracking-wider text-stone-400">
                            {biz.category || "Supplier"}
                          </span>
                          {biz.verified ? (
                            <span className="inline-flex items-center gap-1 text-xs text-emerald-700 font-semibold bg-emerald-100 px-2 py-0.5 rounded-full">
                              <CheckCircle2 className="w-3 h-3" />
                              <span>Verified</span>
                            </span>
                          ) : (
                            <span className="inline-flex items-center gap-1 text-xs text-amber-700 font-semibold bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                              <span>Discovered</span>
                            </span>
                          )}
                        </div>

                        <h4 className="font-serif text-base font-bold text-arch-charcoal">
                          {biz.name}
                        </h4>

                        {biz.rating && (
                          <div className="flex items-center gap-1 text-xs text-amber-600 font-semibold mt-1.5">
                            <Star className="w-3.5 h-3.5 fill-amber-500 text-amber-500" />
                            <span>{biz.rating}</span>
                            {revCount ? (
                              <span className="text-stone-400 font-normal">({revCount} reviews)</span>
                            ) : null}
                          </div>
                        )}

                        {biz.address && (
                          <div className="flex items-start gap-1.5 text-xs text-stone-600 mt-2">
                            <MapPin className="w-3.5 h-3.5 text-stone-400 shrink-0 mt-0.5" />
                            <span className="line-clamp-2">{biz.address}</span>
                          </div>
                        )}

                        {(biz.distance_display || biz.district || biz.city) && (
                          <div className="flex items-center justify-between text-xs text-stone-500 mt-1">
                            <span>{biz.district || biz.city || "Regional Trade Area"}</span>
                            {biz.distance_display ? (
                              <span className="font-semibold text-arch-terracotta">{biz.distance_display}</span>
                            ) : null}
                          </div>
                        )}

                        {(biz.phone || waUrl) && (
                          <div className="flex items-center justify-between text-xs text-stone-700 mt-2">
                            {biz.phone ? (
                              <a
                                href={`tel:${biz.phone}`}
                                className="flex items-center gap-1.5 font-mono hover:text-arch-terracotta transition-colors"
                                title="Call vendor directly"
                              >
                                <Phone className="w-3.5 h-3.5 text-stone-400" />
                                <span>{biz.phone}</span>
                              </a>
                            ) : (
                              <span className="text-stone-400 italic text-xs">No telephone listed</span>
                            )}
                            {waUrl && (
                              <a
                                href={waUrl}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="inline-flex items-center gap-1 text-xs text-emerald-700 font-semibold bg-emerald-50 hover:bg-emerald-100 px-2 py-0.5 rounded-full border border-emerald-200 transition-colors"
                                title="Direct WhatsApp trade inquiry"
                              >
                                <span>WhatsApp</span>
                              </a>
                            )}
                          </div>
                        )}
                      </div>

                      <div className="pt-3 border-t border-stone-200/80 flex items-center justify-between text-xs">
                        {mapsUrl && (
                          <a
                            href={mapsUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex items-center gap-1 text-blue-700 font-semibold hover:underline"
                          >
                            <span>Google Maps</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}

                        <button
                          type="button"
                          onClick={() => {
                            setActiveQuotation({
                              product: { id: 1, name: query || "Architectural Building Supplies" },
                              supplier: {
                                id: 99000 + idx,
                                name: biz.name,
                                supplier_id: 99000 + idx,
                                supplier_name: biz.name,
                                city: location.city || "Local",
                                state: location.state || "India",
                                email: null,
                                phone: biz.phone
                              }
                            });
                          }}
                          className="px-3 py-1 rounded-lg bg-arch-dark hover:bg-arch-terracotta text-white font-semibold text-xs transition-colors ml-auto"
                        >
                          Request Quote
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            );
          })()}
        </div>
      )}

      {/* SECTION 3: 7-TIER HIERARCHICAL REGIONAL SOURCING ENGINE */}
      {entityType !== 'products' && (
        <div className="space-y-6">
          {/* 7-Tier Fallback Pipeline Visualizer */}
          {sourcingData && (
            <SourcingHierarchyVisualizer
              levels={sourcingData.levels_traversed}
              activeLevel={activeLevelFilter}
              onSelectLevel={(lvl) => {
                setActiveLevelFilter(prev => prev === lvl ? undefined : lvl);
              }}
            />
          )}

          {/* Results Header */}
          {sourcingData && (
            <div className="flex flex-wrap items-center justify-between gap-3 pb-3 border-b border-stone-200 text-xs">
              <div>
                <span className="font-serif text-xl font-bold text-arch-charcoal">
                  Found {sourcingData.total_suppliers_found} Sourcing Options
                </span>
                <span className="text-stone-500 ml-2">
                  ({sourcingData.verified_suppliers_count} verified vendors, {sourcingData.potential_suppliers_count} business leads)
                </span>
              </div>

              {activeLevelFilter !== undefined && (
                <div className="flex items-center gap-2">
                  <span className="px-3 py-1 rounded-full bg-arch-terracotta text-white text-xs font-semibold">
                    Filtering: Level {activeLevelFilter} ({sourcingData.levels_traversed.find(l => l.level === activeLevelFilter)?.level_name})
                  </span>
                  <button
                    onClick={() => setActiveLevelFilter(undefined)}
                    className="text-stone-500 hover:text-stone-800 underline text-xs"
                  >
                    Clear Level Filter
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Results List Grouped by Hierarchy Level */}
          {sourcingData ? (
            <div className="space-y-8">
              {sourcingData.levels_traversed
                .filter(lvl => activeLevelFilter === undefined || lvl.level === activeLevelFilter)
                .map((lvl) => {
                  const filteredSuppliers = lvl.suppliers.filter(filterSupplierByEntityType);
                  if (filteredSuppliers.length === 0) return null;

                  return (
                    <div key={lvl.level} className="space-y-3">
                      <div className="flex items-center justify-between pb-2 border-b border-arch-border">
                        <div className="flex items-center gap-2">
                          <span className="w-6 h-6 rounded-full bg-arch-dark text-white text-xs font-bold flex items-center justify-center">
                            {lvl.level}
                          </span>
                          <h3 className="font-serif text-xl font-bold text-arch-charcoal">
                            {lvl.level_name}
                          </h3>
                          <span className="text-xs text-stone-500">
                            — {lvl.radius_desc}
                          </span>
                        </div>
                        <span className="text-xs font-semibold text-arch-terracotta">
                          {filteredSuppliers.length} Supplier{filteredSuppliers.length > 1 ? 's' : ''}
                        </span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {filteredSuppliers.map((sup) => (
                          <div
                            key={sup.supplier_id}
                            className="bg-white rounded-2xl border border-arch-border p-5 hover:shadow-md transition-shadow flex flex-col justify-between"
                          >
                            <div>
                              {/* Header & Verification */}
                              <div className="flex items-start justify-between gap-2 mb-2">
                                <div>
                                  <Link
                                    href={`/supplier/${sup.supplier_id}`}
                                    className="font-serif text-lg font-bold text-arch-charcoal hover:text-arch-terracotta transition-colors"
                                  >
                                    {sup.supplier_name}
                                  </Link>
                                  <span className="block text-xs uppercase font-bold text-stone-400 mt-0.5">
                                    {sup.business_type.replace(/_/g, ' ')}
                                  </span>
                                </div>
                                  <div className="flex items-center gap-2">
                                    <VerificationBadge status={sup.verification_status} isPotential={sup.is_potential} />
                                    <button
                                      type="button"
                                      onClick={(e) => handleToggleSaveVendor(sup.supplier_id, e)}
                                      disabled={savingId === sup.supplier_id}
                                      className={`p-1.5 rounded-lg border text-xs font-medium transition-all ${
                                        savedVendorsMap[sup.supplier_id]
                                          ? 'bg-arch-terracotta text-white border-arch-terracotta'
                                          : 'bg-white hover:bg-stone-100 text-stone-500 border-stone-200 hover:text-arch-terracotta'
                                      }`}
                                      title={savedVendorsMap[sup.supplier_id] ? "Remove saved vendor" : "Save vendor"}
                                      aria-label="Save Vendor"
                                    >
                                      <Bookmark className={`w-3.5 h-3.5 ${savedVendorsMap[sup.supplier_id] ? 'fill-current' : ''}`} />
                                    </button>
                                  </div>
                              </div>

                              {/* Geographic distance & address */}
                              <div className="p-3 bg-stone-50 rounded-xl border border-stone-200 mb-3 space-y-1 text-xs">
                                <div className="flex items-center justify-between font-semibold text-arch-charcoal">
                                  <span>Location Scope:</span>
                                  <span className="text-arch-terracotta font-mono font-bold">
                                    {sup.distance_display ? sup.distance_display : (sup.distance_km !== null && sup.distance_km !== undefined ? `${sup.distance_km} km` : `${sup.city}, ${sup.state}`)}
                                  </span>
                                </div>
                                <div className="flex items-center gap-1.5 text-stone-500 text-xs">
                                  <MapPin className="w-3.5 h-3.5 text-stone-400 shrink-0" />
                                  <span className="truncate">{sup.address}</span>
                                </div>
                                {/* International Craft & Export Details */}
                                {sup.country && sup.country !== "India" && (
                                  <div className="pt-2 mt-2 border-t border-stone-200/80 text-xs text-stone-600 space-y-0.5">
                                    <div className="font-semibold text-arch-charcoal">
                                      Global Origin: <strong>{sup.country}</strong>
                                    </div>
                                    {sup.export_availability && (
                                      <div>Export Status: <span className="text-emerald-700 font-semibold">{sup.export_availability}</span></div>
                                    )}
                                    {sup.shipping_coverage && (
                                      <div>Shipping: <span className="text-stone-700">{sup.shipping_coverage}</span></div>
                                    )}
                                    {sup.import_notes && (
                                      <div className="text-stone-500 italic">{sup.import_notes}</div>
                                    )}
                                  </div>
                                )}
                              </div>

                              {/* Matched Products Preview */}
                              {sup.matched_products.length > 0 && (
                                <div className="mb-3 space-y-1.5">
                                  <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block">
                                    Available Catalog SKUs:
                                  </span>
                                  {sup.matched_products.slice(0, 2).map((mp) => (
                                    <div key={mp.product_id} className="p-2 rounded-lg bg-stone-50 border border-stone-100 text-xs flex items-center justify-between">
                                      <Link
                                        href={`/product/${mp.product_id}`}
                                        className="font-medium text-stone-800 hover:text-arch-terracotta truncate max-w-[65%]"
                                      >
                                        {mp.product_name}
                                      </Link>
                                      {mp.price ? (
                                        <span className="font-serif font-bold text-arch-charcoal">
                                          {mp.currency} {mp.price.toLocaleString()}
                                        </span>
                                      ) : (
                                        <span className="text-xs text-stone-400 italic">Quote</span>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              )}

                              {/* Contacts */}
                              <div className="space-y-1.5 text-xs text-stone-600 mb-3">
                                {(sup.phone || sup.whatsapp) && (
                                  <div className="flex items-center justify-between">
                                    {sup.phone ? (
                                      <a
                                        href={`tel:${sup.phone}`}
                                        className="flex items-center gap-1.5 font-mono hover:text-arch-terracotta transition-colors"
                                        title="Call verified vendor"
                                      >
                                        <Phone className="w-3.5 h-3.5 text-stone-400" />
                                        <span className="font-mono text-stone-800">{sup.phone}</span>
                                      </a>
                                    ) : (
                                      <span className="text-stone-400 italic text-xs">No telephone listed</span>
                                    )}
                                    {sup.whatsapp && (
                                      <a
                                        href={`https://wa.me/${sup.whatsapp.replace(/[^0-9]/g, '')}`}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-flex items-center gap-1 text-xs text-emerald-700 font-semibold bg-emerald-50 hover:bg-emerald-100 px-2 py-0.5 rounded-full border border-emerald-200 transition-colors"
                                        title="Direct WhatsApp trade inquiry"
                                      >
                                        <span>WhatsApp</span>
                                      </a>
                                    )}
                                  </div>
                                )}
                                {sup.district && (
                                  <div className="text-xs text-stone-500">
                                    District: <span className="font-medium text-stone-700">{sup.district}</span>
                                  </div>
                                )}
                                {sup.website && (
                                  <div className="flex items-center gap-1.5">
                                    <Globe className="w-3.5 h-3.5 text-stone-400" />
                                    <a
                                      href={sup.website}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-arch-terracotta hover:underline truncate max-w-[200px]"
                                    >
                                      {sup.website.replace('https://', '')}
                                    </a>
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="pt-3 border-t border-stone-100 flex items-center justify-between gap-2 text-xs">
                              {sup.google_maps_url && (
                                <a
                                  href={sup.google_maps_url}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-stone-500 hover:text-stone-800 font-medium inline-flex items-center gap-1"
                                >
                                  <span>Google Maps</span>
                                  <ExternalLink className="w-3 h-3" />
                                </a>
                              )}

                              <button
                                onClick={() => {
                                  const targetProd = sup.matched_products[0] || { id: 1, name: "Architectural Material Specification" };
                                  setActiveQuotation({
                                    product: targetProd,
                                    supplier: {
                                      ...sup,
                                      id: sup.supplier_id,
                                      name: sup.supplier_name
                                    }
                                  });
                                }}
                                className="px-3 py-1.5 rounded-lg bg-arch-terracotta hover:bg-arch-terracotta-dark text-white font-semibold transition-colors shadow-xs ml-auto"
                              >
                                Request Quotation
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
            </div>
          ) : null}
        </div>
      )}

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
}

export default function SourcingEnginePage() {
  return (
    <Suspense fallback={<div className="max-w-7xl mx-auto px-4 py-20 text-center font-serif text-lg text-stone-500">Loading Regional Sourcing Fallback Engine...</div>}>
      <SourcingContent />
    </Suspense>
  );
}
