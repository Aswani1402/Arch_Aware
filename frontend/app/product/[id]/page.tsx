"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft, ExternalLink, Building2, MapPin, Phone, Globe,
  ShieldCheck, CheckCircle2, Package, Layers, FileText, ChevronRight, Bookmark
} from 'lucide-react';
import { Product, SupplierListingBrief } from '@/types';
import { VerificationBadge } from '@/components/VerificationBadge';
import { QuotationModal } from '@/components/QuotationModal';
import { getProductDetail, toggleSavedItem } from '@/lib/api';

export default function ProductDetailPage() {
  const params = useParams();
  const idOrSlug = params.id as string;
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [activeQuotation, setActiveQuotation] = useState<{ product: any; supplier: any } | null>(null);

  useEffect(() => {
    if (!idOrSlug) return;
    setLoading(true);
    getProductDetail(idOrSlug)
      .then(res => {
        setProduct(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [idOrSlug]);

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center font-serif text-xl text-stone-500">
        Loading material catalog specifications and vendor inventory...
      </div>
    );
  }

  if (!product) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center">
        <h2 className="font-serif text-3xl font-bold text-arch-charcoal">Product not found</h2>
        <Link href="/" className="mt-4 inline-block text-arch-terracotta underline text-sm">
          Return to discovery feed
        </Link>
      </div>
    );
  }

  const specsObj = product.specs ? (() => {
    try {
      return JSON.parse(product.specs);
    } catch (e) {
      return { "Specifications": product.specs };
    }
  })() : {};

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Back Link */}
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-stone-600 hover:text-arch-terracotta transition-colors mb-6"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Continuous Discovery Feed</span>
      </Link>

      <div className="space-y-10">
        {/* Top Product Overview */}
        <div className="bg-white rounded-3xl border border-arch-border p-6 sm:p-10 shadow-sm grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Image */}
          <div className="relative rounded-2xl overflow-hidden bg-stone-100 aspect-square max-h-[460px] border border-stone-200">
            <img
              src={product.image_url || "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80"}
              alt={product.name}
              className="w-full h-full object-cover"
            />
            <div className="absolute top-4 left-4">
              <VerificationBadge status={product.verification_status} />
            </div>
          </div>

          {/* Details */}
          <div className="flex flex-col justify-between">
            <div className="space-y-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
                    {product.category?.name || "Architectural Product"}
                  </span>
                  {product.sku_code && (
                    <span className="text-xs font-mono px-2 py-0.5 rounded-md bg-stone-100 text-stone-700 font-semibold border border-stone-200">
                      SKU: {product.sku_code}
                    </span>
                  )}
                </div>
                <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal leading-tight">
                  {product.name}
                </h1>
                <div className="mt-2 text-xs text-stone-600 flex flex-wrap gap-x-4 gap-y-1">
                  <span>Product Type: <strong className="text-arch-charcoal">{product.product_type || "Commercial Specification"}</strong></span>
                  <span>Origin: <strong className="text-arch-charcoal">{product.country_of_manufacture || product.manufacturer?.country || "Not verified"}</strong></span>
                </div>
              </div>

              {/* Technical Specifications Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs p-4 bg-stone-50 rounded-2xl border border-stone-200">
                <div>
                  <span className="text-stone-400 block text-xs uppercase font-bold">Surface Finish</span>
                  <span className="font-semibold text-arch-charcoal">{product.finish || "Not verified"}</span>
                </div>
                <div>
                  <span className="text-stone-400 block text-xs uppercase font-bold">Color / Tone</span>
                  <span className="font-semibold text-arch-charcoal">{product.color || "Not verified"}</span>
                </div>
                <div>
                  <span className="text-stone-400 block text-xs uppercase font-bold">Dimensions</span>
                  <span className="font-semibold text-arch-charcoal">{product.dimensions || "Not verified"}</span>
                </div>
                <div>
                  <span className="text-stone-400 block text-xs uppercase font-bold">Thickness</span>
                  <span className="font-semibold text-arch-charcoal">{product.thickness || "Standard gauge"}</span>
                </div>
                <div>
                  <span className="text-stone-400 block text-xs uppercase font-bold">Composition</span>
                  <span className="font-semibold text-arch-charcoal">{product.material_composition || product.material_type || "Not verified"}</span>
                </div>
                <div>
                  <span className="text-stone-400 block text-xs uppercase font-bold">Intended Application</span>
                  <span className="font-semibold text-arch-charcoal truncate block" title={product.intended_use || ""}>
                    {product.intended_use || "Not verified"}
                  </span>
                </div>
              </div>

              {/* Installation Requirements if documented */}
              {product.installation_requirements && (
                <div className="p-3 bg-amber-50/60 rounded-xl border border-amber-200/80 text-xs">
                  <span className="text-xs font-bold uppercase tracking-wider text-amber-800 block mb-1">
                    Installation & Substrate Requirements
                  </span>
                  <p className="text-amber-950 leading-relaxed">
                    {product.installation_requirements}
                  </p>
                </div>
              )}

              {/* Official Catalog & Product Links */}
              <div className="flex flex-wrap items-center gap-2 pt-1 text-xs">
                {product.official_product_url && (
                  <a
                    href={product.official_product_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-800 font-semibold transition-colors"
                  >
                    <span>Manufacturer Product Page</span>
                    <ExternalLink className="w-3 h-3 text-stone-500" />
                  </a>
                )}
                {product.official_catalog_url && (
                  <a
                    href={product.official_catalog_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-900 border border-emerald-200 font-semibold transition-colors"
                  >
                    <FileText className="w-3.5 h-3.5 text-emerald-700" />
                    <span>Official Catalog Specs</span>
                    <ExternalLink className="w-3 h-3 text-emerald-700" />
                  </a>
                )}
                {product.last_checked_at && (
                  <span className="text-xs text-stone-400 ml-auto">
                    Source Verified: {new Date(product.last_checked_at).toLocaleDateString()}
                  </span>
                )}
              </div>

              {/* Key Specs Key-Values */}
              {Object.keys(specsObj).length > 0 && (
                <div className="space-y-1.5 text-xs">
                  <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block">
                    Verified Performance Metrics
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(specsObj).map(([key, val]: [string, any]) => (
                      <div key={key} className="px-3 py-1.5 rounded-lg bg-white border border-stone-200 text-stone-700">
                        <span className="text-stone-400 mr-1.5 capitalize">{key.replace(/_/g, ' ')}:</span>
                        <strong className="text-arch-charcoal">{String(val)}</strong>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Sourcing CTA Button */}
            <div className="mt-6 pt-6 border-t border-arch-border flex items-center justify-between gap-4">
              <Link
                href={`/sourcing?product_id=${product.id}`}
                className="flex-grow flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-arch-dark hover:bg-arch-terracotta text-white font-semibold text-xs transition-colors shadow-md"
              >
                <Layers className="w-4 h-4" />
                <span>Launch Regional Sourcing Fallback Engine</span>
              </Link>

              <button
                onClick={async () => {
                  const res = await toggleSavedItem({
                    item_type: 'product',
                    product_id: product.id,
                    project_collection: 'Material Specification'
                  });
                  setIsSaved(res.saved);
                }}
                className={`p-3 rounded-xl border transition-colors ${
                  isSaved ? 'bg-arch-terracotta text-white border-arch-terracotta' : 'bg-white text-stone-600 border-stone-300 hover:bg-stone-50'
                }`}
                title="Save product specification"
              >
                <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
              </button>
            </div>
          </div>
        </div>

        {/* SECTION B: Original Manufacturer / Brand Card (Distinction from Dealers) */}
        {product.manufacturer && (
          <div className="bg-stone-50 rounded-3xl border border-arch-border p-6 sm:p-8">
            <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-4 border-b border-stone-200">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-white border border-stone-200 flex items-center justify-center text-arch-charcoal font-serif font-bold text-xl shadow-xs">
                  {product.manufacturer.name.charAt(0)}
                </div>
                <div>
                  <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta block">
                    Original Product Owner / Brand
                  </span>
                  <h3 className="font-serif text-2xl font-bold text-arch-charcoal">
                    {product.manufacturer.name}
                  </h3>
                  <span className="text-xs text-stone-500">
                    Headquarters / Craft Origin: <strong>{product.manufacturer.country}</strong>
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                {product.manufacturer.official_website && (
                  <a
                    href={product.manufacturer.official_website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-stone-200 text-xs font-medium text-stone-700 hover:text-arch-terracotta transition-colors shadow-xs"
                  >
                    <Globe className="w-3.5 h-3.5 text-stone-400" />
                    <span>Official Website</span>
                    <ExternalLink className="w-3 h-3 text-stone-400" />
                  </a>
                )}
                {product.manufacturer.official_catalog_url && (
                  <a
                    href={product.manufacturer.official_catalog_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-50 border border-emerald-200 text-xs font-semibold text-emerald-900 hover:bg-emerald-100 transition-colors shadow-xs"
                  >
                    <FileText className="w-3.5 h-3.5 text-emerald-700" />
                    <span>Official Catalog PDF / Specs</span>
                    <ExternalLink className="w-3 h-3 text-emerald-700" />
                  </a>
                )}
              </div>
            </div>

            <p className="text-xs text-stone-600 leading-relaxed max-w-3xl">
              {product.manufacturer.description}
            </p>
          </div>
        )}

        {/* SECTION D: Available Suppliers (One Product, Multiple Vendors) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
                Multi-Vendor Comparison
              </span>
              <h3 className="font-serif text-2xl font-bold text-arch-charcoal">
                Available Suppliers ({product.available_suppliers?.length || 0})
              </h3>
            </div>
            <Link
              href={`/sourcing?product_id=${product.id}`}
              className="text-xs font-semibold text-arch-terracotta hover:underline inline-flex items-center gap-1"
            >
              <span>View Expanded Regional Fallback Sourcing</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {product.available_suppliers && product.available_suppliers.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {product.available_suppliers.map((sup) => (
                <div
                  key={sup.supplier_id}
                  className="bg-white rounded-2xl border border-arch-border p-5 hover:shadow-md transition-shadow flex flex-col justify-between"
                >
                  <div>
                    {/* Supplier Name & Verification */}
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <Link
                        href={`/supplier/${sup.supplier_id}`}
                        className="font-serif text-lg font-bold text-arch-charcoal hover:text-arch-terracotta transition-colors"
                      >
                        {sup.supplier_name}
                      </Link>
                      <VerificationBadge status={sup.availability_status} isPotential={sup.is_potential} />
                    </div>

                    {/* Match Type Badge */}
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`text-xs font-bold uppercase tracking-wider px-2 py-0.5 rounded-md ${
                        sup.match_type === 'exact_product'
                          ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                          : sup.match_type === 'verified_equivalent'
                          ? 'bg-blue-50 text-blue-800 border border-blue-200'
                          : 'bg-stone-100 text-stone-700'
                      }`}>
                        {sup.match_type === 'exact_product' ? 'Exact Product Match' : sup.match_type === 'verified_equivalent' ? 'Verified Equivalent' : 'Alternative Offer'}
                      </span>
                      {sup.supplier_product_code && (
                        <span className="text-xs font-mono text-stone-500">
                          Code: {sup.supplier_product_code}
                        </span>
                      )}
                    </div>

                    {/* Location & Delivery */}
                    <div className="flex items-center gap-1.5 text-xs text-stone-500 mb-3">
                      <MapPin className="w-3.5 h-3.5 text-stone-400 shrink-0" />
                      <span>{sup.city}, {sup.state}</span>
                      {sup.delivery_scope && (
                        <span className="text-xs px-2 py-0.5 rounded-full bg-stone-100 text-stone-600 font-mono ml-auto">
                          {sup.delivery_scope}
                        </span>
                      )}
                    </div>

                    {/* Confirmed Price with Unit */}
                    {sup.price ? (
                      <div className="p-3 bg-stone-50 rounded-xl border border-stone-200 mb-3 flex items-baseline justify-between">
                        <span className="text-xs text-stone-500">Confirmed Rate:</span>
                        <div className="font-serif text-xl font-bold text-arch-charcoal">
                          {sup.currency} {sup.price.toLocaleString()}
                          {sup.price_unit && (
                            <span className="text-xs font-sans font-normal text-stone-500 ml-1">
                              / {sup.price_unit}
                            </span>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="p-3 bg-stone-50 rounded-xl border border-stone-200 mb-3 text-xs text-stone-500 text-center italic">
                        Contact vendor for project pricing & freight
                      </div>
                    )}

                    {/* Stock Status & Lead Time */}
                    <div className="flex flex-wrap items-center justify-between gap-1 text-xs mb-3 p-2 bg-stone-50/70 rounded-lg border border-stone-150">
                      <span className={`font-semibold ${
                        sup.stock_status === 'IN_STOCK'
                          ? 'text-emerald-700'
                          : sup.stock_status === 'LEAD_TIME_REQUIRED'
                          ? 'text-amber-700'
                          : 'text-stone-600'
                      }`}>
                        {sup.stock_status === 'IN_STOCK' ? 'In Stock' : sup.stock_status === 'LEAD_TIME_REQUIRED' ? 'Lead Time Required' : (sup.stock_status || 'Stock on request')}
                      </span>
                      {sup.estimated_lead_time_days && (
                        <span className="text-stone-500">
                          ~{sup.estimated_lead_time_days} days lead
                        </span>
                      )}
                      {sup.min_order_quantity && (
                        <span className="text-stone-500 w-full text-xs">
                          MOQ: <strong>{sup.min_order_quantity}</strong>
                        </span>
                      )}
                    </div>

                    {/* Phone Contact */}
                    {sup.phone && (
                      <div className="flex items-center gap-1.5 text-xs text-stone-600 mb-2">
                        <Phone className="w-3.5 h-3.5 text-stone-400" />
                        <span className="font-mono">{sup.phone}</span>
                      </div>
                    )}
                  </div>

                  {/* Actions: Maps link and Quote CTA */}
                  <div className="pt-3 border-t border-stone-100 flex items-center justify-between gap-2 text-xs">
                    <a
                      href={sup.google_maps_url || `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(`${sup.supplier_name} ${sup.city} ${sup.state}`)}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-stone-500 hover:text-arch-terracotta font-medium inline-flex items-center gap-1 text-xs"
                      title="Open address in Google Maps (Zero-Paid Navigation)"
                    >
                      <span>Google Maps</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>

                    <div className="flex items-center gap-2">
                      <Link
                        href={`/supplier/${sup.supplier_id}`}
                        className="text-stone-600 hover:text-arch-charcoal font-medium text-xs"
                      >
                        Profile
                      </Link>

                      <button
                        onClick={() => setActiveQuotation({
                          product,
                          supplier: {
                            ...sup,
                            id: sup.supplier_id,
                            name: sup.supplier_name
                          }
                        })}
                        className="px-3.5 py-1.5 rounded-lg bg-arch-terracotta hover:bg-arch-terracotta-dark text-white font-semibold transition-colors shadow-xs"
                      >
                        Request Quote
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 text-center bg-white rounded-2xl border border-arch-border text-xs text-stone-500">
              No local dealers currently listed for this specific SKU. Use the regional sourcing engine to expand your search radius across South India or Pan-India freight networks.
            </div>
          )}
        </div>

        {/* SECTION C: Related Architectural References */}
        {product.related_references && product.related_references.length > 0 && (
          <div className="space-y-4 pt-6 border-t border-arch-border">
            <h3 className="font-serif text-2xl font-bold text-arch-charcoal">
              Featured In Architectural References
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {product.related_references.map((ref) => (
                <Link
                  key={ref.id}
                  href={`/reference/${ref.slug || ref.id}`}
                  className="group bg-white rounded-2xl border border-arch-border overflow-hidden hover:shadow-md transition-all flex flex-col"
                >
                  <div className="relative aspect-video overflow-hidden bg-stone-100">
                    <img
                      src={ref.thumbnail_url}
                      alt={ref.title}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  </div>
                  <div className="p-4">
                    <h4 className="font-serif text-base font-bold text-arch-charcoal group-hover:text-arch-terracotta transition-colors line-clamp-1">
                      {ref.title}
                    </h4>
                    <span className="text-xs text-stone-500 block mt-1">
                      By {ref.creator_name} ({ref.source_platform})
                    </span>
                  </div>
                </Link>
              ))}
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
}
