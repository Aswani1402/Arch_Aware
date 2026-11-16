"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { X, ExternalLink, Bookmark, MapPin, Layers, Phone, Building2, ChevronRight, CheckCircle2, ShieldCheck, Sparkles, ImageOff, Compass } from 'lucide-react';
import { Reference, ReferenceProductMatch } from '@/types';
import { SourceBadge } from './SourceBadge';
import { VerificationBadge } from './VerificationBadge';
import { YouTubeEmbed } from './YouTubeEmbed';
import { QuotationModal } from './QuotationModal';
import { getReferenceDetail, toggleSavedItem, getSavedItems, getProductDetail, hasAuthToken } from '@/lib/api';

interface ReferenceModalProps {
  referenceId: number | string | null;
  onClose: () => void;
}

export const ReferenceModal: React.FC<ReferenceModalProps> = ({ referenceId, onClose }) => {
  const [detail, setDetail] = useState<Reference | null>(null);
  const [loading, setLoading] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  const [activeQuotation, setActiveQuotation] = useState<{ product: any; supplier: any } | null>(null);
  const [imgError, setImgError] = useState(false);

  useEffect(() => {
    if (!referenceId) return;
    setLoading(true);
    setImgError(false);
    getReferenceDetail(referenceId.toString())
      .then(res => {
        setDetail(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    // Check if already saved when authenticated
    if (hasAuthToken()) {
      getSavedItems()
        .then(items => {
          const isAlreadySaved = items.some(
            i => i.item_type === 'reference' && String(i.reference_id) === String(referenceId)
          );
          setIsSaved(isAlreadySaved);
        })
        .catch(() => {});
    }
  }, [referenceId]);

  const handleLaunchQuote = async (match: ReferenceProductMatch) => {
    try {
      const prodDetail = await getProductDetail(match.product_id.toString());
      const supplier = prodDetail.available_suppliers && prodDetail.available_suppliers.length > 0
        ? prodDetail.available_suppliers[0]
        : null;
      if (supplier) {
        setActiveQuotation({ product: prodDetail, supplier });
      }
    } catch {
      // Do not fabricate an unverified supplier if product lookup fails
    }
  };

  if (!referenceId) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/70 backdrop-blur-sm overflow-y-auto animate-in fade-in duration-200">
      <div className="relative w-full max-w-4xl bg-white rounded-3xl shadow-2xl border border-arch-border overflow-hidden my-auto max-h-[90vh] flex flex-col">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-20 p-2 rounded-full bg-black/40 hover:bg-black/60 text-white backdrop-blur-md transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {loading || !detail ? (
          <div className="p-16 text-center text-stone-500 font-serif text-lg">
            Retrieving architectural reference and sourcable materials...
          </div>
        ) : (
          <div className="overflow-y-auto flex-grow">
            <div className="grid grid-cols-1 md:grid-cols-2">
              {/* Media Column */}
              <div className="bg-stone-100 flex flex-col justify-center p-4 sm:p-6 border-b md:border-b-0 md:border-r border-arch-border">
                {detail.source_platform === 'youtube' && detail.video_embed_id ? (
                  <YouTubeEmbed
                    videoId={detail.video_embed_id}
                    title={detail.title}
                    sourceUrl={detail.source_url}
                  />
                ) : (
                  <div className="relative rounded-2xl overflow-hidden shadow-md bg-stone-200 min-h-[260px] flex items-center justify-center">
                    {imgError ? (
                      <div className="p-8 text-center text-stone-500 space-y-2">
                        <ImageOff className="w-10 h-10 text-stone-400 mx-auto" />
                        <p className="text-xs font-semibold">Image preview unavailable from source</p>
                        <p className="text-xs text-stone-400">Source attribution is preserved below</p>
                      </div>
                    ) : (
                      <img
                        src={detail.inspiration_image_url || detail.thumbnail_url || detail.media_url || "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80"}
                        alt={detail.title}
                        onError={() => setImgError(true)}
                        className="w-full h-auto object-cover max-h-[500px]"
                      />
                    )}
                  </div>
                )}

                {/* Source attribution bar */}
                <div className="mt-4 p-3 bg-white rounded-xl border border-arch-border flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <SourceBadge
                      platform={detail.source_platform}
                      sourceUrl={detail.source_url}
                      creatorName={detail.creator_name}
                    />
                  </div>
                  <a
                    href={detail.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 text-arch-terracotta hover:underline font-medium"
                  >
                    <span>View Original Source</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>
                </div>
              </div>

              {/* Information & Sourcing Column */}
              <div className="p-6 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
                      {detail.category_name || "Architectural Inspiration"}
                    </span>
                    {detail.location_context && (
                      <span className="flex items-center gap-1 text-xs text-stone-500">
                        <MapPin className="w-3.5 h-3.5 text-stone-400" />
                        <span>{detail.location_context}</span>
                      </span>
                    )}
                  </div>

                  <h2 className="font-serif text-2xl font-bold text-arch-charcoal leading-tight">
                    {detail.title}
                  </h2>

                  {/* Provenance Status Tag */}
                  <div className="mt-2">
                    {detail.product_match_status === 'verified_match' && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        <span>Verified Commercial Match</span>
                      </span>
                    )}
                    {detail.product_match_status === 'commercial_specification' && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
                        <ShieldCheck className="w-3 h-3 text-blue-600" />
                        <span>Commercial Specification</span>
                      </span>
                    )}
                    {detail.product_match_status === 'probable_match' && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">
                        <Sparkles className="w-3 h-3 text-amber-600" />
                        <span>Probable Match</span>
                      </span>
                    )}
                    {(!detail.product_match_status || detail.product_match_status === 'unidentified') && (
                      <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-stone-100 text-stone-600 border border-stone-200">
                        <Compass className="w-3 h-3 text-stone-500" />
                        <span>Design Inspiration Reference</span>
                      </span>
                    )}
                  </div>

                  <p className="mt-3 text-xs text-stone-600 leading-relaxed">
                    {detail.description}
                  </p>

                  {/* Identified Materials Section */}
                  <div className="mt-6 pt-5 border-t border-arch-border">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-1.5">
                        <Layers className="w-4 h-4 text-arch-terracotta" />
                        <h4 className="text-xs font-bold uppercase tracking-wider text-arch-charcoal">
                          Identified Materials & Products ({detail.product_matches?.length || 0})
                        </h4>
                      </div>
                      <span className="text-xs text-stone-400">Decoupled Provenance</span>
                    </div>

                    {detail.product_matches && detail.product_matches.length > 0 ? (
                      <div className="space-y-3">
                        {detail.product_matches.map((match) => (
                          <div
                            key={match.product_id}
                            className="p-3.5 bg-stone-50 rounded-xl border border-stone-200 hover:border-arch-terracotta/40 transition-colors"
                          >
                            <div className="flex items-start justify-between gap-2">
                              <div>
                                <Link
                                  href={`/product/${match.product_id}`}
                                  className="text-sm font-semibold text-arch-charcoal hover:text-arch-terracotta transition-colors"
                                >
                                  {match.product_name}
                                </Link>
                                <div className="text-xs text-stone-500 mt-0.5">
                                  Original Brand / Manufacturer: <strong className="text-stone-700">{match.manufacturer_name || "Not verified"}</strong>
                                </div>
                              </div>
                              <VerificationBadge status={match.match_type} />
                            </div>

                            {match.evidence_notes && (
                              <p className="mt-2 text-xs text-stone-600 italic bg-white p-2 rounded border border-stone-100">
                                &ldquo;{match.evidence_notes}&rdquo;
                              </p>
                            )}

                            <div className="mt-3 flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-stone-200/60 text-xs">
                              <Link
                                href={`/product/${match.product_id}`}
                                className="text-arch-terracotta hover:underline font-medium inline-flex items-center gap-1"
                              >
                                <span>Compare Available Vendors</span>
                                <ChevronRight className="w-3.5 h-3.5" />
                              </Link>

                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => handleLaunchQuote(match)}
                                  className="px-2.5 py-1 rounded-lg bg-arch-terracotta hover:bg-arch-terracotta-dark text-white font-medium text-xs transition-colors shadow-xs"
                                >
                                  Request Quotation
                                </button>
                                <Link
                                  href={`/sourcing?product_id=${match.product_id}`}
                                  className="px-2.5 py-1 rounded-lg bg-arch-dark hover:bg-arch-terracotta text-white font-medium text-xs transition-colors shadow-xs"
                                >
                                  Sourcing &rarr;
                                </Link>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="p-4 bg-stone-50 rounded-xl text-center text-xs text-stone-500 space-y-2">
                        <p>This architectural reference is an inspiration / craft technique.</p>
                        <p className="text-xs text-stone-400">No specific commercial manufacturer has been arbitrarily claimed.</p>
                        <div className="pt-1">
                          <Link
                            href={`/sourcing?q=${encodeURIComponent(detail.category_name || detail.title)}`}
                            className="text-arch-terracotta font-medium hover:underline inline-flex items-center gap-1"
                          >
                            <span>Search visually similar regional materials &rarr;</span>
                          </Link>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Footer Actions */}
                <div className="mt-6 pt-4 border-t border-arch-border flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={async () => {
                        const res = await toggleSavedItem({
                          item_type: 'reference',
                          reference_id: detail.id,
                          project_collection: 'Architect Board'
                        });
                        setIsSaved(res.saved);
                      }}
                      className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium border transition-colors ${
                        isSaved
                          ? 'bg-arch-terracotta text-white border-arch-terracotta'
                          : 'bg-white hover:bg-stone-100 text-stone-700 border-stone-300'
                      }`}
                    >
                      <Bookmark className={`w-3.5 h-3.5 ${isSaved ? 'fill-current' : ''}`} />
                      <span>{isSaved ? "Saved to Moodboard" : "Save Reference"}</span>
                    </button>
                  </div>

                  <Link
                    href={`/reference/${detail.slug || detail.id}`}
                    className="text-xs font-semibold text-arch-charcoal hover:text-arch-terracotta"
                  >
                    Open Standalone Page &rarr;
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}
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
