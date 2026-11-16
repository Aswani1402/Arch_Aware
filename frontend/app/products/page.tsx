"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Package, Search, Building2, Layers, Filter, ExternalLink,
  ChevronRight, ArrowRight, ShieldCheck, CheckCircle2
} from 'lucide-react';
import { Product, Category } from '@/types';
import { QuotationModal } from '@/components/QuotationModal';
import { getProducts, getCategories } from '@/lib/api';

export default function ProductsDirectoryPage() {
  const [products, setProducts] = useState<any[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [activeQuotation, setActiveQuotation] = useState<{ product: any; supplier: any } | null>(null);

  useEffect(() => {
    getCategories().then(setCategories).catch(() => {});
  }, []);

  const loadProducts = () => {
    setLoading(true);
    getProducts({
      category: selectedCategory || undefined,
      q: searchQuery || undefined,
    })
      .then((prods) => {
        setProducts(prods);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load products", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    loadProducts();
  }, [selectedCategory]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadProducts();
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="max-w-3xl">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-arch-terracotta/10 text-arch-terracotta border border-arch-terracotta/20 mb-3">
          <Package className="w-3.5 h-3.5" />
          Verified Commercial Building Products Directory
        </span>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal tracking-tight">
          Commercial Material Products & SKUs
        </h1>
        <p className="mt-2 text-sm text-stone-600 leading-relaxed font-sans">
          Explore manufacturer product lines, dimensional specifications, finish variants, and testing standards. Connect directly with verified regional distributors and stockist yards.
        </p>
      </div>

      {/* Search & Filter Toolbar */}
      <div className="bg-white rounded-3xl border border-arch-border p-5 shadow-2xs flex flex-wrap items-center justify-between gap-4">
        {/* Search */}
        <form onSubmit={handleSearchSubmit} className="relative max-w-md w-full">
          <Search className="w-4 h-4 text-stone-400 absolute left-4 top-3.5 pointer-events-none" />
          <input
            type="text"
            placeholder="Search products by name, manufacturer, SKU..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-11 pr-20 py-2.5 rounded-2xl border border-stone-200 bg-stone-50 text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-arch-terracotta/30 focus:border-arch-terracotta transition-all"
          />
          <button
            type="submit"
            className="absolute right-2 top-2 px-3 py-1 bg-arch-dark hover:bg-arch-terracotta text-white rounded-xl text-xs font-semibold transition-colors"
          >
            Find
          </button>
        </form>

        {/* Category Filter */}
        <div className="flex items-center gap-2 text-xs">
          <span className="text-stone-400 font-semibold uppercase text-xs">Category:</span>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 rounded-xl border border-stone-200 bg-stone-50 text-stone-700 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-arch-terracotta"
          >
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c.slug} value={c.slug}>{c.name}</option>
            ))}
          </select>

          {selectedCategory && (
            <button
              onClick={() => setSelectedCategory("")}
              className="text-xs text-arch-terracotta hover:underline font-semibold ml-1"
            >
              Reset
            </button>
          )}
        </div>
      </div>

      {/* Products Grid */}
      {loading ? (
        <div className="py-20 text-center text-stone-400 font-serif">
          <div className="w-8 h-8 border-2 border-arch-terracotta border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-xs">Loading commercial products...</p>
        </div>
      ) : products.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((prod) => (
            <div
              key={prod.id}
              className="bg-white rounded-2xl border border-arch-border hover:border-arch-terracotta/40 hover:shadow-lg transition-all duration-300 p-6 flex flex-col justify-between space-y-4"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta font-mono">
                    {prod.category_name || "Material"}
                  </span>
                  <span className="text-xs text-stone-400 font-mono">
                    {prod.sku || `SKU-${prod.id}`}
                  </span>
                </div>

                <h3 className="font-serif text-xl font-bold text-arch-charcoal leading-snug">
                  <Link href={`/product/${prod.id}`} className="hover:text-arch-terracotta transition-colors">
                    {prod.name}
                  </Link>
                </h3>

                {prod.manufacturer_name && (
                  <div className="flex items-center gap-1.5 text-xs text-stone-600">
                    <Building2 className="w-3.5 h-3.5 text-stone-400 shrink-0" />
                    <span>Brand / Mfg: <strong className="text-stone-800">{prod.manufacturer_name}</strong></span>
                  </div>
                )}

                {prod.description && (
                  <p className="text-xs text-stone-600 line-clamp-3 leading-relaxed">
                    {prod.description}
                  </p>
                )}

                {prod.price_unit && (
                  <div className="text-xs text-stone-500 pt-1">
                    Listed specification unit: <strong className="text-stone-800">{prod.price_unit}</strong>
                  </div>
                )}
              </div>

              <div className="pt-4 border-t border-stone-100 flex items-center justify-between text-xs">
                <Link
                  href={`/product/${prod.id}`}
                  className="font-semibold text-arch-charcoal hover:text-arch-terracotta transition-colors flex items-center gap-1"
                >
                  <span>Technical Specs</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setActiveQuotation({
                      product: { id: prod.id, name: prod.name },
                      supplier: null,
                    })}
                    className="px-2.5 py-1 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-700 font-semibold text-xs transition-colors"
                  >
                    Request RFQ
                  </button>

                  <Link
                    href={`/sourcing?product_id=${prod.id}`}
                    className="px-2.5 py-1 rounded-lg bg-arch-dark hover:bg-arch-terracotta text-white font-medium transition-colors text-xs"
                  >
                    Vendors
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="py-16 text-center bg-white rounded-3xl border border-arch-border p-8">
          <Package className="w-10 h-10 text-stone-300 mx-auto mb-3" />
          <h3 className="font-serif text-xl font-bold text-arch-charcoal">No products found</h3>
          <p className="mt-2 text-xs text-stone-500 max-w-sm mx-auto">
            Try adjusting your search query or category filter.
          </p>
        </div>
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
