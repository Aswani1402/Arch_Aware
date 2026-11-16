def test_login_flow(client):
    res = client.post("/api/auth/login", json={
        "email": "architect@studio.com",
        "password": "password123"
    })
    assert res.status_code == 200
    token_data = res.json()
    assert "access_token" in token_data
    assert token_data["user"]["email"] == "architect@studio.com"

def test_quotation_workflow(client, user_headers):
    # 1. Submit quotation request
    req_res = client.post("/api/quotations", json={
        "product_id": 1,
        "supplier_id": 1,
        "quantity": "25 Drums (500L)",
        "dimensions": "Standard 20L containers",
        "project_location": "Fort Kochi Heritage Villa Project",
        "city": "Kochi",
        "state": "Kerala",
        "pin_code": "682001",
        "delivery_urgency": "standard",
        "additional_notes": "Required in 2 phased batches for exterior stucco work."
    }, headers=user_headers)
    assert req_res.status_code == 200
    qr = req_res.json()
    qr_id = qr["id"]
    assert qr["status"] == "submitted"

    # 2. Supplier responds with formal quotation
    resp_res = client.post(f"/api/quotations/{qr_id}/respond", json={
        "quoted_price": 118750.0,
        "currency": "INR",
        "estimated_delivery_days": 3,
        "delivery_terms": "Door delivery via flatbed truck to Fort Kochi site.",
        "response_message": "We have ready stock in Edappally depot. Batch 1 can dispatch on Monday."
    }, headers=user_headers)
    assert resp_res.status_code == 200
    quoted = resp_res.json()
    assert quoted["quoted_price"] == 118750.0

def test_admin_stats(client, admin_headers, user_headers):
    # Unauthenticated and non-admin requests must be rejected
    assert client.get("/api/admin/stats").status_code == 401
    assert client.get("/api/admin/stats", headers=user_headers).status_code == 403

    res = client.get("/api/admin/stats", headers=admin_headers)
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_references"] >= 5
    assert stats["total_products"] >= 5
    assert stats["total_suppliers"] >= 5
