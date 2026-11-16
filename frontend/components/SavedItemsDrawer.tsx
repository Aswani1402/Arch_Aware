"use client";

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  X, Bookmark, ExternalLink, Trash2, Building2, Layers, 
  MapPin, Phone, MessageSquare, Globe, ArrowRight, Video, Sparkles, Store, CheckCircle2
} from 'lucide-react';
import { SavedItem, Reference } from '@/types';
import { getSavedItems, hasAuthToken, toggleSavedItem } from '@/lib/api';
import { useNavigation } from '@/lib/navigationContext';
import { SourceBadge } from './SourceBadge';
import { VerificationBadge } from './VerificationBadge';

interface SavedItemsDrawerProps {
  isOpen?: boolean;
  onClose?: () => void;
  initialTab?: 'reference' | 'supplier' | 'all';
  onSelectReference?: (reference: Reference) => void;
  onSavedItemsChanged?: () => void;
}

export const SavedItemsDrawer: React.FC<SavedItemsDrawerProps> = ({
  isOpen: propIsOpen,
  onClose: propOnClose,
  initialTab: propInitialTab,
  onSelectReference,
  onSavedItemsChanged
}) => {
  const nav = useNavigation();
  const isOpen = propIsOpen !== undefined ? propIsOpen : nav.savedDrawerOpen;
  const onClose = propOnClose || nav.closeSavedDrawer;
  
  const [items, setItems] = useState<SavedItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [requiresAuth, setRequiresAuth] = useState(false);
  const [activeTab, setActiveTab] = useState<'all' | 'reference' | 'supplier'>(
    propInitialTab || (nav.savedDrawerTab as any) || 'all'
  );

  // Sync tab when opened from navigation
  useEffect(() => {
    if (nav.savedDrawerTab) {
      setActiveTab(nav.savedDrawerTab as any);
    }
  }, [nav.savedDrawerTab]);

  useEffect(() => {
    if (isOpen) {
      loadSavedItems();
    }
  }, [isOpen]);

  const loadSavedItems = async () => {
    if (!hasAuthToken()) {
      setRequiresAuth(true);
      setItems([]);
      setLoading(false);
      return;
    }
    setRequiresAuth(false);
    setLoading(true);
    try {
      const data = await getSavedItems();
      setItems(Array.isArray(data) ? data : []);
    } catch (err: any) {
      if (err?.message?.includes('401') || err?.message?.toLowerCase?.().includes('credentials')) {
        setRequiresAuth(true);
      }
      setItems([]);
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (item: SavedItem) => {
    try {
      await toggleSavedItem({
        item_type: item.item_type,
        reference_id: item.reference_id,
        product_id: item.product_id,
        supplier_id: item.supplier_id
      });
      setItems(prev => prev.filter(i => i.id !== item.id));
      nav.refreshSavedCounts();
      if (onSavedItemsChanged) onSavedItemsChanged();
    } catch (err) {
      console.error("Failed to remove saved item", err);
    }
  };

  const filteredItems = items.filter(item => {
    if (activeTab === 'all') return true;
    return item.item_type === activeTab;
  });

  const refCount = items.filter(i => i.item_type === 'reference').length;
  const supplierCount = items.filter(i => i.item_type === 'supplier').length;

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 dark:bg-black/70 backdrop-blur-xs z-[60] transition-opacity"
        onClick={onClose}
      />

      {/* Side Drawer */}
      <div className="fixed inset-y-0 right-0 z-[60] w-full sm:max-w-lg bg-white dark:bg-arch-dark-card shadow-2xl flex flex-col border-l border-arch-border dark:border-arch-dark-border animate-in slide-in-from-right duration-200">
        {/* Drawer Header */}
        <div className="p-4 sm:p-5 border-b border-arch-border dark:border-arch-dark-border flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-9 h-9 rounded-lg bg-arch-terracotta/10 text-arch-terracotta flex items-center justify-center">
              <Bookmark className="w-5 h-5 fill-current" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-arch-charcoal dark:text-stone-100">Saved Collections</h3>
              <p className="text-secondary text-arch-muted dark:text-arch-dark-muted">{items.length} total saved items</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-stone-400 hover:text-arch-charcoal dark:hover:text-stone-200 rounded-lg hover:bg-stone-100 dark:hover:bg-arch-dark-surface transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Switcher */}
        <div className="px-5 pt-3 pb-2 border-b border-arch-border dark:border-arch-dark-border flex gap-2">
          <button
            onClick={() => setActiveTab('all')}
            className={`px-3 py-1.5 text-secondary font-medium rounded-lg transition-colors flex items-center gap-1.5 ${
              activeTab === 'all'
                ? 'bg-arch-charcoal text-white dark:bg-stone-200 dark:text-arch-charcoal'
                : 'text-arch-muted hover:text-arch-charcoal dark:hover:text-stone-200 hover:bg-stone-100 dark:hover:bg-arch-dark-surface'
            }`}
          >
            <span>All Items</span>
            <span className="text-xs opacity-75 bg-black/10 dark:bg-white/20 px-1.5 py-0.2 rounded-full">{items.length}</span>
          </button>
          <button
            onClick={() => setActiveTab('reference')}
            className={`px-3 py-1.5 text-secondary font-medium rounded-lg transition-colors flex items-center gap-1.5 ${
              activeTab === 'reference'
                ? 'bg-arch-terracotta text-white'
                : 'text-arch-muted hover:text-arch-charcoal dark:hover:text-stone-200 hover:bg-stone-100 dark:hover:bg-arch-dark-surface'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Inspiration</span>
            <span className="text-xs opacity-75 bg-black/10 dark:bg-white/20 px-1.5 py-0.2 rounded-full">{refCount}</span>
          </button>
          <button
            onClick={() => setActiveTab('supplier')}
            className={`px-3 py-1.5 text-secondary font-medium rounded-lg transition-colors flex items-center gap-1.5 ${
              activeTab === 'supplier'
                ? 'bg-blue-600 text-white'
                : 'text-arch-muted hover:text-arch-charcoal dark:hover:text-stone-200 hover:bg-stone-100 dark:hover:bg-arch-dark-surface'
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>Vendors</span>
            <span className="text-xs opacity-75 bg-black/10 dark:bg-white/20 px-1.5 py-0.2 rounded-full">{supplierCount}</span>
          </button>
        </div>

        {/* Items List */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-3.5">
          {loading ? (
            <div className="py-12 text-center text-secondary text-arch-muted dark:text-arch-dark-muted">
              Loading saved items...
            </div>
          ) : requiresAuth ? (
            <div className="py-12 text-center px-4">
              <div className="w-12 h-12 rounded-full bg-stone-100 dark:bg-arch-dark-surface text-arch-terracotta mx-auto flex items-center justify-center mb-3">
                <Bookmark className="w-6 h-6" />
              </div>
              <h4 className="font-medium text-arch-charcoal dark:text-stone-200">Sign in to view your saved library</h4>
              <p className="text-secondary text-arch-muted dark:text-arch-dark-muted mt-1 max-w-xs mx-auto mb-4">
                Your saved moodboards, materials, and supply vendors sync to your account once signed in.
              </p>
              <Link
                href="/login"
                onClick={onClose}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-arch-terracotta hover:bg-arch-terracotta-dark text-white text-secondary font-semibold transition-colors"
              >
                <span>Sign In</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          ) : filteredItems.length === 0 ? (
            <div className="py-12 text-center">
              <div className="w-12 h-12 rounded-full bg-stone-100 dark:bg-arch-dark-surface text-stone-400 mx-auto flex items-center justify-center mb-3">
                <Bookmark className="w-6 h-6" />
              </div>
              <h4 className="font-medium text-arch-charcoal dark:text-stone-200">No saved items found</h4>
              <p className="text-secondary text-arch-muted dark:text-arch-dark-muted mt-1 max-w-xs mx-auto">
                {activeTab === 'supplier' 
                  ? 'Bookmark verified suppliers while sourcing to build your vendor address book.' 
                  : 'Save architectural references and images from the discovery feed to review them later.'}
              </p>
            </div>
          ) : (
            filteredItems.map(item => {
              const data = item.item_data || {};
              const isRef = item.item_type === 'reference';
              const isSupplier = item.item_type === 'supplier';

              return (
                <div 
                  key={item.id}
                  className="group relative bg-stone-50 dark:bg-arch-dark-surface/60 rounded-xl p-3.5 border border-arch-border dark:border-arch-dark-border flex gap-3.5 hover:border-arch-charcoal/20 dark:hover:border-arch-dark-border transition-all"
                >
                  {/* Thumbnail / Icon */}
                  {isRef && data.image_url ? (
                    <div className="relative w-20 h-20 rounded-lg overflow-hidden shrink-0 bg-stone-200 dark:bg-stone-800">
                      <img referrerPolicy="no-referrer" 
                        src={data.image_url} 
                        alt={data.title || "Reference"} 
                        className="w-full h-full object-cover"
                      />
                      {data.media_type === 'reel' && (
                        <div className="absolute bottom-1 right-1 p-0.5 bg-black/60 rounded text-white">
                          <Video className="w-3 h-3" />
                        </div>
                      )}
                    </div>
                  ) : isSupplier ? (
                    <div className="w-12 h-12 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0 border border-blue-100 dark:border-blue-900/40">
                      <Building2 className="w-6 h-6" />
                    </div>
                  ) : (
                    <div className="w-12 h-12 rounded-lg bg-stone-100 dark:bg-arch-dark-surface text-stone-400 flex items-center justify-center shrink-0">
                      <Layers className="w-8 h-8" />
                    </div>
                  )}

                  {/* Body */}
                  <div className="flex-1 min-w-0 pr-6">
                    {isRef && (
                      <div className="mb-1.5 flex items-center gap-1.5 flex-wrap">
                        <SourceBadge platform={data.source_platform || 'pinterest'} size="sm" />
                        <VerificationBadge status={data.verification_status || 'UNKNOWN'} size="sm" />
                        {data.category_name && (
                          <span className="text-secondary text-arch-muted dark:text-arch-dark-muted bg-stone-100 dark:bg-arch-dark-card border border-arch-border dark:border-arch-dark-border px-2 py-0.5 rounded-full truncate">
                            {data.category_name}
                          </span>
                        )}
                      </div>
                    )}

                    <h4 className="text-card-title font-semibold text-arch-charcoal dark:text-stone-100 line-clamp-2 leading-snug">
                      {data.title || data.name || "Untitled Item"}
                    </h4>

                    {isSupplier && (
                      <div className="mt-1.5 space-y-1.5">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          {data.business_type && (
                            <span className="text-xs font-medium text-blue-700 dark:text-blue-300 bg-blue-50 dark:bg-blue-950/40 border border-blue-200 dark:border-blue-900/60 px-2 py-0.5 rounded-full capitalize">
                              {data.business_type.replace(/_/g, ' ')}
                            </span>
                          )}
                          <VerificationBadge
                            status={data.verification_status || 'UNKNOWN'}
                            isPotential={Boolean(data.is_potential)}
                            size="sm"
                          />
                        </div>

                        {data.city && (
                          <div className="flex items-center gap-1.5 text-secondary text-arch-muted dark:text-arch-dark-muted">
                            <MapPin className="w-3.5 h-3.5 text-arch-terracotta shrink-0" />
                            <span>{data.city}{data.state ? `, ${data.state}` : ''}</span>
                          </div>
                        )}

                        {data.materials_sold && (
                          <div className="text-xs text-stone-600 dark:text-stone-300 line-clamp-1">
                            <span className="text-arch-muted dark:text-arch-dark-muted font-medium">Materials: </span>
                            {data.materials_sold}
                          </div>
                        )}

                        <div className="flex items-center gap-3 pt-1 flex-wrap text-secondary">
                          {data.phone && (
                            <a
                              href={`tel:${data.phone}`}
                              className="flex items-center gap-1 text-arch-charcoal dark:text-stone-300 hover:text-arch-terracotta"
                              title="Call"
                            >
                              <Phone className="w-3.5 h-3.5 text-stone-400" />
                              <span>{data.phone}</span>
                            </a>
                          )}
                          {data.whatsapp && (
                            <a
                              href={`https://wa.me/${data.whatsapp.replace(/[^0-9]/g, '')}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 hover:underline"
                              title="Chat on WhatsApp"
                            >
                              <MessageSquare className="w-3.5 h-3.5" />
                              <span>WhatsApp</span>
                            </a>
                          )}
                          {data.google_maps_url && (
                            <a
                              href={data.google_maps_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-1 text-blue-600 dark:text-blue-400 hover:underline"
                              title="Google Maps"
                            >
                              <MapPin className="w-3.5 h-3.5" />
                              <span>Maps</span>
                            </a>
                          )}
                        </div>
                      </div>
                    )}

                    {isRef && data.architect_name && (
                      <span className="text-secondary text-arch-muted dark:text-arch-dark-muted block mt-1">
                        Attributed to {data.architect_name}
                      </span>
                    )}

                    {/* Actions */}
                    <div className="mt-3 flex items-center gap-3">
                      {isRef && (
                        onSelectReference ? (
                          <button
                            onClick={() => {
                              onSelectReference(data as Reference);
                              onClose();
                            }}
                            className="text-secondary font-semibold text-arch-terracotta hover:underline flex items-center gap-1"
                          >
                            <span>Explore Details</span>
                            <ArrowRight className="w-3 h-3" />
                          </button>
                        ) : (
                          <Link
                            href={`/reference/${data.slug || data.id}`}
                            onClick={onClose}
                            className="text-secondary font-semibold text-arch-terracotta hover:underline flex items-center gap-1"
                          >
                            <span>Explore Details</span>
                            <ArrowRight className="w-3 h-3" />
                          </Link>
                        )
                      )}

                      {isSupplier && (
                        <Link
                          href={`/supplier/${data.slug || data.supplier_id || data.id}`}
                          onClick={onClose}
                          className="text-secondary font-semibold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                        >
                          <span>Supplier Profile</span>
                          <ArrowRight className="w-3 h-3" />
                        </Link>
                      )}

                      {(data.source_url || data.inspiration_source_url || (isRef && data.website)) && (
                        <a
                          href={data.source_url || data.inspiration_source_url || data.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-secondary text-arch-muted dark:text-arch-dark-muted hover:text-arch-charcoal dark:hover:text-stone-200 flex items-center gap-1 ml-auto"
                        >
                          <ExternalLink className="w-3 h-3" />
                          <span>View Source</span>
                        </a>
                      )}
                      {isSupplier && data.website && (
                        <a
                          href={data.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-secondary text-arch-muted dark:text-arch-dark-muted hover:text-arch-charcoal dark:hover:text-stone-200 flex items-center gap-1 ml-auto"
                        >
                          <Globe className="w-3 h-3" />
                          <span>Website</span>
                        </a>
                      )}
                    </div>
                  </div>

                  {/* Remove Button */}
                  <button
                    onClick={() => handleRemove(item)}
                    className="absolute top-3.5 right-3.5 p-1.5 text-stone-400 hover:text-red-500 rounded-lg hover:bg-red-50 dark:hover:bg-red-950/40 transition-colors"
                    title="Remove from saved"
                    aria-label="Remove"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>
    </>
  );
};
