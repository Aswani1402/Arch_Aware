/**
 * Dynamic API Base URL Resolution:
 * 1. Server-side (SSR / Server Components): Reads process.env.BACKEND_URL injected by Vercel
 *    service binding, with fallback to NEXT_PUBLIC_API_URL or local dev.
 * 2. Client-side (Browser): Defaults to same-origin relative `/api` routed to the backend service
 *    via Vercel rewrites (or uses NEXT_PUBLIC_API_URL if explicitly pointing to a separate host).
 */
export function getApiBaseUrl(): string {
  if (typeof window === "undefined") {
    const serverUrl = process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";
    const clean = serverUrl.replace(/\/+$/, "");
    return clean.endsWith("/api") ? clean : `${clean}/api`;
  }

  if (process.env.NEXT_PUBLIC_API_URL && !process.env.NEXT_PUBLIC_API_URL.startsWith("/")) {
    const clean = process.env.NEXT_PUBLIC_API_URL.replace(/\/+$/, "");
    return clean.endsWith("/api") ? clean : `${clean}/api`;
  }

  return "/api";
}

const API_BASE = getApiBaseUrl();

if (typeof window !== "undefined" && process.env.NODE_ENV === "production") {
  if (
    process.env.NEXT_PUBLIC_API_URL &&
    (process.env.NEXT_PUBLIC_API_URL.includes("localhost") || process.env.NEXT_PUBLIC_API_URL.includes("127.0.0.1"))
  ) {
    console.warn(
      "[ARCH_AWARE CONFIG WARNING] NEXT_PUBLIC_API_URL is pointing to localhost in production. " +
      "Under Vercel multi-service routing, leave NEXT_PUBLIC_API_URL empty to use same-origin /api routing."
    );
  }
}

const isJwtExpired = (token: string): boolean => {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return true;
    const base64 = parts[1].replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4);
    const jsonStr = typeof atob === 'function'
      ? atob(padded)
      : Buffer.from(padded, 'base64').toString('utf-8');
    const payload = JSON.parse(jsonStr);
    if (typeof payload?.exp === 'number') {
      return payload.exp * 1000 <= Date.now();
    }
    return false;
  } catch {
    return true;
  }
};

export const getValidAuthToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  const token = localStorage.getItem('architect_ai_token');
  if (!token) return null;
  if (isJwtExpired(token)) {
    localStorage.removeItem('architect_ai_token');
    return null;
  }
  return token;
};

export const hasAuthToken = (): boolean => Boolean(getValidAuthToken());

export async function fetchApi<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getValidAuthToken();
  const apiBase = getApiBaseUrl();
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${apiBase}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    if (res.status === 401 && typeof window !== 'undefined' && token) {
      localStorage.removeItem('architect_ai_token');
      window.dispatchEvent(new Event('materiq:auth-expired'));
      window.dispatchEvent(new Event('nivora:auth-expired'));
    }
    const errorData = await res.json().catch(() => ({}));
    throw new Error(errorData.detail || `Request failed with status ${res.status}`);
  }

  return res.json();
}

// Feed & References
export const getFeed = (params: {
  page?: number;
  page_size?: number;
  q?: string;
  category?: string;
  platform?: string;
  country?: string;
  region?: string;
  style?: string;
  project_type?: string;
  era?: string;
  interests?: string;
  refresh?: boolean;
} = {}) => {
  const query = new URLSearchParams();
  if (params.page) query.append('page', params.page.toString());
  if (params.page_size) query.append('page_size', params.page_size.toString());
  if (params.q) query.append('q', params.q);
  if (params.category) query.append('category', params.category);
  if (params.platform) query.append('platform', params.platform);
  if (params.country) query.append('country', params.country);
  if (params.region) query.append('region', params.region);
  if (params.style) query.append('style', params.style);
  if (params.project_type) query.append('project_type', params.project_type);
  if (params.era) query.append('era', params.era);
  if (params.interests) query.append('interests', params.interests);
  if (params.refresh) query.append('refresh', 'true');
  return fetchApi<any>(`/feed?${query.toString()}`);
};

export const getFeedFilters = () => fetchApi<any>('/feed/filters');

