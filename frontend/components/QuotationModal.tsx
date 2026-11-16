"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { X, Send, Building2, Package, MapPin, CheckCircle, Lock } from 'lucide-react';
import { createQuotationRequest, hasAuthToken } from '@/lib/api';
import { useAuth } from '@/lib/authContext';

interface QuotationModalProps {
  isOpen: boolean;
  onClose: () => void;
  product?: { id?: number; name?: string } | null;
  supplier?: { id?: number; supplier_id?: number; name?: string; supplier_name?: string; city?: string; state?: string } | null;
}

export const QuotationModal: React.FC<QuotationModalProps> = ({
  isOpen,
  onClose,
  product,
  supplier
}) => {
  const { location } = useAuth();
  const isAuthenticated = hasAuthToken();
  const [quantity, setQuantity] = useState("500 sq.ft");
  const [dimensions, setDimensions] = useState("");
  const [projectLocation, setProjectLocation] = useState(
    location?.city ? `${location.city}${location.state ? `, ${location.state}` : ""}` : ""
  );
  const [urgency, setUrgency] = useState("standard");
  const [notes, setNotes] = useState("Please provide delivered rate including transport and loading/unloading to project site.");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedId, setSubmittedId] = useState<number | null>(null);

  if (!isOpen) return null;

  const targetSupplierName = supplier?.name || supplier?.supplier_name || "Verified Regional Supplier";
  const targetSupplierLocation = supplier?.city ? `${supplier.city}${supplier.state ? `, ${supplier.state}` : ''}` : "Regional Verification Network";
  const targetProductName = product?.name || "Architectural Material Specification";
  const targetSupplierId = supplier?.id ?? supplier?.supplier_id ?? 1;
  const targetProductId = product?.id ?? 1;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await createQuotationRequest({
        product_id: targetProductId,
        supplier_id: targetSupplierId,
        quantity,
        dimensions,
        project_location: projectLocation,
        city: location.city || "Project Site",
        state: location.state || "India",
        delivery_urgency: urgency,
        additional_notes: notes
      });
      setSubmittedId(res.id);
    } catch (err: any) {
      alert(err.message || "Failed to submit quotation request");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-white rounded-2xl shadow-2xl border border-arch-border p-6 overflow-hidden">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-full hover:bg-stone-100 text-stone-400 hover:text-stone-700 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {!isAuthenticated ? (
          <div className="text-center py-8 space-y-3">
            <div className="w-14 h-14 bg-arch-terracotta/10 text-arch-terracotta rounded-full flex items-center justify-center mx-auto">
              <Lock className="w-7 h-7" />
            </div>
            <h3 className="font-serif text-2xl font-bold text-arch-charcoal">Sign in to request quotation</h3>
            <p className="text-xs text-stone-600 max-w-sm mx-auto">
              Official RFQ inquiries to <span className="font-semibold text-arch-charcoal">{targetSupplierName}</span> require a signed-in account so you can track supplier responses.
            </p>
            <div className="pt-2 flex items-center justify-center gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 rounded-xl text-xs font-medium text-stone-600 hover:bg-stone-100"
              >
                Cancel
              </button>
              <Link
                href="/login"
                className="px-5 py-2.5 rounded-xl bg-arch-terracotta hover:bg-arch-terracotta-dark text-white text-xs font-semibold transition-colors shadow-xs"
              >
                Sign In
              </Link>
            </div>
          </div>
        ) : submittedId ? (
          <div className="text-center py-8">
            <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-8 h-8" />
            </div>
            <h3 className="font-serif text-2xl font-bold text-arch-charcoal">Quotation Request Sent</h3>
            <p className="mt-2 text-sm text-stone-600 max-w-sm mx-auto">
              Inquiry <span className="font-mono font-semibold">#REQ-{submittedId}</span> has been dispatched to{' '}
              <span className="font-semibold text-arch-charcoal">{targetSupplierName}</span>.
            </p>
            <p className="mt-1 text-xs text-stone-500">
              The vendor will review stock availability and delivery logistics {location.city ? `to ${location.city}` : 'for your specified project location'}.
            </p>
            <button
              onClick={onClose}
              className="mt-6 px-6 py-2.5 rounded-xl bg-arch-dark text-white text-xs font-semibold hover:bg-arch-terracotta transition-colors shadow-sm"
            >
              Back to Material Discovery
            </button>
          </div>
        ) : (
          <div>
            <div className="mb-4">
              <span className="text-xs font-semibold tracking-wider uppercase text-arch-terracotta">
                Direct Vendor Inquiry
              </span>
              <h3 className="font-serif text-2xl font-bold text-arch-charcoal leading-tight">
                Request Official Quotation
              </h3>
            </div>

            {/* Target Product & Supplier Details */}
            <div className="p-3 bg-stone-50 rounded-xl border border-stone-200 mb-4 space-y-1.5 text-xs">
              <div className="flex items-center gap-2 text-arch-charcoal font-medium">
                <Package className="w-4 h-4 text-stone-500 shrink-0" />
                <span>Product: <strong className="text-arch-charcoal">{targetProductName}</strong></span>
              </div>
              <div className="flex items-center gap-2 text-stone-600">
                <Building2 className="w-4 h-4 text-stone-500 shrink-0" />
                <span>Supplier: <strong className="text-arch-charcoal">{targetSupplierName}</strong> ({targetSupplierLocation})</span>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-3 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-stone-700 mb-1">Estimated Quantity *</label>
                  <input
                    type="text"
                    required
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    placeholder="e.g. 500 sq.ft or 20 Drums"
                    className="w-full px-3 py-2 rounded-lg border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  />
                </div>
                <div>
                  <label className="block font-medium text-stone-700 mb-1">Dimensions / Thickness</label>
                  <input
                    type="text"
                    value={dimensions}
                    onChange={(e) => setDimensions(e.target.value)}
                    placeholder="e.g. 1200x2400mm 9mm"
                    className="w-full px-3 py-2 rounded-lg border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-stone-700 mb-1">Project Delivery Site *</label>
                <div className="relative">
                  <MapPin className="w-4 h-4 text-stone-400 absolute left-3 top-2.5" />
                  <input
                    type="text"
                    required
                    value={projectLocation}
                    onChange={(e) => setProjectLocation(e.target.value)}
                    placeholder="Project city, state or site address..."
                    className="w-full pl-9 pr-3 py-2 rounded-lg border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-stone-700 mb-1">Delivery Timeframe Urgency</label>
                <select
                  value={urgency}
                  onChange={(e) => setUrgency(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                >
                  <option value="immediate">Immediate Dispatch (Ready Stock Required)</option>
                  <option value="standard">Standard Project Timeline (2-4 Weeks)</option>
                  <option value="flexible">Flexible / Planning Stage (Tender Estimate)</option>
                </select>
              </div>

              <div>
                <label className="block font-medium text-stone-700 mb-1">Additional Specifications / Notes</label>
                <textarea
                  rows={3}
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none resize-none"
                />
              </div>

              <div className="pt-2 flex items-center justify-end gap-3">
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 rounded-lg text-stone-600 hover:bg-stone-100 font-medium"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="flex items-center gap-1.5 px-5 py-2.5 rounded-lg bg-arch-terracotta hover:bg-arch-terracotta-dark text-white font-semibold transition-all shadow-md disabled:opacity-50"
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{isSubmitting ? "Dispatching..." : "Send Request to Supplier"}</span>
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
};
