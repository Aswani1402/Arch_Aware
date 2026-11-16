"""
Nivora (Architect AI) — Unified Discovery Schemas & Data Contract
Phase 5B — Stage 1

Defines the normalized discovery response architecture, three independent
classification dimensions, per-source execution metrics, source status reports,
and multi-source aggregation contracts.
"""

from enum import Enum
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator


# ==============================================================================
# 1. ENUMS: SOURCE STATUS & OVERALL STATUS
# ==============================================================================

class SourceStatusEnum(str, Enum):
    """
    Lifecycle status of an individual external discovery source provider.
    """
    NOT_REQUESTED = "NOT_REQUESTED"
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    EMPTY = "EMPTY"
    FAILED = "FAILED"
    RATE_LIMITED = "RATE_LIMITED"
    QUOTA_EXHAUSTED = "QUOTA_EXHAUSTED"
    NOT_CONFIGURED = "NOT_CONFIGURED"
    DISABLED = "DISABLED"


class DiscoveryOverallStatusEnum(str, Enum):
    """
    Consolidated discovery execution status across all queried sources.
    """
    SUCCESS = "SUCCESS"
    PARTIAL_SUCCESS = "PARTIAL_SUCCESS"
    EMPTY = "EMPTY"
    FAILED = "FAILED"
    RATE_LIMITED = "RATE_LIMITED"


class DiscoveryTabEnum(str, Enum):
    """
    The three high-level architectural discovery user journey tabs (+ all).
    """
    ALL = "all"
    INSPIRATION = "inspiration"
    PROJECTS_WORK = "projects_work"
    PRODUCTS_SUPPLIERS = "products_suppliers"


class ProvenanceEnum(str, Enum):
    """
    Data provenance distinguishing persistent curated repository records from live external query results.
    """
    CURATED_ARCHIVE = "CURATED_ARCHIVE"
    LIVE_DISCOVERY = "LIVE_DISCOVERY"


class InspirationRelevanceTierEnum(str, Enum):
    """
    Discrete material relevance tiers independent of media availability or supplier claims.
    """
    TIER_1_EXACT = "EXACT_METADATA_MATCH"
    TIER_2_ALIAS = "VERIFIED_CATALOGUE_ALIAS"
    TIER_3_CONTEXTUAL = "SUPPORTED_CONTEXTUAL_MATCH"
    TIER_4_AMBIGUOUS = "AMBIGUOUS_MATCH"
    TIER_5_REJECTED = "REJECTED_UNRELATED"


class MediaStatusEnum(str, Enum):
    """
    Independent media availability status distinguishing valid visual assets from text discussions or broken links.
    """
    MEDIA_READY = "MEDIA_READY"
    MEDIA_UNUSABLE = "MEDIA_UNUSABLE"
    TEXT_DISCUSSION = "TEXT_DISCUSSION"


# ==============================================================================
# 2. THE THREE INDEPENDENT CLASSIFICATION DIMENSIONS
# ==============================================================================

class ContentTypeEnum(str, Enum):
    """
    Dimension A: Media / Structural Format (Preserves all existing database values).
    """
    ARCHITECTURAL_PROJECT = "architectural_project"
    YOUTUBE_WALKTHROUGH = "youtube_walkthrough"
    ARCHITECTURAL_REEL = "architectural_reel"
    ARCHITECTURAL_DISCUSSION = "architectural_discussion"
    MANUFACTURER_PRODUCT = "manufacturer_product"
    INSTALLATION_DEMO = "installation_demo"
    MATERIAL_SPECIMEN = "material_specimen"
    PRODUCT_CATALOG = "product_catalog"
    SUPPLIER_BUSINESS = "supplier_business"