export const syncYouTubeFeed = (query?: string) => fetchApi<any>('/feed/sync-youtube', {
  method: 'POST',
  body: JSON.stringify({ query }),
});

export const getReferenceDetail = (idOrSlug: string) => fetchApi<any>(`/references/${idOrSlug}`);
export const detectReferenceMaterials = (idOrSlug: string | number, body?: { user_corrections?: any[] }) => fetchApi<any>(`/references/${idOrSlug}/detect-materials`, {
  method: 'POST',
  body: JSON.stringify(body || {}),
});
export const getProjects = getFeed;
export const getProjectDetail = getReferenceDetail;
export const getCategories = (section?: string) => fetchApi<any[]>(`/categories${section ? `?section=${section}` : ''}`);
export const getCategoryDetail = (idOrSlug: string) => fetchApi<any>(`/categories/${idOrSlug}`);

// Products & Manufacturers
export const getProducts = (params: { category?: string; material?: string; manufacturer?: string; q?: string } = {}) => {
  const query = new URLSearchParams();
  if (params.category) query.append('category', params.category);
  if (params.material) query.append('material', params.material);
  if (params.manufacturer) query.append('manufacturer', params.manufacturer);
  if (params.q) query.append('q', params.q);
  return fetchApi<any[]>(`/products?${query.toString()}`);
};

export const getProductDetail = (idOrSlug: string) => fetchApi<any>(`/products/${idOrSlug}`);
export const getManufacturers = (q?: string) => fetchApi<any[]>(`/manufacturers${q ? `?q=${q}` : ''}`);
export const getManufacturerDetail = (idOrSlug: string) => fetchApi<any>(`/manufacturers/${idOrSlug}`);

// Suppliers & Sourcing
export const getSuppliers = (params: { city?: string; state?: string; q?: string } = {}) => {
  const query = new URLSearchParams();
  if (params.city) query.append('city', params.city);
  if (params.state) query.append('state', params.state);
  if (params.q) query.append('q', params.q);
  return fetchApi<any[]>(`/suppliers?${query.toString()}`);
};

export const getSupplierDetail = (idOrSlug: string) => fetchApi<any>(`/suppliers/${idOrSlug}`);

export const discoverSuppliers = (params: { q?: string; category?: string; city?: string; state?: string; lat?: number | null; lon?: number | null; radius?: number } = {}) => {
  const query = new URLSearchParams();
  if (params.q) query.append('q', params.q);
  if (params.category) query.append('category', params.category);
  if (params.city) query.append('city', params.city);
  if (params.state) query.append('state', params.state);
  if (params.lat !== undefined && params.lat !== null) query.append('lat', params.lat.toString());
  if (params.lon !== undefined && params.lon !== null) query.append('lon', params.lon.toString());
  if (params.radius) query.append('radius', params.radius.toString());
  return fetchApi<any>(`/suppliers/discover?${query.toString()}`);
};

export const registerSupplier = (data: any) => fetchApi<any>('/suppliers/register', {
  method: 'POST',
  body: JSON.stringify(data),
});

export const searchSourcing = (params: { q?: string; product_id?: number; category?: string; city?: string; state?: string; lat?: number | null; lon?: number | null; radius?: number }) => {
  const query = new URLSearchParams();
  if (params.q) query.append('q', params.q);
  if (params.product_id) query.append('product_id', params.product_id.toString());
  if (params.category) query.append('category', params.category);
  if (params.city) query.append('city', params.city);
  if (params.state) query.append('state', params.state);
  if (params.lat !== undefined && params.lat !== null) query.append('lat', params.lat.toString());
  if (params.lon !== undefined && params.lon !== null) query.append('lon', params.lon.toString());
  if (params.radius) query.append('radius', params.radius.toString());
  return fetchApi<any>(`/sourcing/search?${query.toString()}`);
};

export const getLocationPresets = () => fetchApi<any[]>('/locations/presets');
export const geocodeLocation = (q: string) => fetchApi<any>(`/locations/geocode?q=${encodeURIComponent(q)}`);
export const reverseGeocodeLocation = (lat: number, lon: number) => fetchApi<any>(`/locations/reverse?lat=${lat}&lon=${lon}`);

