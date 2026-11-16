export interface User {
  id: number;
  email: string;
  full_name?: string;
  role: 'user' | 'supplier' | 'admin';
  is_active: boolean;
  created_at: string;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  image_url?: string;
  section_code?: string;
  section_name?: string;
  typical_applications?: string;
  subcategories?: string;
  standards_compliance?: string;
  products_count?: number;
  references_count?: number;
  products?: any[];
  references?: any[];
}

export interface Manufacturer {
  id: number;
  name: string;
  company_name?: string;
  slug: string;
  country: string;
  official_website?: string;
  official_catalog_url?: string;
  official_product_page_url?: string;
  official_video_channel_url?: string;
  description?: string;
  logo_url?: string;
  contact_info?: string;
  verification_status: string;
  last_verified_at?: string;
  source_url?: string;
  unverified_notes?: string;
  products_count?: number;
  created_at: string;
  products?: Product[];
}

export interface SupplierListingBrief {
  supplier_id: number;
  supplier_name: string;
  city: string;
  district?: string;
  state: string;
  distance_km?: number;
  match_type?: string;
  supplier_product_code?: string;
  price?: number;
  currency: string;
  price_unit?: string;
  availability_status: string;
  stock_status?: string;
  stock_confirmed_at?: string;
  available_quantity?: number;
  min_order_quantity?: string;
  delivery_scope: string;
  estimated_lead_time_days?: number;
  phone?: string;
  website?: string;
  google_maps_url?: string;
  verification_status?: string;
  is_potential: boolean;
}

export interface Product {
  id: number;
  name: string;
  slug: string;
  sku_code?: string;
  product_type?: string;
  material_type?: string;
  material_composition?: string;
  finish?: string;
  color?: string;
  intended_use?: string;
  dimensions?: string;
  thickness?: string;
  installation_requirements?: string;
  specs?: string;
  official_product_url?: string;
  official_catalog_url?: string;
  country_of_manufacture?: string;
  image_url?: string;
  data_source?: string;
  verification_status: string;
  last_checked_at?: string;
  manufacturer_id?: number;
  manufacturer_name?: string;
  category_id?: number;
  category_name?: string;
  created_at: string;
  manufacturer?: Manufacturer;
  category?: Category;
  available_suppliers?: SupplierListingBrief[];
  related_references?: any[];
}

export interface SupplierProductLink {
  product_id: number;
  product_name: string;
  material_type?: string;
  match_type?: string;
  price?: number;
  currency: string;
  price_unit?: string;
  availability_status: string;
  stock_status?: string;
  min_order_quantity?: string;
  available_quantity?: number;
  delivery_scope: string;
  estimated_lead_time_days?: number;
  image_url?: string;
}

export interface Supplier {
  id: number;
  name: string;
  slug: string;
  business_type: string;
  contact_person?: string;
  address: string;
  city: string;
  district?: string;
  state: string;
  pin_code?: string;
  country: string;
  latitude?: number;
  longitude?: number;
  phone?: string;
  email?: string;
  whatsapp?: string;
  website?: string;
  google_maps_url?: string;
  google_place_id?: string;
  gstin?: string;
  brands_distributed?: string;
  delivery_areas?: string;
  verification_status: string;
  verification_method?: string;
  verification_notes?: string;
  is_potential: boolean;
  delivery_radius_km: number;
  distance_km?: number;
  last_updated_at?: string;
  created_at: string;
  catalog_products?: SupplierProductLink[];
}

export interface ReferenceProductMatch {
  product_id: number;
  product_name: string;
  manufacturer_name?: string;
  match_type: 'verified_exact' | 'visually_similar' | 'alternative_review' | 'source_unknown';
  match_confidence: number;
  evidence_notes?: string;
  verification_status: string;
  image_url?: string;
}

export interface InspirationMaterial {
  id: number;
  reference_id: number;
  name?: string;
  material_name: string;
  category_id?: number;
  category_slug?: string;
  material_category?: string;
  element_location?: string;
  building_component?: string;
  finish_specification?: string;
  identification_state?: string;
  identification_type?: 'confirmed_product' | 'architect_documented' | 'visually_inferred';
  verification_status?: string;
  confidence_score?: number;
  evidence_notes?: string;
  is_visually_inferred?: boolean;
  source_evidence_url?: string;
  detail_image_url?: string;
  crop_image_url?: string;
  notes?: string;
  product_id?: number;
  matched_product_id?: number;
  compatible_alternatives?: string;
  product?: Product;
  matched_product?: any;
}

