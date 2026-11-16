"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft, ExternalLink, Bookmark, MapPin, Layers,
  ChevronRight, Package, Building2, User, CheckCircle2,
  AlertCircle, Sparkles, HelpCircle, ShieldCheck, Share2, Compass
} from 'lucide-react';
import { Reference, InspirationMaterial, Product } from '@/types';
import { SourceBadge } from '@/components/SourceBadge';
import { YouTubeEmbed } from '@/components/YouTubeEmbed';
import { QuotationModal } from '@/components/QuotationModal';
import { getReferenceDetail, toggleSavedItem, getSavedItems, hasAuthToken } from '@/lib/api';

// 16 architectural building components
const BUILDING_COMPONENTS = [
  "Structure",
  "Foundation",
  "Walls and masonry",
  "Roof",
  "Facade and exterior finish",
  "Windows and glazing",
  "Flooring",
  "Interior walls",
  "Ceiling",
  "Doors and hardware",
  "Kitchen and joinery",
  "Bathroom and plumbing",
  "Electrical and lighting",
  "HVAC",
  "Landscape and external works",
  "Sustainable systems",
];

export default function ProjectDetailPage() {
  const params = useParams();
  const idOrSlug = params.id as string;
  const [detail, setDetail] = useState<Reference | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [activeQuotation, setActiveQuotation] = useState<{ product: any; supplier: any } | null>(null);
  const [selectedComponentFilter, setSelectedComponentFilter] = useState<string>("All");

  useEffect(() => {
    if (!idOrSlug) return;
    setLoading(true);
    getReferenceDetail(idOrSlug)
      .then(res => {
        setDetail(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    if (hasAuthToken()) {
      getSavedItems()
        .then(saved => {
          if (Array.isArray(saved)) {
            const found = saved.some(item =>
              item.item_type === 'reference' &&
              (item.reference_id?.toString() === idOrSlug || item.reference?.slug === idOrSlug)
            );
            setIsSaved(found);
          }
        })
        .catch(() => {});
    }
  }, [idOrSlug]);

  const handleToggleSave = async () => {
    if (!detail) return;
    try {
      const res = await toggleSavedItem({
        item_type: 'reference',
        reference_id: detail.id,
      });
      setIsSaved(res.status === 'saved');
    } catch (err: any) {
      alert(err.message || 'Please log in to save to your project collection');
    }
  };

  const renderIdentificationStateBadge = (state?: string, confidence?: number) => {
    if (state === 'confirmed' || state === 'Confirmed in project documentation') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
          <span>Confirmed in project documentation</span>
          {confidence && <span className="text-xs opacity-75 font-mono">({Math.round(confidence * 100)}%)</span>}
        </span>
      );
    }
    if (state === 'likely' || state === 'Likely material — visual inference') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-900 border border-amber-200">
          <Sparkles className="w-3 h-3 text-amber-600" />
          <span>Likely material — visual inference</span>
          {confidence && <span className="text-xs opacity-75 font-mono">({Math.round(confidence * 100)}%)</span>}
        </span>
      );
    }
    if (state === 'similar_product' || state === 'Similar product — not confirmed as the original') {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-900 border border-blue-200">
          <ShieldCheck className="w-3 h-3 text-blue-600" />
          <span>Similar product — not confirmed as the original</span>
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-stone-100 text-stone-700 border border-stone-200">
        <HelpCircle className="w-3 h-3 text-stone-500" />
        <span>Unknown — further investigation needed</span>
      </span>
    );
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center font-serif text-lg text-stone-500">
        <div className="w-8 h-8 border-2 border-arch-terracotta border-t-transparent rounded-full animate-spin mx-auto mb-2" />
        Loading architectural project dossier and material specifications...
      </div>
    );
  }

  if (!detail) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center">
        <h2 className="font-serif text-2xl font-bold text-arch-charcoal">Project not found</h2>
        <Link href="/" className="mt-4 inline-block text-arch-terracotta underline text-xs">
          Return to architectural discovery
        </Link>
      </div>
    );
  }

  // Group materials by building component
  const materials = detail.inspiration_materials || [];
  const groupedMaterials: Record<string, InspirationMaterial[]> = {};

  materials.forEach((mat) => {
    const comp = mat.building_component || "Walls and masonry";
    if (!groupedMaterials[comp]) {
      groupedMaterials[comp] = [];
    }
    groupedMaterials[comp].push(mat);
  });

  const availableComponents = Object.keys(groupedMaterials);

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      {/* Top Navigation Bar */}
      <div className="flex items-center justify-between">
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-stone-600 hover:text-arch-terracotta transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Discover</span>
        </Link>

        <div className="flex items-center gap-2">
          <button
            onClick={handleToggleSave}
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold border transition-colors ${
              isSaved
                ? 'bg-arch-terracotta text-white border-arch-terracotta shadow-xs'
                : 'bg-white text-stone-700 border-stone-200 hover:border-arch-terracotta'
            }`}
          >
            <Bookmark className={`w-3.5 h-3.5 ${isSaved ? 'fill-current' : ''}`} />
            <span>{isSaved ? 'Saved in Moodboard' : 'Save Project'}</span>
          </button>
        </div>
      </div>

      {/* Main Dossier Card */}
      <article className="bg-white rounded-3xl border border-arch-border overflow-hidden shadow-sm">
        {/* Media Presentation Banner */}
        <div className="p-4 sm:p-6 bg-stone-100 border-b border-arch-border">
          {detail.source_platform === 'youtube' && detail.video_embed_id ? (
            <div className="max-w-4xl mx-auto">
              <YouTubeEmbed
                videoId={detail.video_embed_id}
                title={detail.title}
                sourceUrl={detail.source_url}
              />
            </div>
          ) : (
            <div className="relative rounded-2xl overflow-hidden max-w-4xl mx-auto shadow-sm bg-stone-200">
              <img referrerPolicy="no-referrer"
                src={detail.inspiration_image_url || detail.thumbnail_url || detail.media_url || "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"}
                alt={detail.title}
                className="w-full h-auto max-h-[500px] object-cover"
              />
              <div className="absolute bottom-2 right-2 px-2.5 py-1 rounded-md bg-black/60 backdrop-blur-xs text-xs text-white">
                Architectural In-Situ Reference
              </div>
            </div>
          )}
        </div>

        {/* Project Metadata & Attribution */}
        <div className="p-6 sm:p-10 space-y-8">
          <div className="space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div className="flex flex-wrap items-center gap-2">
                <SourceBadge
                  platform={detail.source_platform}
                  sourceUrl={detail.source_url}
                  creatorName={detail.creator_name}
                />
                <span className="text-stone-300">•</span>
                <span className="text-xs font-semibold text-arch-terracotta uppercase tracking-wider">
                  {detail.architectural_style || detail.category_name || "Architectural Project"}
                </span>
                {detail.project_type && (
                  <>
                    <span className="text-stone-300">•</span>
                    <span className="text-xs text-stone-600 font-medium">{detail.project_type}</span>
                  </>
                )}
              </div>

              {(detail.location_context || detail.region || detail.country) && (
                <span className="flex items-center gap-1 text-xs text-stone-500 font-medium">
                  <MapPin className="w-3.5 h-3.5 text-stone-400" />
                  <span>{[detail.region, detail.country].filter(Boolean).join(', ') || detail.location_context}</span>
                </span>
              )}
            </div>

            <h1 className="font-serif text-2xl sm:text-3xl lg:text-4xl font-bold text-arch-charcoal leading-tight">
              {detail.title}
            </h1>

            {detail.architect_name && (
              <div className="flex items-center gap-2 text-xs text-stone-700 bg-stone-50 p-2.5 rounded-xl border border-stone-200/80 w-fit">
                <User className="w-3.5 h-3.5 text-stone-400" />
                <span>Architect / Practice: <strong className="font-semibold text-arch-charcoal">{detail.architect_name}</strong></span>
              </div>
            )}

            <p className="text-xs sm:text-sm text-stone-600 leading-relaxed max-w-4xl">
              {detail.description}
            </p>

            {detail.source_url && (
              <div className="pt-1">
                <a
                  href={detail.source_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs font-semibold text-arch-terracotta hover:underline"
                >
                  <span>View Original Publication / Source</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            )}
          </div>

          {/* DEDICATED MATERIALS USED SECTION BY BUILDING COMPONENT */}
          <section className="pt-8 border-t border-arch-border space-y-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <div className="flex items-center gap-2">
                  <Layers className="w-5 h-5 text-arch-terracotta" />
                  <h2 className="font-serif text-xl sm:text-2xl font-bold text-arch-charcoal">
                    Materials Used in Project ({materials.length})
                  </h2>
                </div>
                <p className="text-xs text-stone-500 mt-1">
                  Organized by architectural component. Commercial matches distinguish verified specifications from visually inferred alternatives.
                </p>
              </div>

              {/* Component Filter Pills */}
              {availableComponents.length > 1 && (
                <div className="flex items-center gap-1.5 overflow-x-auto scrollbar-none py-1">
                  <button
                    onClick={() => setSelectedComponentFilter("All")}
                    className={`px-2.5 py-1 rounded-full text-xs font-medium transition-colors ${
                      selectedComponentFilter === "All"
                        ? "bg-arch-dark text-white"
                        : "bg-stone-100 text-stone-600 hover:bg-stone-200"
                    }`}
                  >
                    All Components
                  </button>
                  {availableComponents.map((comp) => (
                    <button
                      key={comp}
                      onClick={() => setSelectedComponentFilter(comp)}
                      className={`px-2.5 py-1 rounded-full text-xs font-medium whitespace-nowrap transition-colors ${
                        selectedComponentFilter === comp
                          ? "bg-arch-terracotta text-white"
                          : "bg-stone-100 text-stone-600 hover:bg-stone-200"
                      }`}
                    >
                      {comp}
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Component-wise Breakdown Cards */}
            {materials.length > 0 ? (
              <div className="space-y-6">
                {(selectedComponentFilter === "All" ? availableComponents : [selectedComponentFilter]).map((componentName) => {
                  const compMaterials = groupedMaterials[componentName] || [];
                  if (compMaterials.length === 0) return null;

                  return (
                    <div key={componentName} className="space-y-3">
                      <div className="flex items-center gap-2 pb-1 border-b border-stone-200">
                        <span className="w-2 h-2 rounded-full bg-arch-terracotta" />
                        <h3 className="font-serif text-base font-bold text-arch-charcoal">
                          {componentName}
                        </h3>
                        <span className="text-xs text-stone-400 font-mono">({compMaterials.length})</span>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {compMaterials.map((mat) => {
                          const matchedProd = mat.matched_product;

                          return (
                            <div
                              key={mat.id}
                              className="p-5 rounded-2xl bg-stone-50 border border-stone-200 flex flex-col justify-between hover:border-arch-terracotta/40 transition-all space-y-4"
                            >
                              <div>
                                {/* Status Badge & Category */}
                                <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
                                  <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
                                    {mat.category_slug || "Material"}
                                  </span>
                                  {renderIdentificationStateBadge(mat.identification_state, mat.confidence_score)}
                                </div>

                                {/* Material Title */}
                                <h4 className="font-serif text-lg font-bold text-arch-charcoal">
                                  {mat.material_name}
                                </h4>

                                {/* Known Finish / Specification */}
                                {mat.finish_specification && (
                                  <div className="mt-1 text-xs text-stone-700">
                                    <span className="text-stone-400">Spec / Finish: </span>
                                    <span className="font-medium">{mat.finish_specification}</span>
                                  </div>
                                )}

                                {/* Evidence & Notes */}
                                {mat.evidence_notes && (
                                  <div className="mt-2.5 p-3 rounded-xl bg-white border border-stone-100 text-xs text-stone-600 space-y-1">
                                    <div className="font-semibold text-stone-700">Evidence & Provenance:</div>
                                    <p className="italic">&ldquo;{mat.evidence_notes}&rdquo;</p>
                                    {mat.source_evidence_url && (
                                      <a
                                        href={mat.source_evidence_url}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="inline-flex items-center gap-1 text-xs text-arch-terracotta hover:underline mt-1"
                                      >
                                        <span>View Documentation Link</span>
                                        <ExternalLink className="w-2.5 h-2.5" />
                                      </a>
                                    )}
                                  </div>
                                )}

                                {/* Commercial Product Match (if available) */}
                                {matchedProd && (
                                  <div className="mt-3 p-3 rounded-xl bg-white border border-stone-200 space-y-1.5">
                                    <div className="text-xs font-bold uppercase tracking-wider text-stone-400">
                                      Commercial Product Specification
                                    </div>
                                    <div className="flex items-center justify-between">
                                      <Link
                                        href={`/product/${matchedProd.id}`}
                                        className="text-xs font-bold text-arch-charcoal hover:text-arch-terracotta transition-colors"
                                      >
                                        {matchedProd.name}
                                      </Link>
                                      {matchedProd.manufacturer_name && (
                                        <span className="text-xs text-stone-500">
                                          Mfg: <strong>{matchedProd.manufacturer_name}</strong>
                                        </span>
                                      )}
                                    </div>
                                  </div>
                                )}
                              </div>

                              {/* Action Footer: Find Regional Suppliers & Quotation */}
                              <div className="pt-3 border-t border-stone-200/80 flex flex-wrap items-center justify-between gap-2 text-xs">
                                <Link
                                  href={`/sourcing?q=${encodeURIComponent(mat.material_name)}`}
                                  className="inline-flex items-center gap-1 px-3 py-1.5 rounded-xl bg-arch-dark hover:bg-arch-terracotta text-white font-semibold transition-colors shadow-2xs"
                                >
                                  <span>Find Regional Suppliers</span>
                                  <ChevronRight className="w-3.5 h-3.5" />
                                </Link>

                                {matchedProd && (
                                  <button
                                    onClick={() => setActiveQuotation({
                                      product: { id: matchedProd.id, name: matchedProd.name },
                                      supplier: null,
                                    })}
                                    className="px-3 py-1.5 rounded-xl bg-white hover:bg-stone-100 text-stone-700 font-semibold border border-stone-200 transition-colors"
                                  >
                                    Request Quote
                                  </button>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-8 text-center bg-stone-50 rounded-2xl border border-stone-200 text-xs text-stone-500">
                <p>Material identification for this architectural reference is currently under investigation by our curators.</p>
                <Link
                  href="/materials"
                  className="mt-3 inline-block font-semibold text-arch-terracotta underline"
                >
                  Browse Full Materials Catalogue &rarr;
                </Link>
              </div>
            )}
          </section>
        </div>
      </article>

      {/* Direct Quotation Modal */}
      <QuotationModal
        isOpen={!!activeQuotation}
        onClose={() => setActiveQuotation(null)}
        product={activeQuotation?.product}
        supplier={activeQuotation?.supplier}
      />
    </div>
  );
}