// Quotations
export const createQuotationRequest = (data: any) => fetchApi<any>('/quotations', {
  method: 'POST',
  body: JSON.stringify(data),
});
export const getQuotationRequests = () => fetchApi<any[]>('/quotations');
export const respondToQuotation = (requestId: number, data: any) => fetchApi<any>(`/quotations/${requestId}/respond`, {
  method: 'POST',
  body: JSON.stringify(data),
});

// Saved Items
export const toggleSavedItem = (data: { item_type: string; reference_id?: number; product_id?: number; supplier_id?: number; project_collection?: string }) => fetchApi<any>('/saved/toggle', {
  method: 'POST',
  body: JSON.stringify(data),
});
export const getSavedItems = () => fetchApi<any[]>('/saved');

// Connectors & Admin
export const getConnectors = () => fetchApi<any[]>('/connectors');
export const triggerConnectorSync = (platform: string) => fetchApi<any>(`/connectors/${platform}/sync`, { method: 'POST' });
export const getAdminStats = () => fetchApi<any>('/admin/stats');
export const updateSupplierVerification = (supplierId: number, status: string) => fetchApi<any>(`/admin/suppliers/${supplierId}/verify`, {
  method: 'PUT',
  body: JSON.stringify({ status }),
});
export const getQualityAudit = () => fetchApi<any>('/admin/quality-audit');
export const correctRecord = (data: { entity_type: string; entity_id: number; field: string; new_value: any; reason: string }) => fetchApi<any>('/admin/records/correct', {
  method: 'PUT',
  body: JSON.stringify(data),
});
export const createManufacturer = (data: any) => fetchApi<any>('/manufacturers', {
  method: 'POST',
  body: JSON.stringify(data),
});
export const linkSupplierProduct = (supplierId: number, data: any) => fetchApi<any>(`/suppliers/${supplierId}/products`, {
  method: 'POST',
  body: JSON.stringify(data),
});

// Live YouTube Data API Search
export const searchLiveYouTubeVideos = (q: string, limit: number = 12) => {
  return fetchApi<any[]>(`/feed/youtube-search?q=${encodeURIComponent(q)}&limit=${limit}`);
};

// Google Places API Discovery
export const searchGooglePlaces = (params: { material?: string; city?: string; lat?: number; lon?: number; radius_km?: number } = {}) => {
  const query = new URLSearchParams();
  if (params.material) query.append('material', params.material);
  if (params.city) query.append('city', params.city);
  if (params.lat !== undefined && params.lat !== null) query.append('lat', params.lat.toString());
  if (params.lon !== undefined && params.lon !== null) query.append('lon', params.lon.toString());
  if (params.radius_km) query.append('radius_km', params.radius_km.toString());
  return fetchApi<any>(`/locations/google-places/search?${query.toString()}`);
};

// LLM Architectural Intelligence & Sourcing Advisory
export const analyzeProjectWithLLM = (data: { title: string; description?: string; tags?: string[]; category?: string }) => {
  return fetchApi<any>('/llm/analyze-project', {
    method: 'POST',
    body: JSON.stringify(data),
  });
};

export const getSourcingAdviceWithLLM = (data: { query: string; location?: string; material_type?: string }) => {
  return fetchApi<any>('/llm/sourcing-advice', {
    method: 'POST',
    body: JSON.stringify(data),
  });
};

export const draftQuotationRfpWithLLM = (data: { item_name: string; category?: string; location?: string; quantity_notes?: string }) => {
  return fetchApi<any>('/llm/draft-quotation', {
    method: 'POST',
    body: JSON.stringify(data),
  });
};

// Legitimate Architectural Image Search (Google Custom Search, Unsplash, Wikimedia)
export const searchArchitecturalImages = (q: string, limit: number = 12, category?: string) => {
  const query = new URLSearchParams();
  query.append('q', q);
  query.append('limit', limit.toString());
  if (category) query.append('category', category);
  return fetchApi<{ query: string; total_found: number; provider_status: any; images: any[] }>(`/feed/image-search?${query.toString()}`);
};

