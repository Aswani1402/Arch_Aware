"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Building2, Globe, ExternalLink, Package, Search,
  ShieldCheck, MapPin, CheckCircle2, ChevronRight, Phone, Mail
} from 'lucide-react';
import { Manufacturer } from '@/types';
import { getManufacturers } from '@/lib/api';

export default function ManufacturersDirectoryPage() {
  const [manufacturers, setManufacturers] = useState<Manufacturer[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [searchQuery, setSearchQuery] = useState<string>("");
  const [selectedCountry, setSelectedCountry] = useState<string>("");

  useEffect(() => {
    getManufacturers()
      .then((data) => {
        setManufacturers(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load manufacturers", err);
        setLoading(false);
      });
  }, []);

  const countries = Array.from(new Set(manufacturers.map((m) => m.country).filter(Boolean)));

  const filtered = manufacturers.filter((m) => {
    const matchesCountry = !selectedCountry || m.country === selectedCountry;
    const matchesSearch =
      !searchQuery.trim() ||
      m.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (m.company_name && m.company_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (m.description && m.description.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (m.country && m.country.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (m.contact_info && m.contact_info.toLowerCase().includes(searchQuery.toLowerCase()));

    return matchesCountry && matchesSearch;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="max-w-3xl">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-arch-terracotta/10 text-arch-terracotta border border-arch-terracotta/20 mb-3">
          <Building2 className="w-3.5 h-3.5" />
          Original Brand & Primary Producer Registry
        </span>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal tracking-tight">
          Manufacturers & Primary Brands
        </h1>
        <p className="mt-2 text-sm text-stone-600 leading-relaxed font-sans">
          Discover verified commercial manufacturers and brand owners across India and internationally. Inspect official product catalogues, technical documentation, BIS certifications, and authorized dealer networks.
        </p>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="bg-white rounded-3xl border border-arch-border p-5 shadow-2xs flex flex-wrap items-center justify-between gap-4">
        <div className="relative max-w-md w-full">
          <Search className="w-4 h-4 text-stone-400 absolute left-4 top-3.5 pointer-events-none" />
          <input
            type="text"
            placeholder="Search manufacturer, brand name, city..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-11 pr-4 py-2.5 rounded-2xl border border-stone-200 bg-stone-50 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-arch-terracotta/30 focus:border-arch-terracotta transition-all"
          />
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="text-stone-400 font-semibold uppercase text-xs">Country:</span>
          <select
            value={selectedCountry}
            onChange={(e) => setSelectedCountry(e.target.value)}
            className="px-3 py-2 rounded-xl border border-stone-200 bg-stone-50 text-stone-700 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-arch-terracotta"
          >
            <option value="">All Countries</option>
            {countries.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Grid of Manufacturers */}
      {loading ? (
        <div className="py-20 text-center text-stone-400 font-serif">
          <div className="w-8 h-8 border-2 border-arch-terracotta border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-xs">Loading manufacturer directory...</p>
        </div>
      ) : filtered.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((mfg) => (
            <div
              key={mfg.id}
              className="bg-white rounded-2xl border border-arch-border hover:border-arch-terracotta/40 hover:shadow-lg transition-all duration-300 p-6 flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-bold bg-stone-100 text-stone-700 font-mono uppercase">
                    Producer / Brand
                  </span>
                  {mfg.official_website && (
                    <a
                      href={mfg.official_website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-stone-400 hover:text-arch-terracotta transition-colors"
                      title="Verified Official Website"
                    >
                      <Globe className="w-4 h-4" />
                    </a>
                  )}
                </div>

                <h3 className="font-serif text-xl font-bold text-arch-charcoal leading-snug">
                  <Link href={`/manufacturer/${mfg.id}`} className="hover:text-arch-terracotta transition-colors">
                    {mfg.name}
                  </Link>
                </h3>

                {mfg.country && (
                  <div className="flex items-center gap-1 text-xs text-stone-500">
                    <MapPin className="w-3.5 h-3.5 text-stone-400 shrink-0" />
                    <span>{mfg.country}</span>
                  </div>
                )}

                {mfg.description && (
                  <p className="text-xs text-stone-600 line-clamp-3 leading-relaxed">
                    {mfg.description}
                  </p>
                )}

                {mfg.official_catalog_url && (
                  <div className="pt-1">
                    <a
                      href={mfg.official_catalog_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 text-xs font-semibold text-arch-terracotta hover:underline"
                    >
                      <Package className="w-3.5 h-3.5" />
                      <span>Official Product Catalogue</span>
                      <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  </div>
                )}
              </div>

              <div className="pt-4 border-t border-stone-100 flex items-center justify-between text-xs">
                <Link
                  href={`/manufacturer/${mfg.id}`}
                  className="font-semibold text-arch-charcoal hover:text-arch-terracotta transition-colors flex items-center gap-1"
                >
                  <span>View Profile & SKUs</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>

                <Link
                  href={`/sourcing?q=${encodeURIComponent(mfg.name)}`}
                  className="px-2.5 py-1 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-700 font-medium transition-colors text-xs"
                >
                  Locate Dealers
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="py-16 text-center bg-white rounded-3xl border border-arch-border p-8">
          <Building2 className="w-10 h-10 text-stone-300 mx-auto mb-3" />
          <h3 className="font-serif text-xl font-bold text-arch-charcoal">No manufacturers found</h3>
          <p className="mt-2 text-xs text-stone-500 max-w-sm mx-auto">
            Try adjusting your search query or country filter.
          </p>
        </div>
      )}
    </div>
  );
}
