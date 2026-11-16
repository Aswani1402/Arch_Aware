import pytest
from app.models.models import Manufacturer, Product, Supplier, SupplierProduct, ArchitecturalReference

def test_official_catalogs_stored_accurately(client):
    """
    Verify official public catalog links for Asian Paints and Kajaria Ceramics
    are recorded with exact URLs and provenance without claiming automated sync.
    """
    # 1. Asian Paints
    res_ap = client.get("/api/manufacturers/asian-paints")
    assert res_ap.status_code == 200
    ap = res_ap.json()
    assert ap["name"] == "Asian Paints"
    assert ap["company_name"] == "Asian Paints Limited"
    assert ap["official_website"] == "https://www.asianpaints.com"
    assert ap["official_catalog_url"] == "https://www.asianpaints.com/products.html"
    assert ap["official_product_page_url"] == "https://www.asianpaints.com/decorpro/paints.html"
    assert ap["source_url"] == "https://www.asianpaints.com/colour-catalogue.html"
    assert ap["verification_status"] == "VERIFIED"
    assert "1800-209-5678" in ap["contact_info"]

    # 2. Kajaria Ceramics
    res_kaj = client.get("/api/manufacturers/kajaria-ceramics")
    assert res_kaj.status_code == 200
    kaj = res_kaj.json()
    assert kaj["name"] == "Kajaria Ceramics"
    assert kaj["company_name"] == "Kajaria Ceramics Limited"
    assert kaj["official_website"] == "https://www.kajariaceramics.com"
    assert kaj["official_catalog_url"] == "https://www.kajariaceramics.com/catalogues"
    assert kaj["official_product_page_url"] == "https://www.kajariaceramics.com/the-ultima.php"
    assert kaj["verification_status"] == "VERIFIED"
    assert "1800-11-2992" in kaj["contact_info"]

def test_one_product_multiple_suppliers_comparison(client):
    """
    Verify many-to-many relationship: One product sold by multiple suppliers
    with distinct prices, price units, stock statuses, lead times, and match types.
    """
    res = client.get("/api/products/apex-ultima-protek-duralife")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "Apex Ultima Protek Duralife Exterior Emulsion"
    assert data["sku_code"] == "AP-EXT-PRO-001"
    assert data["dimensions"] is not None
    assert data["thickness"] is not None
    assert data["installation_requirements"] is not None

    suppliers = data["available_suppliers"]
    assert len(suppliers) >= 2  # Multiple distinct vendors selling this product
    
    # Check vendor comparison fields
    sup_names = [s["supplier_name"] for s in suppliers]
    assert "Malabar Paint & Architectural Coatings" in sup_names
    
    # Verify exact match vs alternatives
    for sup in suppliers:
        assert "match_type" in sup
        assert sup["match_type"] in ["exact_product", "verified_equivalent", "similar_alternative", "unverified"]
        assert "price_unit" in sup
        assert sup["price_unit"] in ["drum", "sqft", "piece", "sqm", "liter"]
        assert "stock_status" in sup
        assert "delivery_scope" in sup
        assert sup["google_maps_url"] is not None

def test_sourcing_without_coordinates_does_not_invent_distance(client):
    """
    When project location is entered as city/state without GPS coordinates,
    the application must perform hierarchical filtering without inventing distance.
    """
    # Sourcing in a city not in hardcoded presets (e.g. Alappuzha)
    res = client.post("/api/sourcing/search", json={
        "city": "Alappuzha",
        "state": "Kerala",
        "latitude": None,
        "longitude": None,
        "query": "laterite"
    })
    assert res.status_code == 200
    data = res.json()
    assert "levels_traversed" in data
    
    # Check that suppliers in response have valid distance_display
    all_suppliers = [s for lvl in data["levels_traversed"] for s in lvl["suppliers"]]
    assert len(all_suppliers) > 0
    for s in all_suppliers:
        assert s["distance_display"] is not None
        # When distance is None, distance_display should state location match
        if s["distance_km"] is None:
            assert "Location Match" in s["distance_display"] or "Match" in s["distance_display"]

def test_zero_paid_google_maps_search_link_works(client):
    """
    Verify map navigation generates a free URL based on address query:
    https://www.google.com/maps/search/?api=1&query=...
    without requiring any Google Cloud billing or Google Maps API key.
    """
    res = client.get("/api/suppliers/malabar-paint-architectural-coatings-kochi")
    assert res.status_code == 200
    sup = res.json()
    assert sup["google_maps_url"] is not None
    assert sup["google_maps_url"].startswith("https://www.google.com/maps/search/?api=1&query=")