// Similar Relevant References (both images & videos for Three-Dot Details)
export const getSimilarReferences = (referenceId: number, limit: number = 6) => {
  return fetchApi<any[]>(`/feed/similar/${referenceId}?limit=${limit}`);
};

// Category 27: Material Comparisons & Selection Guides
export const getMaterialComparisons = () => {
  return fetchApi<{ total: number; comparisons: any[] }>('/products/comparisons/all');
};

export const getMaterialComparison = (comparisonId: string) => {
  return fetchApi<any>(`/products/comparisons/${comparisonId}`);
};

// 29-Category Architectural Taxonomy
export const getTaxonomyTree = () => {
  return fetchApi<{ total_categories: number; taxonomy: any[] }>('/categories/taxonomy/tree');
};

export const matchTaxonomy = (query: string) => {
  return fetchApi<{ query: string; total_matches: number; matches: any[] }>(`/categories/taxonomy/match?q=${encodeURIComponent(query)}`);
};

// SocialCrawl Pinterest Search API Integration
export interface PinterestItem {
  id: string;
  pin_id?: string;
  title: string | null;
  description: string | null;
  image_url: string;
  thumbnail_url: string;
  source_url: string;
  creator_name: string | null;
  creator_url: string | null;
  is_video?: boolean;
  video_duration?: string | null;
  source_platform: string;
  source_label: string;
  attribution_notice: string;
  verification_status: string;
  content_type: string;
  saved_reference_id?: number | null;
}

export interface PinterestSearchResponse {
  success: boolean;
  dry_run: boolean;
  query: string;
  cursor?: string;
  next_cursor?: string;
  has_more: boolean;
  total_items: number;
  items: PinterestItem[];
  dry_run_details?: any;
  request_id?: string;
  error?: string;
}

export const getPinterestStatus = () => fetchApi<{
  configured: boolean;
  provider: string;
  endpoint: string;
  timeout_seconds: number;
  max_retries: number;
  max_pages: number;
  cached_queries_count: number;
  message: string;
}>('/pinterest/status');

export const getPinterestCategories = () => fetchApi<{
  total: number;
  categories: Array<{
    id: string;
    name: string;
    query: string;
    section: string;
    description: string;
  }>;
}>('/pinterest/categories');

export const searchPinterest = (params: {
  query: string;
  cursor?: string;
  relevance?: string;
  trim?: boolean;
  label?: string;
  dry_run?: boolean;
}) => {
  const query = new URLSearchParams();
  query.append('query', params.query);
  if (params.cursor) query.append('cursor', params.cursor);
  if (params.relevance) query.append('relevance', params.relevance);
  query.append('trim', params.trim !== undefined ? params.trim.toString() : 'false');
  if (params.label) query.append('label', params.label);
  if (params.dry_run) query.append('dry_run', 'true');
  return fetchApi<PinterestSearchResponse>(`/pinterest/search?${query.toString()}`);
};

export const savePinterestPin = (data: {
  pin_id?: string;
  title?: string | null;
  description?: string | null;
  image_url: string;
  source_url: string;
  creator_name?: string | null;
  creator_url?: string | null;
  category_slug?: string | null;
  material_tags?: string | null;
  project_collection?: string;
}) => fetchApi<{
  saved: boolean;
  reference_id: number;
  status: string;
  message: string;
}>('/pinterest/save', {
  method: 'POST',
  body: JSON.stringify(data),
});

// =====================================================================
// SocialCrawl Multi-Platform Integration API
// (Instagram Reels, YouTube, Reddit, Google Business, Google Shopping)
// =====================================================================

