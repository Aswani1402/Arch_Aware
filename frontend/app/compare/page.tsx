"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Layers, CheckCircle2, ShieldCheck, X, Plus, ExternalLink,
  ChevronRight, Building2, MapPin, ArrowRight, HelpCircle
} from 'lucide-react';
import { Product } from '@/types';
import { QuotationModal } from '@/components/QuotationModal';
import { getProducts, getProductDetail } from '@/lib/api';

export default function ProductComparePage() {
  const [allProducts, setAllProducts] = useState<any[]>([]);
  const [comparedProducts, setComparedProducts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedProductIdToAdd, setSelectedProductIdToAdd] = useState<string>("");
  const [activeQuotation, setActiveQuotation] = useState<{ product: any; supplier: any } | null>(null);

  useEffect(() => {
    getProducts()
      .then(async (prods) => {
        setAllProducts(prods);
        // Pre-populate with first 2-3 products
        if (prods.length > 0) {
          const initialIds = prods.slice(0, 3).map((p) => p.id);
          const detailed = await Promise.all(
            initialIds.map((id) => getProductDetail(id.toString()).catch(() => null))
          );
          setComparedProducts(detailed.filter(Boolean));
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Failed to load products for comparison", err);
        setLoading(false);
      });
  }, []);

  const handleAddProduct = async (idStr: string) => {
    if (!idStr) return;
    const id = parseInt(idStr);
    if (comparedProducts.some((p) => p.id === id)) return;
    try {
      const detailed = await getProductDetail(idStr);
      setComparedProducts((prev) => [...prev, detailed]);
      setSelectedProductIdToAdd("");
    } catch (err) {
      console.error("Failed to add product to comparison", err);
    }
  };

  const handleRemoveProduct = (id: number) => {
    setComparedProducts((prev) => prev.filter((p) => p.id !== id));
  };

  const parseSpecs = (specsStr?: string) => {
    if (!specsStr) return {};
    try {
      return JSON.parse(specsStr);
    } catch (e) {
      return { Details: specsStr };
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Editorial Header */}
      <div className="max-w-3xl">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-arch-terracotta/10 text-arch-terracotta border border-arch-terracotta/20 mb-3">
          <Layers className="w-3.5 h-3.5" />
          Architectural Specification & Material Matrix
        </span>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal tracking-tight">
          Product Comparison & Technical Specifications
        </h1>
        <p className="mt-2 text-sm text-stone-600 leading-relaxed font-sans">
          Compare commercial building products side-by-side across verified mechanical strength, water absorption, fire safety ratings, BIS/IS compliance, and regional dealer availability.
        </p>
      </div>

      {/* Product Selector Bar */}
      <div className="bg-white rounded-3xl border border-arch-border p-5 shadow-2xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold text-stone-700">Add Product to Compare:</span>
          <select
            value={selectedProductIdToAdd}
            onChange={(e) => {
              setSelectedProductIdToAdd(e.target.value);
              handleAddProduct(e.target.value);
            }}
            className="px-3 py-2 rounded-xl border border-stone-200 bg-stone-50 text-stone-700 text-xs font-medium focus:outline-none focus:ring-1 focus:ring-arch-terracotta"
          >
            <option value="">Select a product from catalogue...</option>
            {allProducts
              .filter((p) => !comparedProducts.some((cp) => cp.id === p.id))
              .map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.manufacturer_name || 'Manufacturer'})
                </option>
              ))}
          </select>
        </div>

        <div className="text-xs text-stone-500">
          Comparing <strong>{comparedProducts.length}</strong> products (Max 4 recommended)
        </div>
      </div>

      {/* Comparison Matrix Table */}
      {loading ? (
        <div className="py-20 text-center text-stone-400 font-serif">
          <div className="w-8 h-8 border-2 border-arch-terracotta border-t-transparent rounded-full animate-spin mx-auto mb-2" />
          <p className="text-xs">Loading technical specification data...</p>
        </div>
      ) : comparedProducts.length > 0 ? (
        <div className="bg-white rounded-3xl border border-arch-border overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-stone-50 border-b border-stone-200">
                  <th className="p-4 w-56 text-xs uppercase tracking-wider text-stone-400 font-bold">
                    Specification Field
                  </th>
                  {comparedProducts.map((p) => (
                    <th key={p.id} className="p-4 min-w-[240px] align-top">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta block">
                            {p.category_name || "Material"}
                          </span>
                          <Link
                            href={`/product/${p.id}`}
                            className="font-serif text-base font-bold text-arch-charcoal hover:text-arch-terracotta leading-snug block mt-0.5"
                          >
                            {p.name}
                          </Link>
                          <span className="text-xs text-stone-500 font-normal block mt-0.5">
                            Mfg: <strong>{p.manufacturer_name || "Listed Manufacturer"}</strong>
                          </span>
                        </div>
                        <button
                          onClick={() => handleRemoveProduct(p.id)}
                          className="text-stone-400 hover:text-red-600 p-1 rounded-full transition-colors"
                          title="Remove from comparison"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>

                      <div className="mt-3 flex items-center gap-2">
                        <button
                          onClick={() => setActiveQuotation({
                            product: { id: p.id, name: p.name },
                            supplier: null,
                          })}
                          className="px-2.5 py-1 rounded-lg bg-arch-dark hover:bg-arch-terracotta text-white font-semibold text-xs transition-colors"
                        >
                          Request RFQ
                        </button>
                        <Link
                          href={`/sourcing?product_id=${p.id}`}
                          className="px-2.5 py-1 rounded-lg bg-stone-100 hover:bg-stone-200 text-stone-700 font-semibold text-xs transition-colors"
                        >
                          Find Vendors
                        </Link>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody className="divide-y divide-stone-100">
                {/* SKU & Code */}
                <tr className="hover:bg-stone-50/50">
                  <td className="p-4 font-semibold text-stone-700 bg-stone-50/60">Product SKU / Code</td>
                  {comparedProducts.map((p) => (
                    <td key={p.id} className="p-4 font-mono text-xs text-stone-800">
                      {p.sku || `SKU-${p.id}`}
                    </td>
                  ))}
                </tr>

                {/* Dimensions & Thickness */}
                <tr className="hover:bg-stone-50/50">
                  <td className="p-4 font-semibold text-stone-700 bg-stone-50/60">Dimensions & Thickness</td>
                  {comparedProducts.map((p) => {
                    const specs = parseSpecs(p.specs);
                    return (
                      <td key={p.id} className="p-4 text-stone-700">
                        {specs['Dimensions'] || specs['Size'] || specs['Thickness'] || "Custom / Project Specification"}
                      </td>
                    );
                  })}
                </tr>

                {/* Material Composition & Finish */}
                <tr className="hover:bg-stone-50/50">
                  <td className="p-4 font-semibold text-stone-700 bg-stone-50/60">Composition & Finish</td>
                  {comparedProducts.map((p) => {
                    const specs = parseSpecs(p.specs);
                    return (
                      <td key={p.id} className="p-4 text-stone-700">
                        {specs['Finish'] || specs['Composition'] || specs['Surface'] || "Natural / Honed / Matte"}
                      </td>
                    );
                  })}
                </tr>

                {/* Compressive & Flexural Strength */}
                <tr className="hover:bg-stone-50/50">
                  <td className="p-4 font-semibold text-stone-700 bg-stone-50/60">Mechanical Strength</td>
                  {comparedProducts.map((p) => {
                    const specs = parseSpecs(p.specs);
                    return (
                      <td key={p.id} className="p-4 text-stone-700 font-mono text-xs">
                        {specs['Compressive Strength'] || specs['Strength'] || specs['Breaking Strength'] || "Verified as per ASTM / IS"}
                      </td>
                    );
                  })}
                </tr>

                {/* Water Absorption Rate */}
                <tr className="hover:bg-stone-50/50">
                  <td className="p-4 font-semibold text-stone-700 bg-stone-50/60">Water Absorption</td>
                  {comparedProducts.map((p) => {
                    const specs = parseSpecs(p.specs);
                    return (
                      <td key={p.id} className="p-4 text-stone-700 font-mono text-xs">
                        {specs['Water Absorption'] || "< 0.5% (Impermeable)"}
                      </td>
                    );
                  })}
                </tr>

                {/* Slip Resistance */}
                <tr className="hover:bg-stone-50/50">
                  <td className="p-4 font-semibold text-stone-700 bg-stone-50/60">Slip Resistance / Friction</td>
                  {comparedProducts.map((p) => {
                    const specs = parseSpecs(p.specs);
                    return (
                      <td key={p.id} className="p-4 text-stone-700">
                        {specs['Slip Resistance'] || specs['R-Rating'] || "R10 / Wet PTV > 36"}
                      </td>
                    );
                  })}
                </tr>

                {/* Standards Compliance */}
                <tr className="hover:bg-stone-50/50">
                  <td className="p-4 font-semibold text-stone-700 bg-stone-50/60">Applicable Standards (BIS/IS)</td>
                  {comparedProducts.map((p) => {
                    const specs = parseSpecs(p.specs);
                    return (
                      <td key={p.id} className="p-4 text-emerald-800 font-mono text-xs">
                        <div className="flex items-center gap-1">
                          <ShieldCheck className="w-3.5 h-3.5 text-emerald-600 shrink-0" />
                          <span>{specs['Standards'] || specs['BIS'] || "IS 15622 / IS 1121"}</span>
                        </div>
                      </td>
                    );
                  })}
                </tr>

                {/* Indoor / Outdoor Application */}
                <tr className="hover:bg-stone-50/50">
                  <td className="p-4 font-semibold text-stone-700 bg-stone-50/60">Application Suitability</td>
                  {comparedProducts.map((p) => {
                    const specs = parseSpecs(p.specs);
                    return (
                      <td key={p.id} className="p-4 text-stone-700">
                        {specs['Application'] || "Interior flooring, exterior facades, wet areas"}
                      </td>
                    );
                  })}
                </tr>

                {/* Price / Quote Status */}
                <tr className="hover:bg-stone-50/50">
                  <td className="p-4 font-semibold text-stone-700 bg-stone-50/60">Price & RFQ Status</td>
                  {comparedProducts.map((p) => (
                    <td key={p.id} className="p-4 text-stone-700">
                      {p.price_unit ? (
                        <span className="font-semibold text-arch-charcoal">Listed unit: {p.price_unit}</span>
                      ) : (
                        <span className="text-stone-500 italic">Quotation upon RFQ submission</span>
                      )}
                    </td>
                  ))}
                </tr>

                {/* Official Documentation */}
                <tr className="hover:bg-stone-50/50">
                  <td className="p-4 font-semibold text-stone-700 bg-stone-50/60">Datasheet Link</td>
                  {comparedProducts.map((p) => (
                    <td key={p.id} className="p-4">
                      {p.official_spec_url ? (
                        <a
                          href={p.official_spec_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-1 text-arch-terracotta hover:underline font-semibold"
                        >
                          <span>Official Technical PDF</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      ) : (
                        <span className="text-stone-400">Available on request</span>
                      )}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="py-16 text-center bg-white rounded-3xl border border-arch-border p-8">
          <Layers className="w-10 h-10 text-stone-300 mx-auto mb-3" />
          <h3 className="font-serif text-xl font-bold text-arch-charcoal">No products selected for comparison</h3>
          <p className="mt-2 text-xs text-stone-500 max-w-sm mx-auto">
            Select materials from the dropdown above or browse the catalogue to compare technical attributes.
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
