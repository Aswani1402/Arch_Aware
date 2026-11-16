from app.services.catalogue_import_service import import_catalogue_csv


def test_unified_keyword_explorer_endpoint(client, db):
    import_catalogue_csv(db)
    resp = client.get("/api/categories/keywords/unified")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["explorer_categories"]) == 14
    assert data["catalogue_tree"]["total_categories"] == 10
    assert data["catalogue_tree"]["total_subcategories"] == 184
    assert data["catalogue_tree"]["total_materials"] == 6319
    assert isinstance(data["custom_keywords"], list)


def test_keyword_search_returns_taxonomy_and_catalogue(client, db):
    import_catalogue_csv(db)
    resp = client.get("/api/categories/keywords/search", params={"q": "TMT"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["results"]) >= 1
    assert data["catalogue_total"] >= 1
    assert len(data["catalogue_results"]) >= 1

    # Bathroom Fittings regression check via feed + keyword library
    bath_kw = client.get("/api/categories/keywords/search", params={"q": "Bathroom Fittings"})
    assert bath_kw.status_code == 200
    assert len(bath_kw.json()["results"]) >= 1
    bath_feed = client.get("/api/feed", params={"q": "Bathroom Fittings", "page_size": 10})
    assert bath_feed.status_code == 200
    assert bath_feed.json()["total"] >= 1


def test_custom_keyword_save_list_delete(client):
    save_resp = client.post(
        "/api/categories/keywords/custom",
        json={"keyword": "Lime Surkhi Mortar", "category_name": "Construction Materials"},
    )
    assert save_resp.status_code == 200
    saved = save_resp.json()
    assert saved["keyword"] == "Lime Surkhi Mortar"
    assert saved["is_followed"] is True
    kw_id = saved["id"]

    list_resp = client.get("/api/categories/keywords/custom")
    assert list_resp.status_code == 200
    assert any(k["id"] == kw_id for k in list_resp.json())

    del_resp = client.delete(f"/api/categories/keywords/custom/{kw_id}")
    assert del_resp.status_code == 200
    assert del_resp.json()["deleted"] is True