class DiscoveryClassificationEnum(str, Enum):
    """
    Dimension B: Architectural & Ecosystem Role (Preserves original 17 classifications).
    """
    INSPIRATION = "Inspiration"
    COMPLETED_PROJECT = "Completed Project"
    WORK_IN_PROGRESS = "Work in Progress"
    ARCHITECT_PORTFOLIO = "Architect Portfolio"
    BUILDER_PORTFOLIO = "Builder Portfolio"
    CONTRACTOR_WORK = "Contractor Work"
    INTERIOR_DESIGN_PROJECT = "Interior Design Project"
    PRODUCT = "Product"
    PRODUCT_DEMONSTRATION = "Product Demonstration"
    MANUFACTURER = "Manufacturer"
    SUPPLIER = "Supplier"
    WHOLESALER = "Wholesaler"
    RETAILER = "Retailer"
    SHOWROOM = "Showroom"
    INSTALLATION = "Installation"
    TUTORIAL = "Tutorial"
    DISCUSSION = "Discussion"

    @classmethod
    def from_str_lenient(cls, val: Optional[str]) -> Optional["DiscoveryClassificationEnum"]:
        """
        Normalizes snake_case, lowercase, or irregular spacing to canonical Title Case enum.
        """
        if not val or not str(val).strip():
            return None
        clean = str(val).strip().lower().replace("_", " ")
        mapping = {
            "inspiration": cls.INSPIRATION,
            "completed project": cls.COMPLETED_PROJECT,
            "work in progress": cls.WORK_IN_PROGRESS,
            "architect portfolio": cls.ARCHITECT_PORTFOLIO,
            "builder portfolio": cls.BUILDER_PORTFOLIO,
            "contractor work": cls.CONTRACTOR_WORK,
            "interior design project": cls.INTERIOR_DESIGN_PROJECT,
            "interior design": cls.INTERIOR_DESIGN_PROJECT,
            "product": cls.PRODUCT,
            "product demonstration": cls.PRODUCT_DEMONSTRATION,
            "product demo": cls.PRODUCT_DEMONSTRATION,
            "manufacturer": cls.MANUFACTURER,
            "supplier": cls.SUPPLIER,
            "wholesaler": cls.WHOLESALER,
            "retailer": cls.RETAILER,
            "showroom": cls.SHOWROOM,
            "installation": cls.INSTALLATION,
            "tutorial": cls.TUTORIAL,
            "discussion": cls.DISCUSSION
        }
        return mapping.get(clean)


class MetadataClassificationEnum(str, Enum):
    """
    Dimension C: Taxonomy Metadata Domain (Preserves 17 metadata domain types).
    """
    ARCHITECTURAL_PROJECT = "architectural_project"
    INTERIOR_DESIGN = "interior_design"
    CONSTRUCTION_PROGRESS = "construction_progress"
    DETAIL_DRAWING = "detail_drawing"
    MATERIAL_SPECIFICATION = "material_specification"
    PRODUCT_CATALOG = "product_catalog"
    INSTALLATION_GUIDE = "installation_guide"
    SUPPLIER_PROFILE = "supplier_profile"
    COST_BREAKDOWN = "cost_breakdown"
    STRUCTURAL_ENGINEERING = "structural_engineering"
    MEP_SYSTEM = "mep_system"
    LANDSCAPE_DESIGN = "landscape_design"
    FACADE_DETAIL = "facade_detail"
    SUSTAINABLE_BUILDING = "sustainable_building"
    RENOVATION_BEFORE_AFTER = "renovation_before_after"
    ARTISAN_CRAFT = "artisan_craft"
    SMART_HOME_TECH = "smart_home_tech"

    @classmethod
    def from_str_lenient(cls, val: Optional[str]) -> Optional["MetadataClassificationEnum"]:
        """
        Normalizes space-separated or uppercase strings into canonical snake_case enum.
        """
        if not val or not str(val).strip():
            return None
        clean = str(val).strip().lower().replace(" ", "_").replace("-", "_")
        try:
            return cls(clean)
        except ValueError:
            return None


# ==============================================================================
# 3. SOURCE METRICS & SOURCE STATUS REPORT
# ==============================================================================

class SourceStatusReport(BaseModel):
    """
    Detailed operational status for a single discovery source provider.
    Never exposes API keys, credentials, or internal stack traces.
    """
    source_name: str
    status: SourceStatusEnum = SourceStatusEnum.NOT_REQUESTED
    requested: bool = False
    result_count: int = 0
    unique_result_count: int = 0
    pages_fetched: int = 0
    has_more: bool = False
    next_page_token: Optional[str] = None
    error_code: Optional[str] = None
    error_class: Optional[str] = None
    error_message: Optional[str] = None
    duration_ms: float = 0.0

    model_config = ConfigDict(from_attributes=True)


class SourceExecutionMetrics(BaseModel):
    """
    Execution and accounting metrics for a single discovery source query.
    """
    source_name: str
    requested_result_count: int = 0
    returned_result_count: int = 0
    unique_result_count: int = 0
    duplicate_count: int = 0
    pages_fetched: int = 0
    pagination_availability: bool = False
    request_count: int = 0
    cache_hit: bool = False
    duration_ms: float = 0.0
    status: SourceStatusEnum = SourceStatusEnum.NOT_REQUESTED
    error_code: Optional[str] = None
    error_class: Optional[str] = None
    error_message: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# 4. NORMALIZED DISCOVERY RESULT
