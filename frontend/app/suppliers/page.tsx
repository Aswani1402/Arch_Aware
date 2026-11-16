"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Building2, Search, MapPin, Phone, Mail, Globe, ExternalLink,
  ShieldCheck, CheckCircle2, AlertCircle, Filter, ArrowRight,
  MessageSquare, Layers, Bookmark
} from 'lucide-react';
import { Supplier } from '@/types';
import { getSuppliers, getSavedItems, toggleSavedItem, hasAuthToken } from '@/lib/api';
import { useNavigation } from '@/lib/navigationContext';
import { VerificationBadge } from '@/components/VerificationBadge';

const BUSINESS_TYPES = [
  { id: "", label: "All Vendor Types" },
  { id: "quarry", label: "Quarry / Raw Material Producer" },
  { id: "manufacturer", label: "Manufacturer" },
  { id: "distributor", label: "Regional Distributor / Importer" },
  { id: "dealer", label: "Dealer / Stockist Yard" },
  { id: "fabricator", label: "Custom Fabricator" },
  { id: "installer", label: "Contractor / Installer" },
  { id: "supplier", label: "General Supplier" },
];

export default function SuppliersDirectoryPage() {
  const { refreshSavedCounts } = useNavigation();
  const [suppliers, setSuppliers] = useState<Supplier[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedType, setSelectedType] = useState<string>("");
  const [selectedState, setSelectedState] = useState<string>("");
  const [savedVendorsMap, setSavedVendorsMap] = useState<Record<number, boolean>>({});
  const [savingId, setSavingId] = useState<number | null>(null);

  useEffect(() => {
    getSuppliers()
      .then((data) => {
        setSuppliers(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load suppliers", err);
        setLoading(false);
      });

    if (hasAuthToken()) {
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
    }
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

  const states = Array.from(new Set(suppliers.map((s) => s.state).filter(Boolean)));

  const filtered = suppliers.filter((sup) => {
    const matchesType = !selectedType || sup.business_type.toLowerCase() === selectedType.toLowerCase();
    const matchesState = !selectedState || sup.state === selectedState;
    const matchesSearch =
      !searchQuery.trim() ||
      sup.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (sup.city && sup.city.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (sup.address && sup.address.toLowerCase().includes(searchQuery.toLowerCase()));

    return matchesType && matchesState && matchesSearch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="max-w-3xl">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-arch-terracotta/10 text-arch-terracotta border border-arch-terracotta/20 mb-3">
          <Building2 className="w-3.5 h-3.5" />
          Architectural Vendor Directory
        </span>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal tracking-tight">
          Suppliers, Stockists & Fabricators
        </h1>
        <p className="mt-2 text-sm text-stone-600 leading-relaxed font-sans">
          A dedicated vendor directory distinguishing manufacturers, raw material quarries, regional distributors, local stockists, and fabricators. All business contact details and addresses are sourced from verified public records.
        </p>
      </div>

      {/* Category Quick Sourcing Pills (Part 16) */}
      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs text-stone-500 font-medium">
          <span className="flex items-center gap-1.5 font-semibold text-stone-700">
            <Layers className="w-3.5 h-3.5 text-arch-terracotta" />
            Quick Sourcing by Master Category:
          </span>
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="text-arch-terracotta hover:underline text-xs"
            >
              Clear Category Filter
            </button>
          )}
        </div>
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none text-xs">
          {[
            { label: "Pipes & Plumbing (CPVC)", term: "pipe" },
            { label: "Sanitaryware & Bath", term: "sanitaryware" },
            { label: "TMT Steel & Rebar", term: "tmt steel" },
            { label: "Cement & RMC", term: "cement" },
            { label: "Bricks & AAC Blocks", term: "brick" },
            { label: "Tiles & Marble", term: "marble" },
            { label: "Athangudi Tiles", term: "athangudi" },
            { label: "Lighting & Electrical", term: "lighting" },
            { label: "Doors & Windows", term: "door" },
            { label: "Staircase & Railings", term: "staircase" },
            { label: "Modular Kitchen", term: "kitchen" },
            { label: "Landscaping Stone", term: "landscaping" },
          ].map((cat, idx) => {
            const isActive = searchQuery.toLowerCase() === cat.term.toLowerCase();
            return (
              <button
                key={idx}
                onClick={() => setSearchQuery(isActive ? "" : cat.term)}
                className={`px-3 py-1.5 rounded-full border text-xs whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-arch-terracotta text-white border-arch-terracotta font-semibold shadow-xs'
                    : 'bg-white hover:bg-stone-50 text-stone-700 border-stone-200 hover:border-arch-terracotta/40'
                }`}
              >
                {cat.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white rounded-3xl border border-arch-border p-5 shadow-2xs flex flex-wrap items-center justify-between gap-4">
        {/* Search */}
        <div className="relative max-w-md w-full">
          <Search className="w-4 h-4 text-stone-400 absolute left-4 top-3.5 pointer-events-none" />
          <input
            type="text"
            placeholder="Search supplier by name, city (e.g. Kozhikode, Chennai, Kochi)..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-2.5 rounded-2xl border border-stone-200 bg-stone-50 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-arch-terracotta/30 focus:border-arch-terracotta transition-all"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-3 text-xs">
          <div>
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="px-3 py-2 rounded-xl border border-stone-200 bg-stone-50 text-stone-700 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-arch-terracotta"
            >
              {BUSINESS_TYPES.map((t) => (
                <option key={t.id} value={t.id}>{t.label}</option>
              ))}
            </select>
          </div>

          <div>
            <select
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="px-3 py-2 rounded-xl border border-stone-200 bg-stone-50 text-stone-700 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-arch-terracotta"
            >
              <option value="">All States</option>
              {states.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Supplier Results Count */}
      <div className="flex items-center justify-between text-xs text-stone-500 font-medium px-1">
        <span>Showing <strong>{filtered.length}</strong> vendor profiles</span>
        <Link
          href="/suppliers/register"
          className="text-arch-terracotta hover:underline font-semibold"
        >
          Register as a Vendor &rarr;
        </Link>
      </div>

      {/* Suppliers Grid */}
      {loading ? (
        <div className="py-20 text-center text-stone-400 font-serif">
          <div className="w-8 h-8 border-2 border-arch-terracotta border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-xs">Loading vendor directory...</p>
        </div>
      ) : filtered.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((sup) => {
            const cleanPhone = sup.phone ? sup.phone.replace(/[^0-9+]/g, '') : null;
            const whatsappNumber = sup.whatsapp ? sup.whatsapp.replace(/[^0-9]/g, '') : null;

            return (
              <div
                key={sup.id}
                className="bg-white rounded-2xl border border-arch-border hover:border-arch-terracotta/40 hover:shadow-lg transition-all duration-300 p-6 flex flex-col justify-between space-y-4"
              >
                <div className="space-y-3">
                  {/* Entity Type & Status */}
                  <div className="flex items-center justify-between gap-2">
                    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-stone-100 text-stone-700 font-mono uppercase">
                      {sup.business_type.replace(/_/g, ' ')}
                    </span>

                    <div className="flex items-center gap-2">
                      <VerificationBadge
                        status={sup.verification_status}
                        isPotential={Boolean(sup.is_potential)}
                        size="sm"
                      />

                      <button
                        type="button"
                        onClick={(e) => handleToggleSaveVendor(sup.id, e)}
                        disabled={savingId === sup.id}
                        className={`p-1.5 rounded-lg border text-xs font-medium transition-all ${
                          savedVendorsMap[sup.id]
                            ? 'bg-arch-terracotta text-white border-arch-terracotta'
                            : 'bg-white hover:bg-stone-100 text-stone-500 border-stone-200 hover:text-arch-terracotta'
                        }`}
                        title={savedVendorsMap[sup.id] ? "Remove saved vendor" : "Save vendor"}
                        aria-label="Save Vendor"
                      >
                        <Bookmark className={`w-3.5 h-3.5 ${savedVendorsMap[sup.id] ? 'fill-current' : ''}`} />
                      </button>
                    </div>
                  </div>

                  {/* Supplier Name */}
                  <h3 className="font-serif text-xl font-bold text-arch-charcoal leading-snug">
                    <Link href={`/supplier/${sup.id}`} className="hover:text-arch-terracotta transition-colors">
                      {sup.name}
                    </Link>
                  </h3>

                  {/* Location & Address */}
                  <div className="space-y-1 text-xs text-stone-600">
                    <div className="flex items-center gap-1.5 font-medium text-stone-800">
                      <MapPin className="w-3.5 h-3.5 text-arch-terracotta shrink-0" />
                      <span>{sup.city}, {sup.state}</span>
                    </div>
                    {sup.address && (
                      <p className="text-xs text-stone-500 pl-5 line-clamp-2">
                        {sup.address}
                      </p>
                    )}
                  </div>

                  {/* Contact Info (Traceable & Honest) */}
                  <div className="pt-2 border-t border-stone-100 space-y-1.5 text-xs">
                    {sup.phone ? (
                      <div className="flex items-center gap-2 text-stone-700">
                        <Phone className="w-3 h-3 text-stone-400 shrink-0" />
                        <a href={`tel:${cleanPhone}`} className="hover:text-arch-terracotta font-mono text-xs">
                          {sup.phone}
                        </a>
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 text-stone-400 text-xs">
                        <Phone className="w-3 h-3 text-stone-300 shrink-0" />
                        <span>Phone: Contact to confirm</span>
                      </div>
                    )}

                    {sup.email ? (
                      <div className="flex items-center gap-2 text-stone-700">
                        <Mail className="w-3 h-3 text-stone-400 shrink-0" />
                        <a href={`mailto:${sup.email}`} className="hover:text-arch-terracotta truncate text-xs">
                          {sup.email}
                        </a>
                      </div>
                    ) : null}

                    {whatsappNumber && (
                      <div className="flex items-center gap-2 text-emerald-700 text-xs">
                        <MessageSquare className="w-3 h-3 text-emerald-600 shrink-0" />
                        <a
                          href={`https://wa.me/${whatsappNumber}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:underline font-medium"
                        >
                          WhatsApp Inquiry Available
                        </a>
                      </div>
                    )}
                  </div>
                </div>

                {/* Footer Action */}
                <div className="pt-4 border-t border-stone-100 flex items-center justify-between text-xs">
                  <Link
                    href={`/supplier/${sup.id}`}
                    className="font-semibold text-arch-charcoal hover:text-arch-terracotta transition-colors flex items-center gap-1"
                  >
                    <span>View Inventory</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>

                  <Link
                    href={`/sourcing?supplier_id=${sup.id}`}
                    className="px-2.5 py-1 rounded-lg bg-arch-dark hover:bg-arch-terracotta text-white font-medium transition-colors text-xs"
                  >
                    Check Distance
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="py-16 text-center bg-white rounded-3xl border border-arch-border p-8">
          <Building2 className="w-10 h-10 text-stone-300 mx-auto mb-3" />
          <h3 className="font-serif text-xl font-bold text-arch-charcoal">No suppliers match filters</h3>
          <p className="mt-2 text-xs text-stone-500 max-w-sm mx-auto">
            Try adjusting your search query, state, or vendor classification.
          </p>
        </div>
      )}
    </div>
  );
}
