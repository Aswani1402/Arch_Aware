import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.llm_service import architectural_llm_service
from app.services.google_places_service import google_places_service
from app.connectors.youtube_connector import YouTubeConnector

@pytest.fixture
def client():
    return TestClient(app)

def test_live_youtube_search_endpoint(client):
    res = client.get("/api/feed/youtube-search?q=brick%20masonry&limit=3")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    first = items[0]
    assert first["source_platform"] == "youtube"
    assert "source_url" in first
    assert "video_embed_id" in first
    assert first["content_type"] == "youtube_walkthrough"

def test_llm_analyze_project_endpoint(client):
    res = client.post(
        "/api/llm/analyze-project",
        json={
            "title": "Modern Tropical Villa with Exposed Brick and Teak Louvers",
            "description": "Residence featuring Porotherm cavity brick walls, polished concrete, and seasoned teak wood joinery",
            "tags": ["brick", "concrete", "teak", "tropical"],
            "category": "Bricks & Masonry"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "identified_materials" in data
    assert len(data["identified_materials"]) >= 1
    assert "climate_suitability" in data
    assert "applicable_standards" in data or "recommended_sourcing_queries" in data

def test_llm_sourcing_advice_endpoint(client):
    res = client.post(
        "/api/llm/sourcing-advice",
        json={
            "query": "Weather-resistant exterior paint and drainage slabs for coastal home",
            "location": "Nagercoil",
            "material_type": "Paint & Coatings"
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert "advice" in data
    assert data["location"] == "Nagercoil"
    assert "Nagercoil" in data["advice"] or len(data["advice"]) > 50

def test_google_places_service_structure():
    assert hasattr(google_places_service, "search_nearby_suppliers")
    assert hasattr(google_places_service, "is_configured")