export interface SocialCrawlInspirationItem {
  id: string;
  reel_id?: string;
  video_id?: string;
  video_embed_id?: string;
  post_id?: string;
  title: string | null;
  description: string | null;
  image_url: string | null;
  thumbnail_url: string | null;
  video_url?: string | null;
  media_url?: string | null;
  source_url: string;
  creator_name: string | null;
  creator_username?: string | null;
  creator_url: string | null;
  creator_avatar?: string | null;
  is_video?: boolean;
  is_reel?: boolean;
  is_short?: boolean;
  video_duration?: string | null;
  views?: number | null;
  likes?: number | null;
  upvotes?: number | null;
  comments?: number | null;
  shares?: number | null;
  subreddit?: string;
  subreddit_name?: string;
  flair?: string | null;
  material_tags?: string[];
  source_platform: 'instagram' | 'youtube' | 'reddit' | 'pinterest' | 'catalog';
  source_label: string;
  attribution_notice: string;
  verification_status: string;
  content_type: string;
  relevance_score?: number | null;
  published_at?: string | null;
}

export interface SocialCrawlBusinessItem {
  id: string;
  place_id: string;
  name: string;
  category: string;
  categories: string[];
  rating: number | null;
  reviews_count: number;
  address: string;
  city: string;
  region: string;
  country_code: string;
  phone: string | null;
  latitude: number | null;
  longitude: number | null;
  website: string | null;
  maps_url: string | null;
  image_url: string | null;
  thumbnail_url: string | null;
  opening_hours: any[];
  is_open: boolean;
  verified: boolean;
  verification_status: string;
  source_platform: 'google_business';
  source_label: string;
  attribution_notice: string;
}

export interface SocialCrawlShoppingItem {
  id: string;
  product_id: string;
  gid?: string | null;
  data_docid?: string | null;
  title: string;
  description?: string | null;
  seller: string;
  brand?: string | null;
  price: number | null;
  original_price?: number | null;
  currency: string;
  rating: number | null;
  reviews_count: number | null;
  image_url: string | null;
  thumbnail_url: string | null;
  product_url: string | null;
  availability?: string | null;
  source_platform: 'google_shopping';
  source_label: string;
  attribution_notice: string;
  verification_status: string;
}

export interface SocialCrawlSearchResponse<T = any> {
  success: boolean;
  dry_run: boolean;
  query?: string;
  platform: string;
  total_items: number;
  items: T[];
  next_cursor?: string;
  has_more?: boolean;
  credits_used?: number;
  credits_remaining?: number;
  request_id?: string;
  estimate?: any;
}

export const getSocialCrawlStatus = () => fetchApi<{
  configured: boolean;
  provider: string;
  endpoints: Record<string, string>;
  credit_pricing: Record<string, string>;
  cached_queries_count: number;
  message: string;
}>('/socialcrawl/status');

export const getSocialCrawlCategories = () => fetchApi<{
  total: number;
  categories: Array<{
    id: string;
    name: string;
    domain: string;
    queries: Record<string, string>;
  }>;
}>('/socialcrawl/categories');

export const searchSocialCrawlInstagram = (params: {
  query: string;
  cursor?: string;
  date_posted?: string;
  relevance?: string;
  max_pages?: number;
  dry_run?: boolean;
}) => {
  const q = new URLSearchParams();
  q.append('query', params.query);
  if (params.cursor) q.append('cursor', params.cursor);
  if (params.date_posted) q.append('date_posted', params.date_posted);
  if (params.relevance) q.append('relevance', params.relevance);
  if (params.max_pages) q.append('max_pages', params.max_pages.toString());
  if (params.dry_run) q.append('dry_run', 'true');
  return fetchApi<SocialCrawlSearchResponse<SocialCrawlInspirationItem>>(`/socialcrawl/instagram?${q.toString()}`);
};

export interface SocialCrawlInstagramProfile {
  id: string;
  username: string;
  full_name: string;
  biography: string;
  profile_pic_url?: string;
  external_url?: string;
  profile_url?: string;
  category?: string;
  classification: string;
  is_verified: boolean;
  follower_count?: number;
  following_count?: number;
  media_count?: number;
  is_business?: boolean;
  source_platform: 'instagram';
  source_label: 'Instagram';
}

export const searchSocialCrawlInstagramProfiles = (params: {
  query: string;
  cursor?: string;
  max_pages?: number;
  dry_run?: boolean;
}) => {
  const q = new URLSearchParams();
  q.append('query', params.query);
  if (params.cursor) q.append('cursor', params.cursor);
  if (params.max_pages) q.append('max_pages', params.max_pages.toString());
  if (params.dry_run) q.append('dry_run', 'true');
  return fetchApi<SocialCrawlSearchResponse<SocialCrawlInstagramProfile>>(`/socialcrawl/instagram/profiles?${q.toString()}`);
};

