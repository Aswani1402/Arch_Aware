"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft, Layers, ShieldCheck, Building2, MapPin,
  ChevronRight, ExternalLink, Package, FileText, CheckCircle2,
  Compass, Phone, Mail, Globe, ArrowRight, Bookmark
} from 'lucide-react';
import { Category, Product, Reference } from '@/types';
import { QuotationModal } from '@/components/QuotationModal';
import { getCategoryDetail } from '@/lib/api';

export default function CategoryDetailPage() {
  const params = useParams();
  const slug = params.slug as string;
  const [category, setCategory] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeQuotation, setActiveQuotation] = useState<{ product: any; supplier: any } | null>(null);

  useEffect(() => {
    if (!slug) return;
    setLoading(true);
    getCategoryDetail(slug)
      .then((data) => {
        setCategory(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load category", err);
        setLoading(false);
      });
  }, [slug]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center font-serif text-lg text-stone-500">
        <div className="w-8 h-8 border-2 border-arch-terracotta border-t-transparent rounded-full animate-spin mx-auto mb-2" />
        Loading material category dossier, specifications, and regional availability...
      </div>
    );
  }

  if (!category) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center">
        <h2 className="font-serif text-2xl font-bold text-arch-charcoal">Category not found</h2>
        <Link href="/materials" className="mt-4 inline-block text-arch-terracotta underline text-xs">
          Return to materials catalogue
        </Link>
      </div>
    );
  }

  const subcats = category.subcategories
    ? category.subcategories.split(',').map((s: string) => s.trim())
    : [];
  const applications = category.typical_applications
    ? category.typical_applications.split(',').map((s: string) => s.trim())
    : [];
  const products: any[] = category.products || [];
  const references: any[] = category.references || [];

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Back Navigation */}
      <div className="flex items-center justify-between">
        <Link
          href="/materials"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-stone-600 hover:text-arch-terracotta transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Materials Catalogue</span>
        </Link>

        <Link
          href={`/sourcing?category=${encodeURIComponent(category.slug)}`}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-arch-dark hover:bg-arch-terracotta text-white font-semibold text-xs transition-colors shadow-2xs"
        >
          <MapPin className="w-3.5 h-3.5 text-arch-terracotta" />
          <span>Find Regional Suppliers</span>
        </Link>
      </div>

      {/* 1. Category Overview Banner */}
      <section className="bg-white rounded-3xl border border-arch-border p-6 sm:p-10 shadow-sm space-y-6">
        <div className="space-y-3">
          <div className="flex flex-wrap items-center gap-2">
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-stone-100 text-stone-800 font-mono">
              Section {category.section_code || "Taxonomy"}
            </span>
            <span className="text-xs text-stone-400 uppercase tracking-wider font-semibold">
              {category.section_name || "Architectural Material"}
            </span>
          </div>

          <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal leading-tight">
            {category.name}
          </h1>

          <p className="text-sm text-stone-600 leading-relaxed max-w-3xl font-sans">
            {category.description || "Comprehensive architectural classification, applications, and verified manufacturer specifications."}
          </p>
        </div>

        {/* 2 & 3. Subcategories & Applications Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-stone-100 text-xs">
          {/* Subcategories */}
          <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200/80 space-y-2">
            <div className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-stone-500 text-xs">
              <Layers className="w-3.5 h-3.5 text-arch-terracotta" />
              <span>Available Product Types & Subcategories</span>
            </div>
            {subcats.length > 0 ? (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {subcats.map((sub: string) => (
                  <span
                    key={sub}
                    className="px-2.5 py-1 rounded-lg bg-white text-stone-800 font-medium border border-stone-200 shadow-2xs"
                  >
                    {sub}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-stone-400 italic">Subcategories being catalogued by curators.</p>
            )}
          </div>

          {/* Typical Applications */}
          <div className="p-4 rounded-2xl bg-stone-50 border border-stone-200/80 space-y-2">
            <div className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-stone-500 text-xs">
              <Building2 className="w-3.5 h-3.5 text-arch-terracotta" />
              <span>Typical Applications & Building Locations</span>
            </div>
            {applications.length > 0 ? (
              <div className="flex flex-wrap gap-1.5 pt-1">
                {applications.map((app: string) => (
                  <span
                    key={app}
                    className="px-2.5 py-1 rounded-lg bg-white text-stone-800 font-medium border border-stone-200 shadow-2xs"
                  >
                    {app}
                  </span>
                ))}
              </div>
            ) : (
              <p className="text-stone-400 italic">Applications being documented.</p>
            )}
          </div>
        </div>

        {/* 4. Standards & Regulatory Compliance */}
        {category.standards_compliance && (
          <div className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200 text-xs space-y-1">
            <div className="flex items-center gap-1.5 font-bold uppercase tracking-wider text-emerald-800 text-xs">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              <span>Architectural Standards & Testing Codes</span>
            </div>
            <p className="text-emerald-900 font-mono text-xs">
              {category.standards_compliance}
            </p>
            <span className="text-xs text-emerald-700 block">
              Specifications must be verified against current Bureau of Indian Standards (BIS) / IS / ASTM testing certificates prior to tender submission.
            </span>
          </div>
        )}
      </section>

      {/* 5. Verified Manufacturer Products in this Category */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-serif text-2xl font-bold text-arch-charcoal">
              Manufacturer Products & Commercial Specifications ({products.length})
            </h2>
            <p className="text-xs text-stone-500 mt-0.5">
              Verified technical catalog items with dimensional data, testing specs, and dealer networks.
            </p>
          </div>
          <Link
            href="/compare"
            className="text-xs font-semibold text-arch-terracotta hover:underline"
          >
            Compare Products &rarr;
          </Link>
        </div>

        {products.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {products.map((prod) => (
              <div
                key={prod.id}
                className="p-5 rounded-2xl bg-white border border-arch-border hover:border-arch-terracotta/40 hover:shadow-md transition-all flex flex-col justify-between space-y-4"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-xs font-bold uppercase tracking-wider text-stone-400">
                      SKU: {prod.sku || `PROD-${prod.id}`}
                    </span>
                    {prod.price_unit && (
                      <span className="text-xs font-semibold text-stone-600 bg-stone-100 px-2 py-0.5 rounded-md">
                        {prod.price_unit}
                      </span>
                    )}
                  </div>

                  <h3 className="font-serif text-lg font-bold text-arch-charcoal leading-snug">
                    <Link href={`/product/${prod.id}`} className="hover:text-arch-terracotta transition-colors">
                      {prod.name}
                    </Link>
                  </h3>

                  {prod.manufacturer_name && (
                    <div className="text-xs text-stone-600">
                      Manufacturer: <strong className="text-stone-800">{prod.manufacturer_name}</strong>
                    </div>
                  )}

                  {prod.description && (
                    <p className="text-xs text-stone-500 line-clamp-2 leading-relaxed">
                      {prod.description}
                    </p>
                  )}
                </div>

                <div className="pt-3 border-t border-stone-100 flex items-center justify-between text-xs">
                  <Link
                    href={`/product/${prod.id}`}
                    className="font-semibold text-arch-terracotta hover:underline"
                  >
                    Technical Specs &rarr;
                  </Link>

                  <button
                    onClick={() => setActiveQuotation({
                      product: { id: prod.id, name: prod.name },
                      supplier: null,
                    })}
                    className="px-3 py-1 rounded-lg bg-arch-dark hover:bg-arch-terracotta text-white font-semibold text-xs transition-colors"
                  >
                    Request Quote
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center bg-white rounded-2xl border border-arch-border text-xs text-stone-500">
            No specific commercial SKUs verified under this category yet. You can find regional dealers supplying equivalent materials below.
          </div>
        )}
      </section>

      {/* 6. Relevant Projects & Inspiration */}
      {references.length > 0 && (
        <section className="space-y-4">
          <div>
            <h2 className="font-serif text-2xl font-bold text-arch-charcoal">
              Architectural Projects Using {category.name} ({references.length})
            </h2>
            <p className="text-xs text-stone-500 mt-0.5">
              Explore real-world architectural applications and documented material assemblies.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {references.map((ref) => (
              <div
                key={ref.id}
                className="p-4 rounded-2xl bg-white border border-arch-border hover:border-arch-terracotta/40 transition-all flex flex-col justify-between"
              >
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta block mb-1">
                    {ref.source_platform} Reference
                  </span>
                  <h3 className="font-serif text-base font-bold text-arch-charcoal line-clamp-2">
                    <Link href={`/reference/${ref.slug || ref.id}`} className="hover:text-arch-terracotta">
                      {ref.title}
                    </Link>
                  </h3>
                </div>

                <div className="mt-3 pt-3 border-t border-stone-100 flex items-center justify-between text-xs">
                  <span className="text-stone-400 text-xs">In-situ Application</span>
                  <Link
                    href={`/reference/${ref.slug || ref.id}`}
                    className="font-semibold text-arch-charcoal hover:text-arch-terracotta"
                  >
                    Explore &rarr;
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

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
