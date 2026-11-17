/**
* Central Application Branding Configuration
* Easily update the application name, logo, typography and branding tokens from here.
*/

export interface BrandConfig {
  name: string;
  shortName: string;
  tagline: string;
  subTagline: string;
  logoLetter: string;
  sourceLabels: Record<string, string>;
  themeStorageKey: string;
}

export const BRAND: BrandConfig = {
  // Brand name: Arch_Aware
  name: "Arch_Aware",
  shortName: "Arch_Aware",
  tagline: "Architecture Inspiration & Material Intelligence",
  subTagline: "Visual Discovery & Verified Sourcing",
  logoLetter: "A",
  sourceLabels: {
    pinterest: "Pinterest",
    instagram: "Instagram", // Clean name: Instagram (images & videos)
    youtube: "YouTube",
    reddit: "Reddit",
    x: "X",
    twitter: "X",
    shopping: "Google Shopping",
    google_shopping: "Google Shopping",
    search: "Google Search",
    google_search: "Google Search",
    google_places: "Google Places",
    suppliers: "Supply Vendors",
    google_business: "Supply Vendors",
    all: "All Sources",
  },
  themeStorageKey: "nivora_theme",
};

/**
 * Returns formatted source label given platform key
 */
export function getSourceLabel(platformKey: string): string {
  const normalized = platformKey.toLowerCase().trim();
  return BRAND.sourceLabels[normalized] || platformKey;
}