export const getSocialCrawlInstagramProfile = (params: {
  handle: string;
  dry_run?: boolean;
}) => {
  const q = new URLSearchParams();
  q.append('handle', params.handle);
  if (params.dry_run) q.append('dry_run', 'true');
  return fetchApi<{
    success: boolean;
    dry_run: boolean;
    handle: string;
    platform: string;
    data: SocialCrawlInstagramProfile;
    request_id?: string;
  }>(`/socialcrawl/instagram/profile?${q.toString()}`);
};

export const getFocusedInstagramQueries = (term: string, target: 'reels' | 'profiles' | 'all' = 'all') => {
  const q = new URLSearchParams();
  q.append('term', term);
  q.append('target', target);
  return fetchApi<{
    term: string;
    target: string;
    queries: string[];
  }>(`/socialcrawl/instagram/queries?${q.toString()}`);
};

export const searchSocialCrawlYouTube = (params: {
  query: string;
  cursor?: string;
  relevance?: string;
  max_pages?: number;
  dry_run?: boolean;
}) => {
  const q = new URLSearchParams();
  q.append('query', params.query);
  if (params.cursor) q.append('cursor', params.cursor);
  if (params.relevance) q.append('relevance', params.relevance);
  if (params.max_pages) q.append('max_pages', params.max_pages.toString());
  if (params.dry_run) q.append('dry_run', 'true');
  return fetchApi<SocialCrawlSearchResponse<SocialCrawlInspirationItem>>(`/socialcrawl/youtube?${q.toString()}`);
};

export const searchSocialCrawlReddit = (params: {
  query: string;
  cursor?: string;
  relevance?: string;
  max_pages?: number;
  dry_run?: boolean;
}) => {
  const q = new URLSearchParams();
  q.append('query', params.query);
  if (params.cursor) q.append('cursor', params.cursor);
  if (params.relevance) q.append('relevance', params.relevance);
  if (params.max_pages) q.append('max_pages', params.max_pages.toString());
  if (params.dry_run) q.append('dry_run', 'true');
  return fetchApi<SocialCrawlSearchResponse<SocialCrawlInspirationItem>>(`/socialcrawl/reddit?${q.toString()}`);
};

export const searchSocialCrawlTwitter = (params: {
  query: string;
  cursor?: string;
  dry_run?: boolean;
}) => {
  const q = new URLSearchParams();
  q.append('query', params.query);
  if (params.cursor) q.append('cursor', params.cursor);
  if (params.dry_run) q.append('dry_run', 'true');
  return fetchApi<SocialCrawlSearchResponse<SocialCrawlInspirationItem>>(`/socialcrawl/twitter?${q.toString()}`);
};

export const searchSocialCrawlBusinesses = (params: {
  query: string;
  location?: string;
  lat?: number | null;
  lon?: number | null;
  dry_run?: boolean;
}) => {
  const q = new URLSearchParams();
  q.append('query', params.query);
  if (params.location) q.append('location', params.location);
  if (params.lat !== undefined && params.lat !== null) q.append('lat', params.lat.toString());
  if (params.lon !== undefined && params.lon !== null) q.append('lon', params.lon.toString());
  if (params.dry_run) q.append('dry_run', 'true');
  return fetchApi<SocialCrawlSearchResponse<SocialCrawlBusinessItem>>(`/socialcrawl/businesses?${q.toString()}`);
};

export const searchSocialCrawlShopping = (params: {
  query?: string;
  gid?: string;
  product_id?: string;
  country?: string;
  dry_run?: boolean;
}) => {
  const q = new URLSearchParams();
  if (params.query) q.append('query', params.query);
  if (params.gid) q.append('gid', params.gid);
  if (params.product_id) q.append('product_id', params.product_id);
  if (params.country) q.append('country', params.country);
  if (params.dry_run) q.append('dry_run', 'true');
  return fetchApi<SocialCrawlSearchResponse<SocialCrawlShoppingItem>>(`/socialcrawl/shopping?${q.toString()}`);
};

