import pytest
from app.models.models import Supplier, Product, User, SupplierProduct
from app.core.security import create_access_token


def test_link_supplier_product_unauthenticated_rejected(client):
    """
    Verify that an unauthenticated caller attempting to link a product
    to a supplier is rejected with HTTP 401 Unauthorized.
    """
    res = client.post("/api/suppliers/1/products", json={"product_id": 1})
    assert res.status_code == 401
    assert "detail" in res.json()


def test_link_supplier_product_invalid_token_rejected(client):
    """
    Verify that a request with an invalid/malformed token is rejected with HTTP 401.
    """
    res = client.post(
        "/api/suppliers/1/products",
        json={"product_id": 1},
        headers={"Authorization": "Bearer invalid.malformed.token"}
    )
    assert res.status_code == 401


def test_link_supplier_product_supplier_not_found(client, user_headers):
    """
    Verify that linking to a non-existent supplier returns HTTP 404.
    """
    res = client.post(
        "/api/suppliers/999999/products",
        json={"product_id": 1},
        headers=user_headers
    )
    assert res.status_code == 404
    assert res.json()["detail"] == "Supplier not found"


def test_link_supplier_product_missing_product_id(client, user_headers, db):
    """
    Verify that linking without product_id returns HTTP 400.
    """
    sup = db.query(Supplier).first()
    assert sup is not None

    res = client.post(
        f"/api/suppliers/{sup.id}/products",
        json={"price": 1200.0},
        headers=user_headers
    )
    assert res.status_code == 400
    assert "product_id is required" in res.json()["detail"]


def test_link_supplier_product_product_not_found(client, user_headers, db):
    """
    Verify that linking to a non-existent product returns HTTP 404.
    """
    sup = db.query(Supplier).first()
    assert sup is not None

    res = client.post(
        f"/api/suppliers/{sup.id}/products",
        json={"product_id": 999999},
        headers=user_headers
    )
    assert res.status_code == 404
    assert res.json()["detail"] == "Product not found"


def test_link_supplier_product_authenticated_success(client, user_headers, db):
    """
    Verify that an authenticated user can link a valid product to an unassigned supplier.
    """
    sup = db.query(Supplier).filter(Supplier.user_id.is_(None)).first()
    assert sup is not None
    prod = db.query(Product).first()
    assert prod is not None

    payload = {
        "product_id": prod.id,
        "match_type": "exact_product",
        "price": 3250.0,
        "currency": "INR",
        "price_unit": "sq_ft",
        "stock_status": "in_stock",
        "available_quantity": 500.0,
        "min_order_quantity": "50 sq ft",
        "delivery_scope": "national",
        "estimated_lead_time_days": 3,
        "notes": "Verified authentic inventory"
    }

    res = client.post(f"/api/suppliers/{sup.id}/products", json=payload, headers=user_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["supplier_id"] == sup.id
    assert data["product_id"] == prod.id
    assert data["price"] == 3250.0
    assert data["currency"] == "INR"


def test_link_supplier_product_ownership_rbac(client, db):
    """
    Verify RBAC isolation:
    - User A (owner) CAN link products to their supplier.
    - User B (different user) CANNOT link products to User A's supplier (403 Forbidden).
    - Admin CAN link products to any supplier regardless of ownership.
    """
    user_a = db.query(User).filter_by(email="architect@studio.com").first()
    user_b = db.query(User).filter_by(email="supplier@malabarpaints.com").first()
    assert user_a is not None
    assert user_b is not None

    prod = db.query(Product).first()
    assert prod is not None

    # Create a test supplier owned specifically by user A
    sup = Supplier(
        name="User A Proprietary Studio Depot",
        slug="user-a-proprietary-studio-depot",
        user_id=user_a.id,
        business_type="authorized_dealer",
        address="Panampilly Nagar, Kochi",
        city="Kochi",
        state="Kerala",
        country="India"
    )
    db.add(sup)
    db.commit()
    db.refresh(sup)

    token_a = create_access_token(subject=user_a.email, role=user_a.role)
    token_b = create_access_token(subject=user_b.email, role=user_b.role)
    token_admin = create_access_token(subject="admin@architect.ai", role="admin")

    headers_a = {"Authorization": f"Bearer {token_a}"}
    headers_b = {"Authorization": f"Bearer {token_b}"}
    headers_admin = {"Authorization": f"Bearer {token_admin}"}

    payload = {
        "product_id": prod.id,
        "price": 1500.0,
        "currency": "INR",
        "price_unit": "sq_ft"
    }

    # 1. User B attempts to modify User A's supplier -> 403 Forbidden
    res_b = client.post(f"/api/suppliers/{sup.id}/products", json=payload, headers=headers_b)
    assert res_b.status_code == 403
    assert "Not authorized" in res_b.json()["detail"]

    # 2. User A modifies their own supplier -> 200 OK
    res_a = client.post(f"/api/suppliers/{sup.id}/products", json=payload, headers=headers_a)
    assert res_a.status_code == 200
    assert res_a.json()["success"] is True

    # 3. Admin modifies User A's supplier -> 200 OK
    payload_admin = {
        "product_id": prod.id,
        "price": 1450.0,
        "currency": "INR",
        "price_unit": "sq_ft"
    }
    res_admin = client.post(f"/api/suppliers/{sup.id}/products", json=payload_admin, headers=headers_admin)
    assert res_admin.status_code == 200
    assert res_admin.json()["price"] == 1450.0

