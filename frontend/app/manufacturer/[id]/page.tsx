"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft, Globe, FileText, Youtube, ExternalLink, Package,
  Layers, CheckCircle2, ChevronRight
} from 'lucide-react';
import { getManufacturerDetail } from '@/lib/api';

export default function ManufacturerProfilePage() {
  const params = useParams();
  const idOrSlug = params.id as string;
  const [mfg, setMfg] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!idOrSlug) return;
    setLoading(true);
    getManufacturerDetail(idOrSlug)
      .then(res => {
        setMfg(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [idOrSlug]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center font-serif text-xl text-stone-500">
        Loading manufacturer catalog and brand profile...
      </div>
    );
  }

  if (!mfg) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center">
        <h2 className="font-serif text-3xl font-bold text-arch-charcoal">Manufacturer not found</h2>
        <Link href="/" className="mt-4 inline-block text-arch-terracotta underline text-sm">
          Return to discovery feed
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Back Link */}
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-stone-600 hover:text-arch-terracotta transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Architectural Discovery Feed</span>
      </Link>

      {/* Brand Header */}
      <div className="bg-white rounded-3xl border border-arch-border p-6 sm:p-10 shadow-sm space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-4 pb-6 border-b border-arch-border">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-2xl bg-arch-surface border border-arch-border flex items-center justify-center text-arch-charcoal font-serif font-bold text-3xl shadow-xs">
              {mfg.name.charAt(0)}
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
                  Official Brand / Original Product Owner
                </span>
                <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-900 border border-emerald-300">
                  <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                  <span>Manufacturer Confirmed</span>
                </span>
              </div>
              <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal leading-tight">
                {mfg.name}
              </h1>
              {mfg.company_name && mfg.company_name !== mfg.name && (
                <span className="text-xs text-stone-500 mt-0.5 block">
                  Legal Entity: <strong className="text-stone-700">{mfg.company_name}</strong>
                </span>
              )}
              <span className="text-xs text-stone-500 mt-1 block">
                Country of Origin: <strong className="text-stone-800">{mfg.country}</strong>
              </span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {mfg.official_website && (
              <a
                href={mfg.official_website}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-white border border-stone-200 text-xs font-semibold text-stone-700 hover:text-arch-terracotta transition-colors shadow-xs"
              >
                <Globe className="w-4 h-4 text-stone-400" />
                <span>Official Website</span>
                <ExternalLink className="w-3 h-3 text-stone-400" />
              </a>
            )}
            {mfg.official_catalog_url && (
              <a
                href={mfg.official_catalog_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-emerald-50 border border-emerald-200 text-xs font-semibold text-emerald-900 hover:bg-emerald-100 transition-colors shadow-xs"
              >
                <FileText className="w-4 h-4 text-emerald-700" />
                <span>Official Catalog</span>
                <ExternalLink className="w-3 h-3 text-emerald-700" />
              </a>
            )}
            {mfg.official_product_page_url && (
              <a
                href={mfg.official_product_page_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-blue-50 border border-blue-200 text-xs font-semibold text-blue-900 hover:bg-blue-100 transition-colors shadow-xs"
              >
                <Layers className="w-4 h-4 text-blue-700" />
                <span>Professional Paint/Spec Page</span>
                <ExternalLink className="w-3 h-3 text-blue-700" />
              </a>
            )}
            {(mfg.youtube_channel_url || mfg.official_video_channel_url) && (
              <a
                href={mfg.youtube_channel_url || mfg.official_video_channel_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-red-50 border border-red-200 text-xs font-semibold text-red-900 hover:bg-red-100 transition-colors shadow-xs"
              >
                <Youtube className="w-4 h-4 text-red-600" />
                <span>YouTube Channel</span>
                <ExternalLink className="w-3 h-3 text-red-600" />
              </a>
            )}
          </div>
        </div>

        <p className="text-sm text-stone-600 leading-relaxed max-w-3xl">
          {mfg.description}
        </p>

        {/* Provenance & Verification Metadata Box */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs pt-4 border-t border-arch-border">
          <div className="p-3 bg-stone-50 rounded-xl border border-stone-200">
            <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block mb-1">
              Contact Information
            </span>
            <span className="text-stone-800 font-medium">
              {mfg.contact_info || "Published on official website"}
            </span>
          </div>

          <div className="p-3 bg-stone-50 rounded-xl border border-stone-200">
            <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block mb-1">
              Verification Status
            </span>
            <span className="font-semibold text-emerald-800">
              {mfg.verification_status || "VERIFIED"}
            </span>
            {mfg.last_verified_at && (
              <span className="text-xs text-stone-500 block mt-0.5">
                Checked: {new Date(mfg.last_verified_at).toLocaleDateString()}
              </span>
            )}
          </div>

          <div className="p-3 bg-stone-50 rounded-xl border border-stone-200">
            <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block mb-1">
              Data Provenance Source
            </span>
            {mfg.source_url ? (
              <a
                href={mfg.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-arch-terracotta hover:underline font-mono truncate block text-xs"
              >
                {mfg.source_url.replace(/^https?:\/\//, '')}
              </a>
            ) : (
              <span className="text-stone-500 text-xs">Primary manufacturer site</span>
            )}
          </div>

          <div className="p-3 bg-stone-50 rounded-xl border border-stone-200">
            <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block mb-1">
              Unverified Fields Note
            </span>
            <span className="text-stone-500 text-xs">
              {mfg.unverified_notes || "All public catalog links verified."}
            </span>
          </div>
        </div>
      </div>

      {/* Product Catalog */}
      <div className="space-y-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
            Verified Architectural Catalog
          </span>
          <h2 className="font-serif text-2xl font-bold text-arch-charcoal">
            Official Products Produced by {mfg.name} ({mfg.products?.length || 0})
          </h2>
        </div>

        {mfg.products && mfg.products.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {mfg.products.map((p: any) => (
              <div
                key={p.id}
                className="bg-white rounded-2xl border border-arch-border overflow-hidden hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                <div className="relative aspect-video bg-stone-100 overflow-hidden">
                  <img
                    src={p.image_url}
                    alt={p.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="p-5 flex-grow flex flex-col justify-between">
                  <div>
                    <span className="text-xs font-bold uppercase text-arch-terracotta block mb-1">
                      {p.category_name || "Material"}
                    </span>
                    <h3 className="font-serif text-lg font-bold text-arch-charcoal mb-1">
                      {p.name}
                    </h3>
                    <p className="text-xs text-stone-600 mb-2">
                      {p.material_type}
                    </p>
                    <span className="text-xs text-stone-500">
                      Available through <strong className="text-arch-charcoal">{p.available_suppliers_count} regional vendors</strong>
                    </span>
                  </div>

                  <div className="mt-4 pt-3 border-t border-stone-100 flex items-center justify-between text-xs">
                    <Link
                      href={`/product/${p.id}`}
                      className="font-semibold text-arch-terracotta hover:underline inline-flex items-center gap-1"
                    >
                      <span>Specifications & Dealers</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center bg-white rounded-2xl border border-arch-border text-xs text-stone-500">
            No products currently cataloged for this brand.
          </div>
        )}
      </div>
    </div>
  );
}