export const searchAllSocialCrawl = (params: {
  query: string;
  sources?: string[];
  location?: string;
  dry_run?: boolean;
}) => {
  const q = new URLSearchParams();
  q.append('query', params.query);
  if (params.sources && params.sources.length > 0) q.append('sources', params.sources.join(','));
  if (params.location) q.append('location', params.location);
  if (params.dry_run) q.append('dry_run', 'true');
  return fetchApi<{
    query: string;
    sources: string[];
    dry_run: boolean;
    results: Record<string, SocialCrawlSearchResponse>;
    errors: Record<string, string>;
  }>(`/socialcrawl/search-all?${q.toString()}`);
};

export const saveSocialCrawlItem = (data: {
  source_platform: string;
  external_id?: string;
  title?: string | null;
  description?: string | null;
  image_url?: string | null;
  video_url?: string | null;
  source_url: string;
  creator_name?: string | null;
  creator_url?: string | null;
  category_slug?: string | null;
  material_tags?: string | null;
  project_collection?: string;
}) => fetchApi<{
  saved: boolean;
  reference_id: number;
  status: string;
  message: string;
}>('/socialcrawl/save', {
  method: 'POST',
  body: JSON.stringify(data),
});

export const getSocialCrawlSuppliers = (params: {
  q: string;
  location?: string;
  lat?: number | null;
  lon?: number | null;
  dry_run?: boolean;
}) => {
  const q = new URLSearchParams();
  q.append('q', params.q);
  if (params.location) q.append('location', params.location);
  if (params.lat !== undefined && params.lat !== null) q.append('lat', params.lat.toString());
  if (params.lon !== undefined && params.lon !== null) q.append('lon', params.lon.toString());
  if (params.dry_run) q.append('dry_run', 'true');
  return fetchApi<{
    query: string;
    location?: string;
    businesses: any[];
    products: any[];
    businesses_count: number;
    products_count: number;
    dry_run: boolean;
  }>(`/sourcing/socialcrawl-suppliers?${q.toString()}`);
};

export interface TaxonomyItem {
  name: string;
  variants?: string[];
  description?: string;
}

export interface SubcategoryObject {
  name: string;
  keywords: string[];
  items?: TaxonomyItem[];
}

export interface KeywordLibraryGroup {
  id: number;
  name: string;
  slug: string;
  icon?: string;
  description?: string;
  supplier_category?: string;
  count: number;
  subcategories: string[];
  subcategory_objects?: SubcategoryObject[];
  keywords: string[];
  sample_keywords?: string[];
}

export interface KeywordSearchResult {
  keyword: string;
  group_id: number;
  group_name: string;
  group_slug: string;
}

export interface CatalogueSubcategorySummary {
  id: number;
  name: string;
  slug: string;
  materials_count: number;
  materials?: Array<{ id: number; name: string; slug: string }>;
}

export interface CatalogueCategorySummary {
  id: number;
  name: string;
  slug: string;
  explorer_category_slug?: string;
  explorer_category_name?: string;
  description?: string;
  subcategories_count: number;
  materials_count: number;
  subcategories: CatalogueSubcategorySummary[];
}

export interface CatalogueTreeResponse {
  total_categories: number;
  total_subcategories: number;
  total_materials: number;
  distinct_materials_count: number;
  categories: CatalogueCategorySummary[];
}

export interface CatalogueMaterialHit {
  id: number;
  material: string;
  slug: string;
  category: string;
  category_slug: string;
  explorer_category_slug?: string;
  subcategory: string;
  subcategory_slug: string;
  source_row_number?: number;
}

export interface CustomKeywordItem {
  id: number;
  keyword: string;
  category_name?: string;
  is_followed: boolean;
}

export const getKeywordLibrary = () => fetchApi<KeywordLibraryGroup[]>('/categories/keywords/library');

export const getUnifiedKeywordExplorer = () =>
  fetchApi<{
    explorer_categories: KeywordLibraryGroup[];
    catalogue_tree: CatalogueTreeResponse;
    custom_keywords: CustomKeywordItem[];
  }>('/categories/keywords/unified');