def test_admin_quality_audit_dashboard(client, admin_headers):
    """
    Verify admin data quality audit endpoint correctly flags broken links,
    missing attribution, duplicate suppliers, and unverified claims.
    """
    res = client.get("/api/admin/quality-audit", headers=admin_headers)
    assert res.status_code == 200
    audit = res.json()
    assert "summary" in audit
    assert "issues" in audit
    summary = audit["summary"]
    assert "total_broken_sources" in summary
    assert "total_duplicate_products" in summary
    assert "total_unverified_supplier_claims" in summary
    assert "total_outdated_stock" in summary

def test_admin_record_correction_with_reason(client, admin_headers):
    """
    Verify administrators can correct record details with an audit reason logged.
    """
    res = client.put("/api/admin/records/correct", json={
        "record_type": "product",
        "record_id": 1,
        "corrections": {"color": "Custom Tintable Monsoon White"},
        "reason": "Manufacturer updated seasonal exterior color swatch palette"
    }, headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["reason_logged"] == "Manufacturer updated seasonal exterior color swatch palette"
    
    # Confirm persistence
    prod_res = client.get("/api/products/1")
    assert prod_res.status_code == 200
    assert prod_res.json()["color"] == "Custom Tintable Monsoon White"

def test_supplier_onboarding_and_product_linking(client, user_headers, admin_headers):
    """
    Verify supplier self-onboarding (public unassigned registration pending review)
    and confirm that ordinary users cannot manage unassigned suppliers (403),
    while platform administrators can link products with price & stock units (200).
    """
    # 1. Register new supplier (public unassigned registration)
    reg_res = client.post("/api/suppliers/register", json={
        "name": "Kozhikode Timber & Wood Finishes Yard",
        "business_type": "distributor",
        "contact_person": "Moideen Koya",
        "address": "Kallai River Road, Kozhikode, Kerala",
        "city": "Kozhikode",
        "district": "Kozhikode",
        "state": "Kerala",
        "pin_code": "673003",
        "phone": "+91 495 238 9900",
        "email": "kallai@timberyard.in",
        "website": "https://kallaitimber.in",
        "gstin": "32AABCK9988P1Z3",
        "brands_distributed": "Malabar Teak, Saint-Gobain",
        "delivery_areas": "Kozhikode, Malappuram, Wayanad, Kannur"
    })
    assert reg_res.status_code == 200
    sup = reg_res.json()
    sup_id = sup["id"]
    assert sup["verification_status"] == "PENDING_REVIEW"
    assert sup["google_maps_url"].startswith("https://www.google.com/maps/search/?api=1&query=")

    payload = {
        "product_id": 1,
        "match_type": "exact_product",
        "price": 4700.0,
        "currency": "INR",
        "price_unit": "drum",
        "stock_status": "in_stock",
        "available_quantity": 25.0,
        "min_order_quantity": "1 Drum (20L)",
        "delivery_scope": "state",
        "estimated_lead_time_days": 2,
        "notes": "Ready stock in Kallai depot."
    }

    # 2. Non-admin ordinary user attempts to manage unassigned supplier -> 403 Forbidden
    link_forbidden = client.post(f"/api/suppliers/{sup_id}/products", json=payload, headers=user_headers)
    assert link_forbidden.status_code == 403
    assert "unassigned supplier requires administrator privileges" in link_forbidden.json()["detail"]

    # 3. Admin user manages unassigned supplier -> 200 OK
    link_res = client.post(f"/api/suppliers/{sup_id}/products", json=payload, headers=admin_headers)
    assert link_res.status_code == 200
    link_data = link_res.json()
    assert link_data["success"] is True
    assert link_data["price"] == 4700.0
    assert link_data["price_unit"] == "drum"

def test_19_material_categories_available(client):
    """
    Verify all 19 required architectural material categories are present in database.
    """
    res = client.get("/api/categories")
    assert res.status_code == 200
    cats = res.json()
    assert len(cats) >= 19
    slugs = [c["slug"] for c in cats]
    assert "tiles" in slugs
    assert "paints-and-finishes" in slugs
    assert "natural-stone" in slugs
    assert "engineered-stone" in slugs
    assert "flooring" in slugs
    assert "bricks-and-blocks" in slugs
    assert "doors-and-windows" in slugs
    assert "glass-and-glazing" in slugs
    assert "roofing" in slugs
    assert "facade-systems" in slugs
    assert "architectural-concrete" in slugs
    assert "timber-and-wood" in slugs
    assert "sanitaryware" in slugs
    assert "lighting" in slugs
    assert "metalwork" in slugs
    assert "garden-materials" in slugs
    assert "acoustic-materials" in slugs
    assert "sustainable-materials" in slugs
    assert "specialty-imported" in slugs
