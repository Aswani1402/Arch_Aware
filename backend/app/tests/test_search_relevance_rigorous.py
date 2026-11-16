import pytest
from fastapi.testclient import TestClient
from app.main import app
QUERIES_CONFIG = {
    "brick": {
        "required_evidence": ["brick", "masonry"],
        "forbidden_evidence": ["chandelier", "terrazzo flooring", "u-drain", "plumbing pipe"],
        "min_expected_matches": 3
    },
    "drainage": {
        "required_evidence": ["drain", "drainage", "stormwater", "culvert"],
        "forbidden_evidence": ["bedroom", "chandelier", "living room sofa", "residence with brick"],
        "min_expected_matches": 1
    },
    "cement": {
        "required_evidence": ["cement", "concrete", "mortar", "rcc"],
        "forbidden_evidence": ["bedroom loft", "chandelier"],
        "min_expected_matches": 2
    },
    "bedroom": {
        "required_evidence": ["bedroom", "bed", "wardrobe", "loft"],
        "forbidden_evidence": ["drainage", "bridge", "tmt rebar", "sewer"],
        "min_expected_matches": 2
    },
    "lighting": {
        "required_evidence": ["light", "lighting", "chandelier", "sconce", "lamp"],
        "forbidden_evidence": ["drainage slab", "concrete channel", "tmt bar"],
        "min_expected_matches": 2
    },
    "marble": {
        "required_evidence": ["marble", "vein", "carrara"],
        "forbidden_evidence": ["brick arch", "drainage channel", "tmt rebar"],
        "min_expected_matches": 2
    },
    "tiles": {
        "required_evidence": ["tile", "tiles", "porcelain", "vitrified"],
        "forbidden_evidence": ["bridge without pillars", "tmt rebar"],
        "min_expected_matches": 3
    },
    "garden waterfall": {
        "required_evidence": ["waterfall", "water feature", "pond", "rock"],
        "forbidden_evidence": ["bedroom", "chandelier", "tmt bar", "cooking"],
        "min_expected_matches": 1
    },
    "decorative pots": {
        "required_evidence": ["pot", "pots", "planter", "planters", "terracotta"],
        "forbidden_evidence": ["cooking pot", "pressure cooker", "drainage slab", "bridge"],
        "min_expected_matches": 1
    },
    "garden pathway": {
        "required_evidence": ["pathway", "walkway", "stepping stone", "paver"],
        "forbidden_evidence": ["chandelier", "false ceiling", "rebar"],
        "min_expected_matches": 1
    },
    "bathroom renovation": {
        "required_evidence": ["bathroom", "vanity", "shower", "renovation"],
        "forbidden_evidence": ["bridge", "drainage channel", "tmt bar"],
        "min_expected_matches": 1
    },
    "kitchen design": {
        "required_evidence": ["kitchen", "cabinet", "countertop", "modular"],
        "forbidden_evidence": ["bathroom shower", "drainage channel", "rebar"],
        "min_expected_matches": 1
    },
    "boundary wall": {
        "required_evidence": ["boundary wall", "wall", "masonry", "coping", "compound wall"],
        "forbidden_evidence": ["chandelier", "bedroom wardrobe", "bathroom shower"],
        "min_expected_matches": 1
    }
}

@pytest.mark.parametrize("query,rules", list(QUERIES_CONFIG.items()))
def test_search_relevance_rigorous(client, query, rules):
    """
    FEATURE 2: Test that all 13 critical architectural queries return
    positive topic evidence and zero forbidden concept contamination.
    """
    resp = client.get("/api/feed", params={"q": query, "page_size": 20})
    assert resp.status_code == 200
    data = resp.json()
    items = data.get("items", [])
    
    assert len(items) >= rules["min_expected_matches"], (
        f"Query '{query}' expected >= {rules['min_expected_matches']} matches, got {len(items)}"
    )

    for idx, item in enumerate(items, 1):
        title = item.get("title", "")
        desc = item.get("description", "")
        tags = item.get("material_tags", "")
        combined = f"{title} {desc} {tags}".lower()

        # Check positive topic evidence
        has_pos = any(ev.lower() in combined for ev in rules["required_evidence"])
        assert has_pos, f"Result #{idx} '{title}' for query '{query}' lacks positive evidence {rules['required_evidence']}"

        # Check negative contamination exclusion
        for forbidden in rules["forbidden_evidence"]:
            assert forbidden.lower() not in combined, (
                f"Result #{idx} '{title}' for query '{query}' contains forbidden contamination: '{forbidden}'"
            )
