import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_bathroom_fittings_keyword_recognition():
    """
    Test that 'Bathroom Fittings' is recognized by Keyword Explorer search API
    and maps to 'Bath Fittings, Faucets & Showers'.
    """
    response = client.get("/api/categories/keywords/search?q=Bathroom+Fittings")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    results = data["results"]
    assert len(results) > 0, "Expected at least one matching category for 'Bathroom Fittings'"

    # Must match Plumbing & Sanitaryware / Bath Fittings, Faucets & Showers
    subcat_names = []
    for cat in results:
        for match in cat.get("matches", []):
            subcat_names.append(match.get("subcategory"))

    assert "Bath Fittings, Faucets & Showers" in subcat_names, (
        f"Expected 'Bath Fittings, Faucets & Showers' in subcategories, got {subcat_names}"
    )

    # Synonyms should include bath fittings and related terms
    synonyms = data.get("synonyms", [])
    assert any("bath fittings" in s.lower() for s in synonyms), (
        f"Expected 'bath fittings' among synonyms, got {synonyms}"
    )


def test_bath_fittings_keyword_recognition():
    """
    Test that 'Bath Fittings' is recognized by Keyword Explorer search API.
    """
    response = client.get("/api/categories/keywords/search?q=Bath+Fittings")
    assert response.status_code == 200
    data = response.json()
    results = data.get("results", [])
    assert len(results) > 0

    subcat_names = [m.get("subcategory") for c in results for m in c.get("matches", [])]
    assert "Bath Fittings, Faucets & Showers" in subcat_names


def test_faucets_and_showers_recognition():
    """
    Test that 'Faucets' and 'Showers' are recognized by Keyword Explorer search API.
    """
    # Faucets
    resp_faucets = client.get("/api/categories/keywords/search?q=Faucets")
    assert resp_faucets.status_code == 200
    faucet_subcats = [m.get("subcategory") for c in resp_faucets.json().get("results", []) for m in c.get("matches", [])]
    assert "Bath Fittings, Faucets & Showers" in faucet_subcats

    # Showers
    resp_showers = client.get("/api/categories/keywords/search?q=Showers")
    assert resp_showers.status_code == 200
    shower_subcats = [m.get("subcategory") for c in resp_showers.json().get("results", []) for m in c.get("matches", [])]
    assert "Bath Fittings, Faucets & Showers" in shower_subcats


def test_unrelated_bathroom_queries_do_not_map_to_bath_fittings():
    """
    Test that unrelated bathroom queries (e.g. Bathroom Vanity, Bathroom Tile,
    Bathroom Door, Bathroom Mirror) do NOT falsely map to 'Bath Fittings, Faucets & Showers'.
    """
    unrelated_queries = [
        "Bathroom Vanity",
        "Bathroom Tile",
        "Bathroom Door",
        "Bathroom Mirror"
    ]

    for q in unrelated_queries:
        response = client.get(f"/api/categories/keywords/search?q={q.replace(' ', '+')}")
        assert response.status_code == 200
        results = response.json().get("results", [])
        matched_subcats = [m.get("subcategory") for c in results for m in c.get("matches", [])]

        assert "Bath Fittings, Faucets & Showers" not in matched_subcats, (
            f"Query '{q}' should NOT map to 'Bath Fittings, Faucets & Showers', but matched {matched_subcats}"
        )


def test_feed_search_bathroom_fittings_functional():
    """
    Test that the Feed search remains fully functional when queried for 'Bathroom Fittings'.
    """
    response = client.get("/api/feed?q=Bathroom+Fittings")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["total"] > 0, "Expected feed items for 'Bathroom Fittings'"
    assert len(data["items"]) > 0

