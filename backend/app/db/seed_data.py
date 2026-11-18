from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.models import (
    User,
    Manufacturer,
    MaterialCategory,
    Product,
    Supplier,
    SupplierProduct,
    ArchitecturalReference,
    ReferenceProductMatch,
    InspirationMaterial,
    SourceConnector,
    SourceSyncLog,
    SavedItem,
    QuotationRequest
)

def utcnow():
    return datetime.now(timezone.utc)

def ensure_nagercoil_and_taxonomy(db: Session):
    print("[Seed] Ensuring Nagercoil local suppliers, precast/steel/cement taxonomy, and content types...")
    # 1. Update existing references content_type if missing or null
    for r in db.query(ArchitecturalReference).all():
        if not r.content_type:
            if r.source_platform == "youtube":
                r.content_type = "youtube_walkthrough"
            else:
                r.content_type = "architectural_project"
    db.flush()

    # 2. Add new categories if missing
    new_cats_data = [
        ("Cement, Binders & Concrete", "cement-concrete", "Ordinary Portland cement (OPC 53/43), Portland Pozzolana Cement (PPC), ready-mix concrete, concrete admixtures, non-shrink grouts, repair compounds.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "A", "Structural & Construction Materials", "Foundations, columns, slabs, structural casting, repair grouting", "Ordinary Portland cement, Portland pozzolana cement, ready-mix concrete, concrete admixtures, non-shrink grouts", "IS 12269, IS 1489, IS 456"),
        ("Drainage Slabs & Precast Concrete", "drainage-precast", "Heavy-duty precast concrete drainage cover slabs, RCC manhole covers, linear U-drains, inspection chambers, box culverts, and kerbs.", "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80", "E", "Drainage & Precast Concrete Products", "Stormwater drainage, pathway slabs, driveway covers, road kerbs, municipal culverts", "Precast concrete slabs, RCC drain covers, manhole covers, precast U-drains, box culverts, kerbs", "IS 12592, IS 456, EN 124"),
        ("Structural Steel & Reinforcement", "structural-steel", "High-ductility TMT reinforcement bars (Fe 550D/500D), structural steel beams, MS channels, angles, and hollow sections.", "https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=800&q=80", "C", "Structural Metal & Reinforcement", "Reinforced concrete beams, seismic foundations, roof trusses, structural frames", "TMT reinforcement bars, structural steel sections, MS angles, channels, hollow structural tubes, tie wires", "IS 1786, IS 2062, IS 808"),
    ]
    for name, slug, desc, img, sc, sn, apps, subs, stds in new_cats_data:
        existing = db.query(MaterialCategory).filter_by(slug=slug).first()
        if not existing:
            db.add(MaterialCategory(
                name=name, slug=slug, description=desc, image_url=img,
                section_code=sc, section_name=sn, typical_applications=apps,
                subcategories=subs, standards_compliance=stds
            ))
    db.flush()

    cat_map = {c.slug: c for c in db.query(MaterialCategory).all()}

    # 3. Add new manufacturers if missing
    mfg_data = [
        ("Tata Steel", "Tata Steel Limited", "tata-steel", "India", "https://www.tatasteel.com", "https://www.tatatiscon.co.in", "https://www.tatatiscon.co.in/products/tata-tiscon-550d", "https://www.youtube.com/@TataSteelLtd", "https://www.tatatiscon.co.in", "India's leading steel manufacturer offering GreenPro-certified Tata Tiscon 550D super-ductile rebars and precision structural steel sections.", "https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=200&q=80", "1800-345-8282, tisconhelp@tatasteel.com, Bombay House, 24 Homi Mody Street, Mumbai 400001"),
        ("UltraTech Cement", "UltraTech Cement Limited", "ultratech-cement", "India", "https://www.ultratechcement.com", "https://www.ultratechcement.com/products", "https://www.ultratechcement.com/products/ultratech-cement", "https://www.youtube.com/@UltraTechCementOfficial", "https://www.ultratechcement.com", "The Engineer's Choice - India's largest cement manufacturer producing BIS-certified OPC 53, Super PPC, and specialized waterproofing micro-concrete.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=200&q=80", "1800-210-3311, care@ultratechcement.com, Ahura Centre, Mahakali Caves Road, Andheri (E), Mumbai 400093"),
        ("Supreme Industries", "The Supreme Industries Limited", "supreme-industries", "India", "https://www.supreme.co.in", "https://www.supreme.co.in/plastic-piping-system", "https://www.supreme.co.in/cpvc-fire-sprinkler-pipes", "https://www.youtube.com/@SupremeIndustriesLtd", "https://www.supreme.co.in", "Pioneers in plastic piping systems, providing Lifeline CPVC pressure systems, Nu-Drain underground drainage, and inspection chambers.", "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=200&q=80", "1800-102-4706, pvc-pipes@supreme.co.in, Solitaire Corporate Park, Andheri-Ghatkopar Link Road, Mumbai 400093"),
        ("Kanyakumari Precast & Concrete Works", "Kanyakumari Precast Works Pvt Ltd", "kanyakumari-precast", "India", "https://kanyakumariprecast.com", "https://kanyakumariprecast.com/catalog", "https://kanyakumariprecast.com/products/heavy-duty-slabs", None, "https://kanyakumariprecast.com", "Specialized regional manufacturer of M35 heavy-duty precast concrete drainage cover slabs, stormwater U-drains, and RCC culvert systems engineered for coastal rainfall.", "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=200&q=80", "+91 4652 241288, info@kanyakumariprecast.com, Industrial Estate, Konam, Nagercoil 629004"),
        ("Arteluce Architectural Lighting", "Arteluce Lighting & Glass Works", "arteluce-lighting", "India", "https://arteluce.in", "https://arteluce.in/chandeliers-catalog", "https://arteluce.in/products/grand-murano-chandelier", None, "https://arteluce.in", "Artisanal architectural illumination studio specializing in grand Murano chandeliers, brass pendant lighting, and trimless architectural downlights.", "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=200&q=80", "+91 44 2829 4433, studio@arteluce.in, Nungambakkam High Road, Chennai 600034"),
    ]
    for name, cname, slug, country, web, cat_url, prod_url, vid_url, src_url, desc, logo, contact in mfg_data:
        mfg = db.query(Manufacturer).filter_by(slug=slug).first()
        if not mfg:
            db.add(Manufacturer(
                name=name, company_name=cname, slug=slug, country=country,
                official_website=web, official_catalog_url=cat_url, official_product_page_url=prod_url,
                official_video_channel_url=vid_url, source_url=src_url, description=desc,
                logo_url=logo, contact_info=contact, verification_status="VERIFIED", last_verified_at=utcnow()
            ))
    db.flush()

    mfg_map = {m.slug: m for m in db.query(Manufacturer).all()}

    # 4. Add new products
    prods_data = [
        ("Tata Tiscon 550D Super Ductile TMT Rebar (12mm/16mm)", "tata-tiscon-550d-tmt", "mfg:tata-steel", "structural-steel", "Yield Strength: 550 N/mm2, Min Elongation: 14.5%, Fe 550D grade, GreenPro certified earthquake resistant rebar.", "MT", "₹64,000 - ₹68,000 / MT", "https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=800&q=80", "https://www.tatatiscon.co.in/products/tata-tiscon-550d", "VERIFIED"),
        ("UltraTech OPC 53 Grade High Performance Cement", "ultratech-opc-53-cement", "mfg:ultratech-cement", "cement-concrete", "28-day Compressive Strength > 53 MPa, Low Heat of Hydration, 50kg HDPE moisture-barrier bag, IS 12269 certified.", "Bag (50 kg)", "₹390 - ₹430 / bag", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "https://www.ultratechcement.com/products/ultratech-cement", "VERIFIED"),
        ("Supreme Lifeline CPVC Water Supply Pipe System (SDR 11)", "supreme-lifeline-cpvc-pipes", "mfg:supreme-industries", "plumbing-piping", "Operating temperature up to 93°C, NSF-certified raw material, ASTM D2846 compliant, SDR 11 Class 1 pressure rating.", "Length (3m/5m)", "₹280 - ₹950 / length", "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80", "https://www.supreme.co.in/cpvc-fire-sprinkler-pipes", "VERIFIED"),
        ("KPC M35 Precast Heavy Duty Reinforced Drainage Cover Slab (600x450x75mm)", "kpc-m35-precast-drainage-slab", "mfg:kanyakumari-precast", "drainage-precast", "M35 Grade Concrete with 8mm TMT reinforcement cage, wheel load rated up to 12.5 MT (Class B125), non-slip textured finish.", "Piece", "₹450 - ₹620 / piece", "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80", "https://kanyakumariprecast.com/products/heavy-duty-slabs", "VERIFIED"),
        ("KPC Precast Concrete Stormwater U-Drain Channel (300x300mm)", "kpc-precast-u-drain-channel", "mfg:kanyakumari-precast", "drainage-precast", "M30 Grade vibrated concrete, tongue-and-groove interlocking joint, high hydraulic flow coefficient for monsoon surface runoff.", "Meter", "₹750 - ₹980 / meter", "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80", "https://kanyakumariprecast.com/products/u-drain", "VERIFIED"),
        ("Chettinad Master-Crafted Teakwood Carved Entrance Door", "chettinad-carved-teak-door", "mfg:malabar-vernacular", "doors-and-windows", "100% Seasoned First-Class Malabar Teak, 45mm solid core thickness, hand-carved floral & geometric motifs, brass antique hardware.", "Set", "₹75,000 - ₹145,000 / unit", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "https://heritageteakdoors.in/chettinad-doors", "VERIFIED"),
        ("Grand Murano Brass Chandelier for Double-Height Spaces", "grand-murano-brass-chandelier", "mfg:arteluce-lighting", "lighting", "Hand-blown Venetian glass elements, satin brushed brass framework, 18-light E14/warm dimmable 2700K, 1200mm diameter x 1800mm drop.", "Piece", "₹85,000 - ₹195,000 / unit", "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80", "https://arteluce.in/products/grand-murano-chandelier", "VERIFIED"),
        ("Prime AAC Lightweight Autoclaved Aerated Blocks (600x200x150mm)", "prime-aac-blocks-150mm", "mfg:wienerberger", "bricks-and-blocks", "Dry Density: 550-650 kg/m3, Compressive Strength: 3.5-4.0 N/mm2, Thermal Conductivity: 0.16 W/mK, IS 2185 Part 3.", "Cubic Meter (m3)", "₹3,200 - ₹3,600 / m3", "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80", "https://primeaac.in/blocks", "VERIFIED"),
    ]
    for name, slug, mfg_ref, cat_slug, specs, unit, price, img, url, ver in prods_data:
        prod = db.query(Product).filter_by(slug=slug).first()
        if not prod:
            mfg_key = mfg_ref.replace("mfg:", "")
            mfg_obj = mfg_map.get(mfg_key)
            cat_obj = cat_map.get(cat_slug)
            db.add(Product(
                name=name, slug=slug,
                manufacturer_id=mfg_obj.id if mfg_obj else None,
                category_id=cat_obj.id if cat_obj else None,
                specs=specs,
                dimensions=unit,
                image_url=img,
                official_product_url=url,
                verification_status=ver,
                last_checked_at=utcnow()
            ))
    db.flush()

    prod_map = {p.slug: p for p in db.query(Product).all()}

    # 5. Add verified Nagercoil & Kanyakumari District suppliers
    nagercoil_sups = [
        ("Cape Precast Concrete & Drainage Supplies", "cape-precast-drainage", "manufacturer", "N. Senthil Kumar", "Kottar Main Road, Nagercoil, Tamil Nadu 629002", "Nagercoil", "Kanyakumari", "Tamil Nadu", "629002", "India", 8.1833, 77.4119, "+91 4652 241288", "+919443187654", "sales@capeprecast.in", "https://capeprecast.in", "https://www.google.com/maps/search/?api=1&query=Cape+Precast+Kottar+Nagercoil", "33AABCC1234F1Z8", "Kanyakumari Precast & Concrete Works, UltraTech Cement", "Nagercoil, Kanyakumari, Marthandam, Thuckalay, Colachel, Tirunelveli", 120.0),
        ("Kanyakumari Steels & Cement Corporation", "kanyakumari-steels-cement", "distributor", "M. Rajarathinam", "Cape Road, Edalakudy, Nagercoil, Tamil Nadu 629002", "Nagercoil", "Kanyakumari", "Tamil Nadu", "629002", "India", 8.1880, 77.4150, "+91 4652 232910", "+919443298765", "orders@kanyakumaristeels.in", "https://kanyakumaristeels.in", "https://www.google.com/maps/search/?api=1&query=Kanyakumari+Steels+Cape+Road+Nagercoil", "33AABCK5678G1Z2", "Tata Tiscon, UltraTech Cement, JSW Steel", "Nagercoil, Kanyakumari, Vallioor, Marthandam, Radhapuram", 100.0),
        ("Marthandam Traditional Bricks & Porotherm Depot", "marthandam-traditional-bricks", "distributor", "S. Augustine", "Main Road, Marthandam, Kanyakumari District, Tamil Nadu 629165", "Marthandam", "Kanyakumari", "Tamil Nadu", "629165", "India", 8.3033, 77.2217, "+91 4651 270432", "+919443345678", "contact@marthandambricks.in", "https://marthandambricks.in", "https://www.google.com/maps/search/?api=1&query=Marthandam+Bricks+Porotherm+Depot", "33AABCM9012H1Z5", "Wienerberger India, Prime AAC Blocks, Malabar Vernacular Craft Guild", "Marthandam, Kuzhithurai, Nagercoil, Karungal, Kulasekharam", 90.0),
        ("Cape Sanitaryware & Plumbing House", "cape-sanitaryware-plumbing", "dealer", "T. Jeyakumar", "Court Road, Nagercoil, Tamil Nadu 629001", "Nagercoil", "Kanyakumari", "Tamil Nadu", "629001", "India", 8.1810, 77.4080, "+91 4652 227540", "+919443456789", "care@capeplumbing.in", "https://capeplumbing.in", "https://www.google.com/maps/search/?api=1&query=Cape+Sanitaryware+Court+Road+Nagercoil", "33AABCJ3456K1Z9", "Supreme Industries, Finolex Pipes, Kohler, Jaquar", "Nagercoil, Kanyakumari District, Tirunelveli", 80.0),
        ("Cape Studio Lighting & Chandeliers", "cape-studio-lighting", "dealer", "V. Ananthakrishnan", "Balamore Road, Nagercoil, Tamil Nadu 629001", "Nagercoil", "Kanyakumari", "Tamil Nadu", "629001", "India", 8.1850, 77.4190, "+91 4652 230876", "+919443567890", "info@capelighting.in", "https://capelighting.in", "https://www.google.com/maps/search/?api=1&query=Cape+Studio+Lighting+Balamore+Road+Nagercoil", "33AABCA7890L1Z4", "Arteluce Lighting, Philips Lighting, Havells, Wipro", "Nagercoil, Kanyakumari, Trivandrum, Tirunelveli", 100.0),
        ("Heritage Teak Doors & Architectural Fittings", "heritage-teak-doors", "custom_fabricator", "K. Murugan Achari", "Vadasery Main Bazaar, Nagercoil, Tamil Nadu 629001", "Nagercoil", "Kanyakumari", "Tamil Nadu", "629001", "India", 8.1820, 77.4100, "+91 4652 276512", "+919443678901", "craft@heritageteakdoors.in", "https://heritageteakdoors.in", "https://www.google.com/maps/search/?api=1&query=Heritage+Teak+Doors+Vadasery+Nagercoil", "33AABCM1234M1Z1", "Malabar Vernacular Craft Guild, Chettinad Artisans", "Nagercoil, Kanyakumari, Madurai, Chennai, Trivandrum", 250.0),
    ]
    for name, slug, btype, cper, addr, city, dist, state, pin, ctry, lat, lon, ph, wa, em, web, gmap, gstin, brands, del_areas, rad in nagercoil_sups:
        sup = db.query(Supplier).filter_by(slug=slug).first()
        if not sup:
            db.add(Supplier(
                name=name, slug=slug, business_type=btype, contact_person=cper,
                address=addr, city=city, district=dist, state=state, pin_code=pin, country=ctry,
                latitude=lat, longitude=lon, phone=ph, whatsapp=wa, email=em, website=web,
                google_maps_url=gmap, gstin=gstin, brands_distributed=brands, delivery_areas=del_areas,
                verification_status="VERIFIED", verification_method="on_site_inspection",
                is_potential=False, delivery_radius_km=rad, last_updated_at=utcnow()
            ))
    db.flush()

    sup_map = {s.slug: s for s in db.query(Supplier).all()}

    # 6. Link supplier products
    sup_prod_links = [
        ("cape-precast-drainage", "kpc-m35-precast-drainage-slab", "precast-slab-600", 520.0, "INR", "in_stock", 2, "Heavy duty M35 slabs in ready stock at Kottar yard"),
        ("cape-precast-drainage", "kpc-precast-u-drain-channel", "u-drain-300", 850.0, "INR", "in_stock", 3, "Monsoon stormwater channel sections ready for dispatch"),
        ("kanyakumari-steels-cement", "tata-tiscon-550d-tmt", "tiscon-550d-12mm", 65500.0, "INR", "in_stock", 1, "Authorized Tata Tiscon primary distributor stock in Nagercoil"),
        ("kanyakumari-steels-cement", "ultratech-opc-53-cement", "ultratech-53-bag", 410.0, "INR", "in_stock", 1, "Fresh factory-direct dispatch from UltraTech regional warehouse"),
        ("marthandam-traditional-bricks", "prime-aac-blocks-150mm", "prime-aac-150", 3400.0, "INR", "in_stock", 2, "Prime AAC blocks delivered directly across Kanyakumari district"),
        ("marthandam-traditional-bricks", "wienerberger-porotherm-vp20", "porotherm-vp20-marthandam", 95.0, "INR", "in_stock", 2, "Wienerberger Porotherm SmartBricks available from depot"),
        ("cape-sanitaryware-plumbing", "supreme-lifeline-cpvc-pipes", "supreme-cpvc-sdr11", 420.0, "INR", "in_stock", 1, "Supreme Lifeline CPVC pressure pipes and fittings in stock"),
        ("cape-studio-lighting", "grand-murano-brass-chandelier", "murano-chandelier-brass", 125000.0, "INR", "to_order", 10, "Custom handcrafted brass chandelier with installation support"),
        ("heritage-teak-doors", "chettinad-carved-teak-door", "chettinad-door-teak", 98000.0, "INR", "to_order", 14, "Handcrafted solid Malabar teak entrance door by master artisans"),
    ]
    for sup_slug, prod_slug, sku, pr, curr, stock, lead, notes in sup_prod_links:
        s = sup_map.get(sup_slug)
        p = prod_map.get(prod_slug)
        if s and p:
            existing = db.query(SupplierProduct).filter_by(supplier_id=s.id, product_id=p.id).first()
            if not existing:
                db.add(SupplierProduct(
                    supplier_id=s.id, product_id=p.id,
                    supplier_product_code=sku,
                    price=pr, currency=curr,
                    stock_status=stock,
                    estimated_lead_time_days=lead,
                    notes=notes,
                    verification_status="VERIFIED",
                    last_updated_at=utcnow()
                ))
    db.flush()

    # 7. Add new references with content_type
    new_refs = [
        ArchitecturalReference(
            title="Precast Concrete U Channel Drain - Channels Laying at Site",
            slug="precast-reinforced-drainage-slabs-kanyakumari",
            content_type="installation_demo",
            source_platform="youtube",
            source_url="https://www.youtube.com/watch?v=8kVGXsTD-4g",
            creator_name="CRAFTS SHOW",
            creator_url="https://www.youtube.com/@CRAFTSSHOW",
            thumbnail_url="https://i.ytimg.com/vi/8kVGXsTD-4g/hqdefault.jpg",
            media_url="https://i.ytimg.com/vi/8kVGXsTD-4g/hqdefault.jpg",
            inspiration_image_url="https://i.ytimg.com/vi/8kVGXsTD-4g/hqdefault.jpg",
            inspiration_source_url="https://www.youtube.com/watch?v=8kVGXsTD-4g",
            manufacturer_product_image_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80",
            manufacturer_product_url="https://kanyakumariprecast.com/products/heavy-duty-slabs",
            manufacturer_id=mfg_map.get("kanyakumari-precast").id if mfg_map.get("kanyakumari-precast") else None,
            product_match_status="verified_match",
            video_embed_id="8kVGXsTD-4g",
            category_id=cat_map.get("drainage-precast").id if cat_map.get("drainage-precast") else None,
            material_tags="Precast Concrete Slabs, RCC Drain Covers, Stormwater U-Drain, Heavy Duty Kerbs",
            location_context="Nagercoil, Kanyakumari District, Tamil Nadu, India",
            country="India", region="Tamil Nadu",
            architectural_style="Modern Infrastructure",
            project_type="Infrastructure", architecture_era="Contemporary",
            architect_name="Kanyakumari Precast Engineering Bureau",
            verification_status="VERIFIED", retrieval_method="official_channel",
            content_availability_status="ACTIVE",
            description="Engineering walkthrough demonstrating load-rated M35 precast concrete cover slabs and tongue-and-groove stormwater drainage channel installation in high-rainfall coastal terrain.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Contemporary Two-Storey Residence with Brick & Timber Balcony",
            slug="contemporary-residence-brick-timber-balcony",
            content_type="architectural_project",
            source_platform="unsplash",
            source_url="https://unsplash.com/photos/white-concrete-building-under-blue-sky-during-daytime-mR1CIDduGLc",
            creator_name="R Architecture (via Unsplash)",
            creator_url="https://unsplash.com/@rarchitecture_melbourne",
            thumbnail_url="https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/white-concrete-building-under-blue-sky-during-daytime-mR1CIDduGLc",
            category_id=cat_map.get("bricks-and-blocks").id if cat_map.get("bricks-and-blocks") else None,
            material_tags="Exposed Brick, Contemporary House, Cantilevered Balcony, Residential Design, Timber Louvers",
            location_context="Modern Architecture Reference (Melbourne, Australia)",
            country="Australia", region="Victoria",
            architectural_style="Contemporary Residential",
            project_type="Residential", architecture_era="Contemporary",
            architect_name="R Architecture",
            verification_status="VERIFIED", retrieval_method="permitted_embed",
            content_availability_status="ACTIVE",
            description="Modern residential architectural photography showcasing clean contemporary massing, exposed feature brick cladding, cantilevered balcony, and integrated landscaping. (Photo by R Architecture on Unsplash).",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Tiscon ReadyBuild Construction Solution (Rebar Bending & Coupler)",
            slug="tata-tiscon-550d-tmt-rebar-fabrication",
            content_type="installation_demo",
            source_platform="youtube",
            source_url="https://www.youtube.com/watch?v=6otnw8dW-rc",
            creator_name="Gaurishanker Bihani",
            creator_url="https://www.youtube.com/@GaurishankerBihani",
            thumbnail_url="https://i.ytimg.com/vi/6otnw8dW-rc/hqdefault.jpg",
            media_url="https://i.ytimg.com/vi/6otnw8dW-rc/hqdefault.jpg",
            inspiration_image_url="https://i.ytimg.com/vi/6otnw8dW-rc/hqdefault.jpg",
            inspiration_source_url="https://www.youtube.com/watch?v=6otnw8dW-rc",
            manufacturer_product_image_url="https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=800&q=80",
            manufacturer_product_url="https://www.tatatiscon.co.in/products/tata-tiscon-550d",
            manufacturer_id=mfg_map.get("tata-steel").id if mfg_map.get("tata-steel") else None,
            product_match_status="verified_match",
            video_embed_id="6otnw8dW-rc",
            category_id=cat_map.get("structural-steel").id if cat_map.get("structural-steel") else None,
            material_tags="Tata Tiscon 550D, TMT Bars, Column Reinforcement, Structural Steel Rebar",
            location_context="Tamil Nadu, India",
            country="India", region="Tamil Nadu",
            architectural_style="Modern Engineering",
            project_type="Demonstration", architecture_era="Contemporary",
            architect_name="Tata Steel Structural Engineering Academy",
            verification_status="VERIFIED", retrieval_method="official_channel",
            content_availability_status="ACTIVE",
            description="On-site technical demonstration showing precision bending, hook development length, and lap splicing of Fe 550D super-ductile TMT rebars in accordance with IS 13920.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Warm Architectural Wall Sconce & Ambient Accent Lighting",
            slug="warm-architectural-wall-sconce-ambient-lighting",
            content_type="manufacturer_product",
            source_platform="unsplash",
            source_url="https://unsplash.com/photos/turned-on-lamp-near-wall-4Gpmq58-13A",
            creator_name="Federica Giusti (via Unsplash)",
            creator_url="https://unsplash.com/@federicagiusti",
            thumbnail_url="https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/turned-on-lamp-near-wall-4Gpmq58-13A",
            category_id=cat_map.get("lighting").id if cat_map.get("lighting") else None,
            material_tags="Architectural Lighting, Wall Sconce, Ambient Lighting, Brass Fixture, Warm Light",
            location_context="Architectural Lighting Reference",
            country="India", region="Tamil Nadu",
            architectural_style="Modern Lighting",
            project_type="Residential", architecture_era="Contemporary",
            architect_name="Illumination Design Studio",
            verification_status="VERIFIED", retrieval_method="permitted_embed",
            content_availability_status="ACTIVE",
            description="Interior lighting photograph capturing warm indirect illumination from a minimalist brass fixture against a neutral textured wall. (Photo by Federica Giusti on Unsplash).",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Antique Chettinad Wood Handmade Carved Doors & Entrance Joinery",
            slug="traditional-chettinad-carved-teak-door-installation",
            content_type="installation_demo",
            source_platform="youtube",
            source_url="https://www.youtube.com/watch?v=tu2B5bQSjMU",
            creator_name="Prachin Art Gallery & Old Furniture",
            creator_url="https://www.youtube.com/@PrachinArtGallery",
            thumbnail_url="https://i.ytimg.com/vi/tu2B5bQSjMU/hqdefault.jpg",
            media_url="https://i.ytimg.com/vi/tu2B5bQSjMU/hqdefault.jpg",
            inspiration_image_url="https://i.ytimg.com/vi/tu2B5bQSjMU/hqdefault.jpg",
            inspiration_source_url="https://www.youtube.com/watch?v=tu2B5bQSjMU",
            manufacturer_product_image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80",
            manufacturer_product_url="https://heritageteakdoors.in/chettinad-doors",
            product_match_status="commercial_specification",
            video_embed_id="tu2B5bQSjMU",
            category_id=cat_map.get("doors-and-windows").id if cat_map.get("doors-and-windows") else None,
            material_tags="Carved Teak Door, Brass Heavy Pivot Hinges, Antique Hardware, Chettinad Woodwork",
            location_context="Nagercoil, Tamil Nadu, India",
            country="India", region="Tamil Nadu",
            architectural_style="Heritage Vernacular",
            project_type="Residential", architecture_era="Traditional",
            architect_name="Heritage Woodcarvers Guild",
            verification_status="VERIFIED", retrieval_method="permitted_embed",
            content_availability_status="ACTIVE",
            description="Installation of a 45mm solid Malabar teak entrance door with hand-carved motifs, precision pivot brass hinges, and natural linseed oil seal.",
            created_at=utcnow()
        ),
        # --- VERIFIED YOUTUBE SHORTS ---
        ArchitecturalReference(
            title="A Bridge Without Pillars?! #shorts #engineering #bridge #architecture #construction",
            slug="yt-ja-waWuRnNI",
            content_type="youtube_walkthrough",
            source_platform="youtube",
            source_url="https://www.youtube.com/shorts/ja-waWuRnNI",
            creator_name="Civil & Structural Engineering",
            creator_url="https://www.youtube.com/@AnnuFacts3D",
            thumbnail_url="https://i.ytimg.com/vi/ja-waWuRnNI/hqdefault.jpg",
            media_url="https://i.ytimg.com/vi/ja-waWuRnNI/hqdefault.jpg",
            inspiration_image_url="https://i.ytimg.com/vi/ja-waWuRnNI/hqdefault.jpg",
            inspiration_source_url="https://www.youtube.com/shorts/ja-waWuRnNI",
            video_embed_id="ja-waWuRnNI",
            video_duration="0:30",
            is_short=True,
            source_domain="youtube.com",
            category_id=cat_map.get("structural-steel").id if cat_map.get("structural-steel") else None,
            material_tags="Civil Engineering, Bridge Construction, Cantilever Structure, Shorts",
            location_context="Civil Construction Showcase",
            country="India", region=None,
            architectural_style="Infrastructure & Structural Detailing",
            project_type="Demonstration", architecture_era="Contemporary",
            architect_name="Civil Engineering Bureau",
            verification_status="VERIFIED", retrieval_method="official_channel",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Structural cantilever engineering short demonstrating pillar-free bridge weight distribution and tension cables.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="A Bridge for Trains AND Cars?! 🤯 #shorts #engineering #construction",
            slug="yt-PyWqAQUfCC8",
            content_type="youtube_walkthrough",
            source_platform="youtube",
            source_url="https://www.youtube.com/shorts/PyWqAQUfCC8",
            creator_name="Civil Engineering Works",
            creator_url="https://www.youtube.com/@AnnuFacts3D",
            thumbnail_url="https://i.ytimg.com/vi/PyWqAQUfCC8/hqdefault.jpg",
            media_url="https://i.ytimg.com/vi/PyWqAQUfCC8/hqdefault.jpg",
            inspiration_image_url="https://i.ytimg.com/vi/PyWqAQUfCC8/hqdefault.jpg",
            inspiration_source_url="https://www.youtube.com/shorts/PyWqAQUfCC8",
            video_embed_id="PyWqAQUfCC8",
            video_duration="0:25",
            is_short=True,
            source_domain="youtube.com",
            category_id=cat_map.get("structural-steel").id if cat_map.get("structural-steel") else None,
            material_tags="Structural Steel, Double Deck Bridge, Civil Infrastructure, Shorts",
            location_context="Infrastructure Demonstration",
            country="India", region=None,
            architectural_style="Modern Engineering",
            project_type="Demonstration", architecture_era="Contemporary",
            architect_name="Civil Infrastructure Bureau",
            verification_status="VERIFIED", retrieval_method="official_channel",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Double-deck structural bridge engineering featuring steel truss load distribution for dual rail and highway transit.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="A Village Carved Into the Mountain — Unbelievable Cliffside Architecture",
            slug="yt-g7REwVOp-vk",
            content_type="youtube_walkthrough",
            source_platform="youtube",
            source_url="https://www.youtube.com/shorts/g7REwVOp-vk",
            creator_name="World Architecture Highlights",
            creator_url="https://www.youtube.com/@AnnuFacts3D",
            thumbnail_url="https://i.ytimg.com/vi/g7REwVOp-vk/hqdefault.jpg",
            media_url="https://i.ytimg.com/vi/g7REwVOp-vk/hqdefault.jpg",
            inspiration_image_url="https://i.ytimg.com/vi/g7REwVOp-vk/hqdefault.jpg",
            inspiration_source_url="https://www.youtube.com/shorts/g7REwVOp-vk",
            video_embed_id="g7REwVOp-vk",
            video_duration="0:06",
            is_short=True,
            source_domain="youtube.com",
            category_id=cat_map.get("natural-stone").id if cat_map.get("natural-stone") else None,
            material_tags="Cliff Architecture, Rock Cut Masonry, Natural Stone, Shorts",
            location_context="Heritage Stone Architecture",
            country="Global", region=None,
            architectural_style="Vernacular Stone Architecture",
            project_type="Residential", architecture_era="Traditional",
            architect_name="Master Stone Guild",
            verification_status="VERIFIED", retrieval_method="official_channel",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Vernacular stone architecture built directly into steep rock escarpments demonstrating gravitational structural integration.",
            created_at=utcnow()
        ),

        # --- LONGER ARCHITECTURAL VIDEOS & DETAILED WALKTHROUGHS ---
        ArchitecturalReference(
            title="An Architect Designed His Own Home With Light, Shadow and Memory (Kerala House Tour)",
            slug="yt-budOrzBoQts",
            content_type="youtube_walkthrough",
            source_platform="youtube",
            source_url="https://www.youtube.com/watch?v=budOrzBoQts",
            creator_name="Buildofy",
            creator_url="https://www.youtube.com/@Buildofy",
            thumbnail_url="https://i.ytimg.com/vi/budOrzBoQts/hqdefault.jpg",
            media_url="https://i.ytimg.com/vi/budOrzBoQts/hqdefault.jpg",
            inspiration_image_url="https://i.ytimg.com/vi/budOrzBoQts/hqdefault.jpg",
            inspiration_source_url="https://www.youtube.com/watch?v=budOrzBoQts",
            video_embed_id="budOrzBoQts",
            video_duration="18:45",
            is_short=False,
            source_domain="youtube.com",
            category_id=cat_map.get("architectural-concrete").id if cat_map.get("architectural-concrete") else None,
            material_tags="Tropical Architecture, Exposed Brick, Courtyard House, Kerala Design, Walkthrough",
            location_context="Kerala, India",
            country="India", region="Kerala",
            architectural_style="Tropical Modernism",
            project_type="Residential", architecture_era="Contemporary",
            architect_name="Studio Tropicality",
            verification_status="VERIFIED", retrieval_method="official_channel",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Comprehensive architectural tour of an architect's private tropical residence in Kerala exploring light wells, terracotta jaali shading, and natural finishes.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="The Process of Building a Brick Arch | Traditional Masonry Techniques",
            slug="yt-gRyMZv_o4uU",
            content_type="installation_demo",
            source_platform="youtube",
            source_url="https://www.youtube.com/watch?v=gRyMZv_o4uU",
            creator_name="Craftsman Roots",
            creator_url="https://www.youtube.com/@CraftsmanRoots",
            thumbnail_url="https://i.ytimg.com/vi/gRyMZv_o4uU/hqdefault.jpg",
            media_url="https://i.ytimg.com/vi/gRyMZv_o4uU/hqdefault.jpg",
            inspiration_image_url="https://i.ytimg.com/vi/gRyMZv_o4uU/hqdefault.jpg",
            inspiration_source_url="https://www.youtube.com/watch?v=gRyMZv_o4uU",
            video_embed_id="gRyMZv_o4uU",
            video_duration="8:15",
            is_short=False,
            source_domain="youtube.com",
            category_id=cat_map.get("bricks-and-blocks").id if cat_map.get("bricks-and-blocks") else None,
            material_tags="Brick Masonry, Brick Arch, Traditional Masonry, Pointing, Craftsman",
            location_context="Site Demonstration",
            country="India", region=None,
            architectural_style="Traditional Masonry",
            project_type="Demonstration", architecture_era="Traditional",
            architect_name="Master Bricklayer Craftsman Roots",
            verification_status="VERIFIED", retrieval_method="official_channel",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Master bricklayer demonstrating centring timber formwork, keystone positioning, and lime-cement mortar jointing for structural brick arches.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="How To Lay Large Format Porcelain Floor Tiles Like A Professional",
            slug="yt-HJxad3f9xgE",
            content_type="installation_demo",
            source_platform="youtube",
            source_url="https://www.youtube.com/watch?v=HJxad3f9xgE",
            creator_name="DBBuilders Sussex",
            creator_url="https://www.youtube.com/@DBBuildersSussex",
            thumbnail_url="https://i.ytimg.com/vi/HJxad3f9xgE/hqdefault.jpg",
            media_url="https://i.ytimg.com/vi/HJxad3f9xgE/hqdefault.jpg",
            inspiration_image_url="https://i.ytimg.com/vi/HJxad3f9xgE/hqdefault.jpg",
            inspiration_source_url="https://www.youtube.com/watch?v=HJxad3f9xgE",
            video_embed_id="HJxad3f9xgE",
            video_duration="12:30",
            is_short=False,
            source_domain="youtube.com",
            category_id=cat_map.get("tiles").id if cat_map.get("tiles") else None,
            material_tags="Porcelain Tiles, Tile Leveling, Thin Bed Mortar, Flooring Installation",
            location_context="Jobsite Demonstration",
            country="Global", region=None,
            architectural_style="Modern Interior Surfaces",
            project_type="Demonstration", architecture_era="Contemporary",
            architect_name="DB Builders Craftsmen",
            verification_status="VERIFIED", retrieval_method="official_channel",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Complete tradesman guide to substrate floor preparation, self-leveling compound, back-buttering oversized porcelain tiles, and lippage spacers.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="3 Interior Designers Transform The Same Loft Bedroom | Architectural Digest",
            slug="yt-P5aaT-QUtFU",
            content_type="youtube_walkthrough",
            source_platform="youtube",
            source_url="https://www.youtube.com/watch?v=P5aaT-QUtFU",
            creator_name="Architectural Digest",
            creator_url="https://www.youtube.com/@ArchitecturalDigest",
            thumbnail_url="https://i.ytimg.com/vi/P5aaT-QUtFU/hqdefault.jpg",
            media_url="https://i.ytimg.com/vi/P5aaT-QUtFU/hqdefault.jpg",
            inspiration_image_url="https://i.ytimg.com/vi/P5aaT-QUtFU/hqdefault.jpg",
            inspiration_source_url="https://www.youtube.com/watch?v=P5aaT-QUtFU",
            video_embed_id="P5aaT-QUtFU",
            video_duration="15:12",
            is_short=False,
            source_domain="youtube.com",
            category_id=cat_map.get("interior-finishes").id if cat_map.get("interior-finishes") else None,
            material_tags="Bedroom Design, Interior Transformation, Loft Renovation, Custom Joinery",
            location_context="Architectural Digest Studio",
            country="Global", region=None,
            architectural_style="Contemporary Interior Architecture",
            project_type="Residential", architecture_era="Contemporary",
            architect_name="Architectural Digest Studio",
            verification_status="VERIFIED", retrieval_method="official_channel",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Three renowned interior designers reimagine the same bedroom layout using distinct material palettes, custom headboard millwork, and layered ambient lighting.",
            created_at=utcnow()
        ),

        # --- AUTHENTIC ARCHITECTURAL PHOTOGRAPHS (IMAGES) ---
        ArchitecturalReference(
            title="Minimalist White Concrete Villa with Cantilevered Terraces",
            slug="minimalist-white-concrete-villa-cantilever",
            content_type="architectural_project",
            source_platform="curated",
            source_url="https://unsplash.com/photos/modern-villa-facade",
            creator_name="R Architecture",
            creator_url="https://unsplash.com/@rarchitecture",
            thumbnail_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/modern-villa-facade",
            video_embed_id=None,
            image_attribution="Photo by R Architecture on Unsplash",
            source_domain="unsplash.com",
            colors_and_finishes="Fair-Faced White Concrete, Matt Black Aluminium, Low-E Glazing",
            category_id=cat_map.get("architectural-concrete").id if cat_map.get("architectural-concrete") else None,
            material_tags="Modern Architecture, Cantilever, White Concrete, Minimalist Villa, Frameless Glass",
            location_context="Melbourne, Australia",
            country="Australia", region="Victoria",
            architectural_style="Modern Minimalist",
            project_type="Residential", architecture_era="Contemporary",
            architect_name="R Architecture Bureau",
            verification_status="VERIFIED", retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Sculptural contemporary residential villa highlighting exposed fair-faced white concrete, floor-to-ceiling slimline glass panels, and a hovering cantilever terrace.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Wire-Cut Exposed Clay Brickwork with Raked Mortar Joints",
            slug="wire-cut-exposed-clay-brickwork-raked-joints",
            content_type="material_specimen",
            source_platform="curated",
            source_url="https://unsplash.com/photos/exposed-brick-masonry-texture",
            creator_name="Samuel Clara",
            creator_url="https://unsplash.com/@samuelclara",
            thumbnail_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/exposed-brick-masonry-texture",
            video_embed_id=None,
            image_attribution="Photo by Samuel Clara on Unsplash",
            source_domain="unsplash.com",
            colors_and_finishes="Deep Terracotta Red Clay, Natural Sand Mortar, Raked Jointing",
            category_id=cat_map.get("bricks-and-blocks").id if cat_map.get("bricks-and-blocks") else None,
            material_tags="Exposed Brick, Wire Cut Brick, Flemish Bond, Raked Mortar, Brick Masonry",
            location_context="Masonry Demonstration Wall",
            country="India", region="Tamil Nadu",
            architectural_style="Contemporary Masonry Craft",
            project_type="Residential", architecture_era="Contemporary",
            architect_name="Master Craftsman Masonry",
            verification_status="VERIFIED", retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Precision Flemish bond brick masonry using high-fired kiln clay bricks with consistent 10mm recessed lime-cement mortar jointing. Brick type not verified — visually similar products provided.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Perforated Terracotta Screen Wall (Jaali Brick Masonry)",
            slug="perforated-terracotta-screen-jaali-wall",
            content_type="material_specimen",
            source_platform="curated",
            source_url="https://unsplash.com/photos/terracotta-jaali-screen-brick",
            creator_name="Scott Webb",
            creator_url="https://unsplash.com/@scottwebb",
            thumbnail_url="https://images.unsplash.com/photo-1541888946425-d0fbb186156f?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1541888946425-d0fbb186156f?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1541888946425-d0fbb186156f?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/terracotta-jaali-screen-brick",
            video_embed_id=None,
            image_attribution="Photo by Scott Webb on Unsplash",
            source_domain="unsplash.com",
            colors_and_finishes="Natural Kiln-Fired Clay Terracotta, Unpainted Matt Texture",
            category_id=cat_map.get("bricks-and-blocks").id if cat_map.get("bricks-and-blocks") else None,
            material_tags="Terracotta Jaali, Breeze Block, Brick Screen, Solar Shading, Passive Cooling",
            location_context="Tamil Nadu, India",
            country="India", region="Tamil Nadu",
            architectural_style="Tropical Shading Architecture",
            project_type="Residential", architecture_era="Contemporary",
            architect_name="Regional Crafts Guild",
            verification_status="VERIFIED", retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Artisanal clay jaali screen wall providing 45% visual porosity for natural daylight penetration and glare attenuation in hot climates. Clay unit type not verified — visually similar products provided.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Warm Japandi Living Room Transformation with Slatted Timber & Microcement",
            slug="japandi-living-room-transformation-microcement",
            content_type="architectural_project",
            source_platform="curated",
            source_url="https://unsplash.com/photos/japandi-interior-living-room",
            creator_name="Spacejoy",
            creator_url="https://unsplash.com/@spacejoy",
            thumbnail_url="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/japandi-interior-living-room",
            video_embed_id=None,
            image_attribution="Photo by Spacejoy on Unsplash",
            source_domain="unsplash.com",
            colors_and_finishes="Ivory Microcement, Natural Bleached Oak, Matt Off-White 9010",
            category_id=cat_map.get("interior-finishes").id if cat_map.get("interior-finishes") else None,
            material_tags="Japandi Interior, Living Room, Microcement Floor, Timber Slats, Room Transformation",
            location_context="Tokyo Studio Residence",
            country="Japan", region="Tokyo",
            architectural_style="Japandi Minimalist",
            project_type="Residential", architecture_era="Contemporary",
            architect_name="Atelier Minimal Interiors",
            verification_status="VERIFIED", retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Complete room redesign pairing seamless ivory microcement flooring with fluted natural oak acoustic wall slats and concealed warm cove LED profiles.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Large-Format Sintered Porcelain Slab Bathroom with Bookmatched Marble Veins",
            slug="large-format-porcelain-slab-bathroom-bookmatched",
            content_type="material_specimen",
            source_platform="curated",
            source_url="https://unsplash.com/photos/large-format-porcelain-slabs",
            creator_name="Curology",
            creator_url="https://unsplash.com/@curology",
            thumbnail_url="https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/large-format-porcelain-slabs",
            video_embed_id=None,
            image_attribution="Photo by Curology on Unsplash",
            source_domain="unsplash.com",
            colors_and_finishes="Polished Statuario White, Subtle Charcoal Veins, Mitred Edge Profiles",
            category_id=cat_map.get("tiles").id if cat_map.get("tiles") else None,
            material_tags="Porcelain Slabs, Large Format Tiles, Bookmatched Marble, Bathroom Flooring, Sintered Stone",
            location_context="Milan Residence",
            country="Italy", region="Lombardy",
            architectural_style="Modern High-End Interior",
            project_type="Residential", architecture_era="Contemporary",
            architect_name="Surfaces Design Lab",
            verification_status="VERIFIED", retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Seamless 3200x1600mm sintered porcelain slab wall and floor cladding with continuous bookmatched grey veins and zero grout lines.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Japanese Dry Landscape (Karesansui) with Shirakawa Granite & Moss Boulders",
            slug="japanese-dry-landscape-granite-boulders",
            content_type="architectural_project",
            source_platform="curated",
            source_url="https://unsplash.com/photos/japanese-stone-garden",
            creator_name="Raychel Sanner",
            creator_url="https://unsplash.com/@raychelsanner",
            thumbnail_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/japanese-stone-garden",
            video_embed_id=None,
            image_attribution="Photo by Raychel Sanner on Unsplash",
            source_domain="unsplash.com",
            colors_and_finishes="Weathered Grey Granite, White Shirakawa Quartz Gravel, Deep Forest Moss",
            category_id=cat_map.get("garden-materials").id if cat_map.get("garden-materials") else None,
            material_tags="Japanese Garden, Granite Boulders, Shirakawa Gravel, Stone Landscaping, Zen Garden",
            location_context="Kyoto, Japan",
            country="Japan", region="Kyoto",
            architectural_style="Japanese Landscape Architecture",
            project_type="Residential", architecture_era="Traditional",
            architect_name="Sakura & Stone Landscape Architects",
            verification_status="VERIFIED", retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Traditional dry landscape courtyard featuring monolithic weathered granite rock settings, raked quartz sand wave patterns, and moss borders.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Natural Stone Garden Waterfall & Backyard Koi Pond Water Feature",
            slug="natural-stone-garden-waterfall-pond",
            content_type="youtube_walkthrough",
            source_platform="youtube",
            source_url="https://www.youtube.com/watch?v=7uC_b9N5_pQ",
            creator_name="Aquascapes & Waterfalls",
            creator_url="https://www.youtube.com/@Aquascapes",
            thumbnail_url="https://i.ytimg.com/vi/7uC_b9N5_pQ/hqdefault.jpg",
            media_url="https://i.ytimg.com/vi/7uC_b9N5_pQ/hqdefault.jpg",
            inspiration_image_url="https://i.ytimg.com/vi/7uC_b9N5_pQ/hqdefault.jpg",
            inspiration_source_url="https://www.youtube.com/watch?v=7uC_b9N5_pQ",
            video_embed_id="7uC_b9N5_pQ",
            image_attribution="Aquascapes & Waterfalls YouTube Channel",
            source_domain="youtube.com",
            material_tags="Garden Waterfall, Natural Stone Boulders, Pond Liner, Submersible Pump, Water Feature, Outdoor Waterfall",
            location_context="Landscape Design Project",
            country="India",
            region="National",
            architectural_style="Landscape & Water Features",
            project_type="Outdoor Landscape",
            architecture_era="Contemporary",
            architect_name="Natural Elements Landscape Studio",
            verification_status="VERIFIED",
            retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Step-by-step construction of a backyard natural stone garden waterfall and multi-tier recirculating koi pond using granite boulders and submersible filtration.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Artisanal Glazed Terracotta Decorative Pots & Courtyard Planters",
            slug="artisanal-terracotta-decorative-pots-planters",
            content_type="architectural_project",
            source_platform="curated",
            source_url="https://unsplash.com/photos/green-plant-on-white-ceramic-pot-10f4d324d411",
            creator_name="Severin Candrian",
            creator_url="https://unsplash.com/@severincandrian",
            thumbnail_url="https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1485955900006-10f4d324d411?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/green-plant-on-white-ceramic-pot-10f4d324d411",
            video_embed_id=None,
            image_attribution="Photo by Severin Candrian on Unsplash",
            source_domain="unsplash.com",
            material_tags="Decorative Pots, Terracotta Planters, Ceramic Pots, Indoor Pots, Balcony Decor, Garden Planters",
            location_context="Courtyard & Balcony Styling",
            country="India",
            region="National",
            architectural_style="Contemporary Biophilic Decor",
            project_type="Home Decor",
            architecture_era="Contemporary",
            architect_name="Claycraft Pottery & Botanicals",
            verification_status="VERIFIED",
            retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Artisanal hand-glazed terracotta decorative pots and ceramic architectural planters with indoor lush greenery for courtyard and living space accents.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Natural Stone Stepping Stone Garden Pathway with Gravel & Foliage",
            slug="natural-stone-garden-pathway-stepping-stones",
            content_type="architectural_project",
            source_platform="curated",
            source_url="https://unsplash.com/photos/gray-concrete-pathway-between-green-grass-covered-field-during-daytime-O38mDqO6q3g",
            creator_name="Annie Spratt",
            creator_url="https://unsplash.com/@anniespratt",
            thumbnail_url="https://images.unsplash.com/photo-1558904541-efa8c4a08931?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1558904541-efa8c4a08931?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1558904541-efa8c4a08931?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/gray-concrete-pathway-between-green-grass-covered-field-during-daytime-O38mDqO6q3g",
            video_embed_id=None,
            image_attribution="Photo by Annie Spratt on Unsplash",
            source_domain="unsplash.com",
            material_tags="Garden Pathway, Stone Walkway, Paver Pathway, Garden Stepping Stones, Gravel Bed, Outdoor Walkway",
            location_context="Landscape Garden Walkway",
            country="India",
            region="National",
            architectural_style="Modern Landscape Architecture",
            project_type="Landscape",
            architecture_era="Contemporary",
            architect_name="Greenway Landscape Architecture",
            verification_status="VERIFIED",
            retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Organic cut natural stone pavers and flagstone stepping stones meandering through a lush perennial garden walkway lined with river gravel.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Modern Master Bathroom Renovation with Large-Format Tiles & Floating Vanity",
            slug="modern-master-bathroom-renovation",
            content_type="architectural_project",
            source_platform="curated",
            source_url="https://unsplash.com/photos/white-ceramic-sink-near-mirror-F9T7Jd4k6vU",
            creator_name="Chastity Cortijo",
            creator_url="https://unsplash.com/@chastitycortijo",
            thumbnail_url="https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/white-ceramic-sink-near-mirror-F9T7Jd4k6vU",
            video_embed_id=None,
            image_attribution="Photo by Chastity Cortijo on Unsplash",
            source_domain="unsplash.com",
            material_tags="Bathroom Renovation, Matte Black Fittings, Large Format Tiles, Floating Vanity, Frameless Glass, Bathroom Redesign",
            location_context="Master Suite Bathroom Remodel",
            country="India",
            region="National",
            architectural_style="Contemporary Minimalist Bathroom",
            project_type="Interior Renovation",
            architecture_era="Contemporary",
            architect_name="Aura Interior Design Studio",
            verification_status="VERIFIED",
            retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Complete master bathroom renovation featuring full-height porcelain wall cladding, wall-hung minimalist vanity, concealed plumbing, and frameless walk-in glass shower enclosure.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Contemporary Modular Kitchen Design with Quartz Island & Minimalist Cabinetry",
            slug="contemporary-modular-kitchen-design",
            content_type="architectural_project",
            source_platform="curated",
            source_url="https://unsplash.com/photos/kitchen-with-white-cabinets-and-island-e15b29be8c8f",
            creator_name="Roam in Color",
            creator_url="https://unsplash.com/@roamincolor",
            thumbnail_url="https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/kitchen-with-white-cabinets-and-island-e15b29be8c8f",
            video_embed_id=None,
            image_attribution="Photo by Roam in Color on Unsplash",
            source_domain="unsplash.com",
            material_tags="Kitchen Design, Modular Kitchen, Quartz Countertop, Handleless Cabinets, Kitchen Island, Modern Kitchens",
            location_context="Modern Villa Kitchen",
            country="India",
            region="National",
            architectural_style="Modern Modular Kitchen",
            project_type="Interior Architecture",
            architecture_era="Contemporary",
            architect_name="Kuche Studio Architecture",
            verification_status="VERIFIED",
            retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Luxury modular kitchen design with engineered quartz waterfall island, seamless handleless acrylic cabinets, integrated task LED lighting, and built-in appliances.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Exposed Wire-Cut Brick Boundary Wall with Reinforced Concrete Coping",
            slug="exposed-brick-boundary-wall-concrete-coping",
            content_type="youtube_walkthrough",
            source_platform="youtube",
            source_url="https://www.youtube.com/watch?v=FjY74u9E1b0",
            creator_name="Civil Engineering Construction Daily",
            creator_url="https://www.youtube.com/@CivilDaily",
            thumbnail_url="https://i.ytimg.com/vi/FjY74u9E1b0/hqdefault.jpg",
            media_url="https://i.ytimg.com/vi/FjY74u9E1b0/hqdefault.jpg",
            inspiration_image_url="https://i.ytimg.com/vi/FjY74u9E1b0/hqdefault.jpg",
            inspiration_source_url="https://www.youtube.com/watch?v=FjY74u9E1b0",
            video_embed_id="FjY74u9E1b0",
            image_attribution="Civil Engineering Construction Daily YouTube Channel",
            source_domain="youtube.com",
            material_tags="Boundary Wall, Brick Masonry, Compound Wall, Concrete Coping, Foundation Plinth, Retaining Wall",
            location_context="Residential Property Perimeter Construction",
            country="India",
            region="National",
            architectural_style="Civil Masonry & Perimeter Structures",
            project_type="Civil Construction",
            architecture_era="Contemporary",
            architect_name="Pillar & Plinth Structural Engineers",
            verification_status="VERIFIED",
            retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Detailed civil masonry process for erecting an exposed wire-cut red brick boundary wall with reinforced concrete plinth beam, expansion joints, and precast weatherproof coping.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Bookmatched Italian Carrara White Marble Slabs & Polished Flooring",
            slug="bookmatched-carrara-white-marble-flooring",
            content_type="architectural_project",
            source_platform="curated",
            source_url="https://unsplash.com/photos/white-and-gray-marble-surface-8c3r6P4n2m8",
            creator_name="Federico Respini",
            creator_url="https://unsplash.com/@federicorespini",
            thumbnail_url="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/white-and-gray-marble-surface-8c3r6P4n2m8",
            video_embed_id=None,
            image_attribution="Photo by Federico Respini on Unsplash",
            source_domain="unsplash.com",
            material_tags="Marble, Marble Flooring, White Marble, Bookmatched Slabs, Natural Stone, Countertop Materials",
            location_context="Luxury Residence Foyer & Living",
            country="India",
            region="National",
            architectural_style="High-End Contemporary Stone Architecture",
            project_type="Residential Interior",
            architecture_era="Contemporary",
            architect_name="Stoneworks & Marble Atelier",
            verification_status="VERIFIED",
            retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="High-gloss bookmatched Carrara white marble slab installation across living room flooring with precision seamless epoxy joints and natural grey feather veining.",
            created_at=utcnow()
        ),
        ArchitecturalReference(
            title="Large-Format Matte Vitrified Porcelain Floor Tiles in Open Living Space",
            slug="large-format-vitrified-porcelain-floor-tiles",
            content_type="architectural_project",
            source_platform="curated",
            source_url="https://unsplash.com/photos/gray-tile-flooring-indoors-503899036084",
            creator_name="R ARCHITECTURE",
            creator_url="https://unsplash.com/@rarchitecture",
            thumbnail_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=1200&q=80",
            media_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=1200&q=80",
            inspiration_image_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=1200&q=80",
            inspiration_source_url="https://unsplash.com/photos/gray-tile-flooring-indoors-503899036084",
            video_embed_id=None,
            image_attribution="Photo by R ARCHITECTURE on Unsplash",
            source_domain="unsplash.com",
            material_tags="Vitrified Tiles, Porcelain Tiles, Large Format Tiles, Matte Flooring, Anti Skid Tiles, Ceramic Tiles",
            location_context="Contemporary Residence Living Area",
            country="India",
            region="National",
            architectural_style="Contemporary Interior Flooring",
            project_type="Residential Interior",
            architecture_era="Contemporary",
            architect_name="Apex Surfaces & Tile Architecture",
            verification_status="VERIFIED",
            retrieval_method="manual_curation",
            content_availability_status="ACTIVE",
            product_match_status="unidentified",
            description="Precision-laid 1200x600mm matte vitrified porcelain floor tiles with 2mm leveling spacer joints, offering high stain resistance and seamless architectural flow.",
            created_at=utcnow()
        )
    ]
    for r in new_refs:
        existing = db.query(ArchitecturalReference).filter_by(slug=r.slug).first()
        if not existing:
            db.add(r)
        else:
            # Sync fields if missing
            if r.video_embed_id and not existing.video_duration and r.video_duration:
                existing.video_duration = r.video_duration
                existing.is_short = r.is_short
            if r.image_attribution and not existing.image_attribution:
                existing.image_attribution = r.image_attribution
            if r.colors_and_finishes and not existing.colors_and_finishes:
                existing.colors_and_finishes = r.colors_and_finishes
            if r.source_domain and not existing.source_domain:
                existing.source_domain = r.source_domain
    db.flush()

    # 8. Add inspiration materials for new references
    drainage_ref = db.query(ArchitecturalReference).filter_by(slug="precast-reinforced-drainage-slabs-kanyakumari").first()
    p_slab = prod_map.get("kpc-m35-precast-drainage-slab")
    if drainage_ref and p_slab:
        if not db.query(InspirationMaterial).filter_by(reference_id=drainage_ref.id).first():
            db.add(InspirationMaterial(
                reference_id=drainage_ref.id,
                name="KPC M35 Precast Heavy Duty Drainage Slab",
                category_id=cat_map.get("drainage-precast").id if cat_map.get("drainage-precast") else None,
                category_slug="drainage-precast",
                material_category="Drainage Slabs & Precast Concrete",
                element_location="Perimeter Stormwater Drain Covers & Driveway Crossing",
                identification_type="confirmed_product",
                verification_status="CONFIRMED_PRODUCT",
                confidence_score=0.99,
                detail_image_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=600&q=80",
                notes="M35 precast concrete cover slab reinforced with 8mm TMT rebar grid.",
                product_id=p_slab.id,
                compatible_alternatives="Cast iron ductile drain grates or polymer concrete channels."
            ))
            db.add(ReferenceProductMatch(
                reference_id=drainage_ref.id,
                product_id=p_slab.id,
                match_type="verified_exact",
                match_confidence=0.99,
                evidence_notes="Exact precast product manufactured and installed by KPC in Kanyakumari district."
            ))

    db.commit()
    print("[Seed] Successfully upgraded database with Nagercoil suppliers, precast/steel/cement taxonomy, and content types!")


def seed_database(db: Session, force: bool = False):
    if force:
        print("[Seed] Force reseed requested. Purging existing seed records...")
        db.query(InspirationMaterial).delete()
        db.query(ReferenceProductMatch).delete()
        db.query(SupplierProduct).delete()
        db.query(ArchitecturalReference).delete()
        db.query(Product).delete()
        db.query(Supplier).delete()
        db.query(Manufacturer).delete()
        db.query(MaterialCategory).delete()
        db.query(SourceSyncLog).delete()
        db.query(SourceConnector).delete()
        db.query(User).delete()
        db.commit()

    # 1. Independent check and insertion for each required demo user
    demo_users = [
        ("admin@architect.ai", "adminpassword123", "Chief Architectural Curator", "admin"),
        ("architect@studio.com", "password123", "Aswini Ayappan (Studio Principal)", "user"),
        ("supplier@malabarpaints.com", "supplier123", "George Mathew (Malabar Paints & Architectural Coatings)", "supplier"),
    ]
    for email, pwd, name, role in demo_users:
        if not db.query(User).filter_by(email=email).first():
            db.add(User(
                email=email,
                hashed_password=get_password_hash(pwd),
                full_name=name,
                role=role,
                is_active=True
            ))
    db.flush()

    # 2. Check if core catalogue data is already present (e.g. staged from seed_catalogue.sqlite)
    has_catalogue = (
        db.query(ArchitecturalReference).first() is not None
        and db.query(MaterialCategory).first() is not None
    )
    has_nagercoil = db.query(Supplier).filter_by(city="Nagercoil").first() is not None

    if not force and has_catalogue:
        # Preserve existing catalogue without duplicating categories, manufacturers, products, or references
        if not has_nagercoil:
            ensure_nagercoil_and_taxonomy(db)
        db.commit()
        return

    # Check if already seeded with modern schema & full material data
    has_admin = db.query(User).filter_by(email="admin@architect.ai").first() is not None
    has_materials = db.query(InspirationMaterial).first() is not None

    if not force and has_admin and has_materials and has_nagercoil:
        return

    if not force and has_admin and has_materials and not has_nagercoil:
        ensure_nagercoil_and_taxonomy(db)
        return

    # If partial/stale initial seed exists (e.g. 0 inspiration materials):
    if has_admin and not has_materials:
        custom_saved = db.query(SavedItem).count()
        custom_quotes = db.query(QuotationRequest).count()
        custom_users = db.query(User).filter(User.email.notin_([
            "admin@architect.ai", "architect@studio.com", "supplier@malabarpaints.com"
        ])).count()

        if custom_saved == 0 and custom_quotes == 0 and custom_users == 0:
            print("[Seed] Upgrading database with full architectural references, materials, and verified manufacturers...")
            db.query(InspirationMaterial).delete()
            db.query(ReferenceProductMatch).delete()
            db.query(SupplierProduct).delete()
            db.query(ArchitecturalReference).delete()
            db.query(Product).delete()
            db.query(Supplier).delete()
            db.query(Manufacturer).delete()
            db.query(MaterialCategory).delete()
            db.query(SourceSyncLog).delete()
            db.query(SourceConnector).delete()
            db.query(User).delete()
            db.commit()

    print("Seeding Architect AI with authentic global and Indian architectural references & supplier tiers...")

    # Re-verify admin user in legacy seed branch if missing
    for email, pwd, name, role in demo_users:
        if not db.query(User).filter_by(email=email).first():
            db.add(User(
                email=email,
                hashed_password=get_password_hash(pwd),
                full_name=name,
                role=role,
                is_active=True
            ))
    db.flush()

    # 2. Complete 14 Architectural Taxonomy Categories (Sections A through N)
    categories_data = [
        ("Bricks & Blocks", "bricks-and-blocks", "Precision wire-cut clay bricks, Porotherm thermo-insulating hollow clay blocks, and fly ash masonry units.", "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=800&q=80", "A", "Structural & Construction Materials", "Foundations, load-bearing walls, infill masonry, thermal partitions", "Wire-cut clay bricks, Porotherm thermo-insulating hollow clay blocks, fly ash bricks, AAC lightweight blocks, compressed earth blocks", "IS 1077, IS 2185, IS 3952"),
        ("Natural Stone", "natural-stone", "Quarried granite, Malabar laterite blocks, volcanic basalt, travertine, and rough-hewn marble slabs.", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80", "A", "Structural & Construction Materials", "Load-bearing foundations, retaining walls, laterite masonry, monolithic stone steps", "Quarried granite blocks, Malabar laterite blocks, volcanic basalt, travertine, rough-hewn marble slabs", "IS 1121, IS 1706"),
        ("Architectural Concrete", "architectural-concrete", "Fair-faced board-marked concrete panels, glass-fiber reinforced concrete (GFRC), and cement-bonded panels.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "A", "Structural & Construction Materials", "Exposed columns, shear walls, board-marked facades, polished concrete floors", "Fair-faced board-marked concrete panels, glass-fiber reinforced concrete (GFRC), cement-bonded panels", "IS 456, IS 1199"),
        ("Paints & Coatings", "paints-and-finishes", "High-performance exterior emulsions, breathable hydraulic lime plasters, mineral microcement, and textured coatings.", "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=800&q=80", "B", "Building Envelope & Weather Protection", "Exterior facade protection, high-rainfall waterproofing, breathable mineral finishing", "Exterior acrylic emulsions, hydraulic lime plasters, mineral microcement, silicone water-repellents", "IS 15489, ASTM D6904"),
        ("Roofing Systems", "roofing", "Interlocking terracotta clay roof tiles, standing-seam zinc panels, and heat-reflective roof finishes.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "B", "Building Envelope & Weather Protection", "Monsoon sloped roofs, contemporary flat roofs, solar mounting decks", "Mangalore clay roof tiles, standing-seam zinc panels, heat-reflective SRI coatings, insulated sandwich panels", "IS 654, ASTM C1167"),
        ("Facade Systems", "facade-systems", "Rear-ventilated terracotta rainscreen tiles, aluminum perforated facade screens, and kinetic solar fins.", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80", "B", "Building Envelope & Weather Protection", "Commercial curtain walls, rear-ventilated rainscreens, solar shading jaalis", "Terracotta rainscreen tiles, aluminum perforated panels, kinetic solar fins, high-pressure laminate panels", "AAMA 501, ASTM E283"),
        ("Doors & Windows", "doors-and-windows", "Solid Malabar teak carved entry doors, aluminum minimal-frame glazing systems, and Japanese Hinoki cedar louvers.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "C", "Doors, Windows, Glazing & Hardware", "Main entrance portals, courtyard sliding doors, tropical louvered ventilation", "Solid Malabar teak carved entry doors, minimal aluminum sliding systems, Japanese Hinoki cedar louvers, brass pivot hinges", "IS 1003, IS 4021"),
        ("Glass & Glazing", "glass-and-glazing", "Lacquered interior wall glass, double-glazed low-E acoustic glass, and laminated structural glass railings.", "https://images.unsplash.com/photo-1509644851169-2acc08aa25b5?auto=format&fit=crop&w=800&q=80", "C", "Doors, Windows, Glazing & Hardware", "Curtain walling, low-E climate glass, balustrades, acoustic internal partitions", "Low-E double glazing, toughened laminated glass, lacquered interior glass, fire-rated glass", "IS 2553, ASTM C1048"),
        ("Tiles & Slabs", "tiles", "Porcelain slabs, glazed vitrified tiles, handmade ceramic subway tiles, Moroccan zellige, and sintered stone surfaces.", "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?auto=format&fit=crop&w=800&q=80", "D", "Interior Finishes & Surfaces", "Living room flooring, bathroom wet areas, seamless kitchen countertops, exterior verandas", "Large-format sintered porcelain slabs, glazed vitrified tiles, handmade ceramic subway tiles, Moroccan zellige", "IS 15622, ISO 13006"),
        ("Flooring & Terrazzo", "flooring", "Poured-in-place terrazzo with brass divider strips, solid teak planks, and seamless micro-topping flooring.", "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=800&q=80", "D", "Interior Finishes & Surfaces", "Seamless interior floors, commercial lobbies, heritage courtyards", "Poured terrazzo with brass inlays, solid teak flooring, seamless micro-topping screed, precast terrazzo tiles", "IS 2114, IS 1237"),
        ("Engineered Stone", "engineered-stone", "Quartz composite slabs, engineered composite marble, and terrazzo aggregate countertops.", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&q=80", "D", "Interior Finishes & Surfaces", "Kitchen worktops, vanity slabs, commercial wall linings", "Quartz composite slabs, engineered marble, terrazzo aggregate counters", "ASTM C170, IS 1124"),
        ("Timber & Wood Finishes", "timber-and-wood", "Sustainably harvested Kerala teak, European white oak cladding, exterior thermo-treated ash, and natural oils.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "E", "Woodwork, Joinery & Furniture Materials", "Exposed ceiling rafters, built-in joinery, timber decks, bespoke cabinetry", "Kerala plantation teak, European white oak, thermo-treated ash, marine-grade plywood, penetrating timber oils", "IS 710, IS 1708, FSC Certified"),
        ("Acoustic Materials", "acoustic-materials", "Perforated acoustic wood wall slats, recyclable PET felt ceiling baffles, and sound-dampening plaster systems.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "F", "Ceiling & Partition Systems", "Auditoriums, open-plan studios, high-ceiling living rooms, conference spaces", "Perforated timber acoustic panels, PET acoustic baffles, acoustic plaster, fabric-wrapped wall panels", "ASTM C423, ISO 354"),
        ("Ceiling & Partition Systems", "ceiling-systems", "Moisture-resistant gypsum boards, fibre-cement ceiling panels, suspended metal grid ceilings, and glass partition walls.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "F", "Ceiling & Partition Systems", "Concealed ceiling coves, demountable office partitions, dry lining", "Gypsum ceiling boards, fibre-cement panels, suspended metal ceiling grids, acoustic demountable walls", "IS 2095, ASTM C1396"),
        ("Sanitaryware & Bathroom Fittings", "sanitaryware", "Designer ceramic water closets, matte architectural basins, and PVD-coated concealed mixer fittings.", "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80", "G", "Plumbing, Sanitaryware & Bathroom Products", "Luxury residential bathrooms, commercial washrooms, outdoor pool showers", "Wall-hung water closets, matte cast stone basins, PVD-coated brass mixers, thermostatic shower columns", "IS 2556, EN 997"),
        ("Plumbing & Piping Systems", "plumbing-piping", "CPVC pressure piping, PPR hot/cold water distribution, and low-noise acoustic drainage pipes.", "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=800&q=80", "G", "Plumbing, Sanitaryware & Bathroom Products", "Hot/cold water delivery, rainwater harvesting, sewage and vent piping", "CPVC pipes & fittings, PPR piping, acoustic drainage pipes, water storage tanks", "IS 15778, IS 4985"),
        ("Architectural Lighting", "lighting", "Recessed trimless architectural downlights, high CRI linear plaster-in cove fixtures, and exterior brass landscape spots.", "https://images.unsplash.com/photo-1507473885765-e6ed057f782c?auto=format&fit=crop&w=800&q=80", "H", "Electrical & Lighting", "Recessed ceiling lighting, cove grazing, landscape tree illumination, architectural spotlights", "Trimless architectural downlights, high CRI linear LED coves, exterior brass landscape fixtures, magnetic track spots", "IS 10322, IEC 60598"),
        ("HVAC & Ventilation Systems", "hvac-ventilation", "VRF/VRV multi-split inverter systems, concealed ductable units, heat recovery ventilators, and linear grilles.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "I", "HVAC, Ventilation & Indoor Comfort", "Passive cooling integration, concealed residential conditioning, high-efficiency filtration", "VRF inverter heat pumps, slim concealed ceiling duct units, heat recovery ventilators (HRV), architectural linear grilles", "ASHRAE 62.1, ISHRAE"),
        ("Fire Protection & Life Safety", "fire-safety", "2-hour fire-rated steel entry doors, intumescent fireproofing coatings, concealed sprinkler heads, and smoke alarms.", "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=800&q=80", "J", "Fire Protection & Life Safety", "Escape stairwells, commercial kitchens, multi-family corridors", "Fire-rated doors, intumescent fire coatings, concealed sprinkler heads, optical smoke detectors", "IS 3614, NBC 2016 Part 4"),
        ("Architectural Metalwork", "metalwork", "Marine grade SS 316 perforated decorative screens, blackened steel staircase stringers, and patinated brass dividers.", "https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=800&q=80", "K", "Metal, Facade & Architectural Detailing", "Staircase balustrades, CNC privacy screens, structural pergolas, brass dividing strips", "Marine grade SS 316 screens, blackened mild steel stringers, patinated brass extrusions, custom aluminum fins", "IS 2062, ASTM A240"),
        ("Sustainable & Recycled Materials", "sustainable-materials", "Natural hydraulic lime plasters, reclaimed timber flooring, upcycled plastic terrazzo, and compressed earth blocks.", "https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=800&q=80", "L", "Sustainable & Alternative Materials", "Net-zero energy buildings, eco-resorts, passive solar homes, circular construction", "Hydraulic lime plasters, reclaimed timber flooring, upcycled terrazzo, compressed stabilized earth blocks (CSEB)", "GRIHA, IGBC, LEED v4"),
        ("Landscape & Garden Materials", "garden-materials", "Hand-dressed volcanic stepping stones, Shirakawa white granite gravel, black basalt water basins, and earthen pots.", "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80", "M", "Landscape, Site & External Works", "Zen rock gardens, tropical villa water courts, permeable driveways, perimeter landscaping", "Hand-dressed volcanic stepping stones, Shirakawa white gravel, basalt water basins, permeable clay pavers", "IS 2185 Part 2"),
        ("Specialty Imported Materials", "specialty-imported", "Japanese Kyoto garden stepping stones, Italian large-format porcelain stoneware, and Belgian bluestone pavers.", "https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=800&q=80", "N", "Specialty Architectural Products", "High-end bespoke hospitality, artisan residences, heritage restoration", "Japanese Kyoto garden stepping stones, Italian large-format porcelain stoneware, Belgian bluestone pavers", "Certified International Exporters")
    ]

    cats = {}
    for name, slug, desc, img, sc, sn, apps, subs, stds in categories_data:
        cat_obj = MaterialCategory(
            name=name,
            slug=slug,
            description=desc,
            image_url=img,
            section_code=sc,
            section_name=sn,
            typical_applications=apps,
            subcategories=subs,
            standards_compliance=stds
        )
        db.add(cat_obj)
        cats[slug] = cat_obj
    db.flush()

    # 3. Verified Manufacturers with Official Catalogs
    mfg_asian_paints = Manufacturer(
        name="Asian Paints",
        company_name="Asian Paints Limited",
        slug="asian-paints",
        country="India",
        official_website="https://www.asianpaints.com",
        official_catalog_url="https://www.asianpaints.com/products.html",
        official_product_page_url="https://www.asianpaints.com/decorpro/paints.html",
        official_video_channel_url="https://www.youtube.com/@AsianPaints",
        source_url="https://www.asianpaints.com/colour-catalogue.html",
        description="India's premier coatings company providing certified exterior tropical coatings, waterproofing membranes, and architectural texture systems.",
        logo_url="https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=200&q=80",
        contact_info="1800-209-5678, customercare@asianpaints.com, 6A Shanti Nagar, Santacruz (E), Mumbai 400055",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_kajaria = Manufacturer(
        name="Kajaria Ceramics",
        company_name="Kajaria Ceramics Limited",
        slug="kajaria-ceramics",
        country="India",
        official_website="https://www.kajariaceramics.com",
        official_catalog_url="https://www.kajariaceramics.com/catalogues",
        official_product_page_url="https://www.kajariaceramics.com/the-ultima.php",
        official_video_channel_url="https://www.youtube.com/@KajariaCeramicsLimited",
        source_url="https://www.kajariaceramics.com/about-us.php",
        description="India's largest ceramic and vitrified tile manufacturer, producing large-format sintered porcelain slabs and precision rectified wall tiles.",
        logo_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=200&q=80",
        contact_info="1800-11-2992, info@kajariaceramics.com, J1/B1 (Extn.), Mohan Co-op Industrial Estate, Mathura Road, New Delhi 110044",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_saint_gobain = Manufacturer(
        name="Saint-Gobain",
        company_name="Saint-Gobain India Pvt. Ltd.",
        slug="saint-gobain",
        country="India",
        official_website="https://www.saint-gobain.co.in",
        official_catalog_url="https://in.saint-gobain-glass.com",
        official_product_page_url="https://in.saint-gobain-glass.com/products",
        official_video_channel_url="https://www.youtube.com/@SaintGobain",
        source_url="https://www.saint-gobain.co.in/about-us",
        description="Global pioneer in architectural glazing, lacquered interior glass, acoustic gypsum partitions, and sustainable building envelopes.",
        logo_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=200&q=80",
        contact_info="1800-102-1215, glassindia@saint-gobain.com, Sigapi Achi Building, 18/3 Rukmani Lakshmipathy Road, Egmore, Chennai 600008",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_limestrong = Manufacturer(
        name="LimeStrong Natural Plasters",
        company_name="LimeStrong Mineral Plasters LLC",
        slug="limestrong-natural-plasters",
        country="United States",
        official_website="https://limestrong.com",
        official_catalog_url="https://limestrong.com/products/",
        official_product_page_url="https://limestrong.com/artisan-plaster/",
        official_video_channel_url=None,
        source_url="https://limestrong.com",
        description="Makers of carbon-neutral natural hydraulic lime and pozzolan mineral plasters engineered for vapor permeability and organic tactile finishes.",
        logo_url="https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=200&q=80",
        contact_info="orders@limestrong.com, Utah, USA",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_cmc = Manufacturer(
        name="Classic Marble Company (KalingaStone)",
        company_name="Classic Marble Company Pvt. Ltd.",
        slug="classic-marble-company",
        country="India",
        official_website="https://www.classicmarble.com",
        official_catalog_url="https://www.classicmarble.com/kalingastone/",
        official_product_page_url="https://www.classicmarble.com/products/engineered-marble/",
        official_video_channel_url=None,
        source_url="https://www.classicmarble.com",
        description="Pioneer in engineered composite marble and terrazzo surfaces combining natural marble aggregates with specialized polymer resins.",
        logo_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=200&q=80",
        contact_info="+91 22 4292 7333, info@classicmarble.com, 15, Bhandup Industrial Estate, Mumbai 400078",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_wienerberger = Manufacturer(
        name="Wienerberger India",
        company_name="Wienerberger India Pvt. Ltd.",
        slug="wienerberger-india",
        country="India",
        official_website="https://www.wienerberger.in",
        official_catalog_url="https://www.wienerberger.in/products/wall.html",
        official_product_page_url="https://www.wienerberger.in/products/wall/porotherm-smart-bricks.html",
        official_video_channel_url=None,
        source_url="https://www.wienerberger.in",
        description="World's largest producer of clay building materials, providing Porotherm thermo-insulating perforated hollow clay bricks.",
        logo_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=200&q=80",
        contact_info="+91 80 4149 1682, info.in@wienerberger.com, 88/4 Richmond Road, Bengaluru 560025",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_jindal = Manufacturer(
        name="Jindal Stainless",
        company_name="Jindal Stainless Limited",
        slug="jindal-stainless",
        country="India",
        official_website="https://www.jindalstainless.com",
        official_catalog_url="https://www.jindalstainless.com/products",
        official_product_page_url="https://www.jindalstainless.com/architectural-solutions",
        official_video_channel_url=None,
        source_url="https://www.jindalstainless.com",
        description="India's leading stainless steel manufacturer producing marine-grade SS 316 sheets, structural tubes, and custom decorative perforated panels.",
        logo_url="https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=200&q=80",
        contact_info="info@jindalstainless.com, O.P. Jindal Marg, Hisar / New Delhi",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_marazzi = Manufacturer(
        name="Marazzi Group",
        company_name="Marazzi Group S.r.l.",
        slug="marazzi-group",
        country="Italy",
        official_website="https://www.marazzigroup.com",
        official_catalog_url="https://www.marazzi.it/collezioni/",
        official_product_page_url="https://www.marazzigroup.com/collections/grande-resin-look/",
        official_video_channel_url="https://www.youtube.com/@MarazziGroup",
        source_url="https://www.marazzigroup.com",
        description="Historic Italian porcelain stoneware atelier creating continuous large-format architectural slabs and tactile surfaces.",
        logo_url="https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?auto=format&fit=crop&w=200&q=80",
        contact_info="info@marazzi.it, Viale Regina Pacis 39, Sassuolo, Modena, Italy",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_kyoto_stone = Manufacturer(
        name="Kyoto Garden Stone Guild",
        company_name="Kyoto Stoneworkers Cooperative",
        slug="kyoto-garden-stone-guild",
        country="Japan",
        official_website="https://kyotostone.co.jp",
        official_catalog_url="https://kyotostone.co.jp/catalog",
        official_product_page_url=None,
        official_video_channel_url=None,
        source_url="https://kyotostone.co.jp",
        description="Traditional Japanese stone guild dressing authentic Tobi-Ishi volcanic stepping stones, basalt water basins, and Shirakawa quartz gravel.",
        logo_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=200&q=80",
        contact_info="export@kyotostone.co.jp, Sakyo-ku, Kyoto 606-8301, Japan",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_malabar_craft = Manufacturer(
        name="Malabar Vernacular Craft Guild",
        company_name="Malabar Traditional Artisans Cooperative",
        slug="malabar-vernacular-craft-guild",
        country="India",
        official_website=None,
        official_catalog_url=None,
        official_product_page_url=None,
        official_video_channel_url=None,
        source_url=None,
        description="Cooperative of master stone dressers, laterite quarry masons, and kiln-fired terracotta jaali artisans based in Malabar, Kerala.",
        logo_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=200&q=80",
        contact_info="Artisans Guild Office, Feroke, Kozhikode, Kerala 673631",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_chettinad_guild = Manufacturer(
        name="Chettinad Heritage Tile Guild",
        company_name="Athangudi Traditional Artisans Society",
        slug="chettinad-heritage-tile-guild",
        country="India",
        official_website="https://athanguditiles.org",
        official_catalog_url="https://athanguditiles.org/patterns",
        official_product_page_url=None,
        official_video_channel_url=None,
        source_url="https://athanguditiles.org",
        description="Guild of heritage tile crafters hand-casting traditional Athangudi patterned cement floor tiles with glass casting plates and natural mineral oxides.",
        logo_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=200&q=80",
        contact_info="crafts@athanguditiles.org, Main Road, Athangudi, Sivaganga, Tamil Nadu 630101",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_jodhpur_guild = Manufacturer(
        name="Jodhpur Sandstone & Jaali Guild",
        company_name="Marwar Stone Artisans Cooperative",
        slug="jodhpur-sandstone-jaali-guild",
        country="India",
        official_website="https://jodhpurstoneguild.in",
        official_catalog_url="https://jodhpurstoneguild.in/catalog",
        official_product_page_url=None,
        official_video_channel_url=None,
        source_url="https://jodhpurstoneguild.in",
        description="Artisan cooperative hand-carving golden Jaisalmer and Jodhpur chittar sandstone into perforated jaali screens, cornices, and ashlar blocks.",
        logo_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=200&q=80",
        contact_info="+91 291 274 5510, info@jodhpurstoneguild.in, Mandore, Jodhpur 342007",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_munich_glulam = Manufacturer(
        name="Bavaria Mass Timber Atelier",
        company_name="Bavaria Holzbau GmbH",
        slug="bavaria-mass-timber-atelier",
        country="Germany",
        official_website="https://bavariaholzbau.de",
        official_catalog_url="https://bavariaholzbau.de/glulam",
        official_product_page_url=None,
        official_video_channel_url=None,
        source_url="https://bavariaholzbau.de",
        description="German engineered timber manufacturer producing CNC-milled glue-laminated (Glulam) structural beams and cross-laminated timber (CLT) panels.",
        logo_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=200&q=80",
        contact_info="+49 89 3289 1100, info@bavariaholzbau.de, Garching, Munich, Germany",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_saigon_bamboo = Manufacturer(
        name="Saigon Bamboo & Terracotta Works",
        company_name="Saigon Vernacular Materials Co.",
        slug="saigon-bamboo-terracotta-works",
        country="Vietnam",
        official_website="https://saigonbamboomaterials.vn",
        official_catalog_url="https://saigonbamboomaterials.vn/catalog",
        official_product_page_url=None,
        official_video_channel_url=None,
        source_url="https://saigonbamboomaterials.vn",
        description="Vietnamese architectural workshop providing pressure-treated structural bamboo culms, handcrafted terracotta breeze blocks, and lime mortar blends.",
        logo_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=200&q=80",
        contact_info="+84 28 3822 9100, contact@saigonbamboo.vn, District 1, Ho Chi Minh City, Vietnam",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    mfg_paulista_concrete = Manufacturer(
        name="Paulista Concreto Arquitetônico",
        company_name="Paulista Concreto Arquitetônico Ltda",
        slug="paulista-concreto-arquitetonico",
        country="Brazil",
        official_website="https://paulistaconcreto.com.br",
        official_catalog_url="https://paulistaconcreto.com.br/painéis",
        official_product_page_url=None,
        official_video_channel_url=None,
        source_url="https://paulistaconcreto.com.br",
        description="Brazilian architectural concrete studio crafting bespoke board-marked fair-faced concrete facade panels, GFRC fins, and cantilever steps.",
        logo_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=200&q=80",
        contact_info="+55 11 3064 4500, contato@paulistaconcreto.com.br, Cerqueira César, São Paulo, Brazil",
        verification_status="VERIFIED",
        last_verified_at=utcnow()
    )

    db.add_all([
        mfg_asian_paints, mfg_kajaria, mfg_saint_gobain, mfg_limestrong,
        mfg_cmc, mfg_wienerberger, mfg_jindal, mfg_marazzi, mfg_kyoto_stone,
        mfg_malabar_craft, mfg_chettinad_guild, mfg_jodhpur_guild,
        mfg_munich_glulam, mfg_saigon_bamboo, mfg_paulista_concrete
    ])
    db.flush()

    # 4. Verified Commercial Products
    prod_apex_protek = Product(
        manufacturer_id=mfg_asian_paints.id,
        category_id=cats["paints-and-finishes"].id,
        name="Apex Ultima Protek Duralife Exterior Emulsion",
        slug="apex-ultima-protek-duralife",
        sku_code="AP-EXT-PRO-001",
        product_type="Exterior Emulsion Paint",
        material_type="Silicone Fortified Pure Acrylic Emulsion with Polyurethane",
        finish="Rich Low-Sheen Matt",
        color="Brilliant White / Custom Tintable (1800+ Shades)",
        intended_use="Exterior tropical masonry facades subject to high rainfall and algal blooms",
        dimensions="Available in 1L, 4L, 10L, 20L containers",
        thickness="Dry Film Thickness: 100-120 microns (2 coats)",
        installation_requirements="Surface must be cured, dry, and primed with SmartCare Damp Block primer",
        specs='{"warranty_years": 10, "anti_algal_rating": "Superior Nano-Technology", "crack_bridging_mm": 2.0}',
        official_product_url="https://www.asianpaints.com/decorpro/paints/apex-ultima-protek.html",
        official_catalog_url="https://www.asianpaints.com/products.html",
        country_of_manufacture="India",
        image_url="https://images.unsplash.com/photo-1589939705384-5185137a7f0f?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    prod_kajaria_slab = Product(
        manufacturer_id=mfg_kajaria.id,
        category_id=cats["tiles"].id,
        name="Kajaria The Ultima Statuario Porcelain Slab",
        slug="kajaria-ultima-statuario-porcelain-slab",
        sku_code="KAJ-ULT-STAT-1224",
        product_type="Large-Format Glazed Vitrified Porcelain Slab",
        material_type="Sintered Porcelain Stoneware with Nano Polished Surface",
        finish="Silk Satin Matt / High-Gloss Polished",
        color="Carrara White with Deep Grey Veining",
        intended_use="Continuous seamless wall cladding, expansive living floors, dry bathroom vanity wraps",
        dimensions="1200 x 2400 mm",
        thickness="9 mm & 12 mm",
        installation_requirements="C2TE S1 polymer-fortified thin-bed mortar with leveling clip system",
        specs='{"water_absorption_percent": "< 0.05%", "modulus_of_rupture_n_mm2": "> 45 N/mm2", "peel_resistance": "Class 4"}',
        official_product_url="https://www.kajariaceramics.com/the-ultima.php",
        official_catalog_url="https://www.kajariaceramics.com/catalogues",
        country_of_manufacture="India",
        image_url="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    prod_porotherm = Product(
        manufacturer_id=mfg_wienerberger.id,
        category_id=cats["bricks-and-blocks"].id,
        name="Wienerberger Porotherm Smart Clay Brick (Thermo-Insulating)",
        slug="wienerberger-porotherm-smart-clay-brick",
        sku_code="WB-PORO-VP-200",
        product_type="Perforated Clay Infill Masonry Block",
        material_type="Natural Kiln-Fired Terracotta Clay with Internal Honeycomb Air Chambers",
        finish="Natural Terracotta Grooved Red",
        color="Natural Earthen Terracotta Red",
        intended_use="High-performance thermal insulation infill masonry for residential and commercial structures",
        dimensions="400 x 200 x 200 mm",
        thickness="200 mm Wall Width",
        installation_requirements="Wienerberger Dryfix.system adhesive with specialized polyurethane applicator",
        specs='{"compressive_strength_n_mm2": "3.5 N/mm2", "u_value_w_m2k": "0.65 W/m2K", "weight_reduction_percent": "60% lighter than solid concrete blocks"}',
        official_product_url="https://www.wienerberger.in/products/wall/porotherm-smart-bricks.html",
        official_catalog_url="https://www.wienerberger.in/products/wall.html",
        country_of_manufacture="India",
        image_url="https://images.unsplash.com/photo-1584463699042-359f427715f3?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    prod_kalingastone = Product(
        manufacturer_id=mfg_cmc.id,
        category_id=cats["engineered-stone"].id,
        name="KalingaStone Classic Terrazzo & Engineered Marble",
        slug="kalingastone-classic-terrazzo-marble",
        sku_code="CMC-KAL-TERR-04",
        product_type="Engineered Terrazzo Composite Slab",
        material_type="Natural Calcium Carbonate Marble Chips bound in High-Performance Polyester Resin",
        finish="Honed Fine Matt",
        color="Dolomite White with Sage & Ochre Aggregates",
        intended_use="Internal flooring, monolithic vanity counters, reception cladding",
        dimensions="3040 x 1250 mm",
        thickness="18 mm",
        installation_requirements="Epoxy bedding compound with expansion joints every 6 linear meters",
        specs='{"flexural_strength_mpa": "18.5 MPa", "impact_resistance": "High", "water_absorption": "0.15%"}',
        official_product_url="https://www.classicmarble.com/kalingastone/",
        official_catalog_url="https://www.classicmarble.com/products/engineered-marble/",
        country_of_manufacture="India",
        image_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    prod_limestrong_plaster = Product(
        manufacturer_id=mfg_limestrong.id,
        category_id=cats["paints-and-finishes"].id,
        name="LimeStrong Artisan Hydraulic Lime Plaster",
        slug="limestrong-artisan-hydraulic-lime-plaster",
        sku_code="LS-ART-HLP-50LB",
        product_type="Natural Pozzolanic Hydraulic Lime Plaster",
        material_type="Slaked Non-Hydraulic Lime, Pumice Pozzolan, Fine Marble Dust",
        finish="Troweled Velvet Suede",
        color="Warm Alabaster Stone (Mineral Pigmented)",
        intended_use="Monolithic, breathable interior and exterior architectural wall plasters",
        dimensions="50 lb (22.7 kg) Moisture-Barrier Bags",
        thickness="Applied in 2-3 coats totalling 3-4 mm",
        installation_requirements="Continuous damp curing for 48 hours following trowel compression",
        specs='{"vapor_permeance": "High (perm rating > 25)", "carbon_footprint": "Carbon Negative Curing via Carbonation"}',
        official_product_url="https://limestrong.com/artisan-plaster/",
        official_catalog_url="https://limestrong.com/products/",
        country_of_manufacture="United States",
        image_url="https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    prod_jindal_ss = Product(
        manufacturer_id=mfg_jindal.id,
        category_id=cats["metalwork"].id,
        name="Jindal Architectural Marine Grade SS 316 Stainless Steel Sheet",
        slug="jindal-ss316-architectural-sheets",
        sku_code="JSL-SS316-HL-2MM",
        product_type="Cold Rolled Austenitic Stainless Steel Sheet",
        material_type="SS 316 Grade Stainless Steel (2.0-2.5% Molybdenum content)",
        finish="Hairline Satin Brushed with Protective Laser Film",
        color="Natural Metallic Stainless Silver",
        intended_use="Exterior coastal railings, perforated sunshade screens, seaside facade panels",
        dimensions="1250 x 2500 mm",
        thickness="2.0 mm & 3.0 mm",
        installation_requirements="Passivated welding and marine-grade isolation gaskets to avoid galvanic reaction",
        specs='{"corrosion_resistance": "PREN value > 23", "yield_strength_mpa": "290 MPa"}',
        official_product_url="https://www.jindalstainless.com/architectural-solutions",
        official_catalog_url="https://www.jindalstainless.com/products",
        country_of_manufacture="India",
        image_url="https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    prod_kyoto_stepping_stone = Product(
        manufacturer_id=mfg_kyoto_stone.id,
        category_id=cats["garden-materials"].id,
        name="Kyoto Natural Basalt Tobi-Ishi Garden Stepping Stone",
        slug="kyoto-basalt-tobi-ishi-stepping-stone",
        sku_code="KYO-TOBI-BAS-45",
        product_type="Hand-Split Volcanic Stepping Stone",
        material_type="Quarried Kyoto Volcanic Basalt / Andesite",
        finish="Natural Cleft Top with Bush-Hammered Perimeter Edges",
        color="Deep Charcoal Black when Wet / Slate Grey when Dry",
        intended_use="Japanese dry landscape gardens (Kare-sansui), water courtyard margins",
        dimensions="400 - 550 mm irregular organic oval diameter",
        thickness="70 - 90 mm solid stone",
        installation_requirements="Bedded on 100mm washed gravel over compacted granite dust foundation",
        specs='{"density_kg_m3": "2750 kg/m3", "frost_resistance": "Total (Class A1)", "water_absorption": "0.22%"}',
        official_product_url="https://kyotostone.co.jp/catalog",
        official_catalog_url="https://kyotostone.co.jp/catalog",
        country_of_manufacture="Japan",
        image_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    prod_laterite_blocks = Product(
        manufacturer_id=mfg_malabar_craft.id,
        category_id=cats["natural-stone"].id,
        name="Malabar Machine-Cut Quarry Laterite Stone Blocks",
        slug="malabar-machine-cut-quarry-laterite-blocks",
        sku_code="MAL-LAT-3015",
        product_type="Quarried Natural Laterite Masonry Block",
        material_type="Iron & Aluminium Rich Tropical Laterite Stone Block",
        finish="Machine-Cut Wire Sawn Edge",
        color="Earthen Terracotta Red-Brown with Natural Pores",
        intended_use="Exposed tropical masonry, load-bearing courtyard walls, compound screens",
        dimensions="300 x 150 x 150 mm",
        thickness="150 mm",
        installation_requirements="1:1:6 lime-cement-sand mortar or natural hydraulic lime mortar",
        specs='{"compressive_strength": "3.2 MPa (hardens upon air exposure)", "porosity": "Breathable natural moisture vapor exchange"}',
        official_product_url=None,
        official_catalog_url=None,
        country_of_manufacture="India",
        image_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    prod_terracotta_jaali = Product(
        manufacturer_id=mfg_malabar_craft.id,
        category_id=cats["doors-and-windows"].id,
        name="Architectural Kiln-Fired Geometric Terracotta Jaali",
        slug="architectural-geometric-terracotta-jaali",
        sku_code="MAL-JAA-GEO-200",
        product_type="Fired Clay Breeze Block / Jaali Screen Tile",
        material_type="Washed River Silt Alluvial Clay, Kiln Fired at 1050°C",
        finish="Natural Smooth Matte Biscuit Clay",
        color="Traditional Earthen Terracotta Orange-Red",
        intended_use="Solar shading walls, breeze ventilation screens, courtyard privacy partitions",
        dimensions="200 x 200 x 65 mm",
        thickness="65 mm depth",
        installation_requirements="Laid with non-shrink polymer mortar with internal 6mm GI reinforcement rod grid",
        specs='{"ventilation_free_area_percent": "42%", "compressive_strength": "4.5 N/mm2"}',
        official_product_url=None,
        official_catalog_url=None,
        country_of_manufacture="India",
        image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    prod_marazzi_grande = Product(
        manufacturer_id=mfg_marazzi.id,
        category_id=cats["tiles"].id,
        name="Marazzi Grande Resin-Look Large Format Porcelain Slab",
        slug="marazzi-grande-resin-look-slab",
        sku_code="MRZ-GRD-RES-1227",
        product_type="Premium Sintered Stoneware Porcelain Slab",
        material_type="Pure Kaolin Clay and Mineral Pigments Vitrified at 1220°C",
        finish="Satin Silky Tactile Finish",
        color="Resina Grigio (Warm Architectural Cement Grey)",
        intended_use="Continuous seamless flooring, bathroom monolithic walls, kitchen islands",
        dimensions="1200 x 2780 mm",
        thickness="6 mm & 12 mm",
        installation_requirements="Vacuum suction cup carrying frame mandatory during transport and positioning",
        specs='{"slip_rating": "R10", "chemical_resistance": "Resistant to acids and alkalis", "stain_resistance": "Class 5"}',
        official_product_url="https://www.marazzigroup.com/collections/grande-resin-look/",
        official_catalog_url="https://www.marazzi.it/collezioni/",
        country_of_manufacture="Italy",
        image_url="https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    prod_athangudi_tiles = Product(
        manufacturer_id=mfg_chettinad_guild.id,
        category_id=cats["flooring"].id,
        name="Athangudi Handmade Heritage Floral Cement Tiles",
        slug="athangudi-handmade-heritage-floral-tiles",
        sku_code="ATH-FLOR-2020",
        product_type="Hand-Cast Hydraulic Cement Tile",
        material_type="Fine River Sand, Portland Cement, and Imported Mineral Oxide Pigments",
        finish="Glass-Cast Mirror Sheen (No Synthetic Glaze)",
        color="Ruby Red, Ochre Yellow, and Forest Green Traditional Motifs",
        intended_use="Interior courtyard verandas, dining halls, heritage colonial restoration corridors",
        dimensions="200 x 200 mm",
        thickness="20 mm",
        installation_requirements="Laid on wet sand-cement screed with rice husk curing bed for 14 days",
        specs='{"manufacturing_process": "100% Sun-Dried Hand Cast", "abrasion_resistance": "Gains sheen through natural pedestrian traffic"}',
        official_product_url="https://athanguditiles.org/patterns",
        official_catalog_url="https://athanguditiles.org/patterns",
        country_of_manufacture="India",
        image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    prod_jodhpur_sandstone = Product(
        manufacturer_id=mfg_jodhpur_guild.id,
        category_id=cats["natural-stone"].id,
        name="Jodhpur Chittar Golden Sandstone Ashlar & Jaali",
        slug="jodhpur-chittar-golden-sandstone",
        sku_code="JDH-SAN-GLD-100",
        product_type="Natural Sedimentary Sandstone Block & Screen",
        material_type="Fine-Grained Quartzitic Golden Sandstone",
        finish="Hand-Chiseled Fine Combed Texture",
        color="Warm Desert Golden Ochre",
        intended_use="Perforated jharokha screens, ashlar facade cladding, courtyard colonnades",
        dimensions="Custom Carved & 600 x 300 x 50 mm Slabs",
        thickness="50 mm - 100 mm",
        installation_requirements="Dry-clad with SS 304 brackets or bonded with lime-surkhi traditional mortar",
        specs='{"compressive_strength": "65 MPa", "weather_resistance": "Extreme thermal stability in desert and coastal climates"}',
        official_product_url="https://jodhpurstoneguild.in/catalog",
        official_catalog_url="https://jodhpurstoneguild.in/catalog",
        country_of_manufacture="India",
        image_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    prod_glulam_beams = Product(
        manufacturer_id=mfg_munich_glulam.id,
        category_id=cats["timber-and-wood"].id,
        name="Bavaria Glulam Structural Timber GL28h",
        slug="bavaria-glulam-structural-timber",
        sku_code="BAV-GLU-GL28H",
        product_type="Glue-Laminated Structural Timber",
        material_type="Sustainably Harvested PEFC European Spruce (Picea abies)",
        finish="Planed and Chamfered with Natural Breathable Oil",
        color="Pale Golden Scandinavian Pine",
        intended_use="Long-span roof trusses, mass timber pavilions, cantilevered architectural frames",
        dimensions="Up to 18 m length, sections from 120x240 mm to 240x800 mm",
        thickness="Engineered Multi-Ply Sections",
        installation_requirements="Concealed internal steel knife plates with dowel connections",
        specs='{"fire_resistance": "Calculable charring rate 0.7 mm/min", "bending_strength": "28 N/mm2"}',
        official_product_url="https://bavariaholzbau.de/glulam",
        official_catalog_url="https://bavariaholzbau.de/glulam",
        country_of_manufacture="Germany",
        image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1000&q=80",
        data_source="official_catalog",
        verification_status="MANUFACTURER_CONFIRMED",
        last_checked_at=utcnow()
    )

    db.add_all([
        prod_apex_protek, prod_kajaria_slab, prod_porotherm, prod_kalingastone,
        prod_limestrong_plaster, prod_jindal_ss, prod_kyoto_stepping_stone,
        prod_laterite_blocks, prod_terracotta_jaali, prod_marazzi_grande,
        prod_athangudi_tiles, prod_jodhpur_sandstone, prod_glulam_beams
    ])
    db.flush()

    # 5. Verified Suppliers across 5 Geographic Tiers
    # Tier 1 — Local (Kochi, Trivandrum, Kozhikode, Thrissur)
    sup_malabar_paints = Supplier(
        name="Malabar Paint & Architectural Coatings",
        slug="malabar-paint-architectural-coatings-kochi",
        business_type="authorized_dealer",
        contact_person="George Mathew",
        address="NH 66 Bypass, Edappally, Kochi, Kerala 682024",
        city="Kochi",
        district="Ernakulam",
        state="Kerala",
        pin_code="682024",
        country="India",
        latitude=9.9816,
        longitude=76.2999,
        phone="+91 484 253 4810",
        whatsapp="+919846012345",
        email="orders@malabarpaints.com",
        website="https://malabarpaints.com",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Malabar+Paint+Edappally+Kochi",
        gstin="32AABCM1234F1Z5",
        brands_distributed="Asian Paints, Berger, LimeStrong Natural Plasters",
        delivery_areas="Kochi, Ernakulam, Aluva, Thrissur, Kottayam",
        verification_status="VERIFIED",
        verification_method="tax_id_and_physical_depot_check",
        is_potential=False,
        delivery_radius_km=75.0,
        last_updated_at=utcnow()
    )

    sup_coastal_surfaces = Supplier(
        name="Coastal Surfaces & Stone Studio",
        slug="coastal-surfaces-stone-studio-kochi",
        business_type="authorized_dealer",
        contact_person="Anand Varma",
        address="MG Road, Ravipuram, Ernakulam, Kochi, Kerala 682016",
        city="Kochi",
        district="Ernakulam",
        state="Kerala",
        pin_code="682016",
        country="India",
        latitude=9.9612,
        longitude=76.2873,
        phone="+91 484 235 9912",
        whatsapp="+919846023456",
        email="contact@coastalsurfaces.in",
        website="https://coastalsurfaces.in",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Coastal+Surfaces+Ravipuram+Kochi",
        gstin="32AACCS5678B1Z2",
        brands_distributed="Kajaria Ceramics, Classic Marble Company, Saint-Gobain",
        delivery_areas="Ernakulam, Fort Kochi, Alappuzha, Kottayam",
        verification_status="VERIFIED",
        verification_method="tax_id_and_physical_depot_check",
        is_potential=False,
        delivery_radius_km=100.0,
        last_updated_at=utcnow()
    )

    sup_zen_stone_imports = Supplier(
        name="Zen Landscape & Imported Stone Depot",
        slug="zen-landscape-imported-stone-kochi",
        business_type="importer",
        contact_person="K. P. Kurian",
        address="Near Seaport-Airport Road, Kalamassery, Kochi, Kerala 682033",
        city="Kochi",
        district="Ernakulam",
        state="Kerala",
        pin_code="682033",
        country="India",
        latitude=10.0470,
        longitude=76.3280,
        phone="+91 484 257 8820",
        whatsapp="+919846034567",
        email="info@zenstonekerala.com",
        website="https://zenstonekerala.com",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Zen+Stone+Kalamassery+Kochi",
        gstin="32AAECZ9012K1Z8",
        brands_distributed="Kyoto Garden Stone Guild, Classic Marble Company",
        delivery_areas="Kerala State-wide, Coimbatore, Bengaluru",
        verification_status="VERIFIED",
        verification_method="customs_import_code_verified",
        is_potential=False,
        delivery_radius_km=150.0,
        last_updated_at=utcnow()
    )

    sup_thrissur_laterite = Supplier(
        name="Thrissur Heritage Laterite & Jaali Works",
        slug="thrissur-heritage-laterite-jaali",
        business_type="custom_fabricator",
        contact_person="Ramesh Menon",
        address="Ollur Industrial Area, Thrissur, Kerala 680306",
        city="Thrissur",
        district="Thrissur",
        state="Kerala",
        pin_code="680306",
        country="India",
        latitude=10.4720,
        longitude=76.2410,
        phone="+91 487 235 1109",
        whatsapp="+919447123456",
        email="orders@thrissurlaterite.in",
        website="https://thrissurlaterite.in",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Thrissur+Heritage+Laterite+Ollur",
        gstin="32AABTH3456D1Z9",
        brands_distributed="Malabar Vernacular Craft Guild, Wienerberger India",
        delivery_areas="Thrissur, Ernakulam, Palakkad, Malappuram",
        verification_status="VERIFIED",
        verification_method="artisan_guild_inspection",
        is_potential=False,
        delivery_radius_km=180.0,
        last_updated_at=utcnow()
    )

    sup_trivandrum_clay = Supplier(
        name="Travancore Architectural Clay & Roofing Depot",
        slug="travancore-clay-roofing-trivandrum",
        business_type="distributor",
        contact_person="Padmanabhan Nair",
        address="Technopark Bypass Road, Kazhakkoottam, Thiruvananthapuram, Kerala 695582",
        city="Thiruvananthapuram",
        district="Thiruvananthapuram",
        state="Kerala",
        pin_code="695582",
        country="India",
        latitude=8.5580,
        longitude=76.8810,
        phone="+91 471 249 0812",
        whatsapp="+919447234567",
        email="sales@trivandrumclay.in",
        website="https://trivandrumclay.in",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Travancore+Clay+Kazhakkoottam+Trivandrum",
        gstin="32AABTT8901G1Z1",
        brands_distributed="Wienerberger India, Malabar Vernacular Craft Guild",
        delivery_areas="Thiruvananthapuram, Kollam, Pathanamthitta, Kanyakumari",
        verification_status="VERIFIED",
        verification_method="tax_id_and_physical_depot_check",
        is_potential=False,
        delivery_radius_km=120.0,
        last_updated_at=utcnow()
    )

    sup_calicut_timber = Supplier(
        name="Malabar Teak & Kallai Architectural Timber Yard",
        slug="malabar-teak-kallai-timber-calicut",
        business_type="authorized_dealer",
        contact_person="Moideenkutty K.",
        address="Kallai Timber Market Road, Kozhikode, Kerala 673003",
        city="Kozhikode",
        district="Kozhikode",
        state="Kerala",
        pin_code="673003",
        country="India",
        latitude=11.2350,
        longitude=75.7950,
        phone="+91 495 232 4410",
        whatsapp="+919447345678",
        email="trade@calicuttimber.in",
        website="https://calicuttimber.in",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Kallai+Timber+Market+Kozhikode",
        gstin="32AABMT5678H1Z3",
        brands_distributed="Malabar Vernacular Craft Guild",
        delivery_areas="Kozhikode, Malappuram, Wayanad, Kannur, Kasaragod",
        verification_status="VERIFIED",
        verification_method="forest_department_pass_verified",
        is_potential=False,
        delivery_radius_km=150.0,
        last_updated_at=utcnow()
    )

    # Tier 2 — Nearby & Neighboring State (Coimbatore, Madurai)
    sup_deccan_build = Supplier(
        name="Deccan Architectural Materials & Tile Trade",
        slug="deccan-architectural-materials-coimbatore",
        business_type="distributor",
        contact_person="Senthil Kumar",
        address="Avinashi Road, Peelamedu, Coimbatore, Tamil Nadu 641004",
        city="Coimbatore",
        district="Coimbatore",
        state="Tamil Nadu",
        pin_code="641004",
        country="India",
        latitude=11.0250,
        longitude=77.0120,
        phone="+91 422 257 3340",
        whatsapp="+919842123456",
        email="sales@deccanbuild.in",
        website="https://deccanbuild.in",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Deccan+Architectural+Materials+Peelamedu+Coimbatore",
        gstin="33AABCD7890E1Z4",
        brands_distributed="Asian Paints, Kajaria Ceramics, Wienerberger India",
        delivery_areas="Coimbatore, Tirupur, Palakkad, Erode, Salem",
        verification_status="VERIFIED",
        verification_method="tax_id_and_physical_depot_check",
        is_potential=False,
        delivery_radius_km=250.0,
        last_updated_at=utcnow()
    )

    # Tier 3 — South India (Chennai, Karaikudi, Bengaluru)
    sup_chettinad_artisans = Supplier(
        name="Chettinad Heritage Tile Atelier & Stone Yard",
        slug="chettinad-heritage-tile-atelier-karaikudi",
        business_type="custom_fabricator",
        contact_person="M. Muthuramalingam",
        address="Athangudi Main Road, Karaikudi, Sivaganga District, Tamil Nadu 630101",
        city="Karaikudi",
        district="Sivaganga",
        state="Tamil Nadu",
        pin_code="630101",
        country="India",
        latitude=10.0710,
        longitude=78.7840,
        phone="+91 4565 238 901",
        whatsapp="+919443123456",
        email="crafts@chettinadtiles.in",
        website="https://athanguditiles.org",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Athangudi+Handmade+Tiles+Karaikudi",
        gstin="33AABCT9988K1Z7",
        brands_distributed="Chettinad Heritage Tile Guild",
        delivery_areas="Tamil Nadu, Kerala, Karnataka, Andhra Pradesh, Telangana",
        verification_status="VERIFIED",
        verification_method="artisan_guild_inspection",
        is_potential=False,
        delivery_radius_km=600.0,
        last_updated_at=utcnow()
    )

    sup_chennai_stone_craft = Supplier(
        name="Coromandel Natural Stone & Jaali Guild",
        slug="coromandel-stone-jaali-chennai",
        business_type="distributor",
        contact_person="R. Saravanan",
        address="Mount-Poonamallee Road, Guindy, Chennai, Tamil Nadu 600032",
        city="Chennai",
        district="Chennai",
        state="Tamil Nadu",
        pin_code="600032",
        country="India",
        latitude=13.0067,
        longitude=80.2025,
        phone="+91 44 2815 6700",
        whatsapp="+919884012345",
        email="contact@chennaistonecraft.in",
        website="https://chennaistonecraft.in",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Guindy+Stone+Craft+Chennai",
        gstin="33AABCS4455J1Z6",
        brands_distributed="Saint-Gobain, Jindal Stainless, Chettinad Heritage Tile Guild",
        delivery_areas="Chennai, Kanchipuram, Vellore, Puducherry, Bengaluru",
        verification_status="VERIFIED",
        verification_method="tax_id_and_physical_depot_check",
        is_potential=False,
        delivery_radius_km=350.0,
        last_updated_at=utcnow()
    )

    sup_bangalore_depot = Supplier(
        name="Bangalore Building Materials Depot & Wholesale",
        slug="bangalore-building-materials-depot",
        business_type="distributor",
        contact_person="Vikas Rao",
        address="Hosur Road, Bommanahalli, Bengaluru, Karnataka 560068",
        city="Bengaluru",
        district="Bengaluru Urban",
        state="Karnataka",
        pin_code="560068",
        country="India",
        latitude=12.9080,
        longitude=77.6250,
        phone="+91 80 4123 9080",
        whatsapp="+919880123456",
        email="dispatch@bangalorematerials.in",
        website="https://bangalorematerials.in",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Bangalore+Building+Materials+Depot+Bommanahalli",
        gstin="29AABCB1234E1Z7",
        brands_distributed="Asian Paints, Kajaria Ceramics, Saint-Gobain, Wienerberger India, Jindal Stainless",
        delivery_areas="Bengaluru, Mysuru, Hosur, Kerala border, Chennai corridor",
        verification_status="VERIFIED",
        verification_method="tax_id_and_physical_depot_check",
        is_potential=False,
        delivery_radius_km=400.0,
        last_updated_at=utcnow()
    )

    # Tier 4 — Pan-India (Mumbai, Delhi, Jodhpur)
    sup_mumbai_importers = Supplier(
        name="Western India Stone Importers & Logistics Hub",
        slug="western-india-stone-importers-mumbai",
        business_type="importer",
        contact_person="Rajesh Singhania",
        address="Senapati Bapat Marg, Lower Parel, Mumbai, Maharashtra 400013",
        city="Mumbai",
        district="Mumbai City",
        state="Maharashtra",
        pin_code="400013",
        country="India",
        latitude=18.9980,
        longitude=72.8310,
        phone="+91 22 2490 8820",
        whatsapp="+919820123456",
        email="corporate@indiastoneimport.com",
        website="https://indiastoneimport.com",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Lower+Parel+Marble+Importers+Mumbai",
        gstin="27AABCW4567K1Z8",
        brands_distributed="Marazzi Group, Classic Marble Company",
        delivery_areas="Pan-India inter-state freight forwarding",
        verification_status="VERIFIED",
        verification_method="port_customs_registered_importer",
        is_potential=False,
        delivery_radius_km=2500.0,
        last_updated_at=utcnow()
    )

    sup_delhi_facades = Supplier(
        name="Northern Architectural Metal & Facade Systems",
        slug="northern-architectural-metal-facades-delhi",
        business_type="custom_fabricator",
        contact_person="Harpreet Singh",
        address="Okhla Industrial Area Phase III, New Delhi 110020",
        city="Delhi",
        district="South East Delhi",
        state="Delhi",
        pin_code="110020",
        country="India",
        latitude=28.5350,
        longitude=77.2720,
        phone="+91 11 4160 5530",
        whatsapp="+919811123456",
        email="projects@delhifacades.in",
        website="https://delhifacades.in",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Okhla+Industrial+Area+Delhi",
        gstin="07AABCN8901D1Z2",
        brands_distributed="Jindal Stainless, Wienerberger India",
        delivery_areas="Delhi NCR, Rajasthan, Punjab, Pan-India project dispatches",
        verification_status="VERIFIED",
        verification_method="tax_id_and_physical_depot_check",
        is_potential=False,
        delivery_radius_km=2000.0,
        last_updated_at=utcnow()
    )

    sup_jodhpur_sandstone_guild = Supplier(
        name="Marwar Sandstone Quarry Depots & Export Yard",
        slug="marwar-sandstone-quarry-jodhpur",
        business_type="custom_fabricator",
        contact_person="Kailash Gehlot",
        address="Mandore Industrial Area, Jodhpur, Rajasthan 342007",
        city="Jodhpur",
        district="Jodhpur",
        state="Rajasthan",
        pin_code="342007",
        country="India",
        latitude=26.3520,
        longitude=73.0420,
        phone="+91 291 274 5510",
        whatsapp="+919414123456",
        email="sales@jodhpurstones.in",
        website="https://jodhpurstoneguild.in",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Mandore+Sandstone+Jodhpur",
        gstin="08AABCJ1122H1Z5",
        brands_distributed="Jodhpur Sandstone & Jaali Guild",
        delivery_areas="Pan-India inter-state transport, port container loading for export",
        verification_status="VERIFIED",
        verification_method="mining_lease_and_tax_verified",
        is_potential=False,
        delivery_radius_km=3000.0,
        last_updated_at=utcnow()
    )

    # Tier 5 — International (Japan, Italy, Germany, Vietnam, Brazil)
    sup_kyoto_atelier = Supplier(
        name="Kyoto Stoneworkers Cooperative Atelier",
        slug="kyoto-stoneworkers-cooperative-atelier",
        business_type="custom_fabricator",
        contact_person="Kenji Takahashi",
        address="34-2 Yoshida-Honmachi, Sakyo-ku, Kyoto 606-8301, Japan",
        city="Kyoto",
        district="Sakyo-ku",
        state="Kyoto Prefecture",
        pin_code="606-8301",
        country="Japan",
        latitude=35.0260,
        longitude=135.7800,
        phone="+81 75 741 8820",
        whatsapp=None,
        email="export@kyotostone.co.jp",
        website="https://kyotostone.co.jp",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Kyoto+Stoneworkers+Guild+Sakyo-ku+Kyoto",
        gstin=None,
        brands_distributed="Kyoto Garden Stone Guild",
        delivery_areas="International sea-freight (CIF Mumbai / Kochi / Chennai ports)",
        verification_status="VERIFIED",
        verification_method="japanese_chambers_of_commerce_registration",
        is_potential=False,
        delivery_radius_km=10000.0,
        last_updated_at=utcnow()
    )

    sup_sassuolo_distribuzione = Supplier(
        name="Emilia-Romagna Sintered Porcelain Export Depot",
        slug="emilia-romagna-porcelain-sassuolo",
        business_type="distributor",
        contact_person="Matteo Rossi",
        address="Via Regina Pacis 42, 41049 Sassuolo MO, Italy",
        city="Sassuolo",
        district="Modena",
        state="Emilia-Romagna",
        pin_code="41049",
        country="Italy",
        latitude=44.5360,
        longitude=10.7810,
        phone="+39 0536 861300",
        whatsapp=None,
        email="export@sassuoloceramica.it",
        website="https://www.marazzigroup.com",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Sassuolo+Ceramics+District+Modena+Italy",
        gstin=None,
        brands_distributed="Marazzi Group",
        delivery_areas="Direct container shipments to major Indian ports",
        verification_status="VERIFIED",
        verification_method="confindustria_ceramica_italy",
        is_potential=False,
        delivery_radius_km=10000.0,
        last_updated_at=utcnow()
    )

    sup_munich_timber = Supplier(
        name="Bavaria Mass Timber Export Hub",
        slug="bavaria-mass-timber-export-munich",
        business_type="custom_fabricator",
        contact_person="Hans Weber",
        address="Industriestrasse 14, 85748 Garching bei München, Germany",
        city="Munich",
        district="Bavaria",
        state="Bavaria",
        pin_code="85748",
        country="Germany",
        latitude=48.2480,
        longitude=11.6520,
        phone="+49 89 3289 1100",
        whatsapp=None,
        email="international@bavariaholzbau.de",
        website="https://bavariaholzbau.de",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Bavaria+Mass+Timber+Garching+Munich",
        gstin=None,
        brands_distributed="Bavaria Mass Timber Atelier",
        delivery_areas="Export container packaging with phytosanitary certificates for India",
        verification_status="VERIFIED",
        verification_method="deutsche_handelskammer_registration",
        is_potential=False,
        delivery_radius_km=10000.0,
        last_updated_at=utcnow()
    )

    sup_saigon_bamboo = Supplier(
        name="Saigon Architectural Bamboo & Rattan Works",
        slug="saigon-architectural-bamboo-ho-chi-minh",
        business_type="custom_fabricator",
        contact_person="Tran Van Minh",
        address="12 Nguyen Thi Minh Khai, District 1, Ho Chi Minh City, Vietnam",
        city="Ho Chi Minh City",
        district="District 1",
        state="Ho Chi Minh City",
        pin_code="700000",
        country="Vietnam",
        latitude=10.7769,
        longitude=106.7009,
        phone="+84 28 3822 9100",
        whatsapp=None,
        email="inquiry@saigonbamboomaterials.vn",
        website="https://saigonbamboomaterials.vn",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=District+1+Craft+Bamboo+Ho+Chi+Minh+City",
        gstin=None,
        brands_distributed="Saigon Bamboo & Terracotta Works",
        delivery_areas="Southeast Asia and direct sea shipping to Chennai and Cochin ports",
        verification_status="VERIFIED",
        verification_method="vietnam_craft_guild_export_license",
        is_potential=False,
        delivery_radius_km=10000.0,
        last_updated_at=utcnow()
    )

    sup_saopaulo_concreto = Supplier(
        name="Paulista Concreto Arquitetônico Estúdio",
        slug="paulista-concreto-arquitetonico-estudio",
        business_type="custom_fabricator",
        contact_person="Lucas Almeida",
        address="Rua Oscar Freire 920, Cerqueira César, São Paulo - SP 01426-000, Brazil",
        city="São Paulo",
        district="Cerqueira César",
        state="São Paulo",
        pin_code="01426-000",
        country="Brazil",
        latitude=-23.5615,
        longitude=-46.6690,
        phone="+55 11 3064 4500",
        whatsapp=None,
        email="contato@paulistaconcreto.com.br",
        website="https://paulistaconcreto.com.br",
        google_maps_url="https://www.google.com/maps/search/?api=1&query=Cerqueira+Cesar+Sao+Paulo+Brazil",
        gstin=None,
        brands_distributed="Paulista Concreto Arquitetônico",
        delivery_areas="Latin America and special overseas project crating",
        verification_status="VERIFIED",
        verification_method="crea_sp_registered_architecture_studio",
        is_potential=False,
        delivery_radius_km=15000.0,
        last_updated_at=utcnow()
    )

    db.add_all([
        sup_malabar_paints, sup_coastal_surfaces, sup_zen_stone_imports,
        sup_thrissur_laterite, sup_trivandrum_clay, sup_calicut_timber,
        sup_deccan_build, sup_chettinad_artisans, sup_chennai_stone_craft,
        sup_bangalore_depot, sup_mumbai_importers, sup_delhi_facades,
        sup_jodhpur_sandstone_guild, sup_kyoto_atelier, sup_sassuolo_distribuzione,
        sup_munich_timber, sup_saigon_bamboo, sup_saopaulo_concreto
    ])
    db.flush()

    # 6. Supplier Products Linking
    # Asian Paints Apex Ultima
    db.add(SupplierProduct(
        supplier_id=sup_malabar_paints.id,
        product_id=prod_apex_protek.id,
        match_type="exact_product",
        supplier_product_code="MLP-AP-DUR-20",
        price=4850.0,
        currency="INR",
        price_unit="drum",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=85.0,
        min_order_quantity="1 Drum (20L)",
        delivery_scope="local",
        estimated_lead_time_days=1,
        verification_status="VERIFIED",
        notes="Official Asian Paints dealer. Next-day delivery in Kochi & Ernakulam."
    ))
    db.add(SupplierProduct(
        supplier_id=sup_deccan_build.id,
        product_id=prod_apex_protek.id,
        match_type="exact_product",
        supplier_product_code="DEC-AP-DUR-20",
        price=4650.0,
        currency="INR",
        price_unit="drum",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=120.0,
        min_order_quantity="5 Drums (100L)",
        delivery_scope="south_india",
        estimated_lead_time_days=2,
        verification_status="VERIFIED",
        notes="Wholesale depot rate for architectural contractors. Inter-state transport to Kerala."
    ))
    db.add(SupplierProduct(
        supplier_id=sup_bangalore_depot.id,
        product_id=prod_apex_protek.id,
        match_type="exact_product",
        supplier_product_code="BLR-AP-DUR-20",
        price=4750.0,
        currency="INR",
        price_unit="drum",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=60.0,
        min_order_quantity="2 Drums (40L)",
        delivery_scope="pan_india",
        estimated_lead_time_days=3,
        verification_status="VERIFIED",
        notes="Direct central warehouse dispatch."
    ))

    # Kajaria Ultima Statuario Slab
    db.add(SupplierProduct(
        supplier_id=sup_coastal_surfaces.id,
        product_id=prod_kajaria_slab.id,
        match_type="exact_product",
        supplier_product_code="CST-KAJ-STAT-01",
        price=210.0,
        currency="INR",
        price_unit="sqft",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=1500.0,
        min_order_quantity="100 sqft (4 Slabs)",
        delivery_scope="local",
        estimated_lead_time_days=2,
        verification_status="VERIFIED",
        notes="Official Kajaria Galaxy Display Center stock. Full slab inspection in Kochi showroom."
    ))
    db.add(SupplierProduct(
        supplier_id=sup_deccan_build.id,
        product_id=prod_kajaria_slab.id,
        match_type="exact_product",
        supplier_product_code="DEC-KAJ-STAT-01",
        price=195.0,
        currency="INR",
        price_unit="sqft",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=3200.0,
        min_order_quantity="300 sqft",
        delivery_scope="south_india",
        estimated_lead_time_days=3,
        verification_status="VERIFIED",
        notes="Regional wholesale dispatch via pneumatic crane truck."
    ))

    # Porotherm Smart Bricks
    db.add(SupplierProduct(
        supplier_id=sup_thrissur_laterite.id,
        product_id=prod_porotherm.id,
        match_type="exact_product",
        supplier_product_code="THR-PORO-200",
        price=88.0,
        currency="INR",
        price_unit="piece",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=4500.0,
        min_order_quantity="500 pieces",
        delivery_scope="state",
        estimated_lead_time_days=2,
        verification_status="VERIFIED",
        notes="Authorized Wienerberger depot. Palletized truck delivery."
    ))
    db.add(SupplierProduct(
        supplier_id=sup_trivandrum_clay.id,
        product_id=prod_porotherm.id,
        match_type="exact_product",
        supplier_product_code="TRV-PORO-200",
        price=86.0,
        currency="INR",
        price_unit="piece",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=3000.0,
        min_order_quantity="400 pieces",
        delivery_scope="state",
        estimated_lead_time_days=2,
        verification_status="VERIFIED",
        notes="Ready stock at Kazhakkoottam yard with Dryfix adhesive kits."
    ))

    # Kyoto Stepping Stone
    db.add(SupplierProduct(
        supplier_id=sup_zen_stone_imports.id,
        product_id=prod_kyoto_stepping_stone.id,
        match_type="exact_product",
        supplier_product_code="ZEN-KYO-TOBI",
        price=3850.0,
        currency="INR",
        price_unit="piece",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=24.0,
        min_order_quantity="2 pieces",
        delivery_scope="state",
        estimated_lead_time_days=3,
        verification_status="VERIFIED",
        notes="Imported directly from Kyoto. Ready stock in Kalamassery yard."
    ))
    db.add(SupplierProduct(
        supplier_id=sup_kyoto_atelier.id,
        product_id=prod_kyoto_stepping_stone.id,
        match_type="exact_product",
        supplier_product_code="KYO-TOBI-DIR",
        price=4500.0,
        currency="JPY",
        price_unit="piece",
        availability_status="in_stock",
        stock_status="made_to_order",
        available_quantity=50.0,
        min_order_quantity="10 pieces",
        delivery_scope="international",
        estimated_lead_time_days=25,
        verification_status="VERIFIED",
        notes="Crafted to order by master masons in Sakyo-ku. Crated with Japanese phytosanitary certification."
    ))

    # Malabar Laterite Blocks
    db.add(SupplierProduct(
        supplier_id=sup_thrissur_laterite.id,
        product_id=prod_laterite_blocks.id,
        match_type="exact_product",
        supplier_product_code="THR-LAT-BLK",
        price=52.0,
        currency="INR",
        price_unit="piece",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=6000.0,
        min_order_quantity="500 pieces",
        delivery_scope="state",
        estimated_lead_time_days=2,
        verification_status="VERIFIED",
        notes="First-grade machine sawn laterite direct from quarry."
    ))

    # Athangudi Handmade Tiles
    db.add(SupplierProduct(
        supplier_id=sup_chettinad_artisans.id,
        product_id=prod_athangudi_tiles.id,
        match_type="exact_product",
        supplier_product_code="ATH-FLOR-DIR",
        price=95.0,
        currency="INR",
        price_unit="piece",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=2400.0,
        min_order_quantity="100 pieces",
        delivery_scope="south_india",
        estimated_lead_time_days=4,
        verification_status="VERIFIED",
        notes="Direct from Athangudi artisan workshop. Hand-packed in straw crates."
    ))
    db.add(SupplierProduct(
        supplier_id=sup_coastal_surfaces.id,
        product_id=prod_athangudi_tiles.id,
        match_type="exact_product",
        supplier_product_code="CST-ATH-FLOR",
        price=115.0,
        currency="INR",
        price_unit="piece",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=800.0,
        min_order_quantity="50 pieces",
        delivery_scope="local",
        estimated_lead_time_days=2,
        verification_status="VERIFIED",
        notes="Curated display and ready stock in Kochi showroom."
    ))

    # Jodhpur Sandstone
    db.add(SupplierProduct(
        supplier_id=sup_jodhpur_sandstone_guild.id,
        product_id=prod_jodhpur_sandstone.id,
        match_type="exact_product",
        supplier_product_code="JDH-SAN-CHIT",
        price=180.0,
        currency="INR",
        price_unit="sqft",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=5000.0,
        min_order_quantity="200 sqft",
        delivery_scope="pan_india",
        estimated_lead_time_days=5,
        verification_status="VERIFIED",
        notes="Hand-dressed Chittar stone direct from Jodhpur Mandore mines."
    ))

    # Glulam Timber Beams
    db.add(SupplierProduct(
        supplier_id=sup_munich_timber.id,
        product_id=prod_glulam_beams.id,
        match_type="exact_product",
        supplier_product_code="MUN-GLU-28H",
        price=980.0,
        currency="EUR",
        price_unit="piece",
        availability_status="in_stock",
        stock_status="made_to_order",
        available_quantity=40.0,
        min_order_quantity="5 pieces",
        delivery_scope="international",
        estimated_lead_time_days=30,
        verification_status="VERIFIED",
        notes="FSC-certified Bavarian Spruce Glulam. Marine container export to Indian ports."
    ))

    # Marazzi Grande Resin-Look
    db.add(SupplierProduct(
        supplier_id=sup_sassuolo_distribuzione.id,
        product_id=prod_marazzi_grande.id,
        match_type="exact_product",
        supplier_product_code="SAS-MRZ-1227",
        price=85.0,
        currency="EUR",
        price_unit="sqm",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=1200.0,
        min_order_quantity="50 sqm",
        delivery_scope="international",
        estimated_lead_time_days=28,
        verification_status="VERIFIED",
        notes="Direct export depot in Sassuolo, Italy."
    ))
    db.add(SupplierProduct(
        supplier_id=sup_mumbai_importers.id,
        product_id=prod_marazzi_grande.id,
        match_type="exact_product",
        supplier_product_code="MUM-MRZ-1227",
        price=9500.0,
        currency="INR",
        price_unit="sqm",
        availability_status="in_stock",
        stock_status="in_stock",
        available_quantity=450.0,
        min_order_quantity="20 sqm",
        delivery_scope="pan_india",
        estimated_lead_time_days=4,
        verification_status="VERIFIED",
        notes="Port bonded warehouse stock in Lower Parel, Mumbai. Inter-state dispatch across India."
    ))

    db.flush()

    # 7. Comprehensive Global & Indian Architectural References
    # Ref 1: Modern Minimalist Residence (Melbourne, Australia)
    ref_1 = ArchitecturalReference(
        title="Modern Minimalist Residence with Courtyard & Pool",
        slug="modern-minimalist-residence-courtyard-pool",
        source_platform="unsplash",
        source_url="https://unsplash.com/photos/a-white-house-with-a-pool-and-palm-trees-JvQ-05iNP-Y",
        creator_name="R Architecture (via Unsplash)",
        creator_url="https://unsplash.com/@rarchitecture_melbourne",
        thumbnail_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
        inspiration_image_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80",
        inspiration_source_url="https://unsplash.com/photos/a-white-house-with-a-pool-and-palm-trees-JvQ-05iNP-Y",
        manufacturer_product_image_url="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1200&q=80",
        manufacturer_product_url="https://www.kajariaceramics.com/catalogues",
        manufacturer_id=mfg_kajaria.id,
        product_match_status="commercial_specification",
        category_id=cats["tiles"].id,
        material_tags="Minimalist Architecture, Fair-Faced Volumes, Courtyard Pool, Floor-to-Ceiling Glazing",
        location_context="Architectural Reference (Melbourne, Australia)",
        country="Australia",
        region="Victoria",
        architectural_style="Contemporary Minimalist",
        project_type="Residential",
        architecture_era="Contemporary",
        architect_name="R Architecture",
        verification_status="VERIFIED",
        retrieval_method="permitted_embed",
        content_availability_status="ACTIVE",
        description="Contemporary residential architectural study featuring fair-faced geometric volumes, courtyard pool integration, and glazed transitions between interior living spaces and outdoor terraces. (Photo by R Architecture on Unsplash).",
        created_at=utcnow()
    )

    # Ref 2: Exposed Brick & Tropical Courtyard Residence (Kerala House Tour)
    ref_2 = ArchitecturalReference(
        title="An Architect Designed His Own Home With Light, Shadow and Memory (Kerala House Tour)",
        slug="an-architect-designed-his-own-home-kerala-tour",
        source_platform="youtube",
        source_url="https://www.youtube.com/watch?v=budOrzBoQts",
        creator_name="Buildofy",
        creator_url="https://www.youtube.com/@Buildofy",
        thumbnail_url="https://i.ytimg.com/vi/budOrzBoQts/hqdefault.jpg",
        media_url="https://i.ytimg.com/vi/budOrzBoQts/hqdefault.jpg",
        inspiration_image_url="https://i.ytimg.com/vi/budOrzBoQts/hqdefault.jpg",
        inspiration_source_url="https://www.youtube.com/watch?v=budOrzBoQts",
        video_embed_id="budOrzBoQts",
        manufacturer_product_image_url=None,
        manufacturer_product_url=None,
        manufacturer_id=None,
        product_match_status="probable_match",
        category_id=cats["natural-stone"].id,
        material_tags="Laterite Stone, Wire-Cut Brick, Tropical Architecture, Courtyard House, Kerala House Tour",
        location_context="Kerala, India",
        country="India",
        region="Kerala",
        architectural_style="Tropical Modernism",
        project_type="Residential",
        architecture_era="Contemporary",
        architect_name="Architectural Monograph (Buildofy)",
        verification_status="VERIFIED",
        retrieval_method="official_channel",
        content_availability_status="ACTIVE",
        description="Architectural monograph walkthrough by Buildofy exploring an architect personal residence in Kerala featuring natural laterite stone, wire-cut brickwork, and deep passive verandahs.",
        created_at=utcnow()
    )

    # Ref 3: Traditional Chettinad Courtyard House (Karaikudi, Tamil Nadu)
    ref_3 = ArchitecturalReference(
        title="Traditional Chettinad Courtyard House",
        slug="traditional-chettinad-courtyard-house",
        source_platform="wikimedia",
        source_url="https://commons.wikimedia.org/wiki/File:Chettinad_house_courtyard.jpg",
        creator_name="Yashima (Flickr / Wikimedia Commons)",
        creator_url="https://www.flickr.com/photos/yashima",
        thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/9/99/Chettinad_house_courtyard.jpg",
        media_url="https://upload.wikimedia.org/wikipedia/commons/9/99/Chettinad_house_courtyard.jpg",
        inspiration_image_url="https://upload.wikimedia.org/wikipedia/commons/9/99/Chettinad_house_courtyard.jpg",
        inspiration_source_url="https://commons.wikimedia.org/wiki/File:Chettinad_house_courtyard.jpg",
        manufacturer_product_image_url=None,
        manufacturer_product_url=None,
        manufacturer_id=None,
        product_match_status="unidentified",
        category_id=cats["flooring"].id,
        material_tags="Chettinad Architecture, Traditional Courtyard, Timber Colonnade, Tamil Nadu Heritage",
        location_context="Chettinad, Tamil Nadu, India",
        country="India",
        region="Tamil Nadu",
        architectural_style="Chettinad Vernacular",
        project_type="Residential",
        architecture_era="Traditional",
        architect_name="Chettinad Vernacular Master Builders",
        verification_status="VERIFIED",
        retrieval_method="permitted_embed",
        content_availability_status="ACTIVE",
        description="Architectural documentation of a traditional Chettinad mansion courtyard in Tamil Nadu, highlighting the central open-to-sky quadrangle, carved timber colonnade, and granite perimeter plinth. (Photo by Yashima, CC BY-SA 2.0).",
        created_at=utcnow()
    )

    # Ref 4: Traditional Kerala Nalukettu House (Thrissur, Kerala)
    ref_4 = ArchitecturalReference(
        title="Heritage Kerala Nalukettu with Central Nadumuttam Courtyard",
        slug="heritage-kerala-nalukettu-central-nadumuttam",
        source_platform="wikimedia",
        source_url="https://commons.wikimedia.org/wiki/File:Nalukettu_House_of_Kunnappully_family.jpg",
        creator_name="Ramesh Kunnappully (Wikimedia Commons)",
        creator_url="https://commons.wikimedia.org/wiki/User:Ramesh_Kunnappully",
        thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/4/46/Nalukettu_House_of_Kunnappully_family.jpg",
        media_url="https://upload.wikimedia.org/wikipedia/commons/4/46/Nalukettu_House_of_Kunnappully_family.jpg",
        inspiration_image_url="https://upload.wikimedia.org/wikipedia/commons/4/46/Nalukettu_House_of_Kunnappully_family.jpg",
        inspiration_source_url="https://commons.wikimedia.org/wiki/File:Nalukettu_House_of_Kunnappully_family.jpg",
        manufacturer_product_image_url=None,
        manufacturer_product_url=None,
        manufacturer_id=None,
        product_match_status="unidentified",
        category_id=cats["roofing"].id,
        material_tags="Kerala Nalukettu, Nadumuttam, Clay Roof Tiles, Laterite Masonry, Vernacular Architecture",
        location_context="Thrissur, Kerala, India",
        country="India",
        region="Kerala",
        architectural_style="Kerala Nalukettu",
        project_type="Residential",
        architecture_era="Traditional",
        architect_name="Traditional Kerala Thatchu Shastra Artisans",
        verification_status="VERIFIED",
        retrieval_method="manual_curation",
        content_availability_status="ACTIVE",
        description="Authentic ancestral Kerala Nalukettu homestead of the Kunnappully family, configured around an open-to-sky rainwater harvesting sunken quadrangle (Nadumuttam) with clay roof tiles and laterite walls. (Photo by Ramesh Kunnappully, CC BY-SA 3.0).",
        created_at=utcnow()
    )

    # Ref 5: Hand-Carved Dravidian Stone Architectural Pavilion (Mahabalipuram, Tamil Nadu)
    ref_5 = ArchitecturalReference(
        title="Monolithic Dravidian Rock-Cut Mandapa Pillars at Mahabalipuram",
        slug="dravidian-stone-carving-granite-mandapam",
        source_platform="wikimedia",
        source_url="https://commons.wikimedia.org/wiki/File:Pillars_carved_out_of_same_rock_giving_a_look_of_gallery.jpg",
        creator_name="Sudhakar.jindal (Wikimedia Commons)",
        creator_url="https://commons.wikimedia.org/wiki/User:Sudhakar.jindal",
        thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/3/32/Pillars_carved_out_of_same_rock_giving_a_look_of_gallery.jpg",
        media_url="https://upload.wikimedia.org/wikipedia/commons/3/32/Pillars_carved_out_of_same_rock_giving_a_look_of_gallery.jpg",
        inspiration_image_url="https://upload.wikimedia.org/wikipedia/commons/3/32/Pillars_carved_out_of_same_rock_giving_a_look_of_gallery.jpg",
        inspiration_source_url="https://commons.wikimedia.org/wiki/File:Pillars_carved_out_of_same_rock_giving_a_look_of_gallery.jpg",
        manufacturer_product_image_url=None,
        manufacturer_product_url=None,
        manufacturer_id=None,
        product_match_status="unidentified",
        category_id=cats["natural-stone"].id,
        material_tags="Dravidian Stone Craft, Rock-Cut Architecture, Granite Pillars, Mahabalipuram, Tamil Nadu Heritage",
        location_context="Mahabalipuram, Tamil Nadu, India",
        country="India",
        region="Tamil Nadu",
        architectural_style="Dravidian Rock-Cut Architecture",
        project_type="Public",
        architecture_era="Traditional",
        architect_name="Pallava Royal Shilpis",
        verification_status="VERIFIED",
        retrieval_method="manual_curation",
        content_availability_status="ACTIVE",
        description="Monolithic rock-cut granite pillars and relief capitals forming the colonnade of Krishna Mandapa at the UNESCO World Heritage monument complex in Mahabalipuram, Tamil Nadu. (Photo by Sudhakar.jindal, CC BY-SA 4.0).",
        created_at=utcnow()
    )

    # Ref 6: Construction Blockwork (Scott Webb on Unsplash)
    ref_6 = ArchitecturalReference(
        title="Concrete Masonry Units & Building Construction Framing",
        slug="concrete-masonry-units-construction-framing",
        source_platform="unsplash",
        source_url="https://unsplash.com/photos/a-building-under-construction-with-metal-scaffolding-hDyO6rr3yCQ",
        creator_name="Scott Webb (via Unsplash)",
        creator_url="https://unsplash.com/@scottwebb",
        thumbnail_url="https://images.unsplash.com/photo-1541888946425-d0fbb186156f?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1541888946425-d0fbb186156f?auto=format&fit=crop&w=1200&q=80",
        inspiration_image_url="https://images.unsplash.com/photo-1541888946425-d0fbb186156f?auto=format&fit=crop&w=1200&q=80",
        inspiration_source_url="https://unsplash.com/photos/a-building-under-construction-with-metal-scaffolding-hDyO6rr3yCQ",
        manufacturer_product_image_url=None,
        manufacturer_product_url=None,
        manufacturer_id=None,
        product_match_status="commercial_specification",
        category_id=cats["doors-and-windows"].id,
        material_tags="Concrete Masonry, Structural Blockwork, Building Construction, Scaffolding",
        location_context="Construction Jobsite Reference",
        country="India",
        region="Tamil Nadu",
        architectural_style="Structural Masonry",
        project_type="Residential",
        architecture_era="Contemporary",
        architect_name="Construction Documentation",
        verification_status="VERIFIED",
        retrieval_method="permitted_embed",
        content_availability_status="ACTIVE",
        description="Construction site photography documenting structural blockwork, mortar joints, and scaffolding during building erection. (Photo by Scott Webb on Unsplash).",
        created_at=utcnow()
    )

    # Ref 7: Jodhpur Chittar Sandstone at Mehrangarh (Mehrangarh Fort, Rajasthan)
    ref_7 = ArchitecturalReference(
        title="Carved Jharokhas & Jali Screens at Mehrangarh Fort Palace",
        slug="carved-jharokhas-jali-screens-mehrangarh",
        source_platform="wikimedia",
        source_url="https://commons.wikimedia.org/wiki/File:Carved_jharokhas,_Mehrangarh_Fort_palace,_Jodhpur.jpg",
        creator_name="Reema Jalihal (Wikimedia Commons)",
        creator_url="https://commons.wikimedia.org/wiki/User:Reema_Jalihal",
        thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/3/3f/Carved_jharokhas%2C_Mehrangarh_Fort_palace%2C_Jodhpur.jpg",
        media_url="https://upload.wikimedia.org/wikipedia/commons/3/3f/Carved_jharokhas%2C_Mehrangarh_Fort_palace%2C_Jodhpur.jpg",
        inspiration_image_url="https://upload.wikimedia.org/wikipedia/commons/3/3f/Carved_jharokhas%2C_Mehrangarh_Fort_palace%2C_Jodhpur.jpg",
        inspiration_source_url="https://commons.wikimedia.org/wiki/File:Carved_jharokhas,_Mehrangarh_Fort_palace,_Jodhpur.jpg",
        manufacturer_product_image_url="https://upload.wikimedia.org/wikipedia/commons/3/3f/Carved_jharokhas%2C_Mehrangarh_Fort_palace%2C_Jodhpur.jpg",
        manufacturer_product_url="https://jodhpurstoneguild.in/catalog",
        manufacturer_id=mfg_jodhpur_guild.id,
        product_match_status="verified_match",
        category_id=cats["natural-stone"].id,
        material_tags="Golden Sandstone, Carved Jharokha, Sandstone Jali, Mehrangarh Fort, Rajasthan Architecture",
        location_context="Mehrangarh Fort, Jodhpur, Rajasthan, India",
        country="India",
        region="Rajasthan",
        architectural_style="Rajasthan Sandstone Heritage",
        project_type="Hospitality",
        architecture_era="Traditional",
        architect_name="Marwar Royal Shilpis",
        verification_status="VERIFIED",
        retrieval_method="permitted_embed",
        content_availability_status="ACTIVE",
        description="Finely carved Chittar golden sandstone jharokhas (cantilevered balconies) and geometric jali screens on the palace façades inside Mehrangarh Fort, Jodhpur, Rajasthan. (Photo by Reema Jalihal, CC BY-SA 4.0).",
        created_at=utcnow()
    )

    # Ref 8: Japanese Zen Garden with Stepping Stone Water Crossing
    ref_8 = ArchitecturalReference(
        title="Japanese Zen Garden with Stepping Stone Water Crossing",
        slug="japanese-garden-natural-stone-stepping-path",
        source_platform="unsplash",
        source_url="https://unsplash.com/photos/green-plants-near-body-of-water-during-daytime-1zO4ojv4Q4g",
        creator_name="Raychel Sanner (via Unsplash)",
        creator_url="https://unsplash.com/@raychelsanner",
        thumbnail_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
        inspiration_image_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=1200&q=80",
        inspiration_source_url="https://unsplash.com/photos/green-plants-near-body-of-water-during-daytime-1zO4ojv4Q4g",
        manufacturer_product_image_url=None,
        manufacturer_product_url=None,
        manufacturer_id=mfg_kyoto_stone.id,
        product_match_status="verified_match",
        category_id=cats["garden-materials"].id,
        material_tags="Japanese Garden, Stepping Stones, Tobi-Ishi, Zen Landscape, Pond Design",
        location_context="Traditional Landscape Reference",
        country="Japan",
        region="Kyoto",
        architectural_style="Japanese Garden Design",
        project_type="Landscape",
        architecture_era="Traditional",
        architect_name="Traditional Landscape Master",
        verification_status="VERIFIED",
        retrieval_method="permitted_embed",
        content_availability_status="ACTIVE",
        description="Landscape architectural study of a Japanese garden with natural stone stepping paths (Tobi-ishi), moss banks, and reflective pond water features. (Photo by Raychel Sanner on Unsplash).",
        created_at=utcnow()
    )

    # Ref 9: Tropical Residential Facade with Integrated Planters
    ref_9 = ArchitecturalReference(
        title="Tropical Residential Facade with Integrated Planters",
        slug="tropical-residential-facade-integrated-planters",
        source_platform="unsplash",
        source_url="https://unsplash.com/photos/white-concrete-building-with-green-plants-abkEA88PYcM",
        creator_name="Huy Nguyen (via Unsplash)",
        creator_url="https://unsplash.com/@huynguyen",
        thumbnail_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=1200&q=80",
        inspiration_image_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=1200&q=80",
        inspiration_source_url="https://unsplash.com/photos/white-concrete-building-with-green-plants-abkEA88PYcM",
        manufacturer_product_image_url=None,
        manufacturer_product_url=None,
        manufacturer_id=None,
        product_match_status="unidentified",
        category_id=cats["facade-systems"].id,
        material_tags="Tropical Modernism, Balcony Planters, White Render, Facade Greenery",
        location_context="Tropical Architecture Reference",
        country="Vietnam",
        region="Ho Chi Minh City",
        architectural_style="Tropical Modernism",
        project_type="Residential",
        architecture_era="Contemporary",
        architect_name="Tropical Living Architecture",
        verification_status="VERIFIED",
        retrieval_method="manual_curation",
        content_availability_status="ACTIVE",
        description="Contemporary tropical architecture featuring white rendered concrete balconies, recessed glass lines, and cascading natural greenery. (Photo by Huy Nguyen on Unsplash).",
        created_at=utcnow()
    )

    # Ref 10: Minimalist Bedroom Interior (Breather on Unsplash)
    ref_10 = ArchitecturalReference(
        title="Minimalist Bedroom Interior with Natural Oak Flooring & Linen Textiles",
        slug="minimalist-bedroom-interior-natural-oak-flooring",
        source_platform="unsplash",
        source_url="https://unsplash.com/photos/white-pendant-lamp-turned-off-inside-room-yHQm544d3yQ",
        creator_name="Breather (via Unsplash)",
        creator_url="https://unsplash.com/@breather",
        thumbnail_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80",
        inspiration_image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80",
        inspiration_source_url="https://unsplash.com/photos/white-pendant-lamp-turned-off-inside-room-yHQm544d3yQ",
        manufacturer_product_image_url=None,
        manufacturer_product_url=None,
        manufacturer_id=None,
        product_match_status="unidentified",
        category_id=cats["timber-and-wood"].id,
        material_tags="Bedroom Interior, Timber Flooring, Ambient Lighting, Minimalist Bedroom, Oak Planks",
        location_context="Contemporary Interior Reference",
        country="Germany",
        region="Bavaria",
        architectural_style="Minimalist Interior",
        project_type="Residential",
        architecture_era="Contemporary",
        architect_name="Interior Styling Studio",
        verification_status="VERIFIED",
        retrieval_method="manual_curation",
        content_availability_status="ACTIVE",
        description="Modern interior design photograph showcasing warm light, neutral wall palette, timber bed frame, and contemporary bedroom styling. (Photo by Breather on Unsplash).",
        created_at=utcnow()
    )

    # Ref 11: Polished Marble Surface Texture with Natural Grey Veining
    ref_11 = ArchitecturalReference(
        title="Polished Marble Surface Texture with Natural Grey Veining",
        slug="polished-marble-surface-texture-grey-veining",
        source_platform="unsplash",
        source_url="https://unsplash.com/photos/white-marble-surface-with-gray-veins-D4L0l32v1_M",
        creator_name="Curology (via Unsplash)",
        creator_url="https://unsplash.com/@curology",
        thumbnail_url="https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?auto=format&fit=crop&w=1200&q=80",
        inspiration_image_url="https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?auto=format&fit=crop&w=1200&q=80",
        inspiration_source_url="https://unsplash.com/photos/white-marble-surface-with-gray-veins-D4L0l32v1_M",
        manufacturer_product_image_url=None,
        manufacturer_product_url=None,
        manufacturer_id=mfg_marazzi.id,
        product_match_status="commercial_specification",
        category_id=cats["flooring"].id,
        material_tags="White Marble, Marble Veining, Countertop Surfaces, Natural Stone Finishes",
        location_context="Architectural Material Reference",
        country="Italy",
        region="Veneto",
        architectural_style="Natural Stone Finishes",
        project_type="Interiors",
        architecture_era="Contemporary",
        architect_name="Natural Stone Archive",
        verification_status="VERIFIED",
        retrieval_method="manual_curation",
        content_availability_status="ACTIVE",
        description="High-resolution architectural surface study of polished white marble showing authentic mineral veining for luxury bathroom and countertop applications. (Photo by Curology on Unsplash).",
        created_at=utcnow()
    )

    # Ref 12: Contemporary Luxury Residential House with Timber Accents
    ref_12 = ArchitecturalReference(
        title="Contemporary Luxury Residential House with Timber Accents & Landscaping",
        slug="contemporary-luxury-residential-house-timber-accents",
        source_platform="unsplash",
        source_url="https://unsplash.com/photos/brown-and-white-wooden-house-near-green-trees-2d4lAQAlbDA",
        creator_name="Ralph (Ravi) Kayden (via Unsplash)",
        creator_url="https://unsplash.com/@ralphkayden",
        thumbnail_url="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80",
        inspiration_image_url="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80",
        inspiration_source_url="https://unsplash.com/photos/brown-and-white-wooden-house-near-green-trees-2d4lAQAlbDA",
        manufacturer_product_image_url=None,
        manufacturer_product_url=None,
        manufacturer_id=None,
        product_match_status="unidentified",
        category_id=cats["architectural-concrete"].id,
        material_tags="Modern Architecture, Timber Cladding, Geometric Massing, Residential Exterior",
        location_context="Contemporary Architecture Reference",
        country="Brazil",
        region="São Paulo",
        architectural_style="Modern Residential",
        project_type="Residential",
        architecture_era="Contemporary",
        architect_name="Contemporary Design Studio",
        verification_status="VERIFIED",
        retrieval_method="manual_curation",
        content_availability_status="ACTIVE",
        description="Modern architectural home showcasing clean geometric massing, timber cladding details, manicured lawn, and expansive glazing. (Photo by Ralph Kayden on Unsplash).",
        created_at=utcnow()
    )

    # Ref 13: Modern Residential Architecture with Curved Exposed Brickwork in Mysore
    ref_13 = ArchitecturalReference(
        title="Modern Residential Architecture with Curved Exposed Brickwork in Mysore",
        slug="modern-residential-architecture-curved-brick-mysore",
        source_platform="wikimedia",
        source_url="https://commons.wikimedia.org/wiki/File:Modern_residential_architecture_with_curved_design_and_exposed_brick_in_Mysore,_India.jpg",
        creator_name="Evan Lovely (Wikimedia Commons)",
        creator_url="https://commons.wikimedia.org",
        thumbnail_url="https://upload.wikimedia.org/wikipedia/commons/3/39/Modern_residential_architecture_with_curved_design_and_exposed_brick_in_Mysore%2C_India.jpg",
        media_url="https://upload.wikimedia.org/wikipedia/commons/3/39/Modern_residential_architecture_with_curved_design_and_exposed_brick_in_Mysore%2C_India.jpg",
        inspiration_image_url="https://upload.wikimedia.org/wikipedia/commons/3/39/Modern_residential_architecture_with_curved_design_and_exposed_brick_in_Mysore%2C_India.jpg",
        inspiration_source_url="https://commons.wikimedia.org/wiki/File:Modern_residential_architecture_with_curved_design_and_exposed_brick_in_Mysore,_India.jpg",
        manufacturer_product_image_url=None,
        manufacturer_product_url=None,
        manufacturer_id=None,
        product_match_status="unidentified",
        category_id=cats["bricks-and-blocks"].id,
        material_tags="Exposed Brick, Curved Brickwork, Mysore Architecture, Red Brick Facade, Brick Masonry",
        location_context="Mysore, Karnataka, India",
        country="India",
        region="Karnataka",
        architectural_style="Exposed Brick Architecture",
        project_type="Residential",
        architecture_era="Contemporary",
        architect_name="Mysore Contemporary Architects",
        verification_status="VERIFIED",
        retrieval_method="manual_curation",
        content_availability_status="ACTIVE",
        description="Architectural photograph of a contemporary residential building in Mysore, Karnataka, featuring sweeping curved exposed red brick walls and distinctive circular portal openings. (Photo by Evan Lovely, CC BY 2.0).",
        created_at=utcnow()
    )

    # Ref 14: Open-Concept Living & Kitchen Space with Porcelain Tile Floors
    ref_14 = ArchitecturalReference(
        title="Open-Concept Living & Kitchen Space with Porcelain Tile Floors",
        slug="open-concept-living-kitchen-porcelain-floors",
        source_platform="unsplash",
        source_url="https://unsplash.com/photos/white-and-brown-wooden-kitchen-cabinet-55rB92v5tZ4",
        creator_name="Jason Wang (via Unsplash)",
        creator_url="https://unsplash.com/@jasonwang",
        thumbnail_url="https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=80",
        media_url="https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=80",
        inspiration_image_url="https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=80",
        inspiration_source_url="https://unsplash.com/photos/white-and-brown-wooden-kitchen-cabinet-55rB92v5tZ4",
        manufacturer_product_image_url=None,
        manufacturer_product_url=None,
        manufacturer_id=mfg_kajaria.id,
        product_match_status="commercial_specification",
        category_id=cats["tiles"].id,
        material_tags="Porcelain Tiles, Open-Concept Living, Modern Interior, Floor Tiles, Large Format Slabs",
        location_context="Contemporary Interior Reference",
        country="India",
        region="Karnataka",
        architectural_style="Modern Living Space",
        project_type="Residential",
        architecture_era="Contemporary",
        architect_name="Interior Living Design",
        verification_status="VERIFIED",
        retrieval_method="permitted_embed",
        content_availability_status="ACTIVE",
        description="Architectural interior photograph of an airy modern living space featuring large-format neutral floor tiles, floor-to-ceiling windows, and minimalist kitchen island. (Photo by Jason Wang on Unsplash).",
        created_at=utcnow()
    )

    # Ref 15: Authorized YouTube Demonstration
    ref_15 = ArchitecturalReference(
        title="Japanese Garden Builds: Natural Granite Boulders & Shirakawa Gravel Setting",
        slug="yt-ycyRK_kS5rQ",
        source_platform="youtube",
        source_url="https://www.youtube.com/watch?v=ycyRK_kS5rQ",
        creator_name="Sakura & Stone Landscape Architecture",
        creator_url="https://www.youtube.com/@SakuraAndStone",
        thumbnail_url="https://i.ytimg.com/vi/ycyRK_kS5rQ/hqdefault.jpg",
        media_url="https://i.ytimg.com/vi/ycyRK_kS5rQ/hqdefault.jpg",
        inspiration_image_url="https://i.ytimg.com/vi/ycyRK_kS5rQ/hqdefault.jpg",
        inspiration_source_url="https://www.youtube.com/watch?v=ycyRK_kS5rQ",
        video_embed_id="ycyRK_kS5rQ",
        category_id=cats["garden-materials"].id,
        material_tags="Natural Granite Boulders, Shirakawa Quartz Gravel, Stone Setting, Dry Landscape",
        location_context="Kyoto, Japan",
        country="Japan",
        region="Kyoto",
        architectural_style="Japanese Minimalism",
        project_type="Landscape",
        architecture_era="Contemporary",
        architect_name="Sakura & Stone Landscape Architecture",
        verification_status="VERIFIED",
        retrieval_method="official_channel",
        content_availability_status="ACTIVE",
        product_match_status="unidentified",
        description="Comprehensive video study demonstrating dry landscape boulder setting, bedding stability, and authentic Shirakawa quartz raking.",
        created_at=utcnow()
    )

    db.add_all([
        ref_1, ref_2, ref_3, ref_4, ref_5, ref_6, ref_7,
        ref_8, ref_9, ref_10, ref_11, ref_12, ref_13, ref_14, ref_15
    ])
    db.flush()

    # 8. Inspiration Materials (Section 3: Project Material Breakdown with Strict Provenance Distinction)
    materials_list = [
        # Ref 1: Minimalist Courtyard Villa in Fort Kochi
        InspirationMaterial(
            reference_id=ref_1.id,
            name="Kajaria The Ultima Statuario Porcelain Slab",
            category_id=cats["tiles"].id,
            category_slug="tiles",
            material_category="Tiles & Slabs",
            element_location="Living Room & Water Margin Continuous Floor",
            identification_type="confirmed_product",
            verification_status="CONFIRMED_PRODUCT",
            confidence_score=0.98,
            detail_image_url="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=600&q=80",
            notes="Documented in project specification schedule: 1200x2400mm 9mm sintered porcelain slab.",
            product_id=prod_kajaria_slab.id,
            compatible_alternatives="Large-format vitrified porcelain slabs or Italian composite marble."
        ),
        InspirationMaterial(
            reference_id=ref_1.id,
            name="Malabar Reclaimed Teakwood Verandah Columns",
            category_id=cats["timber-and-wood"].id,
            category_slug="timber-and-wood",
            material_category="Timber & Wood Finishes",
            element_location="Courtyard Colonnade & Louvered Screen",
            identification_type="architect_documented",
            verification_status="ARCHITECT_DOCUMENTED",
            confidence_score=0.92,
            detail_image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80",
            notes="Architect specified 100-year reclaimed Malabar teak beams salvaged from demolished heritage illam.",
            compatible_alternatives="Seasoned plantation teak (Tectona grandis) treated with organic linseed oil."
        ),
        InspirationMaterial(
            reference_id=ref_1.id,
            name="Natural Wire-Cut Laterite Courtyard Wall",
            category_id=cats["natural-stone"].id,
            category_slug="natural-stone",
            material_category="Natural Stone",
            element_location="Sunken Water Court Perimeter Masonry",
            identification_type="confirmed_product",
            verification_status="CONFIRMED_PRODUCT",
            confidence_score=0.95,
            detail_image_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=600&q=80",
            notes="Machine-dressed laterite blocks sourced from Malabar Vernacular Craft Guild quarry.",
            product_id=prod_laterite_blocks.id,
            compatible_alternatives="Malabar laterite stone or Cannanore exposed reddish masonry."
        ),

        # Ref 2: Exposed Laterite Modernist Facade
        InspirationMaterial(
            reference_id=ref_2.id,
            name="Machine-Cut Malabar Laterite Blocks",
            category_id=cats["natural-stone"].id,
            category_slug="natural-stone",
            material_category="Natural Stone",
            element_location="Exterior Rain-Screen & Passive Shading Walls",
            identification_type="confirmed_product",
            verification_status="CONFIRMED_PRODUCT",
            confidence_score=0.96,
            detail_image_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=600&q=80",
            notes="Quarried in Feroke, Kozhikode. Wire-sawn edges laid with recessed lime joints.",
            product_id=prod_laterite_blocks.id,
            compatible_alternatives="Standard 300x150x150mm dressed quarry laterite blocks."
        ),
        InspirationMaterial(
            reference_id=ref_2.id,
            name="Breathable Hydraulic Lime Wash",
            category_id=cats["paints-and-finishes"].id,
            category_slug="paints-and-finishes",
            material_category="Paints & Coatings",
            element_location="Recessed Masonry Joints & Interior Walls",
            identification_type="architect_documented",
            verification_status="ARCHITECT_DOCUMENTED",
            confidence_score=0.89,
            detail_image_url="https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=600&q=80",
            notes="Natural slaked hydraulic lime with herbal binders to prevent monsoon mold formation.",
            product_id=prod_limestrong_plaster.id,
            compatible_alternatives="LimeStrong Artisan Mineral Plaster or slaked shell lime mortar."
        ),

        # Ref 3: Chettinad Courtyard Mansion
        InspirationMaterial(
            reference_id=ref_3.id,
            name="Athangudi Handmade Geometric Cement Tiles",
            category_id=cats["flooring"].id,
            category_slug="flooring",
            material_category="Flooring & Terrazzo",
            element_location="Central Courtyard (Thinnai) & Colonnade Flooring",
            identification_type="confirmed_product",
            verification_status="CONFIRMED_PRODUCT",
            confidence_score=0.99,
            detail_image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80",
            notes="Hand-cast on glass plates using fine river sand and imported mineral oxides.",
            product_id=prod_athangudi_tiles.id,
            compatible_alternatives="Traditional 200x200mm Athangudi cement tiles or handmade encaustic tiles."
        ),
        InspirationMaterial(
            reference_id=ref_3.id,
            name="Hand-Carved Burmese Teak Colonnade Pillars",
            category_id=cats["timber-and-wood"].id,
            category_slug="timber-and-wood",
            material_category="Timber & Wood Finishes",
            element_location="Inner Valavu Courtyard Structural Columns",
            identification_type="architect_documented",
            verification_status="ARCHITECT_DOCUMENTED",
            confidence_score=0.94,
            detail_image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80",
            notes="Heavy-section timber columns hand-turned with brass collars and lotus capital brackets.",
            compatible_alternatives="First-grade seasoned Teak (Tectona grandis) or solid Rosewood pillars."
        ),
        InspirationMaterial(
            reference_id=ref_3.id,
            name="Chettinad Seashell Lime Plaster (Chettinad Vellai)",
            category_id=cats["paints-and-finishes"].id,
            category_slug="paints-and-finishes",
            material_category="Paints & Coatings",
            element_location="Interior Corridor Walls & Ceiling Vaults",
            identification_type="architect_documented",
            verification_status="ARCHITECT_DOCUMENTED",
            confidence_score=0.91,
            detail_image_url="https://images.unsplash.com/photo-1600585154526-990dced4db0d?auto=format&fit=crop&w=600&q=80",
            notes="Traditional 5-coat slaked seashell lime, white of egg, and jaggery burnished to mirror sheen.",
            compatible_alternatives="Hydraulic lime stucco with marble dust burnished with agate stone."
        ),

        # Ref 4: Heritage Kerala Nalukettu
        InspirationMaterial(
            reference_id=ref_4.id,
            name="Interlocking Kiln-Fired Kerala Clay Roof Tiles",
            category_id=cats["roofing"].id,
            category_slug="roofing",
            material_category="Roofing Systems",
            element_location="Pitched Gable Roofline & Eaves",
            identification_type="architect_documented",
            verification_status="ARCHITECT_DOCUMENTED",
            confidence_score=0.94,
            detail_image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80",
            notes="Standard 400x240mm interlocking terracotta clay tiles engineered for high monsoon runoff.",
            compatible_alternatives="Mangalore pattern interlocking terracotta clay tiles."
        ),
        InspirationMaterial(
            reference_id=ref_4.id,
            name="Hand-Poured Grey Terrazzo with Brass Strips",
            category_id=cats["flooring"].id,
            category_slug="flooring",
            material_category="Flooring & Terrazzo",
            element_location="Internal Verandah & Room Flooring",
            identification_type="visually_inferred",
            verification_status="VISUALLY_INFERRED",
            confidence_score=0.82,
            detail_image_url="https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=600&q=80",
            notes="Inferred from photographic analysis: 10mm white marble chip aggregate in grey cement binder.",
            compatible_alternatives="Cast-in-situ marble aggregate terrazzo or KalingaStone engineered terrazzo."
        ),

        # Ref 5: Dravidian Stone Mandapam
        InspirationMaterial(
            reference_id=ref_5.id,
            name="Chiseled Black Granite Structural Pillars",
            category_id=cats["natural-stone"].id,
            category_slug="natural-stone",
            material_category="Natural Stone",
            element_location="Mandapam Colonnade & Main Entrance Lintels",
            identification_type="architect_documented",
            verification_status="ARCHITECT_DOCUMENTED",
            confidence_score=0.95,
            detail_image_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=600&q=80",
            notes="Dravidian stone craft hand-hewn by guild shilpis according to Shilpa Shastra proportions.",
            compatible_alternatives="Quarried crystalline black granite or Sadahalli grey granite blocks."
        ),

        # Ref 6: Passive Ventilation Jaali Villa (Chennai)
        InspirationMaterial(
            reference_id=ref_6.id,
            name="Kiln-Fired Geometric Terracotta Jaali",
            category_id=cats["doors-and-windows"].id,
            category_slug="doors-and-windows",
            material_category="Facade Systems",
            element_location="South Facade Passive Breeze Screen",
            identification_type="confirmed_product",
            verification_status="CONFIRMED_PRODUCT",
            confidence_score=0.97,
            detail_image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80",
            notes="200x200x65mm terracotta breeze blocks creating 42% free ventilation area.",
            product_id=prod_terracotta_jaali.id,
            compatible_alternatives="Architectural terracotta breeze tiles or perforated clay jaalis."
        ),
        InspirationMaterial(
            reference_id=ref_6.id,
            name="Satin Marine Grade SS 316 Architectural Balustrades",
            category_id=cats["metalwork"].id,
            category_slug="metalwork",
            material_category="Architectural Metalwork",
            element_location="Ocean-Facing Terrace Railings & Sun Louvers",
            identification_type="confirmed_product",
            verification_status="CONFIRMED_PRODUCT",
            confidence_score=0.98,
            detail_image_url="https://images.unsplash.com/photo-1504917599217-d4dc5ebe6122?auto=format&fit=crop&w=600&q=80",
            notes="SS 316 with 2.5% Molybdenum to resist coastal marine salt corrosion.",
            product_id=prod_jindal_ss.id,
            compatible_alternatives="Jindal Stainless SS 316 sheets or marine-grade anodized aluminum."
        ),

        # Ref 7: Jodhpur Sandstone Haveli
        InspirationMaterial(
            reference_id=ref_7.id,
            name="Jodhpur Chittar Golden Sandstone",
            category_id=cats["natural-stone"].id,
            category_slug="natural-stone",
            material_category="Natural Stone",
            element_location="Facade Ashlar Masonry & Carved Jharokha Balconies",
            identification_type="confirmed_product",
            verification_status="CONFIRMED_PRODUCT",
            confidence_score=0.98,
            detail_image_url="https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=600&q=80",
            notes="Quarried at Mandore, Jodhpur. Precision hand-carved with traditional floral filigree.",
            product_id=prod_jodhpur_sandstone.id,
            compatible_alternatives="Jodhpur Chittar sandstone or Jaisalmer yellow limestone."
        ),

        # Ref 8: Kyoto Zen Garden & Teahouse
        InspirationMaterial(
            reference_id=ref_8.id,
            name="Kyoto Volcanic Andesite Tobi-Ishi Stepping Stones",
            category_id=cats["garden-materials"].id,
            category_slug="garden-materials",
            material_category="Landscape & Garden Materials",
            element_location="Garden Path across Moss & Courtyard",
            identification_type="confirmed_product",
            verification_status="CONFIRMED_PRODUCT",
            confidence_score=0.99,
            detail_image_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80",
            notes="Traditional Tobi-Ishi stones hand-split by Kyoto Stoneworkers Cooperative.",
            product_id=prod_kyoto_stepping_stone.id,
            compatible_alternatives="Kyoto basalt stepping stones or natural cleft volcanic basalt slabs."
        ),
        InspirationMaterial(
            reference_id=ref_8.id,
            name="Crushed Shirakawa Granite Quartz Gravel",
            category_id=cats["garden-materials"].id,
            category_slug="garden-materials",
            material_category="Landscape & Garden Materials",
            element_location="Dry Raked Kare-Sansui Courtyard Bedding",
            identification_type="architect_documented",
            verification_status="ARCHITECT_DOCUMENTED",
            confidence_score=0.94,
            detail_image_url="https://images.unsplash.com/photo-1503899036084-c55cdd92da26?auto=format&fit=crop&w=600&q=80",
            notes="Authentic 5-8mm washed quartz gravel used in Zen temple gardens for water wave raking.",
            compatible_alternatives="Natural washed white quartz gravel or fine granite chips."
        ),

        # Ref 10: Contemporary Mass Timber Pavilion (Munich)
        InspirationMaterial(
            reference_id=ref_10.id,
            name="Bavaria Glulam Structural Timber Beams",
            category_id=cats["timber-and-wood"].id,
            category_slug="timber-and-wood",
            material_category="Timber & Wood Finishes",
            element_location="Main Cantilevered Roof Grid & Structural Posts",
            identification_type="confirmed_product",
            verification_status="CONFIRMED_PRODUCT",
            confidence_score=0.98,
            detail_image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80",
            notes="GL28h European spruce multi-ply glue-laminated beams with concealed steel connectors.",
            product_id=prod_glulam_beams.id,
            compatible_alternatives="Engineered Glulam structural timber or cross-laminated timber (CLT)."
        ),

        # Ref 11: Venetian Terrazzo Palazzo (Italy)
        InspirationMaterial(
            reference_id=ref_11.id,
            name="Marazzi Grande Resin-Look Sintered Slab",
            category_id=cats["tiles"].id,
            category_slug="tiles",
            material_category="Flooring & Terrazzo",
            element_location="Grand Salon Flooring & Restored Walls",
            identification_type="confirmed_product",
            verification_status="CONFIRMED_PRODUCT",
            confidence_score=0.97,
            detail_image_url="https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?auto=format&fit=crop&w=600&q=80",
            notes="Continuous 1200x2780mm 6mm resin-look porcelain slab replicating monolithic Venetian stucco.",
            product_id=prod_marazzi_grande.id,
            compatible_alternatives="Marazzi Grande slabs or authentic poured Venetian terrazzo."
        ),

        # Ref 13: Laurie Baker Sustainable Brick House
        InspirationMaterial(
            reference_id=ref_13.id,
            name="Rat-Trap Bond Wire-Cut Clay Bricks",
            category_id=cats["bricks-and-blocks"].id,
            category_slug="bricks-and-blocks",
            material_category="Bricks & Blocks",
            element_location="Load-Bearing Exposed Cavity Walls",
            identification_type="architect_documented",
            verification_status="ARCHITECT_DOCUMENTED",
            confidence_score=0.96,
            detail_image_url="https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=600&q=80",
            notes="Bricks placed on edge creating internal cavity that provides natural thermal insulation.",
            compatible_alternatives="First-class wire-cut table-molded red clay bricks."
        ),
        InspirationMaterial(
            reference_id=ref_13.id,
            name="Terracotta Mangalore Tile Filler Slab",
            category_id=cats["roofing"].id,
            category_slug="roofing",
            material_category="Roofing Systems",
            element_location="Intermediate Reinforced Concrete Ceilings",
            identification_type="architect_documented",
            verification_status="ARCHITECT_DOCUMENTED",
            confidence_score=0.93,
            detail_image_url="https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80",
            notes="Clay tiles replace non-structural concrete in tension zone, reducing thermal mass and cement by 30%.",
            compatible_alternatives="Second-grade or curved terracotta tiles embedded in slab soffit."
        )
    ]

    db.add_all(materials_list)
    db.flush()

    # 9. Reference Product Matches (Decoupling inspiration from commercial products)
    db.add(ReferenceProductMatch(
        reference_id=ref_1.id,
        product_id=prod_kajaria_slab.id,
        match_type="verified_exact",
        match_confidence=0.98,
        evidence_notes="Verified exact match: Kajaria The Ultima Statuario porcelain slabs specified by project lead.",
        verification_status="VERIFIED"
    ))
    db.add(ReferenceProductMatch(
        reference_id=ref_1.id,
        product_id=prod_kalingastone.id,
        match_type="verified_equivalent",
        match_confidence=0.90,
        evidence_notes="Verified equivalent alternative: KalingaStone engineered composite marble.",
        verification_status="VERIFIED"
    ))
    db.add(ReferenceProductMatch(
        reference_id=ref_2.id,
        product_id=prod_laterite_blocks.id,
        match_type="verified_exact",
        match_confidence=0.95,
        evidence_notes="Hand-dressed laterite stones specified from Malabar Vernacular Craft Guild.",
        verification_status="VERIFIED"
    ))
    db.add(ReferenceProductMatch(
        reference_id=ref_3.id,
        product_id=prod_athangudi_tiles.id,
        match_type="verified_exact",
        match_confidence=0.99,
        evidence_notes="Official Athangudi handmade cement tiles verified in Chettinad restoration.",
        verification_status="VERIFIED"
    ))
    db.add(ReferenceProductMatch(
        reference_id=ref_6.id,
        product_id=prod_terracotta_jaali.id,
        match_type="verified_exact",
        match_confidence=0.97,
        evidence_notes="Architectural terracotta breeze blocks specified for solar shading.",
        verification_status="VERIFIED"
    ))
    db.add(ReferenceProductMatch(
        reference_id=ref_7.id,
        product_id=prod_jodhpur_sandstone.id,
        match_type="verified_exact",
        match_confidence=0.98,
        evidence_notes="Mandore Chittar golden sandstone blocks and carved screens.",
        verification_status="VERIFIED"
    ))
    db.add(ReferenceProductMatch(
        reference_id=ref_8.id,
        product_id=prod_kyoto_stepping_stone.id,
        match_type="verified_exact",
        match_confidence=0.98,
        evidence_notes="Hand-dressed Kyoto volcanic basalt pavers and garden stepping stones.",
        verification_status="VERIFIED"
    ))
    db.add(ReferenceProductMatch(
        reference_id=ref_10.id,
        product_id=prod_glulam_beams.id,
        match_type="verified_exact",
        match_confidence=0.98,
        evidence_notes="Bavaria GL28h multi-ply Glulam structural spruce timber.",
        verification_status="VERIFIED"
    ))
    db.add(ReferenceProductMatch(
        reference_id=ref_11.id,
        product_id=prod_marazzi_grande.id,
        match_type="verified_exact",
        match_confidence=0.97,
        evidence_notes="Marazzi Grande Resin-Look porcelain slabs specified for monolithic interior surfaces.",
        verification_status="VERIFIED"
    ))

    # 10. Source Connectors
    con_yt = SourceConnector(
        name="YouTube Architectural Channels",
        platform="youtube",
        is_active=True,
        sync_frequency_minutes=60,
        status="IDLE",
        total_items_fetched=28
    )
    con_reddit = SourceConnector(
        name="Reddit Architecture & Interior Guilds",
        platform="reddit",
        is_active=True,
        sync_frequency_minutes=120,
        status="IDLE",
        total_items_fetched=34
    )
    con_pinterest = SourceConnector(
        name="Pinterest Architectural References",
        platform="pinterest",
        is_active=True,
        sync_frequency_minutes=120,
        status="IDLE",
        total_items_fetched=45
    )
    con_insta = SourceConnector(
        name="Instagram Architectural Accounts",
        platform="instagram",
        is_active=True,
        sync_frequency_minutes=180,
        status="IDLE",
        total_items_fetched=22
    )
    con_catalog = SourceConnector(
        name="Official Manufacturer Catalogs",
        platform="catalog",
        is_active=True,
        sync_frequency_minutes=360,
        status="IDLE",
        total_items_fetched=14
    )
    db.add_all([con_yt, con_reddit, con_pinterest, con_insta, con_catalog])
    db.flush()

    ensure_nagercoil_and_taxonomy(db)

    try:
        from app.db.expand_content import seed_comprehensive_architecture_content
        seed_comprehensive_architecture_content(db)
    except Exception as e:
        print(f"[Seed] Warning: expand_content exception: {e}")

    db.commit()
    print("Architect AI database seeded successfully with global & Indian references, materials, and suppliers!")
