"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import {
  ArrowLeft, Building2, MapPin, Phone, Mail, Globe, ExternalLink,
  ShieldCheck, Package, Layers, ChevronRight, Bookmark, MessageSquare
} from 'lucide-react';
import { Supplier } from '@/types';
import { VerificationBadge } from '@/components/VerificationBadge';
import { QuotationModal } from '@/components/QuotationModal';
import { getSupplierDetail, toggleSavedItem, getSavedItems, hasAuthToken } from '@/lib/api';
import { useNavigation } from '@/lib/navigationContext';

export default function SupplierProfilePage() {
  const params = useParams();
  const idOrSlug = params.id as string;
  const { refreshSavedCounts } = useNavigation();
  const [supplier, setSupplier] = useState<Supplier | null>(null);
  const [loading, setLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [activeQuotation, setActiveQuotation] = useState<{ product: any; supplier: any } | null>(null);

  useEffect(() => {
    if (!idOrSlug) return;
    setLoading(true);
    getSupplierDetail(idOrSlug)
      .then(res => {
        setSupplier(res);
        setLoading(false);
        // Check saved status
        if (hasAuthToken()) {
          getSavedItems()
            .then((items: any[]) => {
              if (Array.isArray(items)) {
                const saved = items.some(
                  i => i.item_type === 'supplier' && (i.supplier_id === res.id || (i.item_data && i.item_data.id === res.id))
                );
                setIsSaved(saved);
              }
            })
            .catch(() => {});
        }
      })
      .catch(() => setLoading(false));
  }, [idOrSlug]);

  const handleToggleSave = async () => {
    if (!supplier || saving) return;
    setSaving(true);
    try {
      const res = await toggleSavedItem({
        item_type: 'supplier',
        supplier_id: supplier.id,
        project_collection: 'Verified Trade Directory'
      });
      setIsSaved(Boolean(res.saved));
      refreshSavedCounts();
    } catch (err) {
      console.error("Failed to toggle save supplier", err);
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center font-serif text-xl text-stone-500">
        Loading supplier business credentials and inventory...
      </div>
    );
  }

  if (!supplier) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-20 text-center">
        <h2 className="font-serif text-3xl font-bold text-arch-charcoal">Supplier not found</h2>
        <Link href="/sourcing" className="mt-4 inline-block text-arch-terracotta underline text-sm">
          Return to regional sourcing engine
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Back Link */}
      <Link
        href="/sourcing"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-stone-600 hover:text-arch-terracotta transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Regional Sourcing Engine</span>
      </Link>

      {/* Supplier Profile Card */}
      <div className="bg-white rounded-3xl border border-arch-border p-6 sm:p-10 shadow-sm space-y-6">
        <div className="flex flex-wrap items-start justify-between gap-4 pb-6 border-b border-arch-border">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-2xl bg-arch-surface border border-arch-border flex items-center justify-center text-arch-terracotta font-serif font-bold text-2xl shadow-xs">
              <Building2 className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
                  {supplier.business_type.replace(/_/g, ' ')}
                </span>
                <VerificationBadge status={supplier.verification_status} isPotential={supplier.is_potential} />
              </div>
              <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal leading-tight">
                {supplier.name}
              </h1>
              <div className="flex items-center gap-2 text-xs text-stone-500 mt-1">
                <MapPin className="w-3.5 h-3.5 text-stone-400" />
                <span>{supplier.address}, {supplier.city}, {supplier.state} ({supplier.country})</span>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <button
              onClick={() => {
                const firstProd = supplier.catalog_products?.[0];
                setActiveQuotation({
                  product: {
                    id: firstProd?.product_id || 1,
                    name: firstProd?.product_name || "Architectural Material Specification"
                  },
                  supplier
                });
              }}
              className="px-4 py-2.5 rounded-xl bg-arch-terracotta hover:bg-arch-terracotta-dark text-white text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 shadow-xs"
            >
              <span>Get Quote</span>
            </button>

            <button
              onClick={handleToggleSave}
              disabled={saving}
              className={`p-2.5 rounded-xl border text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 shadow-xs ${
                isSaved ? 'bg-arch-terracotta text-white border-arch-terracotta' : 'bg-white text-stone-700 border-stone-300 hover:bg-stone-50 hover:border-arch-terracotta/40'
              }`}
              title={isSaved ? "Saved in collection" : "Save supplier"}
            >
              <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-current' : ''}`} />
              <span>{isSaved ? "Saved Supplier" : "Bookmark Supplier"}</span>
            </button>
          </div>
        </div>

        {/* Business Credentials & Contacts Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs">
          <div className="p-4 bg-stone-50 rounded-2xl border border-stone-200">
            <span className="text-stone-400 uppercase text-xs font-bold block mb-1">Telephone</span>
            {supplier.phone ? (
              <a href={`tel:${supplier.phone.replace(/[^0-9+]/g, '')}`} className="font-mono font-semibold text-arch-charcoal text-sm hover:text-arch-terracotta transition-colors block">
                {supplier.phone}
              </a>
            ) : (
              <span className="text-stone-400 italic">Not publicly listed</span>
            )}
            {supplier.whatsapp && (
              <div className="mt-2 pt-2 border-t border-stone-200">
                <a
                  href={`https://wa.me/${supplier.whatsapp.replace(/[^0-9]/g, '')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-xs text-emerald-700 font-semibold hover:underline"
                  title="Direct WhatsApp trade inquiry"
                >
                  <MessageSquare className="w-3 h-3 text-emerald-600" />
                  <span>WhatsApp Verified</span>
                </a>
              </div>
            )}
          </div>

          <div className="p-4 bg-stone-50 rounded-2xl border border-stone-200">
            <span className="text-stone-400 uppercase text-xs font-bold block mb-1">Email / Inquiry</span>
            {supplier.email ? (
              <span className="font-mono text-arch-charcoal truncate block">{supplier.email}</span>
            ) : (
              <span className="text-stone-400 italic">Submit via app quotation</span>
            )}
          </div>

          <div className="p-4 bg-stone-50 rounded-2xl border border-stone-200">
            <span className="text-stone-400 uppercase text-xs font-bold block mb-1">Official Website</span>
            {supplier.website ? (
              <a
                href={supplier.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-arch-terracotta font-medium hover:underline inline-flex items-center gap-1 truncate block"
              >
                <span>{supplier.website.replace('https://', '')}</span>
                <ExternalLink className="w-3 h-3 shrink-0" />
              </a>
            ) : (
              <span className="text-stone-400 italic">No website registered</span>
            )}
          </div>

          <div className="p-4 bg-stone-50 rounded-2xl border border-stone-200">
            <span className="text-stone-400 uppercase text-xs font-bold block mb-1">Delivery Radius</span>
            <span className="font-semibold text-arch-charcoal text-sm">
              {supplier.delivery_radius_km ? `${supplier.delivery_radius_km} km` : "State-wide logistics"}
            </span>
          </div>
        </div>

        {supplier.google_maps_url && (
          <div className="pt-2 flex justify-end">
            <a
              href={supplier.google_maps_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1.5 text-xs font-semibold text-stone-600 hover:text-arch-terracotta transition-colors"
            >
              <span>View On Google Maps & Navigation</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        )}
      </div>

      {/* SECTION: Catalog of Products Sold by this Vendor (One Supplier, Many Products) */}
      <div className="space-y-4">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
            Inventory & Authorized Lines
          </span>
          <h2 className="font-serif text-2xl font-bold text-arch-charcoal">
            Products Distributed by {supplier.name} ({supplier.catalog_products?.length || 0})
          </h2>
        </div>

        {supplier.catalog_products && supplier.catalog_products.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {supplier.catalog_products.map((prod) => (
              <div
                key={prod.product_id}
                className="bg-white rounded-2xl border border-arch-border p-5 hover:shadow-md transition-shadow flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <Link
                      href={`/product/${prod.product_id}`}
                      className="font-serif text-lg font-bold text-arch-charcoal hover:text-arch-terracotta transition-colors"
                    >
                      {prod.product_name}
                    </Link>
                    <VerificationBadge status={prod.availability_status} />
                  </div>

                  <div className="text-xs text-stone-600 mb-3">
                    Composition: <strong className="text-stone-800">{prod.material_type || "Commercial specification"}</strong>
                  </div>

                  {prod.price ? (
                    <div className="p-3 bg-stone-50 rounded-xl border border-stone-200 mb-3 flex items-baseline justify-between">
                      <span className="text-xs text-stone-500">Confirmed Rate:</span>
                      <div className="font-serif text-xl font-bold text-arch-charcoal">
                        {prod.currency} {prod.price.toLocaleString()}
                      </div>
                    </div>
                  ) : (
                    <div className="p-3 bg-stone-50 rounded-xl border border-stone-200 mb-3 text-xs text-stone-500 italic text-center">
                      Custom project quotation required
                    </div>
                  )}

                  {prod.min_order_quantity && (
                    <div className="text-xs text-stone-500 mb-2">
                      MOQ: <strong>{prod.min_order_quantity}</strong>
                    </div>
                  )}
                </div>

                <div className="pt-3 border-t border-stone-100 flex items-center justify-between gap-2 text-xs">
                  <Link
                    href={`/product/${prod.product_id}`}
                    className="font-semibold text-stone-600 hover:text-arch-charcoal"
                  >
                    View Specs
                  </Link>

                  <button
                    onClick={() => setActiveQuotation({ product: { id: prod.product_id, name: prod.product_name }, supplier })}
                    className="px-3.5 py-1.5 rounded-lg bg-arch-terracotta hover:bg-arch-terracotta-dark text-white font-semibold transition-colors shadow-xs"
                  >
                    Request Quotation
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="p-8 text-center bg-white rounded-2xl border border-arch-border text-xs text-stone-500">
            This vendor has registered their trade profile. Contact them directly to confirm specific SKU stock.
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
