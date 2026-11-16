"use client";

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import {
  X, Layers, Check, ChevronRight, MoreHorizontal,
  Plus, History, Package, CheckSquare, Square
} from 'lucide-react';
import {
  getUnifiedKeywordExplorer,
  getKeywordLibrary,
  searchCatalogueMaterials,
  saveCustomKeyword,
  deleteCustomKeyword,
  KeywordLibraryGroup,
  CatalogueTreeResponse,
  CatalogueMaterialHit,
  CustomKeywordItem,
} from '@/lib/api';

interface KeywordExplorerPanelProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectKeyword: (keyword: string, groupName?: string, category?: string, subcategory?: string) => void;
  selectedKeyword?: string;
}

const RECENT_STORAGE_KEY = 'materiq_recent_keywords';
const LEGACY_RECENT_STORAGE_KEY = 'nivora_recent_keywords';
const MATERIALS_PAGE_SIZE = 120;

export const KeywordExplorerPanel: React.FC<KeywordExplorerPanelProps> = ({
  isOpen,
  onClose,
  onSelectKeyword,
  selectedKeyword = "",
}) => {
  const [explorerMode, setExplorerMode] = useState<'taxonomy' | 'catalogue'>('catalogue');
  const [groups, setGroups] = useState<KeywordLibraryGroup[]>([]);
  const [catalogueTree, setCatalogueTree] = useState<CatalogueTreeResponse | null>(null);
  const [customKeywords, setCustomKeywords] = useState<CustomKeywordItem[]>([]);
  const [recentKeywords, setRecentKeywords] = useState<string[]>([]);
  const [newCustomKeyword, setNewCustomKeyword] = useState<string>("");
  const [moreMenuOpen, setMoreMenuOpen] = useState<boolean>(false);

  const [loading, setLoading] = useState<boolean>(true);

  // Taxonomy mode state
  const [selectedGroupId, setSelectedGroupId] = useState<number>(1);
  const [activeSubcategory, setActiveSubcategory] = useState<string | null>(null);

  // Catalogue mode state (10 Categories -> 184 Subcategories -> 6,319 Materials)
  const [selectedCatalogueCatId, setSelectedCatalogueCatId] = useState<number | null>(null);
  const [selectedCatalogueSubSlug, setSelectedCatalogueSubSlug] = useState<string | null>(null);
  const [catalogueMaterials, setCatalogueMaterials] = useState<CatalogueMaterialHit[]>([]);
  const [catalogueMaterialsLoading, setCatalogueMaterialsLoading] = useState<boolean>(false);
  const [catalogueMaterialsLoadingMore, setCatalogueMaterialsLoadingMore] = useState<boolean>(false);
  const [catalogueMaterialsTotal, setCatalogueMaterialsTotal] = useState<number>(0);

  // Multi-selection state (inside ... menu)
  const [multiSelectMode, setMultiSelectMode] = useState<boolean>(false);
  const [selectedKeywordsList, setSelectedKeywordsList] = useState<string[]>([]);

  // Refs for type-ahead scrolling
  const catListRef = useRef<HTMLDivElement>(null);
  const subListRef = useRef<HTMLDivElement>(null);
  const matListRef = useRef<HTMLDivElement>(null);

  // Load recent keywords from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem(RECENT_STORAGE_KEY) || localStorage.getItem(LEGACY_RECENT_STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed)) setRecentKeywords(parsed.slice(0, 8));
      }
    } catch {}
  }, []);

  const recordRecentKeyword = useCallback((kw: string) => {
    const clean = kw.trim();
    if (!clean) return;
    setRecentKeywords(prev => {
      const next = [clean, ...prev.filter(x => x.toLowerCase() !== clean.toLowerCase())].slice(0, 8);
      try {
        localStorage.setItem(RECENT_STORAGE_KEY, JSON.stringify(next));
      } catch {}
      return next;
    });
  }, []);

  // Load catalogue tree on first open
  useEffect(() => {
    if (isOpen && groups.length === 0) {
      setLoading(true);
      getUnifiedKeywordExplorer()
        .then((data) => {
          const list = Array.isArray(data?.explorer_categories) ? data.explorer_categories : [];
          if (list.length > 0) {
            setGroups(list);
            setSelectedGroupId(list[0].id);
          }
          if (data?.catalogue_tree) {
            setCatalogueTree(data.catalogue_tree);
            const firstCat = data.catalogue_tree.categories?.[0];
            if (firstCat) {
              setSelectedCatalogueCatId(firstCat.id);
              const firstSub = firstCat.subcategories?.[0];
              if (firstSub) setSelectedCatalogueSubSlug(firstSub.slug);
            }
          }
          if (Array.isArray(data?.custom_keywords)) {
            setCustomKeywords(data.custom_keywords);
          }
        })
        .catch(() => {
          return getKeywordLibrary().then((list) => {
            if (Array.isArray(list) && list.length > 0) {
              setGroups(list);
              setSelectedGroupId(list[0].id);
            }
          });
        })
        .finally(() => setLoading(false));
    }
  }, [isOpen, groups.length]);

  // Load materials when catalogue category/subcategory changes
  useEffect(() => {
    if (explorerMode !== 'catalogue' || !catalogueTree || !selectedCatalogueCatId) return;
    const activeCat = catalogueTree.categories.find(c => c.id === selectedCatalogueCatId);
    if (!activeCat) return;

    setCatalogueMaterialsLoading(true);
    searchCatalogueMaterials({
      category: activeCat.slug,
      subcategory: selectedCatalogueSubSlug || undefined,
      limit: MATERIALS_PAGE_SIZE,
      offset: 0,
    })
      .then((res) => {
        setCatalogueMaterials(res.items || []);
        setCatalogueMaterialsTotal(res.total || (res.items || []).length);
      })
      .catch(() => {
        setCatalogueMaterials([]);
        setCatalogueMaterialsTotal(0);
      })
      .finally(() => setCatalogueMaterialsLoading(false));
  }, [explorerMode, catalogueTree, selectedCatalogueCatId, selectedCatalogueSubSlug]);

  // Load more materials pagination
  const handleLoadMoreMaterials = async () => {
    if (explorerMode !== 'catalogue' || !catalogueTree || !selectedCatalogueCatId || catalogueMaterialsLoadingMore) return;
    const activeCat = catalogueTree.categories.find(c => c.id === selectedCatalogueCatId);
    if (!activeCat) return;

    setCatalogueMaterialsLoadingMore(true);
    try {
      const res = await searchCatalogueMaterials({
        category: activeCat.slug,
        subcategory: selectedCatalogueSubSlug || undefined,
        limit: MATERIALS_PAGE_SIZE,
        offset: catalogueMaterials.length,
      });
      if (res.items && res.items.length > 0) {
        setCatalogueMaterials(prev => [...prev, ...res.items]);
      }
    } catch {}
    finally {
      setCatalogueMaterialsLoadingMore(false);
    }
  };

  // Click selects material immediately
  const handleKeywordClick = (
    keyword: string,
    groupName?: string,
    category?: string,
    subcategory?: string
  ) => {
    const clean = keyword.trim();
    if (!clean) return;

    if (multiSelectMode) {
      setSelectedKeywordsList(prev =>
        prev.includes(clean) ? prev.filter(k => k !== clean) : [...prev, clean]
      );
      return;
    }

    recordRecentKeyword(clean);
    onSelectKeyword(clean, groupName, category, subcategory);
    onClose();
  };

  // Type-ahead navigation handler
  const handleTypeAhead = (e: React.KeyboardEvent<HTMLDivElement>, items: { name: string }[], containerRef: React.RefObject<HTMLDivElement | null>) => {
    if (e.key.length === 1 && !e.ctrlKey && !e.metaKey && !e.altKey) {
      const char = e.key.toLowerCase();
      const matchIdx = items.findIndex(it => it.name.toLowerCase().startsWith(char));
      if (matchIdx >= 0 && containerRef.current) {
        const targetEl = containerRef.current.children[matchIdx] as HTMLElement;
        if (targetEl) {
          targetEl.scrollIntoView({ block: 'nearest' });
          targetEl.focus();
        }
      }
    }
  };

  const activeCatalogueCategory = useMemo(() => {
    if (!catalogueTree || !selectedCatalogueCatId) return null;
    return catalogueTree.categories.find(c => c.id === selectedCatalogueCatId) || catalogueTree.categories[0];
  }, [catalogueTree, selectedCatalogueCatId]);

  const activeCatalogueSubcategory = useMemo(() => {
    if (!activeCatalogueCategory || !selectedCatalogueSubSlug) return null;
    return activeCatalogueCategory.subcategories.find(s => s.slug === selectedCatalogueSubSlug) || null;
  }, [activeCatalogueCategory, selectedCatalogueSubSlug]);

  const activeTaxonomyGroup = useMemo(() => {
    return groups.find(g => g.id === selectedGroupId) || groups[0];
  }, [groups, selectedGroupId]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 md:p-6 bg-black/60 backdrop-blur-xs animate-in fade-in duration-200">
      <div
        className="relative w-full max-w-6xl h-[88vh] bg-white dark:bg-arch-dark-card rounded-2xl shadow-2xl border border-arch-border dark:border-arch-dark-border flex flex-col overflow-hidden text-arch-charcoal dark:text-arch-dark-text"
        onClick={() => setMoreMenuOpen(false)}
      >
        {/* 1. HEADER: Title, Recent Materials, Options Menu, Close */}
        <div className="px-5 py-3 border-b border-arch-border dark:border-arch-dark-border flex items-center justify-between shrink-0 bg-white dark:bg-arch-dark-card z-20">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-arch-terracotta/10 text-arch-terracotta flex items-center justify-center">
              <Layers className="w-4 h-4" />
            </div>
            <div>
              <h2 className="font-serif font-bold text-lg text-arch-charcoal dark:text-stone-100 leading-none">
                {explorerMode === 'catalogue' ? 'Physical Material Catalogue' : 'Design Taxonomy Explorer'}
              </h2>
              <span className="text-xs text-arch-muted dark:text-arch-dark-muted mt-0.5 block">
                {explorerMode === 'catalogue' ? '10 Categories &middot; 184 Subcategories &middot; 6,319 Materials' : '14 Architectural Classifications'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Options Menu (...) */}
            <div className="relative">
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setMoreMenuOpen(!moreMenuOpen);
                }}
                className="p-2 rounded-xl hover:bg-stone-100 dark:hover:bg-arch-dark-surface text-arch-muted dark:text-arch-dark-muted hover:text-arch-charcoal dark:hover:text-stone-100 transition-colors"
                title="Catalogue & Explorer Options"
                aria-label="Catalogue options"
              >
                <MoreHorizontal className="w-5 h-5" />
              </button>

              {moreMenuOpen && (
                <div
                  onClick={(e) => e.stopPropagation()}
                  className="absolute right-0 top-full mt-1.5 w-64 bg-white dark:bg-arch-dark-surface border border-arch-border dark:border-arch-dark-border rounded-xl shadow-xl py-2 z-30 space-y-1 text-secondary"
                >
                  <div className="px-3 py-1 text-xs uppercase font-semibold text-arch-muted dark:text-arch-dark-muted tracking-wider">
                    Catalogue Mode
                  </div>
                  <button
                    onClick={() => {
                      setExplorerMode('catalogue');
                      setMoreMenuOpen(false);
                    }}
                    className={`w-full px-3 py-1.5 text-left flex items-center justify-between hover:bg-stone-100 dark:hover:bg-stone-800 ${
                      explorerMode === 'catalogue' ? 'text-arch-terracotta font-semibold' : ''
                    }`}
                  >
                    <span>Physical Construction (6,319)</span>
                    {explorerMode === 'catalogue' && <Check className="w-4 h-4" />}
                  </button>
                  <button
                    onClick={() => {
                      setExplorerMode('taxonomy');
                      setMoreMenuOpen(false);
                    }}
                    className={`w-full px-3 py-1.5 text-left flex items-center justify-between hover:bg-stone-100 dark:hover:bg-stone-800 ${
                      explorerMode === 'taxonomy' ? 'text-arch-terracotta font-semibold' : ''
                    }`}
                  >
                    <span>Design Taxonomy (14 Groups)</span>
                    {explorerMode === 'taxonomy' && <Check className="w-4 h-4" />}
                  </button>

                  <div className="border-t border-arch-border dark:border-arch-dark-border my-1" />

                  <button
                    onClick={() => {
                      setMultiSelectMode(!multiSelectMode);
                      setMoreMenuOpen(false);
                    }}
                    className="w-full px-3 py-1.5 text-left flex items-center justify-between hover:bg-stone-100 dark:hover:bg-stone-800"
                  >
                    <span>Multi-Select Mode</span>
                    {multiSelectMode ? <CheckSquare className="w-4 h-4 text-arch-terracotta" /> : <Square className="w-4 h-4 text-stone-400" />}
                  </button>
                </div>
              )}
            </div>

            {/* Close Panel Button */}
            <button
              onClick={onClose}
              type="button"
              className="p-2 rounded-xl hover:bg-stone-100 dark:hover:bg-arch-dark-surface text-stone-400 hover:text-arch-charcoal dark:hover:text-stone-100 transition-colors"
              aria-label="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Recent Materials Strip */}
        {recentKeywords.length > 0 && (
          <div className="px-5 py-2 bg-stone-50 dark:bg-stone-900 border-b border-arch-border dark:border-arch-dark-border flex items-center gap-2 overflow-x-auto scrollbar-none text-secondary shrink-0">
            <span className="text-xs font-semibold text-arch-muted dark:text-arch-dark-muted uppercase tracking-wider shrink-0 flex items-center gap-1">
              <History className="w-3.5 h-3.5" />
              <span>Recent:</span>
            </span>
            {recentKeywords.map((kw, i) => (
              <button
                key={i}
                type="button"
                onClick={() => handleKeywordClick(kw)}
                className="px-2.5 py-1 rounded-lg text-xs font-medium bg-white dark:bg-arch-dark-card border border-arch-border dark:border-arch-dark-border hover:border-arch-terracotta dark:hover:border-arch-terracotta hover:text-arch-terracotta transition-colors shrink-0"
              >
                {kw}
              </button>
            ))}
          </div>
        )}

        {/* 2. BODY: THREE COLUMNS (Categories, Subcategories, Materials) */}
        {loading ? (
          <div className="flex-1 flex flex-col items-center justify-center p-12 text-arch-muted">
            <div className="w-8 h-8 border-2 border-arch-terracotta border-t-transparent rounded-full animate-spin mb-3" />
            <p className="text-secondary font-medium">Loading architectural catalogue...</p>
          </div>
        ) : explorerMode === 'catalogue' && catalogueTree ? (
          <div className="flex-1 grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-arch-border dark:divide-arch-dark-border min-h-0 overflow-hidden">
            
            {/* COLUMN 1: CATEGORIES (Name + Count) */}
            <div
              tabIndex={0}
              onKeyDown={(e) => handleTypeAhead(e, catalogueTree.categories, catListRef)}
              className="flex flex-col h-full overflow-hidden bg-stone-50/50 dark:bg-arch-dark-surface/40 focus:outline-hidden"
            >
              <div className="px-4 py-2.5 border-b border-arch-border dark:border-arch-dark-border text-secondary font-semibold text-arch-charcoal dark:text-stone-200 flex items-center justify-between shrink-0">
                <span>Categories</span>
                <span className="text-xs text-arch-muted dark:text-arch-dark-muted font-normal">
                  {catalogueTree.total_categories}
                </span>
              </div>
              <div ref={catListRef} className="flex-1 overflow-y-auto p-2 space-y-1">
                {catalogueTree.categories.map((cat) => {
                  const isSelected = cat.id === activeCatalogueCategory?.id;
                  return (
                    <button
                      key={cat.id}
                      type="button"
                      onClick={() => {
                        setSelectedCatalogueCatId(cat.id);
                        const firstSub = cat.subcategories?.[0];
                        setSelectedCatalogueSubSlug(firstSub ? firstSub.slug : null);
                      }}
                      className={`w-full px-3 py-2 rounded-xl text-left transition-all flex items-center justify-between group ${
                        isSelected
                          ? 'bg-arch-terracotta/10 text-arch-terracotta font-semibold shadow-2xs'
                          : 'text-arch-charcoal dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-arch-dark-surface'
                      }`}
                    >
                      <span className="text-body-base truncate pr-2">{cat.name}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
                        isSelected ? 'bg-arch-terracotta text-white' : 'bg-stone-200/70 dark:bg-stone-800 text-stone-600 dark:text-stone-400'
                      }`}>
                        {cat.materials_count}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* COLUMN 2: SUBCATEGORIES (Name + Count) */}
            <div
              tabIndex={0}
              onKeyDown={(e) => handleTypeAhead(e, activeCatalogueCategory?.subcategories || [], subListRef)}
              className="flex flex-col h-full overflow-hidden bg-stone-50/20 dark:bg-arch-dark-surface/20 focus:outline-hidden"
            >
              <div className="px-4 py-2.5 border-b border-arch-border dark:border-arch-dark-border text-secondary font-semibold text-arch-charcoal dark:text-stone-200 flex items-center justify-between shrink-0">
                <span>Subcategories</span>
                <span className="text-xs text-arch-muted dark:text-arch-dark-muted font-normal">
                  {activeCatalogueCategory?.subcategories.length || 0}
                </span>
              </div>
              <div ref={subListRef} className="flex-1 overflow-y-auto p-2 space-y-1">
                {/* All Subcategories Option */}
                <button
                  type="button"
                  onClick={() => setSelectedCatalogueSubSlug(null)}
                  className={`w-full px-3 py-2 rounded-xl text-left transition-all flex items-center justify-between ${
                    selectedCatalogueSubSlug === null
                      ? 'bg-arch-charcoal text-white dark:bg-stone-100 dark:text-arch-dark-bg font-semibold shadow-xs'
                      : 'text-arch-charcoal dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-arch-dark-surface'
                  }`}
                >
                  <span className="text-body-base truncate pr-2">All Subcategories</span>
                  <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
                    selectedCatalogueSubSlug === null ? 'bg-white/20 text-white' : 'bg-stone-200/70 dark:bg-stone-800 text-stone-600 dark:text-stone-400'
                  }`}>
                    {activeCatalogueCategory?.materials_count || 0}
                  </span>
                </button>

                {activeCatalogueCategory?.subcategories.map((sub) => {
                  const isSelected = sub.slug === selectedCatalogueSubSlug;
                  return (
                    <button
                      key={sub.id}
                      type="button"
                      onClick={() => setSelectedCatalogueSubSlug(sub.slug)}
                      className={`w-full px-3 py-2 rounded-xl text-left transition-all flex items-center justify-between ${
                        isSelected
                          ? 'bg-arch-terracotta/10 text-arch-terracotta font-semibold shadow-2xs'
                          : 'text-arch-charcoal dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-arch-dark-surface'
                      }`}
                    >
                      <span className="text-body-base truncate pr-2">{sub.name}</span>
                      <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
                        isSelected ? 'bg-arch-terracotta text-white' : 'bg-stone-200/70 dark:bg-stone-800 text-stone-600 dark:text-stone-400'
                      }`}>
                        {sub.materials_count}
                      </span>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* COLUMN 3: MATERIALS (Name Only, Click selects immediately) */}
            <div
              tabIndex={0}
              onKeyDown={(e) => handleTypeAhead(e, catalogueMaterials.map(m => ({ name: m.material })), matListRef)}
              className="flex flex-col h-full overflow-hidden bg-white dark:bg-arch-dark-card focus:outline-hidden"
            >
              <div className="px-4 py-2.5 border-b border-arch-border dark:border-arch-dark-border text-secondary font-semibold text-arch-charcoal dark:text-stone-200 flex items-center justify-between shrink-0">
                <span>Materials</span>
                <span className="text-xs text-arch-muted dark:text-arch-dark-muted font-normal">
                  {catalogueMaterialsTotal} items
                </span>
              </div>

              <div ref={matListRef} className="flex-1 overflow-y-auto p-2 space-y-1">
                {catalogueMaterialsLoading ? (
                  <div className="py-12 flex flex-col items-center justify-center text-arch-muted">
                    <div className="w-6 h-6 border-2 border-arch-terracotta border-t-transparent rounded-full animate-spin mb-2" />
                    <span className="text-secondary">Loading materials...</span>
                  </div>
                ) : catalogueMaterials.length === 0 ? (
                  <div className="py-12 text-center text-secondary text-arch-muted">
                    No materials found in this category.
                  </div>
                ) : (
                  <>
                    {catalogueMaterials.map((mat) => {
                      const isSelected = selectedKeyword.toLowerCase() === mat.material.toLowerCase();
                      return (
                        <button
                          key={mat.id}
                          type="button"
                          onClick={() => handleKeywordClick(mat.material, mat.category, mat.category, mat.subcategory)}
                          className={`w-full px-3 py-2 rounded-xl text-left transition-colors text-body-base font-medium flex items-center justify-between group ${
                            isSelected
                              ? 'bg-arch-terracotta text-white font-semibold'
                              : 'text-arch-charcoal dark:text-stone-200 hover:bg-stone-100 dark:hover:bg-arch-dark-surface'
                          }`}
                        >
                          <span className="truncate">{mat.material}</span>
                          {isSelected && <Check className="w-4 h-4 text-white shrink-0" />}
                        </button>
                      );
                    })}

                    {catalogueMaterials.length < catalogueMaterialsTotal && (
                      <div className="pt-2 pb-4 text-center">
                        <button
                          type="button"
                          onClick={handleLoadMoreMaterials}
                          disabled={catalogueMaterialsLoadingMore}
                          className="px-4 py-2 rounded-xl bg-stone-100 hover:bg-stone-200 dark:bg-arch-dark-surface text-secondary font-medium transition-colors text-arch-charcoal dark:text-stone-200"
                        >
                          {catalogueMaterialsLoadingMore ? 'Loading more...' : `Load more (${catalogueMaterialsTotal - catalogueMaterials.length} remaining)`}
                        </button>
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>

          </div>
        ) : (
          /* DESIGN TAXONOMY MODE (14 Groups) */
          <div className="flex-1 grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-arch-border dark:divide-arch-dark-border min-h-0 overflow-hidden">
            {/* Column 1: Groups */}
            <div className="flex flex-col h-full overflow-hidden bg-stone-50/50 dark:bg-arch-dark-surface/40">
              <div className="px-4 py-2.5 border-b border-arch-border dark:border-arch-dark-border text-secondary font-semibold text-arch-charcoal dark:text-stone-200">
                Design Groups ({groups.length})
              </div>
              <div className="flex-1 overflow-y-auto p-2 space-y-1">
                {groups.map((grp) => (
                  <button
                    key={grp.id}
                    onClick={() => {
                      setSelectedGroupId(grp.id);
                      setActiveSubcategory(grp.subcategories?.[0] || null);
                    }}
                    className={`w-full px-3 py-2 rounded-xl text-left text-body-base transition-colors flex items-center justify-between ${
                      grp.id === activeTaxonomyGroup?.id
                        ? 'bg-arch-terracotta/10 text-arch-terracotta font-semibold'
                        : 'text-arch-charcoal dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-arch-dark-surface'
                    }`}
                  >
                    <span className="truncate">{grp.name}</span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-stone-200/70 dark:bg-stone-800 text-stone-600 dark:text-stone-400">
                      {grp.subcategories?.length || 0}
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Column 2: Taxonomy Subcategories */}
            <div className="flex flex-col h-full overflow-hidden bg-stone-50/20 dark:bg-arch-dark-surface/20">
              <div className="px-4 py-2.5 border-b border-arch-border dark:border-arch-dark-border text-secondary font-semibold text-arch-charcoal dark:text-stone-200">
                Subcategories ({activeTaxonomyGroup?.subcategories?.length || 0})
              </div>
              <div className="flex-1 overflow-y-auto p-2 space-y-1">
                {activeTaxonomyGroup?.subcategories?.map((subName: string, sIdx: number) => (
                  <button
                    key={sIdx}
                    onClick={() => setActiveSubcategory(subName)}
                    className={`w-full px-3 py-2 rounded-xl text-left text-body-base transition-colors flex items-center justify-between ${
                      subName === activeSubcategory
                        ? 'bg-arch-terracotta/10 text-arch-terracotta font-semibold'
                        : 'text-arch-charcoal dark:text-stone-300 hover:bg-stone-100 dark:hover:bg-arch-dark-surface'
                    }`}
                  >
                    <span className="truncate">{subName}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Column 3: Taxonomy Keywords */}
            <div className="flex flex-col h-full overflow-hidden bg-white dark:bg-arch-dark-card">
              <div className="px-4 py-2.5 border-b border-arch-border dark:border-arch-dark-border text-secondary font-semibold text-arch-charcoal dark:text-stone-200">
                Materials &amp; Terms ({activeTaxonomyGroup?.keywords?.length || 0})
              </div>
              <div className="flex-1 overflow-y-auto p-2 space-y-1">
                {activeTaxonomyGroup?.keywords?.map((kw: string, kwIdx: number) => (
                  <button
                    key={kwIdx}
                    onClick={() => handleKeywordClick(kw, activeTaxonomyGroup.name, activeTaxonomyGroup.name, activeSubcategory || undefined)}
                    className="w-full px-3 py-2 rounded-xl text-left text-body-base font-medium text-arch-charcoal dark:text-stone-200 hover:bg-stone-100 dark:hover:bg-arch-dark-surface transition-colors"
                  >
                    {kw}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
