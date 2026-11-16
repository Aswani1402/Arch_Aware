import pytest
from fastapi.testclient import TestClient
from app.main import app

AUDIT_18_QUERIES = [
    ("Different types of bricks for a house", 3, ["brick", "masonry"], ["chandelier", "u-drain", "plumbing"]),
    ("Exposed brick wall", 1, ["brick", "exposed"], ["bedroom", "chandelier"]),
    ("AAC block wall", 1, ["aac", "block"], ["chandelier", "rebar"]),
    ("Laterite wall", 1, ["laterite"], ["chandelier", "rebar"]),
    ("Rammed earth wall", 1, ["rammed", "earth"], ["chandelier", "rebar"]),
    ("Marble flooring", 1, ["marble"], ["brick arch", "tmt bar"]),
    ("Wood-look tiles", 1, ["wood", "tile"], ["chandelier", "drain"]),
    ("Screws and bolts", 1, ["screw", "bolt", "fastener"], ["chandelier", "bedroom"]),
    ("Electrical switches and switchboards", 1, ["switch", "switchboard"], ["chandelier", "drain"]),
    ("Exterior lighting", 1, ["exterior", "facade", "lighting"], ["drainage slab", "concrete channel"]),
    ("Rainwater drainage", 1, ["drain", "stormwater", "drainage"], ["bedroom", "chandelier"]),
    ("Garden waterfall", 1, ["waterfall", "pond", "water feature"], ["bedroom", "chandelier"]),
    ("House renovation before and after", 1, ["renovation", "before"], ["drainage channel", "bridge"]),
    ("Kerala traditional house", 1, ["kerala", "nalukettu", "traditional"], ["chandelier", "drainage"]),
    ("Modern tropical architecture", 1, ["tropical", "architecture"], ["drainage", "bridge"]),
    ("Small bathroom design", 1, ["bathroom", "design"], ["bridge", "rebar"]),
    ("Kitchen storage", 1, ["kitchen", "storage"], ["bathroom shower", "rebar"]),
    ("Construction site walkthrough", 1, ["construction", "walkthrough", "site"], ["chandelier", "bedroom"])
]

@pytest.mark.parametrize("query,min_expected,required_evidence,forbidden_evidence", AUDIT_18_QUERIES)
def test_real_world_18_query_accuracy(client, query, min_expected, required_evidence, forbidden_evidence):
    """
    SECTION 2: Verify that each of the 18 exact real-world architectural queries
    returns positive evidence matches and ZERO concept contamination or unrelated items.
    """
    resp = client.get("/api/feed", params={"q": query, "page_size": 20})
    assert resp.status_code == 200
    data = resp.json()
    items = data.get("items", [])
    
    assert len(items) >= min_expected, (
        f"Query '{query}' expected >= {min_expected} matches, got {len(items)}"
    )

    seen_ids = set()
    for idx, item in enumerate(items, 1):
        # 1. Check for duplicates
        item_id = item.get("id")
        video_id = item.get("video_embed_id")
        assert item_id not in seen_ids, f"Duplicate item ID #{item_id} in query '{query}'"
        seen_ids.add(item_id)

        title = item.get("title", "")
        desc = item.get("description", "")
        tags = item.get("material_tags", "")
        combined = f"{title} {desc} {tags}".lower()

        # 2. Check positive topic evidence
        has_pos = any(ev.lower() in combined for ev in required_evidence)
        assert has_pos, (
            f"Result #{idx} '{title}' for query '{query}' lacks positive evidence {required_evidence}"
        )

        # 3. Check negative contamination exclusion
        for forbidden in forbidden_evidence:
            assert forbidden.lower() not in combined, (
                f"Result #{idx} '{title}' for query '{query}' contains forbidden contamination: '{forbidden}'"
            )
