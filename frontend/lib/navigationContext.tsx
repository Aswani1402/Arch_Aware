"use client";

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';
import { getSavedItems, hasAuthToken } from '@/lib/api';
import { SavedItem } from '@/types';

export type SavedTab = 'reference' | 'supplier';

interface NavigationContextType {
  keywordExplorerOpen: boolean;
  setKeywordExplorerOpen: (open: boolean) => void;
  openKeywordExplorer: () => void;
  
  savedDrawerOpen: boolean;
  savedDrawerTab: SavedTab;
  openSavedInspiration: () => void;
  openSavedVendors: () => void;
  closeSavedDrawer: () => void;
  
  savedInspirationCount: number;
  savedVendorsCount: number;
  refreshSavedCounts: () => void;

  switchToSupplyVendors: () => void;
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined);

export const NavigationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const router = useRouter();
  const pathname = usePathname();
  
  const [keywordExplorerOpen, setKeywordExplorerOpen] = useState(false);
  const [savedDrawerOpen, setSavedDrawerOpen] = useState(false);
  const [savedDrawerTab, setSavedDrawerTab] = useState<SavedTab>('reference');
  
  const [savedInspirationCount, setSavedInspirationCount] = useState(0);
  const [savedVendorsCount, setSavedVendorsCount] = useState(0);

  const refreshSavedCounts = () => {
    if (!hasAuthToken()) {
      setSavedInspirationCount(0);
      setSavedVendorsCount(0);
      return;
    }
    getSavedItems()
      .then((items: SavedItem[]) => {
        if (Array.isArray(items)) {
          let inspCount = 0;
          let vendCount = 0;
          items.forEach(item => {
            if (item.item_type === 'reference') inspCount++;
            if (item.item_type === 'supplier') vendCount++;
          });
          setSavedInspirationCount(inspCount);
          setSavedVendorsCount(vendCount);
        }
      })
      .catch(() => {});
  };

  useEffect(() => {
    refreshSavedCounts();
    const handleAuthChange = () => refreshSavedCounts();
    window.addEventListener('materiq:auth-expired', handleAuthChange);
    window.addEventListener('nivora:auth-expired', handleAuthChange);
    window.addEventListener('storage', handleAuthChange);
    return () => {
      window.removeEventListener('materiq:auth-expired', handleAuthChange);
      window.removeEventListener('nivora:auth-expired', handleAuthChange);
      window.removeEventListener('storage', handleAuthChange);
    };
  }, []);

  const openKeywordExplorer = () => {
    if (pathname === '/') {
      setKeywordExplorerOpen(prev => !prev);
    } else {
      router.push('/?openKeywords=true');
    }
  };

  const openSavedInspiration = () => {
    setSavedDrawerTab('reference');
    setSavedDrawerOpen(true);
  };

  const openSavedVendors = () => {
    setSavedDrawerTab('supplier');
    setSavedDrawerOpen(true);
  };

  const closeSavedDrawer = () => {
    setSavedDrawerOpen(false);
  };

  const switchToSupplyVendors = () => {
    if (pathname === '/') {
      // Trigger suppliers filter via custom event or URL
      window.dispatchEvent(new CustomEvent('materiq:switch-source', { detail: 'suppliers' }));
      window.dispatchEvent(new CustomEvent('nivora:switch-source', { detail: 'suppliers' }));
    } else {
      router.push('/?source=suppliers');
    }
  };

  return (
    <NavigationContext.Provider
      value={{
        keywordExplorerOpen,
        setKeywordExplorerOpen,
        openKeywordExplorer,
        savedDrawerOpen,
        savedDrawerTab,
        openSavedInspiration,
        openSavedVendors,
        closeSavedDrawer,
        savedInspirationCount,
        savedVendorsCount,
        refreshSavedCounts,
        switchToSupplyVendors,
      }}
    >
      {children}
    </NavigationContext.Provider>
  );
};

export const useNavigation = () => {
  const context = useContext(NavigationContext);
  if (!context) {
    throw new Error('useNavigation must be used within a NavigationProvider');
  }
  return context;
};

