"use client";

import React, { useState, useEffect, useMemo } from 'react';
import {
  X, Bookmark, ExternalLink, Building2, MapPin,
  Phone, Globe, ShieldCheck, CheckCircle2, AlertCircle, Compass,
  Layers, MessageSquare, Mail, Tag, Video, Sparkles, Check, ImageOff
} from 'lucide-react';
import {
  Reference,
  InspirationMaterial,
  HierarchicalSourcingResponse,
  SourcingSupplierResult
} from '@/types';
import { SourceBadge } from './SourceBadge';
import { VerificationBadge } from './VerificationBadge';
import {
  getReferenceDetail,
  searchSourcing,
  detectReferenceMaterials,
  toggleSavedItem,
  getSavedItems,
  hasAuthToken
} from '@/lib/api';
import { useAuth } from '@/lib/authContext';
import { useNavigation } from '@/lib/navigationContext';

interface ContextualDetailsDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  reference: Reference | null;
  referenceId?: number | string | null;
  onOpenQuotation?: (product: any, supplier: any) => void;
  onOpenSaveModal?: (item: any) => void;
  onSelectCategory?: (categorySlug: string) => void;
  onSearchQuery?: (query: string) => void;
}

export const ContextualDetailsDrawer: React.FC<ContextualDetailsDrawerProps> = ({
  isOpen,
  onClose,
  reference: initialReference,
  referenceId,
}) => {
  const { location } = useAuth();
  const { refreshSavedCounts } = useNavigation();
  const [reference, setReference] = useState<Reference | null>(initialReference);
  const [loading, setLoading] = useState(false);

  // Saved state
  const [isSaved, setIsSaved] = useState(false);
  const [savedVendorsMap, setSavedVendorsMap] = useState<Record<number, boolean>>({});

  // Materials state (Section 1: AI Materials)
  const [detectionData, setDetectionData] = useState<any>(null);
  const [detectingMaterials, setDetectingMaterials] = useState(false);

  // Sourcing & Vendor state (Section 2: Suppliers / Vendors)
  const [sourcingData, setSourcingData] = useState<HierarchicalSourcingResponse | null>(null);
  const [sourcingLoading, setSourcingLoading] = useState(false);

  // Sync reference when opened
  useEffect(() => {
    if (initialReference) {
      setReference(initialReference);
    } else if (referenceId && isOpen) {
      setLoading(true);
      getReferenceDetail(String(referenceId))
        .then((data) => setReference(data))
        .catch((err) => console.error("Error loading reference details", err))
        .finally(() => setLoading(false));
    }
  }, [initialReference, referenceId, isOpen]);

  // Check saved status
  useEffect(() => {
    if (!isOpen || !reference || !hasAuthToken()) return;
    getSavedItems()
      .then((items) => {
        if (Array.isArray(items)) {
          const refSaved = items.some(
            (i) => i.item_type === 'reference' && i.reference_id === reference.id
          );
          setIsSaved(refSaved);

          const vendorMap: Record<number, boolean> = {};
          items.forEach((i) => {
            if (i.item_type === 'supplier' && i.supplier_id) {
              vendorMap[i.supplier_id] = true;
            }
          });
          setSavedVendorsMap(vendorMap);
        }
      })
      .catch(() => {});
  }, [isOpen, reference]);

  // Fetch AI Materials analysis (only for persisted SQLite reference rows)
  useEffect(() => {
    if (!isOpen || !reference) return;
    if (typeof reference.id === 'number' && reference.id < 0) {
      setDetectionData(null);
      setDetectingMaterials(false);
      return;
    }

    setDetectingMaterials(true);
    detectReferenceMaterials(reference.id || reference.slug)
      .then((res) => {
        setDetectionData(res);
      })
      .catch((e) => {
        console.error("AI Material detection error", e);
      })
      .finally(() => setDetectingMaterials(false));
  }, [isOpen, reference]);

  // Fetch Suppliers / Vendors based on materials and location hierarchy
  useEffect(() => {
    if (!isOpen || !reference) return;

    setSourcingLoading(true);
    const searchTerm =
      reference.material_tags?.split(',')[0]?.trim() ||
      reference.title?.split(' ')[0] ||
      reference.category?.name ||
      "architecture";

    searchSourcing({
      q: searchTerm,
      city: location.city || undefined,
      state: location.state || undefined,
      lat: location.lat || undefined,
      lon: location.lon || undefined,
      radius: 40
    })
      .then((res) => {
        setSourcingData(res);
      })
      .catch((e) => {
        console.error("Failed to load hierarchical sourcing", e);
      })
      .finally(() => setSourcingLoading(false));
  }, [isOpen, reference, location.city, location.state, location.lat, location.lon]);

  const listingMeta = useMemo(() => {
    if (!reference?.colors_and_finishes) return null;
    try {
      return JSON.parse(reference.colors_and_finishes);
    } catch {
      return null;
    }
  }, [reference]);

  const handleToggleSaveRef = async () => {
    if (!reference || !hasAuthToken() || (typeof reference.id === 'number' && reference.id < 0)) return;
    try {
      const res = await toggleSavedItem({
        item_type: 'reference',
        reference_id: reference.id
      });
      setIsSaved(res.saved);
      refreshSavedCounts();
    } catch (e) {
      console.error("Failed to toggle save reference", e);
    }
  };

  const handleToggleSaveVendor = async (supplierId: number) => {
    try {
      const res = await toggleSavedItem({
        item_type: 'supplier',
        supplier_id: supplierId,
        project_collection: 'Verified Trade Directory'
      });
      setSavedVendorsMap(prev => ({
        ...prev,
        [supplierId]: res.saved
      }));
      refreshSavedCounts();
    } catch (e) {
      console.error("Failed to toggle save supplier", e);
    }
  };

  // Build clean list of AI Materials
  const materialsList = useMemo(() => {
    const list: Array<{
      objectOrMaterial: string;
      identification: string;
      category: string;
      tier: 'verified' | 'detected' | 'inferred';
      confidence?: number;
      productUrl?: string;
    }> = [];

    // 1. Verified product matches
    if (reference?.product_matches) {
      reference.product_matches.forEach((pm) => {
        if (pm.product_name) {
          list.push({
            objectOrMaterial: "Verified Product",
            identification: pm.manufacturer_name ? `${pm.product_name} (${pm.manufacturer_name})` : pm.product_name,
            category: "Verified Product Match",
            tier: 'verified',
            confidence: pm.match_confidence || 1.0,
            productUrl: pm.image_url
          });
        }
      });
    }

    // 2. Visually detected from AI response
    if (detectionData?.visually_detected) {
      detectionData.visually_detected.forEach((vd: any) => {
        list.push({
          objectOrMaterial: vd.element || vd.object || "Visual Object",
          identification: vd.detected_material || vd.description || "Identified in frame",
          category: vd.category || "Visual Feature",
          tier: 'detected',
          confidence: vd.confidence || 0.95
        });
      });
    }

    // 3. AI-inferred materials with uncertainty qualifiers
    if (detectionData?.inferred) {
      detectionData.inferred.forEach((inf: any) => {
        list.push({
          objectOrMaterial: inf.category || "Surface / Fixture",
          identification: inf.qualified_label || `${inf.name}, likely`,
          category: inf.category || "Material",
          tier: 'inferred',
          confidence: inf.confidence || 0.85
        });
      });
    }

    // Fallback parsing from reference material tags if detection is empty
    if (list.length === 0 && reference?.material_tags) {
      const tags = reference.material_tags.split(',').map(t => t.trim()).filter(Boolean);
      tags.forEach((tag, idx) => {
        list.push({
          objectOrMaterial: idx === 0 ? "Primary Material" : "Secondary Material",
          identification: `${tag}, likely`,
          category: reference.category?.name || "Architectural Material",
          tier: 'inferred',
          confidence: 0.82
        });
      });
    }

    return list;
  }, [reference, detectionData]);

  // Combine and deduplicate vendors across hierarchical tiers
  const hierarchicalVendors = useMemo(() => {
    if (!sourcingData) return [];
    const vendors: Array<SourcingSupplierResult & { tierLabel: string; id: number; name: string; materials_sold?: string }> = [];

    if (Array.isArray(sourcingData.levels_traversed)) {
      sourcingData.levels_traversed.forEach((lvl) => {
        (lvl.suppliers || []).forEach((v) => {
          vendors.push({
            ...v,
            id: v.supplier_id,
            name: v.supplier_name,
            tierLabel: lvl.level_name || `${v.city}, ${v.state}`,
            materials_sold: v.matched_products?.map(p => p.product_name).join(', ') || v.business_type
          });
        });
      });
    }

    if (vendors.length === 0 && Array.isArray(sourcingData.tiers)) {
      sourcingData.tiers.forEach((tier) => {
        (tier.suppliers || []).forEach((v) => {
          vendors.push({
            ...v,
            id: v.supplier_id,
            name: v.supplier_name,
            tierLabel: tier.tier_name,
            materials_sold: v.matched_products?.map(p => p.product_name).join(', ') || v.business_type
          });
        });
      });
    }

    // Fallback checking tier1 to tier5
    if (vendors.length === 0) {
      const allTierArrays = [
        ...(sourcingData.tier1_suppliers || []),
        ...(sourcingData.tier2_suppliers || []),
        ...(sourcingData.tier3_suppliers || []),
        ...(sourcingData.tier4_suppliers || []),
        ...(sourcingData.tier5_suppliers || []),
      ];
      allTierArrays.forEach((v) => {
        vendors.push({
          ...v,
          id: v.supplier_id,
          name: v.supplier_name,
          tierLabel: v.geographic_scope || `${v.city}, ${v.state}`,
          materials_sold: v.matched_products?.map(p => p.product_name).join(', ') || v.business_type
        });
      });
    }

    // Deduplicate by id
    const seen = new Set<number>();
    return vendors.filter((v) => {
      if (seen.has(v.id)) return false;
      seen.add(v.id);
      return true;
    });
  }, [sourcingData]);

  // Get external source button label
  const getSourceButtonLabel = (platform?: string) => {
    switch (platform?.toLowerCase()) {
      case 'instagram':
        return 'Open in Instagram';
      case 'youtube':
        return 'Open in YouTube';
      case 'pinterest':
        return 'Open in Pinterest';
      case 'reddit':
        return 'Open in Reddit';
      case 'x':
      case 'twitter':
        return 'Open in X';
      case 'shopping':
      case 'google_shopping':
        return 'Open Product Listing';
      case 'google':
      case 'google_search':
        return 'Open Google Result';
      default:
        return 'Open Original Source';
    }
  };

  const [drawerImgError, setDrawerImgError] = useState(false);

  useEffect(() => {
    setDrawerImgError(false);
  }, [reference?.id]);

  if (!isOpen || !reference) return null;

  const originalUrl = reference.source_url || reference.inspiration_source_url;
  const rawImageUrl = reference.inspiration_image_url || reference.thumbnail_url || reference.media_url;
  const imageUrl = (typeof rawImageUrl === 'string' && rawImageUrl.startsWith('http')) ? rawImageUrl : null;

  return (
    <>
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-stone-900/60 backdrop-blur-xs z-50 transition-opacity"
        onClick={onClose}
      />

      {/* Main Clean Detail Panel */}
      <div className="fixed inset-y-0 right-0 z-50 w-full max-w-2xl bg-white dark:bg-arch-dark-card shadow-2xl flex flex-col border-l border-arch-border dark:border-arch-dark-border animate-in slide-in-from-right duration-200">
        
        {/* Panel Header */}
        <div className="px-6 py-4 border-b border-arch-border dark:border-arch-dark-border bg-stone-50/90 dark:bg-arch-dark-surface/90 flex items-center justify-between gap-3 shrink-0 min-w-0">
          <div className="flex items-center gap-2 min-w-0 flex-1">
            <div className="shrink-0">
              <SourceBadge platform={reference.source_platform || 'pinterest'} size="md" />
            </div>
            <span className="text-secondary font-semibold text-arch-charcoal dark:text-stone-100 truncate min-w-0">
              {reference.title || "Architectural Inspiration"}
            </span>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            {/* Save Button */}
            <button
              onClick={handleToggleSaveRef}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-secondary font-medium whitespace-nowrap transition-all ${
                isSaved
                  ? 'bg-arch-terracotta text-white shadow-xs'
                  : 'bg-white dark:bg-arch-dark-surface border border-arch-border dark:border-arch-dark-border text-stone-700 dark:text-stone-300 hover:border-arch-terracotta hover:text-arch-terracotta'
              }`}
              title={isSaved ? "Saved to your inspiration" : "Save to inspiration"}
            >
              <Bookmark className={`w-3.5 h-3.5 shrink-0 ${isSaved ? 'fill-white' : ''}`} />
              <span>{isSaved ? "Saved" : "Save"}</span>
            </button>

            {/* Open Original Source */}
            {originalUrl && (
              <a
                href={originalUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-secondary font-medium whitespace-nowrap bg-arch-charcoal dark:bg-stone-100 text-white dark:text-arch-dark-bg hover:bg-stone-800 dark:hover:bg-white transition-colors shadow-xs"
              >
                <span>{getSourceButtonLabel(reference.source_platform)}</span>
                <ExternalLink className="w-3.5 h-3.5 shrink-0" />
              </a>
            )}

            <button
              onClick={onClose}
              aria-label="Close details drawer"
              className="p-1.5 rounded-xl text-stone-400 hover:text-stone-600 dark:hover:text-stone-200 hover:bg-stone-200/60 dark:hover:bg-stone-800 transition-colors shrink-0"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Scrollable Body: Strictly 2 Sections (AI Materials & Suppliers / Vendors) */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">

          {/* Media Thumbnail Preview */}
          <div className="relative rounded-xl overflow-hidden bg-stone-100 dark:bg-arch-dark-surface border border-arch-border dark:border-arch-dark-border min-h-[140px] max-h-72 flex items-center justify-center">
            {imageUrl && !drawerImgError ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={imageUrl}
                alt={reference.title || "Inspiration"}
                referrerPolicy="no-referrer"
                onError={() => setDrawerImgError(true)}
                className="w-full h-full object-cover max-h-72"
              />
            ) : (
              <div className="w-full p-6 flex flex-col items-center justify-center text-center space-y-1.5">
                <ImageOff className="w-7 h-7 text-stone-300 dark:text-stone-600" />
                <p className="text-xs font-semibold text-arch-charcoal dark:text-stone-200">
                  {reference.source_platform === 'reddit' ? 'Reddit Discussion Specimen' : 'Architectural Reference Specimen'}
                </p>
                <p className="text-xs text-arch-muted dark:text-arch-dark-muted max-w-sm line-clamp-2">
                  {reference.description || reference.title}
                </p>
              </div>
            )}
            {reference.video_embed_id && (
              <div className="absolute inset-0 bg-black/20 flex items-center justify-center pointer-events-none">
                <span className="px-3 py-1.5 rounded-full bg-black/60 text-white text-xs font-medium backdrop-blur-md flex items-center gap-1.5">
                  <Video className="w-4 h-4 text-arch-terracotta" />
                  Video / Reel
                </span>
              </div>
            )}
          </div>

          {/* Commercial Listing / Product Details (Google Shopping / External Listings) */}
          {(reference.source_platform === 'google_shopping' || listingMeta?.price_label || listingMeta?.seller) && (
            <div className="rounded-xl border border-emerald-200 bg-emerald-50/40 p-4 space-y-2.5">
              <div className="flex items-center justify-between gap-2 flex-wrap">
                <span className="text-xs font-semibold text-arch-charcoal uppercase tracking-wider">
                  Commercial Listing Details
                </span>
                <VerificationBadge
                  status={reference.verification_status || 'UNVERIFIED'}
                  size="sm"
                />
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                {listingMeta?.price_label && (
                  <div>
                    <span className="text-stone-500">Price: </span>
                    <span className="font-semibold text-emerald-700">{listingMeta.price_label}</span>
                  </div>
                )}
                <div>
                  <span className="text-stone-500">Seller: </span>
                  <span className="font-medium text-stone-800">
                    {listingMeta?.seller || reference.creator_name || "Not provided by listing"}
                  </span>
                </div>
                {listingMeta?.brand && (
                  <div>
                    <span className="text-stone-500">Brand: </span>
                    <span className="font-medium text-stone-800">{listingMeta.brand}</span>
                  </div>
                )}
                {listingMeta?.availability && (
                  <div>
                    <span className="text-stone-500">Availability: </span>
                    <span className="font-medium text-stone-800">{listingMeta.availability}</span>
                  </div>
                )}
                {listingMeta?.rating != null && (
                  <div>
                    <span className="text-stone-500">Rating: </span>
                    <span className="font-medium text-stone-800">
                      {listingMeta.rating}{listingMeta?.reviews_count != null ? ` (${listingMeta.reviews_count} reviews)` : ''}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ========================================================= */}
          {/* SECTION 1: AI MATERIALS                                    */}
          {/* ========================================================= */}
          <div className="rounded-xl border border-arch-border bg-white p-5 shadow-xs">
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-arch-border">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-md bg-arch-terracotta/10 text-arch-terracotta flex items-center justify-center">
                  <Sparkles className="w-3.5 h-3.5" />
                </div>
                <h3 className="text-sm font-semibold text-arch-charcoal">
                  1. AI Materials
                </h3>
              </div>
              <span className="text-xs text-stone-400">
                Visual Inspection &amp; Inference
              </span>
            </div>

            {detectingMaterials ? (
              <div className="py-6 flex items-center justify-center text-xs text-stone-400 gap-2">
                <div className="w-4 h-4 border-2 border-arch-terracotta border-t-transparent rounded-full animate-spin" />
                <span>Analyzing visible materials &amp; finishes...</span>
              </div>
            ) : materialsList.length === 0 ? (
              <div className="py-4 text-center text-xs text-stone-500">
                Visual materials detected as general architectural finishes.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-stone-200 text-stone-400 uppercase text-xs tracking-wider">
                      <th className="py-2 pr-3 font-semibold">AI Material / Object</th>
                      <th className="py-2 px-3 font-semibold">Identification</th>
                      <th className="py-2 pl-3 font-semibold text-right">Confidence / Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-stone-100">
                    {materialsList.map((item, idx) => (
                      <tr key={idx} className="hover:bg-stone-50/80 transition-colors">
                        <td className="py-2.5 pr-3 font-medium text-stone-800">
                          {item.objectOrMaterial}
                        </td>
                        <td className="py-2.5 px-3 text-stone-600">
                          <span>{item.identification}</span>
                          {item.productUrl && (
                            <a
                              href={item.productUrl}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="ml-2 inline-flex items-center gap-0.5 text-arch-terracotta hover:underline text-xs"
                            >
                              <span>View Product</span>
                              <ExternalLink className="w-2.5 h-2.5" />
                            </a>
                          )}
                        </td>
                        <td className="py-2.5 pl-3 text-right">
                          {item.tier === 'verified' ? (
                            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
                              <Check className="w-3 h-3 text-emerald-600" />
                              Verified Match
                            </span>
                          ) : item.tier === 'detected' ? (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200">
                              Visually Detected
                            </span>
                          ) : (
                            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-stone-100 text-stone-600 border border-stone-200">
                              AI Inferred ({Math.round((item.confidence || 0.85) * 100)}%)
                            </span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* ========================================================= */}
          {/* SECTION 2: SUPPLIERS / VENDORS                             */}
          {/* ========================================================= */}
          <div className="rounded-xl border border-arch-border bg-white p-5 shadow-xs">
            <div className="flex items-center justify-between pb-3 mb-3 border-b border-arch-border">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-md bg-arch-dark text-white flex items-center justify-center">
                  <Building2 className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-arch-charcoal">
                    2. Suppliers / Vendors
                  </h3>
                </div>
              </div>
              <div className="flex items-center gap-1 text-xs text-stone-500">
                <MapPin className="w-3 h-3 text-arch-terracotta" />
                <span>Prioritised by: {location.city ? `${location.city}${location.state ? `, ${location.state}` : ''}` : "Regional & National Trade Hubs"}</span>
              </div>
            </div>

            {/* Sourcing hierarchy note */}
            <div className="mb-3 p-2 rounded-lg bg-stone-50 border border-stone-200 flex items-center justify-between text-xs text-stone-500">
              <span className="flex items-center gap-1">
                <Compass className="w-3.5 h-3.5 text-arch-terracotta" />
                Sourcing Hierarchy: Nearby Locality &rarr; City &rarr; District &rarr; State &rarr; Pan-India
              </span>
              <span className="font-medium text-stone-700">
                {hierarchicalVendors.length} Verified Sources
              </span>
            </div>

            {sourcingLoading ? (
              <div className="py-6 flex items-center justify-center text-xs text-stone-400 gap-2">
                <div className="w-4 h-4 border-2 border-arch-terracotta border-t-transparent rounded-full animate-spin" />
                <span>Locating regional manufacturers, dealers &amp; showrooms...</span>
              </div>
            ) : hierarchicalVendors.length === 0 ? (
              <div className="py-4 text-center text-xs text-stone-500">
                No local suppliers found for this exact material in the current radius. Sourcing nationwide distributors.
              </div>
            ) : (
              <div className="space-y-3">
                {hierarchicalVendors.slice(0, 8).map((vendor) => {
                  const isVendorSaved = Boolean(savedVendorsMap[vendor.id]);
                  return (
                    <div
                      key={vendor.id}
                      className="p-3.5 rounded-xl border border-arch-border bg-stone-50/50 hover:bg-white hover:border-stone-300 hover:shadow-xs transition-all flex flex-col gap-2"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <div className="flex items-center gap-1.5 flex-wrap">
                            <h4 className="text-xs font-semibold text-arch-charcoal">
                              {vendor.name}
                            </h4>
                            <VerificationBadge
                              status={vendor.verification_status || 'UNKNOWN'}
                              isPotential={Boolean(vendor.is_potential || String(vendor.verification_status || '').toUpperCase().startsWith('POTENTIAL'))}
                              size="sm"
                            />
                            <span className="text-xs text-arch-terracotta bg-orange-50 border border-orange-200 px-1.5 py-0.2 rounded-full font-medium">
                              {vendor.tierLabel}
                            </span>
                          </div>

                          <div className="mt-1 flex items-center gap-2 text-xs text-stone-500">
                            <span className="flex items-center gap-0.5">
                              <MapPin className="w-3 h-3 text-stone-400" />
                              {vendor.city}{vendor.state ? `, ${vendor.state}` : ''}
                            </span>
                            {vendor.materials_sold && (
                              <span className="text-stone-400">&bull; {vendor.materials_sold}</span>
                            )}
                          </div>

                          {/* Honest Match Type Label (Part 16) */}
                          {vendor.match_label && (
                            <div className="mt-1.5 flex items-center gap-1.5 flex-wrap">
                              <span className={`inline-flex items-center px-2 py-0.5 rounded-md font-medium text-xs ${
                                vendor.match_type === 'exact_product'
                                  ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                                  : 'bg-amber-50 text-amber-800 border border-amber-200'
                              }`}>
                                {vendor.match_label}
                              </span>
                              {vendor.match_explanation && (
                                <span className="text-stone-500 text-xs italic">
                                  ({vendor.match_explanation})
                                </span>
                              )}
                            </div>
                          )}
                        </div>

                        {/* Save Vendor Button */}
                        <button
                          onClick={() => handleToggleSaveVendor(vendor.id)}
                          className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
                            isVendorSaved
                              ? 'bg-arch-terracotta text-white'
                              : 'bg-white border border-arch-border text-stone-600 hover:text-arch-terracotta'
                          }`}
                          title={isVendorSaved ? "Saved vendor" : "Save vendor to board"}
                        >
                          <Bookmark className={`w-3 h-3 ${isVendorSaved ? 'fill-white' : ''}`} />
                          <span>{isVendorSaved ? "Saved" : "Save Vendor"}</span>
                        </button>
                      </div>

                      {/* Contact Channels (Only when available - no fabricated contact info) */}
                      <div className="pt-2 border-t border-stone-200/60 flex items-center gap-3 flex-wrap text-xs">
                        {vendor.phone && (
                          <a
                            href={`tel:${vendor.phone}`}
                            className="flex items-center gap-1 text-stone-700 hover:text-arch-charcoal font-medium"
                          >
                            <Phone className="w-3 h-3 text-stone-400" />
                            <span>{vendor.phone}</span>
                          </a>
                        )}

                        {vendor.whatsapp && (
                          <a
                            href={`https://wa.me/${vendor.whatsapp.replace(/[^0-9]/g, '')}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-emerald-700 hover:text-emerald-800 font-medium"
                          >
                            <MessageSquare className="w-3 h-3 text-emerald-600" />
                            <span>WhatsApp</span>
                          </a>
                        )}

                        {vendor.email && (
                          <a
                            href={`mailto:${vendor.email}`}
                            className="flex items-center gap-1 text-stone-600 hover:text-arch-charcoal"
                          >
                            <Mail className="w-3 h-3 text-stone-400" />
                            <span>Email</span>
                          </a>
                        )}

                        {vendor.google_maps_url ? (
                          <a
                            href={vendor.google_maps_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-blue-600 hover:underline text-xs"
                          >
                            <MapPin className="w-3 h-3 text-blue-500" />
                            <span>Maps / Directions</span>
                          </a>
                        ) : vendor.address ? (
                          <a
                            href={`https://www.google.com/maps/dir/?api=1&destination=${encodeURIComponent(vendor.name + ' ' + vendor.address + ' ' + (vendor.city || ''))}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-blue-600 hover:underline text-xs"
                          >
                            <MapPin className="w-3 h-3 text-blue-500" />
                            <span>Directions</span>
                          </a>
                        ) : null}

                        {vendor.website && (
                          <a
                            href={vendor.website}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex items-center gap-1 text-arch-terracotta hover:underline ml-auto"
                          >
                            <span>Website</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

        </div>
      </div>
    </>
  );
};