export interface Reference {
  id: number;
  title: string;
  slug: string;
  source_platform: 'youtube' | 'reddit' | 'pinterest' | 'instagram' | 'catalog' | 'curated' | 'wikimedia' | 'unsplash' | string;
  source_url: string;
  creator_name?: string;
  creator_url?: string;
  thumbnail_url?: string;
  media_url?: string;
  video_embed_id?: string;
  category_id?: number;
  category_name?: string;
  material_tags?: string;
  location_context?: string;
  country?: string;
  region?: string;
  architectural_style?: string;
  project_type?: string;
  architecture_era?: string;
  architect_name?: string;
  content_type?: 'architectural_project' | 'material_specimen' | 'manufacturer_product' | 'installation_demo' | 'youtube_walkthrough' | 'product_catalog' | string;
  verification_status: string;
  description?: string;
  inspiration_image_url?: string;
  inspiration_source_url?: string;
  manufacturer_product_image_url?: string;
  manufacturer_product_url?: string;
  manufacturer_id?: number;
  manufacturer_name?: string;
  product_match_status?: 'verified_match' | 'probable_match' | 'commercial_specification' | 'unidentified' | string;
  video_duration?: string;
  is_short?: boolean;
  image_attribution?: string;
  source_domain?: string;
  colors_and_finishes?: string;
  retrieval_method?: string;
  content_availability_status?: string;
  provenance?: 'CURATED_ARCHIVE' | 'LIVE_DISCOVERY' | string;
  inspiration_relevance_tier?: string;
  media_status?: 'MEDIA_READY' | 'MEDIA_UNUSABLE' | 'TEXT_DISCUSSION' | string;
  matched_products_count: number;
  created_at: string;
  category?: Category;
  product_matches?: ReferenceProductMatch[];
  materials?: InspirationMaterial[];
  inspiration_materials?: InspirationMaterial[];
}

export interface FeedResponse {
  items: Reference[];
  total: number;
  page: number;
  page_size: number;
  has_more: boolean;
  connector_status?: {
    youtube_configured: boolean;
    total_references: number;
    youtube_count: number;
    curated_count: number;
    quota_exceeded?: boolean;
    last_synced_at?: string;
  };
}

export interface FeedFilters {
  countries: string[];
  regions: string[];
  styles: string[];
  project_types: string[];
  eras: string[];
  categories: Category[];
}

export interface SourcingSupplierResult {
  supplier_id: number;
  supplier_name: string;
  business_type: string;
  address: string;
  city: string;
  district?: string;
  state: string;
  country: string;
  distance_km?: number;
  distance_display?: string;
  geographic_scope: string;
  verification_status: string;
  is_potential: boolean;
  phone?: string;
  whatsapp?: string;
  contact_person?: string;
  email?: string;
  website?: string;
  google_maps_url?: string;
  catalog_url?: string;
  brands_distributed?: string;
  delivery_areas?: string;
  last_confirmed_contact?: string;
  export_availability?: boolean;
  shipping_coverage?: string;
  import_notes?: string;
  match_type?: string;
  match_label?: string;
  match_explanation?: string;
  category_name?: string;
  matched_products: SupplierProductLink[];
}

export interface SourcingTierResult {
  tier_id: number;
  tier_name: string;
  geographic_scope: string;
  description: string;
  suppliers: SourcingSupplierResult[];
}

export interface FallbackLevelResult {
  level: number;
  level_name: string;
  radius_desc: string;
  explanation?: string;
  suppliers: SourcingSupplierResult[];
  searched: boolean;
}

export interface HierarchicalSourcingResponse {
  query?: string;
  user_location: {
    city: string;
    state: string;
    latitude: number;
    longitude: number;
  };
  initial_radius_km: number;
  total_suppliers_found: number;
  levels_traversed: FallbackLevelResult[];
  tiers?: SourcingTierResult[];
  tier1_suppliers?: SourcingSupplierResult[];
  tier2_suppliers?: SourcingSupplierResult[];
  tier3_suppliers?: SourcingSupplierResult[];
  tier4_suppliers?: SourcingSupplierResult[];
  tier5_suppliers?: SourcingSupplierResult[];
  verified_suppliers_count: number;
  potential_suppliers_count: number;
}

export interface QuotationResponse {
  id: number;
  supplier_id: number;
  supplier_name: string;
  quoted_price: number;
  currency: string;
  estimated_delivery_days?: number;
  delivery_terms?: string;
  response_message: string;
  created_at: string;
}

export interface QuotationRequest {
  id: number;
  user_id: number;
  product_id: number;
  product_name: string;
  supplier_id: number;
  supplier_name: string;
  quantity: string;
  dimensions?: string;
  project_location: string;
  city: string;
  state: string;
  pin_code?: string;
  delivery_urgency: string;
  additional_notes?: string;
  status: string;
  created_at: string;
  responses: QuotationResponse[];
}

export interface SavedItem {
  id: number;
  user_id: number;
  item_type: 'reference' | 'product' | 'supplier';
  reference_id?: number;
  product_id?: number;
  supplier_id?: number;
  project_collection: string;
  created_at: string;
  item_data?: any;
}
