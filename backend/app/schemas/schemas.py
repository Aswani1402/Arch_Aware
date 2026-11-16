from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field

try:
    from pydantic import EmailStr
    class _EmailTest(BaseModel):
        e: EmailStr
except Exception:
    EmailStr = str

# ----------------- Auth & User -----------------
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "user"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut

class TokenData(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

# ----------------- Category -----------------
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    section_code: Optional[str] = None
    section_name: Optional[str] = None
    typical_applications: Optional[str] = None
    subcategories: Optional[str] = None
    standards_compliance: Optional[str] = None

class CategoryOut(CategoryBase):
    id: int

    class Config:
        from_attributes = True

class CategoryDetailOut(CategoryOut):
    products_count: int = 0
    references_count: int = 0
    products: List[Any] = []
    references: List[Any] = []

# ----------------- Manufacturer -----------------
class ManufacturerBase(BaseModel):
    name: str
    company_name: Optional[str] = None
    slug: str
    country: str = "India"
    official_website: Optional[str] = None
    official_catalog_url: Optional[str] = None
    official_product_page_url: Optional[str] = None
    official_video_channel_url: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    contact_info: Optional[str] = None
    verification_status: str = "MANUFACTURER_CONFIRMED"
    source_url: Optional[str] = None
    unverified_notes: Optional[str] = None

class ManufacturerCreate(ManufacturerBase):
    pass

class ManufacturerOut(ManufacturerBase):
    id: int
    last_verified_at: Optional[datetime] = None
    created_at: datetime
    products_count: Optional[int] = 0

    class Config:
        from_attributes = True

# ----------------- Product -----------------
class ProductBase(BaseModel):
    name: str
    slug: str
    sku_code: Optional[str] = None
    product_type: Optional[str] = None
    material_type: Optional[str] = None
    material_composition: Optional[str] = None
    finish: Optional[str] = None
    color: Optional[str] = None
    intended_use: Optional[str] = None
    dimensions: Optional[str] = None
    thickness: Optional[str] = None
    installation_requirements: Optional[str] = None
    specs: Optional[str] = None
    official_product_url: Optional[str] = None
    official_catalog_url: Optional[str] = None
    country_of_manufacture: Optional[str] = None
    image_url: Optional[str] = None
    data_source: Optional[str] = "official_catalog"
    verification_status: str = "MANUFACTURER_CONFIRMED"

class ProductCreate(ProductBase):
    manufacturer_id: Optional[int] = None
    category_id: Optional[int] = None

class SupplierListingBrief(BaseModel):
    supplier_id: int
    supplier_name: str
    city: str
    district: Optional[str] = None
    state: str
    distance_km: Optional[float] = None
    match_type: str = "exact_product"
    supplier_product_code: Optional[str] = None
    price: Optional[float] = None
    currency: str = "INR"
    price_unit: str = "piece"
    availability_status: str = "in_stock"
    stock_status: str = "in_stock"
    stock_confirmed_at: Optional[datetime] = None
    available_quantity: Optional[float] = None
    min_order_quantity: Optional[str] = None
    delivery_scope: str = "state"
    estimated_lead_time_days: Optional[int] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    google_maps_url: Optional[str] = None
    verification_status: str = "VERIFIED"
    is_potential: bool = False

    class Config:
        from_attributes = True

class ProductOut(ProductBase):
    id: int
    manufacturer_id: Optional[int] = None
    category_id: Optional[int] = None
    manufacturer_name: Optional[str] = None
    category_name: Optional[str] = None
    last_checked_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class ProductDetailOut(ProductOut):
    manufacturer: Optional[ManufacturerOut] = None
    category: Optional[CategoryOut] = None
    available_suppliers: List[SupplierListingBrief] = []
    related_references: List[Any] = []

# ----------------- Supplier -----------------
class SupplierBase(BaseModel):
    name: str
    slug: str
    business_type: str = "authorized_dealer"
    contact_person: Optional[str] = None
    address: str
    city: str
    district: Optional[str] = None
    state: str
    pin_code: Optional[str] = None
    country: str = "India"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    google_maps_url: Optional[str] = None
    google_place_id: Optional[str] = None
    gstin: Optional[str] = None
    brands_distributed: Optional[str] = None
    delivery_areas: Optional[str] = None
    materials_sold: Optional[str] = None
    verification_status: str = "SUPPLIER_CONFIRMED"
    verification_method: Optional[str] = None
    verification_notes: Optional[str] = None
    is_potential: bool = False
    is_demo: bool = False
    delivery_radius_km: float = 100.0

class SupplierCreate(SupplierBase):
    user_id: Optional[int] = None

class SupplierRegister(BaseModel):
    name: str
    business_type: str = "authorized_dealer"
    contact_person: Optional[str] = None
    address: str
    city: str
    district: Optional[str] = None
    state: str
    pin_code: Optional[str] = None
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: EmailStr
    website: Optional[str] = None
    gstin: Optional[str] = None
    brands_distributed: Optional[str] = None
    delivery_areas: Optional[str] = None
    materials_sold: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    delivery_radius_km: float = 100.0

class SupplierProductLink(BaseModel):
    product_id: int
    product_name: str
    material_type: Optional[str] = None
    match_type: str = "exact_product"
    price: Optional[float] = None
    currency: str = "INR"
    price_unit: str = "piece"
    availability_status: str = "in_stock"
    stock_status: str = "in_stock"
    available_quantity: Optional[float] = None
    min_order_quantity: Optional[str] = None
    delivery_scope: str = "state"
    estimated_lead_time_days: Optional[int] = None
    image_url: Optional[str] = None

class SupplierOut(SupplierBase):
    id: int
    distance_km: Optional[float] = None
    match_type: Optional[str] = "category_match"
    match_label: Optional[str] = "Category Match"
    match_explanation: Optional[str] = None
    category_name: Optional[str] = None
    last_updated_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SupplierDetailOut(SupplierOut):
    catalog_products: List[SupplierProductLink] = []

# ----------------- Inspiration Materials -----------------
class InspirationMaterialOut(BaseModel):
    id: int
    reference_id: int
    name: str
    category_id: Optional[int] = None
    category_slug: Optional[str] = None
    material_category: str
    element_location: str
    identification_type: str = "visually_inferred"  # confirmed_product, architect_documented, visually_inferred
    verification_status: str = "VISUALLY_INFERRED"
    confidence_score: float = 0.85
    detail_image_url: Optional[str] = None
    notes: Optional[str] = None
    product_id: Optional[int] = None
    compatible_alternatives: Optional[str] = None
    product: Optional[ProductOut] = None

    @property
    def material_name(self) -> str:
        return self.name

    class Config:
        from_attributes = True

# ----------------- Architectural Reference & Feed -----------------
class ReferenceProductMatchOut(BaseModel):
    product_id: int
    product_name: str
    manufacturer_name: Optional[str] = None
    match_type: str  # verified_exact, visually_similar, alternative_review, source_unknown
    match_confidence: float
    evidence_notes: Optional[str] = None
    verification_status: str
    image_url: Optional[str] = None

    class Config:
        from_attributes = True

class ReferenceBase(BaseModel):
    title: str
    slug: str
    source_platform: str
    source_url: str
    creator_name: Optional[str] = None
    creator_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    media_url: Optional[str] = None
    video_embed_id: Optional[str] = None
    material_tags: Optional[str] = None
    location_context: Optional[str] = None
    country: str = "India"
    region: Optional[str] = None
    architectural_style: Optional[str] = None
    project_type: str = "Residential"
    architecture_era: str = "Contemporary"
    architect_name: Optional[str] = None
    content_type: str = "architectural_project"
    verification_status: str = "UNVERIFIED"
    description: Optional[str] = None
    inspiration_image_url: Optional[str] = None
    inspiration_source_url: Optional[str] = None
    manufacturer_product_image_url: Optional[str] = None
    manufacturer_product_url: Optional[str] = None
    manufacturer_id: Optional[int] = None
    manufacturer_name: Optional[str] = None
    product_match_status: str = "unidentified"  # verified_match, probable_match, commercial_specification, unidentified
    retrieval_method: Optional[str] = "manual_curation"
    content_availability_status: Optional[str] = "ACTIVE"
    video_duration: Optional[str] = None
    is_short: bool = False
    image_attribution: Optional[str] = None
    source_domain: Optional[str] = None
    colors_and_finishes: Optional[str] = None
    provenance: Optional[str] = "CURATED_ARCHIVE"
    inspiration_relevance_tier: Optional[str] = None
    media_status: Optional[str] = "MEDIA_READY"

class ReferenceCreate(ReferenceBase):
    category_id: Optional[int] = None

class ReferenceOut(ReferenceBase):
    id: int
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    matched_products_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class ReferenceDetailOut(ReferenceOut):
    category: Optional[CategoryOut] = None
    product_matches: List[ReferenceProductMatchOut] = []
    materials: List[InspirationMaterialOut] = []

class FeedResponse(BaseModel):
    items: List[ReferenceOut]
    total: int
    page: int
    page_size: int
    has_more: bool
    connector_status: Optional[dict] = None

class FeedFiltersOut(BaseModel):
    countries: List[str] = []
    regions: List[str] = []
    styles: List[str] = []
    project_types: List[str] = []
    eras: List[str] = []
    categories: List[CategoryOut] = []

# ----------------- Sourcing & Hierarchical Fallback -----------------
class SourcingSearchQuery(BaseModel):
    query: Optional[str] = None
    product_id: Optional[int] = None
    category_slug: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    initial_radius_km: float = 25.0

class SourcingSupplierResult(BaseModel):
    supplier_id: int
    supplier_name: str
    business_type: str
    contact_person: Optional[str] = None
    address: str
    city: str
    district: Optional[str] = None
    state: str
    country: str
    distance_km: Optional[float] = None
    distance_display: Optional[str] = None
    geographic_scope: str  # Local (<25km), Extended (25-50km), Regional (50-100km), State-wide, Neighbouring State, South India, National, International
    verification_status: str
    is_potential: bool
    is_demo: bool = False
    phone: Optional[str] = None
    whatsapp: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    google_maps_url: Optional[str] = None
    catalog_url: Optional[str] = None
    brands_distributed: Optional[str] = None
    delivery_areas: Optional[str] = None
    materials_sold: Optional[str] = None
    last_confirmed_contact: Optional[str] = None
    export_availability: Optional[bool] = None
    shipping_coverage: Optional[str] = None
    import_notes: Optional[str] = None
    match_type: str = "category_match"  # exact_product, category_match, related_supplier, manufacturer, distributor, installer
    match_label: str = "Category Match"
    match_explanation: Optional[str] = None  # e.g. "Pipe supplier — CPVC availability not confirmed"
    category_name: Optional[str] = None
    matched_products: List[SupplierProductLink] = []

class FallbackLevelResult(BaseModel):
    level: int
    level_name: str
    radius_desc: str
    explanation: Optional[str] = None
    suppliers: List[SourcingSupplierResult]
    searched: bool

class SourcingTierResult(BaseModel):
    tier: int
    tier_name: str  # "Local", "Nearby", "South India", "India", "International"
    description: str
    suppliers: List[SourcingSupplierResult]

class HierarchicalSourcingResponse(BaseModel):
    query: Optional[str] = None
    user_location: Dict[str, Any]
    initial_radius_km: float
    total_suppliers_found: int
    levels_traversed: List[FallbackLevelResult]
    tiers: List[SourcingTierResult] = []
    verified_suppliers_count: int
    potential_suppliers_count: int

# ----------------- Quotations -----------------
class QuotationRequestCreate(BaseModel):
    product_id: int
    supplier_id: int
    quantity: str
    dimensions: Optional[str] = None
    project_location: str
    city: str
    state: str
    pin_code: Optional[str] = None
    delivery_urgency: str = "standard"
    additional_notes: Optional[str] = None

class QuotationResponseCreate(BaseModel):
    quoted_price: float
    currency: str = "INR"
    estimated_delivery_days: Optional[int] = None
    delivery_terms: Optional[str] = None
    response_message: str

class QuotationResponseOut(BaseModel):
    id: int
    supplier_id: int
    supplier_name: str
    quoted_price: float
    currency: str
    estimated_delivery_days: Optional[int] = None
    delivery_terms: Optional[str] = None
    response_message: str
    created_at: datetime

    class Config:
        from_attributes = True

class QuotationRequestOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    product_name: str
    supplier_id: int
    supplier_name: str
    quantity: str
    dimensions: Optional[str] = None
    project_location: str
    city: str
    state: str
    pin_code: Optional[str] = None
    delivery_urgency: str
    additional_notes: Optional[str] = None
    status: str
    created_at: datetime
    responses: List[QuotationResponseOut] = []

    class Config:
        from_attributes = True

# ----------------- Saved Items -----------------
class SavedItemCreate(BaseModel):
    item_type: str  # reference, product, supplier
    reference_id: Optional[int] = None
    product_id: Optional[int] = None
    supplier_id: Optional[int] = None
    project_collection: str = "Default Collection"

class SavedItemOut(BaseModel):
    id: int
    user_id: int
    item_type: str
    reference_id: Optional[int] = None
    product_id: Optional[int] = None
    supplier_id: Optional[int] = None
    project_collection: str
    created_at: datetime
    item_data: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

# ----------------- Connectors -----------------
class ConnectorOut(BaseModel):
    id: int
    name: str
    platform: str
    is_active: bool
    sync_frequency_minutes: int
    last_synced_at: Optional[datetime] = None
    status: str
    total_items_fetched: int

    class Config:
        from_attributes = True

# ----------------- AI Material Detection (Feature 7) -----------------
class DetectedMaterialItem(BaseModel):
    name: str
    qualified_label: str
    category: str
    confidence: float
    confidence_category: str  # 'High', 'Moderate', 'Inferred'
    is_confirmed: bool  # False for AI-inferred, True for source-confirmed
    evidence: str
    uncertainty_note: Optional[str] = None
    is_code: Optional[str] = None

class MaterialDetectionRequest(BaseModel):
    user_corrections: Optional[List[Dict[str, Any]]] = None

class MaterialDetectionResponse(BaseModel):
    reference_id: int
    media_analyzed_url: str
    media_type: str  # 'image' or 'video_frame'
    source_confirmed_materials: List[DetectedMaterialItem] = []
    ai_inferred_materials: List[DetectedMaterialItem] = []
    uncertainty_notes: List[str] = []
    disclaimer: str
    cached: bool = False


# ----------------- Unified Discovery (Phase 5B) -----------------
from app.schemas.discovery import (
    SourceStatusEnum,
    DiscoveryOverallStatusEnum,
    DiscoveryTabEnum,
    ContentTypeEnum,
    DiscoveryClassificationEnum,
    MetadataClassificationEnum,
    SourceStatusReport,
    SourceExecutionMetrics,
    NormalizedDiscoveryResult,
    DiscoveryPagination,
    UnifiedDiscoveryResponse,
    determine_relevant_discovery_tabs,
)

