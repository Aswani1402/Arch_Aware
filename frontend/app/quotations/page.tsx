"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { FileText, Building2, Package, MapPin, Clock, CheckCircle2, MessageSquare, ArrowRight } from 'lucide-react';
import { QuotationRequest } from '@/types';
import { getQuotationRequests, respondToQuotation, hasAuthToken } from '@/lib/api';

export default function QuotationsPage() {
  const [requests, setRequests] = useState<QuotationRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [requiresAuth, setRequiresAuth] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [respondingId, setRespondingId] = useState<number | null>(null);
  const [quotePrice, setQuotePrice] = useState<number>(45000);
  const [deliveryDays, setDeliveryDays] = useState<number>(5);
  const [quoteMessage, setQuoteMessage] = useState<string>("Ready stock confirmed in regional warehouse. Flatbed transport arranged.");

  const fetchRequests = () => {
    if (!hasAuthToken()) {
      setRequiresAuth(true);
      setRequests([]);
      setLoading(false);
      return;
    }
    setRequiresAuth(false);
    setErrorMsg(null);
    setLoading(true);
    getQuotationRequests()
      .then(res => {
        setRequests(Array.isArray(res) ? res : []);
        setLoading(false);
      })
      .catch((err) => {
        if (!hasAuthToken()) {
          setRequiresAuth(true);
        } else {
          setErrorMsg(err?.message || "Unable to load quotation requests right now.");
        }
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleSimulateSupplierResponse = async (reqId: number) => {
    try {
      await respondToQuotation(reqId, {
        quoted_price: quotePrice,
        currency: "INR",
        estimated_delivery_days: deliveryDays,
        delivery_terms: "Site delivery with unloading crane included.",
        response_message: quoteMessage
      });
      setRespondingId(null);
      fetchRequests();
    } catch (err: any) {
      alert(err.message || "Failed to submit quotation response");
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="max-w-3xl">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-arch-terracotta/10 text-arch-terracotta border border-arch-terracotta/20 mb-3">
          <FileText className="w-3.5 h-3.5" />
          <span>Vendor Quotation & Inquiry Tracking</span>
        </div>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal">
          Material Quotation Inquiries
        </h1>
        <p className="mt-2 text-sm text-stone-600">
          Track official pricing, lead times, and freight terms received from regional vendors and national distributors for your architectural specifications.
        </p>
      </div>

      {loading ? (
        <div className="py-20 text-center font-serif text-lg text-stone-500">
          Retrieving quotation records...
        </div>
      ) : requiresAuth ? (
        <div className="py-16 text-center bg-white rounded-3xl border border-arch-border p-8 max-w-lg mx-auto space-y-3">
          <FileText className="w-10 h-10 text-arch-terracotta mx-auto" />
          <h3 className="font-serif text-xl font-bold text-arch-charcoal">Sign in to view quotation inquiries</h3>
          <p className="text-xs text-stone-500">
            Official supplier quotation requests and responses are private to your account.
          </p>
          <Link
            href="/login"
            className="inline-flex items-center gap-1.5 px-5 py-2.5 bg-arch-terracotta text-white font-semibold text-xs rounded-xl hover:bg-arch-terracotta-dark transition-colors"
          >
            <span>Sign In</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      ) : errorMsg ? (
        <div className="py-16 text-center bg-white rounded-3xl border border-red-200 p-8 max-w-lg mx-auto space-y-3">
          <p className="text-sm text-red-700 font-medium">{errorMsg}</p>
        </div>
      ) : requests.length > 0 ? (
        <div className="space-y-6">
          {requests.map((req) => (
            <div
              key={req.id}
              className="bg-white rounded-3xl border border-arch-border p-6 sm:p-8 shadow-sm space-y-5"
            >
              {/* Header */}
              <div className="flex flex-wrap items-center justify-between gap-3 pb-4 border-b border-arch-border">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-stone-400">
                      #REQ-{req.id}
                    </span>
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider ${
                      req.status === 'quoted'
                        ? 'bg-emerald-100 text-emerald-800 border border-emerald-200'
                        : 'bg-amber-100 text-amber-800 border border-amber-200'
                    }`}>
                      {req.status === 'quoted' ? 'Quotation Received' : 'Under Vendor Review'}
                    </span>
                  </div>
                  <h3 className="font-serif text-2xl font-bold text-arch-charcoal mt-1">
                    {req.product_name}
                  </h3>
                </div>

                <div className="text-right text-xs text-stone-500">
                  <div className="flex items-center gap-1 text-stone-400 justify-end">
                    <Clock className="w-3.5 h-3.5" />
                    <span>{new Date(req.created_at).toLocaleDateString()}</span>
                  </div>
                  <span className="text-xs font-medium text-arch-terracotta capitalize">
                    Urgency: {req.delivery_urgency}
                  </span>
                </div>
              </div>

              {/* Inquiry Details Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 text-xs bg-stone-50 p-4 rounded-2xl border border-stone-200">
                <div>
                  <span className="text-stone-400 uppercase text-xs font-bold block mb-1">Target Supplier</span>
                  <Link href={`/supplier/${req.supplier_id}`} className="font-semibold text-arch-charcoal hover:underline">
                    {req.supplier_name}
                  </Link>
                </div>
                <div>
                  <span className="text-stone-400 uppercase text-xs font-bold block mb-1">Quantity Requested</span>
                  <span className="font-semibold text-arch-charcoal">{req.quantity}</span>
                </div>
                <div>
                  <span className="text-stone-400 uppercase text-xs font-bold block mb-1">Project Site Location</span>
                  <span className="font-semibold text-arch-charcoal truncate block">{req.project_location} ({req.city})</span>
                </div>
                <div>
                  <span className="text-stone-400 uppercase text-xs font-bold block mb-1">Specified Dimensions</span>
                  <span className="font-semibold text-arch-charcoal">{req.dimensions || "Standard commercial"}</span>
                </div>
              </div>

              {req.additional_notes && (
                <div className="text-xs text-stone-600 bg-stone-50/60 p-3 rounded-xl border border-stone-100">
                  <strong className="text-stone-700">Project Notes: </strong>
                  {req.additional_notes}
                </div>
              )}

              {/* Supplier Responses */}
              {req.responses && req.responses.length > 0 ? (
                <div className="mt-4 pt-4 border-t border-arch-border space-y-3">
                  <span className="text-xs font-bold uppercase tracking-wider text-emerald-700 flex items-center gap-1.5">
                    <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                    Formal Supplier Quotation Received
                  </span>

                  {req.responses.map((resp) => (
                    <div key={resp.id} className="p-4 rounded-2xl bg-emerald-50/60 border border-emerald-200 text-xs space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-semibold text-emerald-950">
                          {resp.supplier_name} Offer:
                        </span>
                        <div className="font-serif text-2xl font-bold text-emerald-900">
                          {resp.currency} {resp.quoted_price.toLocaleString()}
                        </div>
                      </div>

                      <p className="text-emerald-900 leading-relaxed font-sans">
                        &ldquo;{resp.response_message}&rdquo;
                      </p>

                      <div className="flex flex-wrap items-center gap-4 pt-2 text-xs text-emerald-800">
                        {resp.estimated_delivery_days && (
                          <span>Estimated Lead Time: <strong>{resp.estimated_delivery_days} business days</strong></span>
                        )}
                        {resp.delivery_terms && (
                          <span>Freight Terms: <strong>{resp.delivery_terms}</strong></span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="pt-2 flex items-center justify-between text-xs">
                  <span className="text-stone-500 italic">
                    Awaiting response from supplier sales team...
                  </span>

                  {/* Supplier Demo Simulation Responder */}
                  <button
                    onClick={() => setRespondingId(req.id)}
                    className="text-xs text-arch-terracotta hover:underline font-medium"
                  >
                    Simulate Vendor Response (Demo Mode)
                  </button>
                </div>
              )}

              {/* Supplier Response Simulation Drawer */}
              {respondingId === req.id && (
                <div className="p-4 bg-orange-50/80 rounded-2xl border border-orange-200 text-xs space-y-3 mt-3">
                  <span className="font-semibold text-orange-950 block">
                    Vendor Response Simulator ({req.supplier_name})
                  </span>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-stone-700 font-medium mb-1">Quoted Total Rate (INR)</label>
                      <input
                        type="number"
                        value={quotePrice}
                        onChange={(e) => setQuotePrice(parseFloat(e.target.value) || 0)}
                        className="w-full px-3 py-1.5 rounded-lg border border-orange-300 bg-white"
                      />
                    </div>
                    <div>
                      <label className="block text-stone-700 font-medium mb-1">Estimated Lead Days</label>
                      <input
                        type="number"
                        value={deliveryDays}
                        onChange={(e) => setDeliveryDays(parseInt(e.target.value) || 1)}
                        className="w-full px-3 py-1.5 rounded-lg border border-orange-300 bg-white"
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-stone-700 font-medium mb-1">Vendor Note / Freight Terms</label>
                    <input
                      type="text"
                      value={quoteMessage}
                      onChange={(e) => setQuoteMessage(e.target.value)}
                      className="w-full px-3 py-1.5 rounded-lg border border-orange-300 bg-white"
                    />
                  </div>
                  <div className="flex justify-end gap-2">
                    <button
                      onClick={() => setRespondingId(null)}
                      className="px-3 py-1.5 rounded-lg text-stone-600 hover:bg-stone-100"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleSimulateSupplierResponse(req.id)}
                      className="px-4 py-1.5 rounded-lg bg-arch-dark text-white font-semibold hover:bg-arch-terracotta transition-colors"
                    >
                      Submit Response
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="py-20 text-center bg-white rounded-3xl border border-arch-border p-8">
          <FileText className="w-10 h-10 text-stone-300 mx-auto mb-3" />
          <h3 className="font-serif text-2xl font-bold text-arch-charcoal">No quotation requests submitted yet</h3>
          <p className="mt-2 text-xs text-stone-500 max-w-sm mx-auto">
            When you discover an architectural product or material, you can request an official price and delivery quotation from verified suppliers near your site.
          </p>
          <Link
            href="/"
            className="mt-4 inline-block px-4 py-2 bg-arch-dark text-white rounded-xl text-xs font-semibold hover:bg-arch-terracotta transition-colors"
          >
            Discover Materials & Suppliers
          </Link>
        </div>
      )}
    </div>
  );
}
