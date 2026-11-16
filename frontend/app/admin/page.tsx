"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  Shield, CheckCircle2, Clock, AlertTriangle, Layers, Building2,
  RefreshCw, Globe, ExternalLink, Package, ArrowUpRight, Check, X,
  AlertCircle, Edit3, CheckCircle, Database, Youtube
} from 'lucide-react';
import {
  getAdminStats, getConnectors, triggerConnectorSync,
  getSuppliers, updateSupplierVerification,
  getQualityAudit, correctRecord, syncYouTubeFeed
} from '@/lib/api';

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<any>(null);
  const [connectors, setConnectors] = useState<any[]>([]);
  const [suppliers, setSuppliers] = useState<any[]>([]);
  const [qualityAudit, setQualityAudit] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [syncingPlatform, setSyncingPlatform] = useState<string | null>(null);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  // YouTube Ingestion Diagnostics State
  const [youtubeQuery, setYoutubeQuery] = useState("");
  const [youtubeSyncing, setYoutubeSyncing] = useState(false);
  const [youtubeSyncNotice, setYoutubeSyncNotice] = useState<string | null>(null);

  // Record Correction Modal State
  const [showCorrectionModal, setShowCorrectionModal] = useState(false);
  const [correctingIssue, setCorrectingIssue] = useState<any>(null);
  const [entityType, setEntityType] = useState("product");
  const [entityId, setEntityId] = useState<number>(1);
  const [correctionField, setCorrectionField] = useState("image_url");
  const [newValue, setNewValue] = useState("");
  const [correctionReason, setCorrectionReason] = useState("");
  const [isSubmittingCorrection, setIsSubmittingCorrection] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, connRes, supRes, auditRes] = await Promise.all([
        getAdminStats(),
        getConnectors(),
        getSuppliers(),
        getQualityAudit().catch(() => null)
      ]);
      setStats(statsRes);
      setConnectors(connRes);
      setSuppliers(supRes);
      setQualityAudit(auditRes);
    } catch (err) {
      console.error("Failed to load admin data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSync = async (platform: string) => {
    setSyncingPlatform(platform);
    setSyncMessage(null);
    try {
      const res = await triggerConnectorSync(platform);
      setSyncMessage(res.message);
      loadData();
    } catch (err: any) {
      alert(err.message || "Failed to sync connector");
    } finally {
      setSyncingPlatform(null);
    }
  };

  const handleUpdateStatus = async (supplierId: number, status: string) => {
    try {
      await updateSupplierVerification(supplierId, status);
      loadData();
    } catch (err: any) {
      alert(err.message || "Failed to update supplier verification status");
    }
  };

  const handleManualYouTubeSync = async () => {
    setYoutubeSyncing(true);
    setYoutubeSyncNotice(null);
    try {
      const res = await syncYouTubeFeed(youtubeQuery || undefined);
      setYoutubeSyncNotice(res.message || "YouTube content successfully synchronized into architectural references.");
      loadData();
    } catch (err: any) {
      setYoutubeSyncNotice(`YouTube sync error: ${err.message || "Failed to sync"}`);
    } finally {
      setYoutubeSyncing(false);
      setTimeout(() => setYoutubeSyncNotice(null), 8000);
    }
  };

  const openCorrectionForIssue = (issue: any) => {
    setCorrectingIssue(issue);
    setEntityType(issue.entity_type);
    setEntityId(issue.entity_id);
    if (issue.issue_type === "missing_image") {
      setCorrectionField("image_url");
      setNewValue("");
    } else if (issue.issue_type === "broken_source_link") {
      setCorrectionField("source_url");
      setNewValue("");
    } else if (issue.issue_type === "unverified_price") {
      setCorrectionField("price_unit");
      setNewValue("sqft");
    } else if (issue.issue_type === "unchecked_catalog") {
      setCorrectionField("official_catalog_url");
      setNewValue("");
    } else {
      setCorrectionField("notes");
      setNewValue("");
    }
    setCorrectionReason(`Resolved audit finding: ${issue.description}`);
    setShowCorrectionModal(true);
  };

  const handleApplyCorrection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!correctionReason.trim()) {
      alert("A documented reason is mandatory for curator record corrections.");
      return;
    }
    setIsSubmittingCorrection(true);
    try {
      const res = await correctRecord({
        entity_type: entityType,
        entity_id: entityId,
        field: correctionField,
        new_value: newValue,
        reason: correctionReason
      });
      setSyncMessage(res.message);
      setShowCorrectionModal(false);
      loadData();
    } catch (err: any) {
      alert(err.message || "Failed to apply correction");
    } finally {
      setIsSubmittingCorrection(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20 text-center font-serif text-xl text-stone-500">
        Loading curator dashboard and provenance quality audits...
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="max-w-3xl">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-arch-dark text-white mb-3">
          <Shield className="w-3.5 h-3.5 text-arch-terracotta" />
          <span>Curator & Data Provenance Administration</span>
        </div>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal">
          Architectural Content & Supplier Verification
        </h1>
        <p className="mt-2 text-sm text-stone-600">
          Enforce source authenticity, inspect social media connector pipelines, review supplier verification, and audit catalog provenance to ensure data integrity without fabricated credentials.
        </p>
      </div>

      {/* Sync notification message */}
      {syncMessage && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-xs text-emerald-900 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
            <span>{syncMessage}</span>
          </div>
          <button onClick={() => setSyncMessage(null)} className="text-emerald-700 font-bold">
            &times;
          </button>
        </div>
      )}

      {/* Metric Cards */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
          <div className="bg-white p-5 rounded-2xl border border-arch-border shadow-xs">
            <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block mb-1">
              References
            </span>
            <div className="font-serif text-3xl font-bold text-arch-charcoal">
              {stats.total_references}
            </div>
            <span className="text-xs text-stone-500 mt-1 block">Inspiration Items</span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-arch-border shadow-xs">
            <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block mb-1">
              Products
            </span>
            <div className="font-serif text-3xl font-bold text-arch-charcoal">
              {stats.total_products}
            </div>
            <span className="text-xs text-stone-500 mt-1 block">Commercial SKUs</span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-arch-border shadow-xs">
            <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block mb-1">
              Verified Suppliers
            </span>
            <div className="font-serif text-3xl font-bold text-emerald-700">
              {stats.verified_suppliers}
            </div>
            <span className="text-xs text-emerald-600 mt-1 block">Confirmed Yards</span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-arch-border shadow-xs">
            <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block mb-1">
              Review Queue
            </span>
            <div className="font-serif text-3xl font-bold text-amber-700">
              {stats.pending_suppliers}
            </div>
            <span className="text-xs text-amber-600 mt-1 block">Pending / Leads</span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-arch-border shadow-xs">
            <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block mb-1">
              Brands / Mfgs
            </span>
            <div className="font-serif text-3xl font-bold text-arch-charcoal">
              {stats.total_manufacturers}
            </div>
            <span className="text-xs text-stone-500 mt-1 block">Original Owners</span>
          </div>

          <div className="bg-white p-5 rounded-2xl border border-arch-border shadow-xs">
            <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block mb-1">
              Connectors
            </span>
            <div className="font-serif text-3xl font-bold text-arch-charcoal">
              {stats.connectors_count}
            </div>
            <span className="text-xs text-stone-500 mt-1 block">Active Ingestion</span>
          </div>
        </div>
      )}

      {/* API INTEGRATIONS & INGESTION DIAGNOSTICS (RELOCATED FROM HOMEPAGE) */}
      <div className="bg-white rounded-3xl border border-arch-border p-6 sm:p-8 shadow-sm space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-arch-border">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
              External API Services & Ingestion Diagnostics
            </span>
            <h2 className="font-serif text-2xl font-bold text-arch-charcoal">
              YouTube Data API v3 & Connector Diagnostics
            </h2>
          </div>
          <span className="text-xs text-stone-500">
            Administrative synchronization controls relocated from public discovery feed
          </span>
        </div>

        {/* Status Alert or Sync Notice */}
        {youtubeSyncNotice && (
          <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-2xl text-xs text-emerald-900 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>{youtubeSyncNotice}</span>
            </div>
            <button onClick={() => setYoutubeSyncNotice(null)} className="text-emerald-700 font-bold">
              &times;
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Left: YouTube Status & Sync Form */}
          <div className="p-5 rounded-2xl bg-stone-50 border border-stone-200 space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 font-bold text-sm text-arch-charcoal">
                <Youtube className="w-5 h-5 text-red-600" />
                <span>YouTube Data API v3 Status</span>
              </div>
              <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">
                <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                <span>Ready for Ingestion</span>
              </span>
            </div>

            <p className="text-xs text-stone-600 leading-relaxed">
              Fetches architectural project walkthroughs, studio monographs, and construction tours. Respects rate quotas with curated cache fallbacks.
            </p>

            <div className="space-y-2 pt-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-stone-500">
                Ingest Specific Style or Region Walkthroughs:
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="e.g. Kerala Nalukettu, Chettinad, Laterite House..."
                  value={youtubeQuery}
                  onChange={(e) => setYoutubeQuery(e.target.value)}
                  className="flex-grow px-3 py-2 rounded-xl border border-stone-300 bg-white text-xs outline-none focus:ring-1 focus:ring-arch-terracotta"
                />
                <button
                  onClick={handleManualYouTubeSync}
                  disabled={youtubeSyncing}
                  className="px-4 py-2 rounded-xl bg-arch-dark hover:bg-arch-terracotta text-white font-semibold text-xs transition-colors flex items-center gap-1.5 disabled:opacity-50 shrink-0"
                >
                  <RefreshCw className={`w-3.5 h-3.5 ${youtubeSyncing ? 'animate-spin' : ''}`} />
                  <span>{youtubeSyncing ? 'Ingesting...' : 'Sync YouTube'}</span>
                </button>
              </div>
              <span className="text-xs text-stone-400 block">
                Leave empty to run standard algorithmic discovery across verified architectural channels.
              </span>
            </div>
          </div>

          {/* Right: API Architecture & Quota Policies */}
          <div className="p-5 rounded-2xl bg-stone-50 border border-stone-200 space-y-3 text-xs">
            <div className="font-bold text-sm text-arch-charcoal flex items-center gap-2">
              <Shield className="w-4 h-4 text-arch-terracotta" />
              <span>Integration Security & Quota Policies</span>
            </div>

            <ul className="space-y-2 text-stone-600 leading-relaxed list-disc list-inside">
              <li>
                <strong>API Keys Encapsulation:</strong> Private credentials stored in backend environment variables. Never exposed in client code.
              </li>
              <li>
                <strong>Graceful Degradation:</strong> If YouTube quota limits or Google Places limits are reached, the system smoothly falls back to verified curated archives.
              </li>
              <li>
                <strong>Zero Scraping:</strong> Only official APIs and verified manufacturer public websites are accessed. No unauthorized Instagram/Pinterest scraping.
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* PHASE 10: DATA QUALITY & PROVENANCE AUDIT DASHBOARD */}
      {qualityAudit && (
        <div className="bg-white rounded-3xl border border-arch-border p-6 sm:p-8 shadow-sm space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-arch-border">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
                  Phase 10 — Data Provenance & Integrity Audit
                </span>
                <span className="px-2 py-0.5 rounded-full text-xs font-bold uppercase bg-stone-100 text-stone-800">
                  {qualityAudit.summary.health_status}
                </span>
              </div>
              <h2 className="font-serif text-2xl font-bold text-arch-charcoal">
                Data Quality Audit Dashboard
              </h2>
            </div>
            <div className="text-xs text-stone-500 flex items-center gap-2">
              <span className="font-semibold text-arch-charcoal">{qualityAudit.summary.total_issues} flagged issues</span>
              <span>across catalog, supplier claims, and source links</span>
            </div>
          </div>

          {/* Audit Category Metric Badges */}
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3 text-xs">
            <div className="p-3 bg-stone-50 rounded-xl border border-stone-200">
              <span className="text-xs text-stone-400 font-bold block uppercase">Broken Links</span>
              <span className="font-serif text-xl font-bold text-stone-800">{qualityAudit.summary.broken_links}</span>
            </div>
            <div className="p-3 bg-stone-50 rounded-xl border border-stone-200">
              <span className="text-xs text-stone-400 font-bold block uppercase">Missing Images</span>
              <span className="font-serif text-xl font-bold text-stone-800">{qualityAudit.summary.missing_images}</span>
            </div>
            <div className="p-3 bg-stone-50 rounded-xl border border-stone-200">
              <span className="text-xs text-stone-400 font-bold block uppercase">Duplicate Vendors</span>
              <span className="font-serif text-xl font-bold text-stone-800">{qualityAudit.summary.duplicate_suppliers}</span>
            </div>
            <div className="p-3 bg-stone-50 rounded-xl border border-stone-200">
              <span className="text-xs text-stone-400 font-bold block uppercase">Unverified Claims</span>
              <span className="font-serif text-xl font-bold text-amber-700">{qualityAudit.summary.unverified_claims}</span>
            </div>
            <div className="p-3 bg-stone-50 rounded-xl border border-stone-200">
              <span className="text-xs text-stone-400 font-bold block uppercase">Outdated Stock</span>
              <span className="font-serif text-xl font-bold text-stone-800">{qualityAudit.summary.outdated_stock}</span>
            </div>
            <div className="p-3 bg-stone-50 rounded-xl border border-stone-200">
              <span className="text-xs text-stone-400 font-bold block uppercase">Unchecked Catalogs</span>
              <span className="font-serif text-xl font-bold text-stone-800">{qualityAudit.summary.unchecked_catalogs}</span>
            </div>
            <div className="p-3 bg-stone-50 rounded-xl border border-stone-200">
              <span className="text-xs text-stone-400 font-bold block uppercase">Missing Attribution</span>
              <span className="font-serif text-xl font-bold text-stone-800">{qualityAudit.summary.missing_attributions}</span>
            </div>
          </div>

          {/* List of Flagged Audit Issues */}
          {qualityAudit.issues && qualityAudit.issues.length > 0 ? (
            <div className="space-y-2.5">
              <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block">
                Flagged Audit Items Requiring Curator Review
              </span>
              <div className="max-h-72 overflow-y-auto space-y-2 pr-1">
                {qualityAudit.issues.map((iss: any, idx: number) => (
                  <div
                    key={idx}
                    className="p-3.5 bg-stone-50 rounded-xl border border-stone-200 flex flex-wrap items-center justify-between gap-3 text-xs hover:bg-stone-100/70 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <span className={`px-2 py-0.5 rounded text-xs font-bold uppercase tracking-wider shrink-0 mt-0.5 ${
                        iss.severity === 'HIGH'
                          ? 'bg-red-100 text-red-800'
                          : iss.severity === 'MEDIUM'
                          ? 'bg-amber-100 text-amber-800'
                          : 'bg-stone-200 text-stone-700'
                      }`}>
                        {iss.severity}
                      </span>
                      <div>
                        <div className="font-semibold text-arch-charcoal flex items-center gap-2">
                          <span>{iss.description}</span>
                          <span className="text-xs font-mono text-stone-400">
                            [{iss.entity_type} #{iss.entity_id}]
                          </span>
                        </div>
                        <span className="text-xs text-stone-500 block mt-0.5">
                          Audit Finding: {iss.issue_type.replace(/_/g, ' ')}
                        </span>
                      </div>
                    </div>

                    <button
                      onClick={() => openCorrectionForIssue(iss)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-stone-300 hover:border-arch-terracotta hover:text-arch-terracotta text-stone-700 font-semibold text-xs shadow-xs transition-colors shrink-0"
                    >
                      <Edit3 className="w-3.5 h-3.5" />
                      <span>Correct Record</span>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-xl text-xs text-emerald-800 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
              <span>All catalog links, supplier claims, and product specifications satisfy quality standards.</span>
            </div>
          )}
        </div>
      )}

      {/* Source Connectors Section */}
      <div className="bg-white rounded-3xl border border-arch-border p-6 sm:p-8 shadow-sm space-y-5">
        <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-arch-border">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
              Modular Content Ingestion
            </span>
            <h2 className="font-serif text-2xl font-bold text-arch-charcoal">
              Source Connectors
            </h2>
          </div>
          <span className="text-xs text-stone-500">
            Official APIs with zero-paid fallback curation to avoid unauthorized scraping
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {connectors.map((conn) => (
            <div
              key={conn.id}
              className="p-5 rounded-2xl bg-stone-50 border border-stone-200 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-sm text-arch-charcoal capitalize">
                    {conn.name}
                  </span>
                  <span className={`text-xs px-2 py-0.5 rounded-full font-bold uppercase tracking-wider ${
                    conn.status === 'SYNCING'
                      ? 'bg-amber-100 text-amber-800'
                      : conn.status === 'ERROR'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-emerald-100 text-emerald-800'
                  }`}>
                    {conn.status}
                  </span>
                </div>

                <div className="text-xs text-stone-500 space-y-1 mb-4">
                  <div>Platform ID: <strong className="font-mono text-stone-700">{conn.platform}</strong></div>
                  <div>Total Ingested: <strong className="text-stone-700">{conn.total_items_fetched} references</strong></div>
                  <div>
                    Last Sync: {conn.last_synced_at ? new Date(conn.last_synced_at).toLocaleTimeString() : 'Initial seed'}
                  </div>
                </div>
              </div>

              <div className="pt-3 border-t border-stone-200/80 flex items-center justify-between">
                <span className="text-xs text-stone-400">
                  Runs every {conn.sync_frequency_minutes} mins
                </span>
                <button
                  onClick={() => handleSync(conn.platform)}
                  disabled={syncingPlatform === conn.platform}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-arch-dark hover:bg-arch-terracotta text-white text-xs font-semibold transition-colors disabled:opacity-50"
                >
                  <RefreshCw className={`w-3 h-3 ${syncingPlatform === conn.platform ? 'animate-spin' : ''}`} />
                  <span>{syncingPlatform === conn.platform ? "Syncing..." : "Sync Now"}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Supplier Verification Queue */}
      <div className="bg-white rounded-3xl border border-arch-border p-6 sm:p-8 shadow-sm space-y-5">
        <div className="flex items-center justify-between pb-4 border-b border-arch-border">
          <div>
            <span className="text-xs font-bold uppercase tracking-wider text-arch-terracotta">
              Trust & Verification Standard
            </span>
            <h2 className="font-serif text-2xl font-bold text-arch-charcoal">
              Supplier Verification Management
            </h2>
          </div>
          <span className="text-xs text-stone-500">
            Review dealer licenses, yard locations, and zero-paid map navigation links
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-stone-600">
            <thead className="text-xs uppercase tracking-wider text-stone-400 bg-stone-50 border-b border-stone-200">
              <tr>
                <th className="py-3 px-4">Supplier Name</th>
                <th className="py-3 px-4">City / State</th>
                <th className="py-3 px-4">Classification</th>
                <th className="py-3 px-4">Current Status</th>
                <th className="py-3 px-4 text-right">Verification Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {suppliers.map((sup) => (
                <tr key={sup.id} className="hover:bg-stone-50/60 transition-colors">
                  <td className="py-3 px-4 font-semibold text-arch-charcoal">
                    <Link href={`/supplier/${sup.id}`} className="hover:text-arch-terracotta">
                      {sup.name}
                    </Link>
                    {sup.is_potential && (
                      <span className="block text-xs text-amber-600 font-normal">
                        Google Places lead (unconfirmed stock)
                      </span>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    {sup.city}, {sup.state}
                  </td>
                  <td className="py-3 px-4 uppercase text-xs font-mono">
                    {sup.business_type.replace(/_/g, ' ')}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold tracking-wider uppercase ${
                      sup.verification_status === 'VERIFIED'
                        ? 'bg-emerald-100 text-emerald-800'
                        : sup.verification_status === 'PENDING_REVIEW'
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-stone-100 text-stone-700'
                    }`}>
                      {sup.verification_status}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-right space-x-1">
                    {sup.verification_status !== 'VERIFIED' ? (
                      <button
                        onClick={() => handleUpdateStatus(sup.id, 'VERIFIED')}
                        className="px-2.5 py-1 rounded-md bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs transition-colors"
                        title="Mark verified after checking business credentials"
                      >
                        Verify Supplier
                      </button>
                    ) : (
                      <button
                        onClick={() => handleUpdateStatus(sup.id, 'PENDING_REVIEW')}
                        className="px-2.5 py-1 rounded-md bg-stone-200 hover:bg-stone-300 text-stone-700 text-xs transition-colors"
                      >
                        Revoke
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Record Correction Modal */}
      {showCorrectionModal && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-3xl border border-arch-border max-w-lg w-full p-6 sm:p-8 shadow-2xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-arch-border">
              <div>
                <h3 className="font-serif text-2xl font-bold text-arch-charcoal">
                  Correct Record & Log Reason
                </h3>
                <p className="text-xs text-stone-500">
                  Curators can correct inaccurate attributes while maintaining strict audit provenance.
                </p>
              </div>
              <button
                onClick={() => setShowCorrectionModal(false)}
                className="text-stone-400 hover:text-stone-700 text-xl font-bold"
              >
                &times;
              </button>
            </div>

            <form onSubmit={handleApplyCorrection} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-medium text-stone-700 mb-1">Entity Type</label>
                  <select
                    value={entityType}
                    onChange={(e) => setEntityType(e.target.value)}
                    className="w-full px-3 py-2 rounded-xl border border-arch-border bg-stone-50 outline-none"
                  >
                    <option value="product">Product</option>
                    <option value="supplier">Supplier</option>
                    <option value="supplier_product">Supplier Listing</option>
                    <option value="reference">Reference</option>
                    <option value="manufacturer">Manufacturer</option>
                  </select>
                </div>
                <div>
                  <label className="block font-medium text-stone-700 mb-1">Record ID</label>
                  <input
                    type="number"
                    value={entityId}
                    onChange={(e) => setEntityId(parseInt(e.target.value) || 1)}
                    className="w-full px-3 py-2 rounded-xl border border-arch-border bg-stone-50 outline-none font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block font-medium text-stone-700 mb-1">Target Field to Correct *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. image_url, price_unit, official_catalog_url, verification_status"
                  value={correctionField}
                  onChange={(e) => setCorrectionField(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 outline-none font-mono"
                />
              </div>

              <div>
                <label className="block font-medium text-stone-700 mb-1">New Verified Value *</label>
                <input
                  type="text"
                  required
                  placeholder="Enter the corrected URL, unit, or string value"
                  value={newValue}
                  onChange={(e) => setNewValue(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 outline-none"
                />
              </div>

              <div>
                <label className="block font-medium text-stone-700 mb-1">
                  Mandatory Reason for Correction *
                </label>
                <textarea
                  rows={3}
                  required
                  placeholder="Document source check, phone confirmation, or official website inspection details..."
                  value={correctionReason}
                  onChange={(e) => setCorrectionReason(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-arch-border bg-stone-50 outline-none"
                />
              </div>

              <div className="pt-2 flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => setShowCorrectionModal(false)}
                  className="px-4 py-2 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-700 font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmittingCorrection}
                  className="px-5 py-2 rounded-xl bg-arch-dark hover:bg-arch-terracotta text-white font-semibold transition-colors disabled:opacity-50"
                >
                  {isSubmittingCorrection ? "Saving Correction..." : "Apply & Audit Log"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
