"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { Building2, CheckCircle2, MapPin, Phone, Mail, Globe, Shield, ArrowLeft } from 'lucide-react';
import { registerSupplier } from '@/lib/api';

export default function SupplierRegisterPage() {
  const [name, setName] = useState("");
  const [businessType, setBusinessType] = useState("authorized_dealer");
  const [contactPerson, setContactPerson] = useState("");
  const [address, setAddress] = useState("");
  const [city, setCity] = useState("");
  const [district, setDistrict] = useState("");
  const [state, setState] = useState("");
  const [pinCode, setPinCode] = useState("");
  const [phone, setPhone] = useState("");
  const [whatsapp, setWhatsapp] = useState("");
  const [email, setEmail] = useState("");
  const [website, setWebsite] = useState("");
  const [brandsDistributed, setBrandsDistributed] = useState("");
  const [deliveryAreas, setDeliveryAreas] = useState("");
  const [gstin, setGstin] = useState("");
  const [radius, setRadius] = useState<number>(100);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submittedSupplier, setSubmittedSupplier] = useState<any>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const res = await registerSupplier({
        name,
        business_type: businessType,
        contact_person: contactPerson || undefined,
        address,
        city,
        district: district || undefined,
        state,
        pin_code: pinCode,
        phone,
        whatsapp: whatsapp || undefined,
        email,
        website: website.startsWith("http") ? website : website ? `https://${website}` : undefined,
        brands_distributed: brandsDistributed || undefined,
        delivery_areas: deliveryAreas || undefined,
        gstin: gstin || undefined,
        delivery_radius_km: radius
      });
      setSubmittedSupplier(res);
    } catch (err: any) {
      alert(err.message || "Failed to register supplier");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      <Link
        href="/"
        className="inline-flex items-center gap-1.5 text-xs font-semibold text-stone-600 hover:text-arch-terracotta transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Architectural Discovery</span>
      </Link>

      <div className="bg-white rounded-3xl border border-arch-border p-6 sm:p-10 shadow-sm">
        {submittedSupplier ? (
          <div className="text-center py-10 space-y-4">
            <div className="w-16 h-16 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <h2 className="font-serif text-3xl font-bold text-arch-charcoal">
              Supplier Registration Submitted
            </h2>
            <p className="text-sm text-stone-600 max-w-md mx-auto">
              Thank you, <strong className="text-arch-charcoal">{submittedSupplier.name}</strong>. Your profile has been created with status <span className="font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">PENDING REVIEW</span>.
            </p>
            <p className="text-xs text-stone-500 max-w-sm mx-auto leading-relaxed">
              In accordance with Arch_Aware verification standards, an architectural curator reviews trade credentials before marking a vendor as verified.
            </p>
            <div className="pt-4 flex justify-center gap-3">
              <Link
                href={`/supplier/${submittedSupplier.id}`}
                className="px-5 py-2.5 rounded-xl bg-arch-dark hover:bg-arch-terracotta text-white font-semibold text-xs transition-colors"
              >
                View Supplier Profile Preview
              </Link>
              <Link
                href="/"
                className="px-5 py-2.5 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-700 font-semibold text-xs transition-colors"
              >
                Return to Discovery Feed
              </Link>
            </div>
          </div>
        ) : (
          <div>
            <div className="mb-6 pb-4 border-b border-arch-border">
              <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
                Architectural Trade Onboarding
              </span>
              <h1 className="font-serif text-3xl font-bold text-arch-charcoal mt-1">
                Register as an Architectural Supplier
              </h1>
              <p className="text-xs text-stone-500 mt-1">
                Connect your materials, tiles, natural stone, or coatings catalog directly to architects, landscape studios, and interior designers across India.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block font-medium text-stone-700 mb-1">Business / Company Name *</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Malabar Natural Stone Depot"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  />
                </div>
                <div>
                  <label className="block font-medium text-stone-700 mb-1">Contact Person</label>
                  <input
                    type="text"
                    value={contactPerson}
                    onChange={(e) => setContactPerson(e.target.value)}
                    placeholder="e.g. Mr. Rajesh Nair"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  />
                </div>
                <div>
                  <label className="block font-medium text-stone-700 mb-1">Business Classification *</label>
                  <select
                    value={businessType}
                    onChange={(e) => setBusinessType(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  >
                    <option value="authorized_dealer">Authorized Brand Dealer</option>
                    <option value="retail_supplier">Retail Building Material Supplier</option>
                    <option value="distributor">Regional Wholesale Distributor</option>
                    <option value="importer">Direct Material Importer</option>
                    <option value="custom_manufacturer">Artisanal / Custom Manufacturer</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block font-medium text-stone-700 mb-1">Physical Street Address / Yard *</label>
                <input
                  type="text"
                  required
                  value={address}
                  onChange={(e) => setAddress(e.target.value)}
                  placeholder="Street address, industrial area, landmark..."
                  className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">
                <div>
                  <label className="block font-medium text-stone-700 mb-1">City / Town *</label>
                  <input
                    type="text"
                    required
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                    placeholder="e.g. Kochi"
                    className="w-full px-3 py-2 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  />
                </div>
                <div>
                  <label className="block font-medium text-stone-700 mb-1">District</label>
                  <input
                    type="text"
                    value={district}
                    onChange={(e) => setDistrict(e.target.value)}
                    placeholder="e.g. Ernakulam"
                    className="w-full px-3 py-2 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  />
                </div>
                <div>
                  <label className="block font-medium text-stone-700 mb-1">State *</label>
                  <input
                    type="text"
                    required
                    value={state}
                    onChange={(e) => setState(e.target.value)}
                    placeholder="e.g. Kerala"
                    className="w-full px-3 py-2 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  />
                </div>
                <div>
                  <label className="block font-medium text-stone-700 mb-1">PIN Code</label>
                  <input
                    type="text"
                    value={pinCode}
                    onChange={(e) => setPinCode(e.target.value)}
                    placeholder="682024"
                    className="w-full px-3 py-2 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block font-medium text-stone-700 mb-1">Public Business Telephone</label>
                  <input
                    type="text"
                    value={phone}
                    onChange={(e) => setPhone(e.target.value)}
                    placeholder="+91 484 253 4810"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none font-mono"
                  />
                </div>
                <div>
                  <label className="block font-medium text-stone-700 mb-1">WhatsApp Trade Inquiry</label>
                  <input
                    type="text"
                    value={whatsapp}
                    onChange={(e) => setWhatsapp(e.target.value)}
                    placeholder="+91 94471 23456"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none font-mono"
                  />
                </div>
                <div>
                  <label className="block font-medium text-stone-700 mb-1">Inquiry / Contact Email *</label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="orders@yourbusiness.com"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block font-medium text-stone-700 mb-1">Official Website / Catalog URL</label>
                  <input
                    type="text"
                    value={website}
                    onChange={(e) => setWebsite(e.target.value)}
                    placeholder="https://yourbusiness.com"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  />
                </div>
                <div>
                  <label className="block font-medium text-stone-700 mb-1">GSTIN / Trade Registration (Confidential)</label>
                  <input
                    type="text"
                    value={gstin}
                    onChange={(e) => setGstin(e.target.value)}
                    placeholder="32AAAAA0000A1Z5"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block font-medium text-stone-700 mb-1">Manufacturer Brands Distributed</label>
                  <input
                    type="text"
                    value={brandsDistributed}
                    onChange={(e) => setBrandsDistributed(e.target.value)}
                    placeholder="e.g. Asian Paints, Kajaria, Saint-Gobain"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  />
                </div>
                <div>
                  <label className="block font-medium text-stone-700 mb-1">Delivery Logistics Coverage Areas</label>
                  <input
                    type="text"
                    value={deliveryAreas}
                    onChange={(e) => setDeliveryAreas(e.target.value)}
                    placeholder="e.g. Ernakulam, Thrissur, Kottayam, Kerala statewide"
                    className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-stone-700 mb-1">Delivery Logistics Radius (km)</label>
                <input
                  type="number"
                  value={radius}
                  onChange={(e) => setRadius(parseFloat(e.target.value) || 50)}
                  placeholder="100"
                  className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 focus:bg-white focus:ring-1 focus:ring-arch-terracotta outline-none"
                />
              </div>

              <div className="p-3 bg-stone-50 rounded-xl border border-stone-200 text-xs text-stone-500 flex items-start gap-2">
                <Shield className="w-4 h-4 text-arch-terracotta shrink-0 mt-0.5" />
                <span>
                  All supplier registrations are reviewed to confirm legitimate brick-and-mortar yards, dealer licenses, or craft credentials. We never publish fictional contact details.
                </span>
              </div>

              <div className="pt-4 flex justify-end">
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-6 py-3 rounded-xl bg-arch-terracotta hover:bg-arch-terracotta-dark text-white font-semibold text-xs transition-colors shadow-md disabled:opacity-50"
                >
                  {isSubmitting ? "Submitting Registration..." : "Complete Supplier Registration"}
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