# ==============================================================================

class NormalizedDiscoveryResult(BaseModel):
    """
    Single normalized discovery entity across all 7 sources and local database.
    Retains full data provenance, taxonomy links, and 3 independent classification dimensions.
    """
    # Identity
    id: Optional[int] = None
    source: str  # 'pinterest', 'instagram', 'youtube', 'reddit', 'google_shopping', 'google_business', 'curated', 'local_db'
    source_result_id: Optional[str] = None
    original_url: str
    canonical_url: Optional[str] = None

    # Content
    title: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    creator_name: Optional[str] = None
    creator_url: Optional[str] = None
    published_at: Optional[Union[datetime, str]] = None
    retrieved_at: Optional[Union[datetime, str]] = None

    # Classification: The 3 Independent Dimensions
    content_type: Optional[str] = None  # Dimension A
    discovery_classification: Optional[DiscoveryClassificationEnum] = None  # Dimension B
    metadata_classification: Optional[MetadataClassificationEnum] = None  # Dimension C

    # Taxonomy Anchors
    category_id: Optional[int] = None
    category: Optional[str] = None
    subcategory_id: Optional[int] = None
    subcategory: Optional[str] = None
    item: Optional[str] = None
    variant: Optional[str] = None
    matched_keywords: List[str] = Field(default_factory=list)

    # Location & Business Information (Optional; never fabricated)
    location: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    business_category: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None

    # Provenance & Discovery Meta
    source_attribution: Optional[str] = None
    discovery_query: Optional[str] = None
    retrieval_timestamp: Optional[str] = None
    verification_status: str = "UNVERIFIED"  # 'VERIFIED', 'UNVERIFIED', 'POTENTIAL_GOOGLE_PLACE'
    provenance: str = ProvenanceEnum.LIVE_DISCOVERY.value
    inspiration_relevance_tier: Optional[str] = None
    media_status: str = MediaStatusEnum.MEDIA_READY.value
    source_metadata: Optional[Dict[str, Any]] = None
    relevance_score: float = 0.0
    confidence_score: float = 1.0
    relevant_tabs: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

    @field_validator("discovery_classification", mode="before")
    @classmethod
    def validate_discovery_classification(cls, v: Any) -> Optional[DiscoveryClassificationEnum]:
        if v is None or isinstance(v, DiscoveryClassificationEnum):
            return v
        enum_val = DiscoveryClassificationEnum.from_str_lenient(str(v))
        if enum_val is None:
            # If string given does not match the 17 allowed, reject or set None
            raise ValueError(f"Invalid discovery_classification '{v}'. Must be one of the 17 canonical roles.")
        return enum_val

    @field_validator("metadata_classification", mode="before")
    @classmethod
    def validate_metadata_classification(cls, v: Any) -> Optional[MetadataClassificationEnum]:
        if v is None or isinstance(v, MetadataClassificationEnum):
            return v
        enum_val = MetadataClassificationEnum.from_str_lenient(str(v))
        if enum_val is None:
            raise ValueError(f"Invalid metadata_classification '{v}'. Must be one of the 17 metadata domains.")
        return enum_val


# ==============================================================================
# 5. PAGINATION & RESPONSE METADATA
# ==============================================================================