export const getCatalogueTree = (includeMaterials: boolean = false) =>
  fetchApi<CatalogueTreeResponse>(`/categories/catalogue/tree?include_materials=${includeMaterials ? 'true' : 'false'}`);

export const searchCatalogueMaterials = (params: {
  q?: string;
  category?: string;
  subcategory?: string;
  limit?: number;
  offset?: number;
} = {}) => {
  const qs = new URLSearchParams();
  if (params.q) qs.set('q', params.q);
  if (params.category) qs.set('category', params.category);
  if (params.subcategory) qs.set('subcategory', params.subcategory);
  if (params.limit) qs.set('limit', String(params.limit));
  if (params.offset) qs.set('offset', String(params.offset));
  return fetchApi<{ total: number; limit: number; offset: number; items: CatalogueMaterialHit[] }>(
    `/categories/catalogue/search?${qs.toString()}`
  );
};

export const getCustomKeywords = () => fetchApi<CustomKeywordItem[]>('/categories/keywords/custom');

export const saveCustomKeyword = (keyword: string, category_name?: string) =>
  fetchApi<CustomKeywordItem>('/categories/keywords/custom', {
    method: 'POST',
    body: JSON.stringify({ keyword, category_name, is_followed: true }),
  });

export const deleteCustomKeyword = (id: number) =>
  fetchApi<{ deleted: boolean; id: number }>(`/categories/keywords/custom/${id}`, {
    method: 'DELETE',
  });

export const searchKeywordLibrary = (q: string) =>
  fetchApi<{
    query: string;
    synonyms: string[];
    results: KeywordSearchResult[];
    catalogue_results?: CatalogueMaterialHit[];
    catalogue_total?: number;
  }>(
    `/categories/keywords/search?q=${encodeURIComponent(q)}`
  );

export interface SearchContextLocation {
  lat?: number | null;
  lng?: number | null;
  district?: string | null;
  state?: string | null;
}

export interface SearchContext {
  material_id?: number | null;
  material?: string | null;
  aliases?: string[];
  category?: string | null;
  subcategory?: string | null;
  location?: SearchContextLocation | null;
  source?: string | null;
  page?: number;
}

export const discoverySearch = (params: {
  q: string;
  tab?: string;
  sources?: string;
  page?: number;
  page_size?: number;
  limit?: number;
  category?: string;
  subcategory?: string;
  material?: string;
  city?: string;
  state?: string;
  lat?: number | null;
  lng?: number | null;
  district?: string | null;
  material_id?: number | null;
  aliases?: string[];
  context?: SearchContext;
}) => {
  const qs = new URLSearchParams();
  qs.set('q', params.q);
  if (params.tab) qs.set('tab', params.tab);
  if (params.sources) qs.set('sources', params.sources);
  if (params.page) qs.set('page', String(params.page));
  const resolvedPageSize = params.page_size ?? params.limit;
  if (resolvedPageSize) qs.set('page_size', String(resolvedPageSize));
  if (params.category) qs.set('category', params.category);
  if (params.subcategory) qs.set('subcategory', params.subcategory);
  if (params.material) qs.set('material', params.material);
  if (params.city) qs.set('city', params.city);
  if (params.state) qs.set('state', params.state);
  if (params.district) qs.set('district', params.district);
  if (params.lat !== undefined && params.lat !== null) qs.set('lat', String(params.lat));
  if (params.lng !== undefined && params.lng !== null) qs.set('lon', String(params.lng));
  if (params.material_id) qs.set('material_id', String(params.material_id));
  if (params.aliases && params.aliases.length > 0) qs.set('aliases', params.aliases.join(','));
  return fetchApi<any>(`/discovery/search?${qs.toString()}`);
};

export const getDailyCollectionStatus = () => fetchApi<any>('/admin/daily-collection/status');

export const triggerDailyCollection = (options: { run_all?: boolean; budget_limit?: number } = {}) =>
  fetchApi<any>('/admin/daily-collection/trigger', {
    method: 'POST',
    body: JSON.stringify(options),
  });


