from datetime import datetime, timezone
import json
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum, UniqueConstraint
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="user")  # 'user', 'supplier', 'admin'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    saved_items = relationship("SavedItem", back_populates="user", cascade="all, delete-orphan")
    quotation_requests = relationship("QuotationRequest", back_populates="user")
    managed_suppliers = relationship("Supplier", back_populates="owner")


class Manufacturer(Base):
    __tablename__ = "manufacturers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    company_name = Column(String(255), nullable=True)  # Legal company entity name
    slug = Column(String(255), unique=True, index=True, nullable=False)
    country = Column(String(100), default="India", index=True)
    official_website = Column(String(500), nullable=True)
    official_catalog_url = Column(String(500), nullable=True)
    official_product_page_url = Column(String(500), nullable=True)
    official_video_channel_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    logo_url = Column(String(500), nullable=True)
    contact_info = Column(Text, nullable=True)
    verification_status = Column(String(50), default="MANUFACTURER_CONFIRMED")
    last_verified_at = Column(DateTime, default=utcnow)
    source_url = Column(String(500), nullable=True)
    unverified_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    products = relationship("Product", back_populates="manufacturer")


class MaterialCategory(Base):
    __tablename__ = "material_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    section_code = Column(String(10), nullable=True, index=True)  # 'A' through 'N'
    section_name = Column(String(150), nullable=True)
    typical_applications = Column(Text, nullable=True)
    subcategories = Column(Text, nullable=True)  # Comma-separated or JSON string of subcategories
    standards_compliance = Column(Text, nullable=True)

    # Relationships
    products = relationship("Product", back_populates="category")
    references = relationship("ArchitecturalReference", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"), nullable=True, index=True)
    category_id = Column(Integer, ForeignKey("material_categories.id"), nullable=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    sku_code = Column(String(100), nullable=True, index=True)
    product_type = Column(String(100), nullable=True, index=True)
    material_type = Column(String(150), index=True, nullable=True)
    material_composition = Column(Text, nullable=True)
    finish = Column(String(100), nullable=True)
    color = Column(String(100), nullable=True)
    intended_use = Column(String(255), nullable=True)  # Exterior, Interior, Landscaping, Wet Areas
    dimensions = Column(String(100), nullable=True)
    thickness = Column(String(50), nullable=True)
    installation_requirements = Column(Text, nullable=True)
    specs = Column(Text, nullable=True)  # JSON or descriptive technical specs
    official_product_url = Column(String(500), nullable=True)
    official_catalog_url = Column(String(500), nullable=True)
    country_of_manufacture = Column(String(100), nullable=True)
    image_url = Column(String(500), nullable=True)
    data_source = Column(String(100), default="official_catalog")
    verification_status = Column(String(50), default="MANUFACTURER_CONFIRMED", index=True)
    last_checked_at = Column(DateTime, default=utcnow)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    manufacturer = relationship("Manufacturer", back_populates="products")
    category = relationship("MaterialCategory", back_populates="products")
    supplier_links = relationship("SupplierProduct", back_populates="product", cascade="all, delete-orphan")
    reference_matches = relationship("ReferenceProductMatch", back_populates="product")
    quotation_requests = relationship("QuotationRequest", back_populates="product")


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    business_type = Column(String(100), default="authorized_dealer")  # authorized_dealer, retail_supplier, distributor, importer, custom_fabricator
    contact_person = Column(String(255), nullable=True)
    address = Column(String(500), nullable=False)
    city = Column(String(100), index=True, nullable=False)
    district = Column(String(100), index=True, nullable=True)
    state = Column(String(100), index=True, nullable=False)
    pin_code = Column(String(20), index=True, nullable=True)
    country = Column(String(100), default="India", index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    phone = Column(String(50), nullable=True)
    whatsapp = Column(String(50), nullable=True)
    email = Column(String(255), nullable=True)
    website = Column(String(500), nullable=True)
    google_maps_url = Column(String(500), nullable=True)
    google_place_id = Column(String(255), nullable=True)
    gstin = Column(String(50), nullable=True)
    brands_distributed = Column(Text, nullable=True)
    delivery_areas = Column(Text, nullable=True)
    instagram_url = Column(String(500), nullable=True)
    materials_sold = Column(Text, nullable=True)
    verification_status = Column(String(50), default="SUPPLIER_CONFIRMED", index=True)  # VERIFIED, PENDING_REVIEW, REJECTED, SUSPENDED, EXPIRED, POTENTIAL_GOOGLE_PLACE
    verification_method = Column(String(100), nullable=True)
    verification_notes = Column(Text, nullable=True)
    is_potential = Column(Boolean, default=False)
    is_demo = Column(Boolean, default=False, index=True)
    delivery_radius_km = Column(Float, default=100.0)
    last_updated_at = Column(DateTime, default=utcnow)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    owner = relationship("User", back_populates="managed_suppliers")
    product_links = relationship("SupplierProduct", back_populates="supplier", cascade="all, delete-orphan")
    material_evidence = relationship("SupplierMaterialEvidence", back_populates="supplier", cascade="all, delete-orphan")
    quotation_requests = relationship("QuotationRequest", back_populates="supplier")
    quotation_responses = relationship("QuotationResponse", back_populates="supplier")


class SupplierProduct(Base):
    __tablename__ = "supplier_products"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    match_type = Column(String(50), default="exact_product")  # exact_product, verified_equivalent, similar_alternative, unverified
    supplier_product_code = Column(String(100), nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String(10), default="INR")
    price_unit = Column(String(50), default="piece")  # piece, box, sqft, sqm, tonne, liter, drum
    availability_status = Column(String(50), default="in_stock")  # in_stock, pre_order, contact_to_confirm, discontinued
    stock_status = Column(String(50), default="in_stock")  # in_stock, available_to_order, made_to_order, out_of_stock, unknown
    stock_confirmed_at = Column(DateTime, default=utcnow)
    available_quantity = Column(Float, nullable=True)
    min_order_quantity = Column(String(100), nullable=True)
    delivery_scope = Column(String(50), default="state")  # local, state, south_india, india_wide, international
    estimated_lead_time_days = Column(Integer, nullable=True)
    listing_url = Column(String(500), nullable=True)
    verification_status = Column(String(50), default="VERIFIED")
    last_confirmed_date = Column(DateTime, default=utcnow)
    last_updated_at = Column(DateTime, default=utcnow)
    notes = Column(Text, nullable=True)

    # Relationships
    supplier = relationship("Supplier", back_populates="product_links")
    product = relationship("Product", back_populates="supplier_links")


class SupplierMaterialEvidence(Base):
    """
    Stage 7 Additive Evidence Table:
    Tracks verified material supply evidence per supplier with source text, provenance, and confidence strength.
    """
    __tablename__ = "supplier_material_evidence"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("catalogue_materials.id"), nullable=True, index=True)
    evidence_type = Column(String(50), nullable=False)  # supplier_declared, product_list, listing_text, website, manual_review
    evidence_text = Column(Text, nullable=False)
    source_url = Column(String(500), nullable=True)
    checked_at = Column(DateTime, default=utcnow)
    strength = Column(Float, default=1.0)  # 0.0 to 1.0 confidence strength

    # Relationships
    supplier = relationship("Supplier", back_populates="material_evidence")
    material = relationship("CatalogueMaterial")



class ArchitecturalReference(Base):
    __tablename__ = "architectural_references"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    source_platform = Column(String(50), index=True, nullable=False)  # youtube, reddit, pinterest, instagram, catalog, curated
    source_url = Column(String(1000), nullable=False)
    creator_name = Column(String(255), nullable=True)
    creator_url = Column(String(500), nullable=True)
    thumbnail_url = Column(String(1000), nullable=True)
    media_url = Column(String(1000), nullable=True)
    video_embed_id = Column(String(100), nullable=True)  # YouTube Video ID
    category_id = Column(Integer, ForeignKey("material_categories.id"), nullable=True, index=True)
    material_tags = Column(Text, nullable=True)  # Comma-separated or JSON string
    location_context = Column(String(255), nullable=True)  # e.g. "Kyoto, Japan" or "Alappuzha, Kerala"
    country = Column(String(100), default="India", index=True)
    region = Column(String(100), nullable=True, index=True)
    architectural_style = Column(String(100), nullable=True, index=True)
    project_type = Column(String(100), default="Residential", index=True)
    architecture_era = Column(String(100), default="Contemporary", index=True)
    architect_name = Column(String(255), nullable=True)
    content_type = Column(String(50), default="architectural_project", index=True)  # architectural_project, material_specimen, manufacturer_product, installation_demo, youtube_walkthrough, product_catalog
    verification_status = Column(String(50), default="UNVERIFIED", index=True)
    description = Column(Text, nullable=True)
    retrieval_method = Column(String(50), default="manual_curation")  # official_channel, permitted_embed, manual_curation, api_sync
    content_availability_status = Column(String(50), default="ACTIVE")  # ACTIVE, FLAGGED_FOR_REVIEW, BROKEN_LINK
    inspiration_image_url = Column(String(1000), nullable=True)  # verified architectural project or installation image
    inspiration_source_url = Column(String(1000), nullable=True)  # original source page or authorized media link
    manufacturer_product_image_url = Column(String(1000), nullable=True)  # verified image specifically representing the commercial product
    manufacturer_product_url = Column(String(1000), nullable=True)  # original manufacturer product or catalog URL
    manufacturer_id = Column(Integer, ForeignKey("manufacturers.id"), nullable=True, index=True)
    product_match_status = Column(String(50), default="unidentified", index=True)  # verified_match, probable_match, commercial_specification, unidentified
    video_duration = Column(String(50), nullable=True)  # Formatted duration e.g. "0:30", "14:20"
    is_short = Column(Boolean, default=False)  # True for YouTube Shorts & vertical reels
    image_attribution = Column(String(500), nullable=True)  # Photographer / Source / License
    source_domain = Column(String(100), nullable=True)  # youtube.com, commons.wikimedia.org, unsplash.com, etc.
    colors_and_finishes = Column(String(255), nullable=True)  # Colors, texture, and finish specifications
    external_source_id = Column(String(255), nullable=True, index=True)
    search_keyword = Column(String(255), nullable=True, index=True)
    date_collected = Column(String(50), nullable=True, index=True)
    last_checked_at = Column(DateTime, default=utcnow)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    category = relationship("MaterialCategory", back_populates="references")
    manufacturer = relationship("Manufacturer")
    product_matches = relationship("ReferenceProductMatch", back_populates="reference", cascade="all, delete-orphan")
    materials = relationship("InspirationMaterial", back_populates="reference", cascade="all, delete-orphan", order_by="InspirationMaterial.id")


class InspirationMaterial(Base):
    __tablename__ = "inspiration_materials"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(Integer, ForeignKey("architectural_references.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("material_categories.id"), nullable=True, index=True)
    category_slug = Column(String(100), nullable=True, index=True)
    material_category = Column(String(100), nullable=False)
    element_location = Column(String(255), nullable=False)
    identification_type = Column(String(50), default="visually_inferred")  # confirmed_product, architect_documented, visually_inferred
    verification_status = Column(String(50), default="VISUALLY_INFERRED")
    confidence_score = Column(Float, default=0.85)
    detail_image_url = Column(String(1000), nullable=True)
    notes = Column(Text, nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True, index=True)
    compatible_alternatives = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    reference = relationship("ArchitecturalReference", back_populates="materials")
    category = relationship("MaterialCategory")
    product = relationship("Product")


class ReferenceProductMatch(Base):
    __tablename__ = "reference_product_matches"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(Integer, ForeignKey("architectural_references.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    match_type = Column(String(50), default="visually_similar")  # verified_exact, visually_similar, alternative_review, source_unknown
    match_confidence = Column(Float, default=0.85)
    evidence_notes = Column(Text, nullable=True)
    verification_status = Column(String(50), default="VERIFIED")

    # Relationships
    reference = relationship("ArchitecturalReference", back_populates="product_matches")
    product = relationship("Product", back_populates="reference_matches")


class QuotationRequest(Base):
    __tablename__ = "quotation_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False, index=True)
    quantity = Column(String(100), nullable=False)
    dimensions = Column(String(100), nullable=True)
    project_location = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    pin_code = Column(String(20), nullable=True)
    delivery_urgency = Column(String(50), default="standard")  # immediate, standard, flexible
    additional_notes = Column(Text, nullable=True)
    status = Column(String(50), default="submitted")  # submitted, under_review, quoted, declined
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    user = relationship("User", back_populates="quotation_requests")
    product = relationship("Product", back_populates="quotation_requests")
    supplier = relationship("Supplier", back_populates="quotation_requests")
    responses = relationship("QuotationResponse", back_populates="quotation_request", cascade="all, delete-orphan")


class QuotationResponse(Base):
    __tablename__ = "quotation_responses"

    id = Column(Integer, primary_key=True, index=True)
    quotation_request_id = Column(Integer, ForeignKey("quotation_requests.id"), nullable=False, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    quoted_price = Column(Float, nullable=False)
    currency = Column(String(10), default="INR")
    estimated_delivery_days = Column(Integer, nullable=True)
    delivery_terms = Column(Text, nullable=True)
    response_message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    quotation_request = relationship("QuotationRequest", back_populates="responses")
    supplier = relationship("Supplier", back_populates="quotation_responses")


class SavedItem(Base):
    __tablename__ = "saved_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    item_type = Column(String(50), nullable=False)  # reference, product, supplier
    reference_id = Column(Integer, ForeignKey("architectural_references.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    project_collection = Column(String(100), default="Default Collection")
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    user = relationship("User", back_populates="saved_items")


class SourceConnector(Base):
    __tablename__ = "source_connectors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    platform = Column(String(50), unique=True, nullable=False)  # youtube, reddit, pinterest, instagram, catalog
    is_active = Column(Boolean, default=True)
    sync_frequency_minutes = Column(Integer, default=60)
    last_synced_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="IDLE")  # IDLE, SYNCING, ERROR
    total_items_fetched = Column(Integer, default=0)
    config_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    logs = relationship("SourceSyncLog", back_populates="connector", cascade="all, delete-orphan")


class SourceSyncLog(Base):
    __tablename__ = "source_sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    connector_id = Column(Integer, ForeignKey("source_connectors.id"), nullable=False, index=True)
    status = Column(String(50), nullable=False)  # SUCCESS, FAILED, DEMO_MODE
    items_ingested = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utcnow)

    # Relationships
    connector = relationship("SourceConnector", back_populates="logs")


class DailyCollectionRecord(Base):
    __tablename__ = "daily_collection_records"

    id = Column(Integer, primary_key=True, index=True)
    collection_date = Column(String(50), index=True, nullable=False)  # YYYY-MM-DD in Asia/Kolkata
    source = Column(String(50), index=True, nullable=False)  # instagram, youtube, reddit, google_business, google_shopping, pinterest
    category = Column(String(100), index=True, nullable=True)
    keyword = Column(String(255), index=True, nullable=False)
    requested_quantity = Column(Integer, default=50)
    actual_quantity = Column(Integer, default=0)
    status = Column(String(50), default="Pending", index=True)  # Pending, Running, Completed, Partially completed, Failed
    error_details = Column(Text, nullable=True)
    completion_timestamp = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=utcnow)


class CatalogueCategory(Base):
    __tablename__ = "catalogue_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, index=True, nullable=False)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    explorer_category_slug = Column(String(150), nullable=True, index=True)
    explorer_category_name = Column(String(150), nullable=True)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=utcnow)

    subcategories = relationship(
        "CatalogueSubcategory",
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="CatalogueSubcategory.id",
    )
    materials = relationship(
        "CatalogueMaterial",
        back_populates="category",
        cascade="all, delete-orphan",
    )


class CatalogueSubcategory(Base):
    __tablename__ = "catalogue_subcategories"
    __table_args__ = (
        UniqueConstraint("category_id", "name", name="uq_catalogue_subcat_cat_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("catalogue_categories.id"), nullable=False, index=True)
    name = Column(String(200), index=True, nullable=False)
    slug = Column(String(200), index=True, nullable=False)
    category_subcategory_key = Column(String(350), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=utcnow)

    category = relationship("CatalogueCategory", back_populates="subcategories")
    materials = relationship(
        "CatalogueMaterial",
        back_populates="subcategory",
        cascade="all, delete-orphan",
        order_by="CatalogueMaterial.id",
    )


class CatalogueMaterial(Base):
    __tablename__ = "catalogue_materials"
    __table_args__ = (
        UniqueConstraint("subcategory_id", "name", name="uq_catalogue_material_subcat_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("catalogue_categories.id"), nullable=False, index=True)
    subcategory_id = Column(Integer, ForeignKey("catalogue_subcategories.id"), nullable=False, index=True)
    name = Column(String(255), index=True, nullable=False)
    slug = Column(String(255), index=True, nullable=False)
    normalized_name = Column(String(255), index=True, nullable=False)
    source_row_number = Column(Integer, nullable=True)
    source_dataset = Column(
        String(255),
        default="Construction_Materials_Products_Machinery_Catalogue_Clean(2).csv",
    )
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    category = relationship("CatalogueCategory", back_populates="materials")
    subcategory = relationship("CatalogueSubcategory", back_populates="materials")


class CatalogueImportRun(Base):
    __tablename__ = "catalogue_import_runs"

    id = Column(Integer, primary_key=True, index=True)
    source_filename = Column(String(255), nullable=False)
    file_sha256 = Column(String(64), index=True, nullable=False)
    total_csv_rows = Column(Integer, default=0)
    inserted_rows = Column(Integer, default=0)
    updated_rows = Column(Integer, default=0)
    skipped_rows = Column(Integer, default=0)
    categories_count = Column(Integer, default=0)
    subcategories_count = Column(Integer, default=0)
    distinct_materials_count = Column(Integer, default=0)
    status = Column(String(50), default="COMPLETED")
    notes = Column(Text, nullable=True)
    imported_at = Column(DateTime, default=utcnow)


class CustomKeyword(Base):
    __tablename__ = "custom_keywords"

    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(200), unique=True, index=True, nullable=False)
    category_name = Column(String(150), nullable=True)
    is_followed = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)