class DiscoveryPagination(BaseModel):
    """
    Pagination metadata for cursor and offset traversal.
    """
    page: int = 1
    page_size: int = 30
    total_results: int = 0
    unique_results: int = 0
    total_pages: Optional[int] = None
    has_more: bool = False
    next_cursor: Optional[str] = None
    per_source_cursors: Dict[str, Optional[str]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# 6. UNIFIED DISCOVERY RESPONSE
# ==============================================================================

class UnifiedDiscoveryResponse(BaseModel):
    """
    Master response schema for Nivora Multi-Source Discovery Engine.
    Guarantees partial success representation, granular source status,
    and tab routing.
    """
    query: str
    normalized_query: str
    selected_taxonomy_context: Optional[Dict[str, Any]] = None
    active_discovery_tab: DiscoveryTabEnum = DiscoveryTabEnum.ALL
    overall_status: DiscoveryOverallStatusEnum = DiscoveryOverallStatusEnum.SUCCESS
    total_results: int = 0
    unique_results: int = 0
    results: List[NormalizedDiscoveryResult] = Field(default_factory=list)
    source_metrics: Dict[str, SourceExecutionMetrics] = Field(default_factory=dict)
    source_statuses: Dict[str, SourceStatusReport] = Field(default_factory=dict)
    pagination: DiscoveryPagination
    warnings: List[str] = Field(default_factory=list)
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    request_id: str
    retrieval_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    model_config = ConfigDict(from_attributes=True)


# ==============================================================================
# 7. TAB ROUTING RULES HELPER
# ==============================================================================

def determine_relevant_discovery_tabs(
    item: NormalizedDiscoveryResult
) -> List[str]:
    """
    Evaluates an item across the three classification dimensions, content type,
    and business data to determine which discovery tab(s) it belongs to.
    A single item can belong to multiple tabs if warranted.
    """
    tabs: List[str] = []

    # 1. Inspiration Tab Rules
    inspiration_roles = {
        DiscoveryClassificationEnum.INSPIRATION,
        DiscoveryClassificationEnum.INTERIOR_DESIGN_PROJECT,
        DiscoveryClassificationEnum.DISCUSSION
    }
    inspiration_content_types = {
        "material_specimen",
        "architectural_reel"
    }
    if (
        item.discovery_classification in inspiration_roles
        or item.content_type in inspiration_content_types
        or item.source in ("pinterest", "curated")
        or (item.image_url and not item.price and not item.phone)
    ):
        tabs.append(DiscoveryTabEnum.INSPIRATION.value)

    # 2. Projects & Work Tab Rules
    projects_work_roles = {
        DiscoveryClassificationEnum.COMPLETED_PROJECT,
        DiscoveryClassificationEnum.WORK_IN_PROGRESS,
        DiscoveryClassificationEnum.ARCHITECT_PORTFOLIO,
        DiscoveryClassificationEnum.BUILDER_PORTFOLIO,
        DiscoveryClassificationEnum.CONTRACTOR_WORK,
        DiscoveryClassificationEnum.INSTALLATION,
        DiscoveryClassificationEnum.TUTORIAL,
        DiscoveryClassificationEnum.DISCUSSION
    }
    projects_work_content_types = {
        "architectural_project",
        "youtube_walkthrough",
        "installation_demo",
        "architectural_discussion"
    }
    if (
        item.discovery_classification in projects_work_roles
        or item.content_type in projects_work_content_types
        or item.source in ("youtube", "reddit")
    ):
        tabs.append(DiscoveryTabEnum.PROJECTS_WORK.value)

    # 3. Products & Suppliers Tab Rules
    products_suppliers_roles = {
        DiscoveryClassificationEnum.PRODUCT,
        DiscoveryClassificationEnum.PRODUCT_DEMONSTRATION,
        DiscoveryClassificationEnum.MANUFACTURER,
        DiscoveryClassificationEnum.SUPPLIER,
        DiscoveryClassificationEnum.WHOLESALER,
        DiscoveryClassificationEnum.RETAILER,
        DiscoveryClassificationEnum.SHOWROOM
    }
    products_suppliers_content_types = {
        "manufacturer_product",
        "product_catalog",
        "supplier_business"
    }
    if (
        item.discovery_classification in products_suppliers_roles
        or item.content_type in products_suppliers_content_types
        or item.source in ("google_shopping", "google_business", "shopping", "suppliers")
        or item.price is not None
        or bool(item.phone or item.address or item.website or item.business_category)
    ):
        tabs.append(DiscoveryTabEnum.PRODUCTS_SUPPLIERS.value)

    # Default fallback: if unclassified, place in inspiration by default
    if not tabs:
        tabs.append(DiscoveryTabEnum.INSPIRATION.value)

    return sorted(list(set(tabs)))


# ==============================================================================
# 7. SEARCH CONTEXT SCHEMA (Stage 4 Contract)
# ==============================================================================

class SearchContextLocation(BaseModel):
    lat: Optional[float] = None
    lng: Optional[float] = None
    district: Optional[str] = None
    state: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class SearchContext(BaseModel):
    material_id: Optional[int] = None
    material: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    subcategory: Optional[str] = None
    location: Optional[SearchContextLocation] = None
    source: Optional[str] = None
    page: int = 1

    model_config = ConfigDict(from_attributes=True)


