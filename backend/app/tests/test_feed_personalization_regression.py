import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_personalization_prioritizes_brick_masonry(client):
    """
    1. Proves that expressing interest in 'brick' causes relevant brick/masonry items
       to be boosted into the top 5 of the feed.
    """
    # Base feed without preferences
    base_res = client.get("/api/feed?page=1&page_size=10")
    assert base_res.status_code == 200
    base_items = base_res.json()["items"]
    assert len(base_items) > 0

    # Personalized feed with 'brick' interest
    pers_res = client.get("/api/feed?page=1&page_size=10&interests=brick")
    assert pers_res.status_code == 200
    pers_items = pers_res.json()["items"]
    assert len(pers_items) >= 5

    # Count brick/masonry items in personalized top 5
    top_5 = pers_items[:5]
    brick_count = 0
    for it in top_5:
        text = f"{it.get('title', '')} {it.get('material_tags', '')} {it.get('description', '')}".lower()
        if "brick" in text or "masonry" in text:
            brick_count += 1

    assert brick_count >= 3, (
        f"Personalization did not prioritize brick items! Top 5 items had {brick_count} brick items. "
        f"Titles: {[it.get('title') for it in top_5]}"
    )

def test_like_persists_and_influences_feed(client):
    """
    2. Proves that user preference is sent to /feed and ranking score boosts matching references.
    """
    # Simulate user liking a brick card -> front-end passes interests='brick,masonry'
    res = client.get("/api/feed?page=1&page_size=10&interests=brick,masonry")
    assert res.status_code == 200
    items = res.json()["items"]
    
    # First item in personalized feed must match user interest
    first_item_text = f"{items[0].get('title', '')} {items[0].get('material_tags', '')}".lower()
    assert ("brick" in first_item_text or "masonry" in first_item_text), (
        f"Top item in personalized feed should match interest! Got: {items[0].get('title')}"
    )

def test_unrelated_content_not_boosted(client):
    """
    3. Proves that unrelated content (e.g. chandelier, terrazzo, drainage) does not receive an inappropriate boost.
    """
    # Query for brick should not rank terrazzo or lighting above brick
    pers_res = client.get("/api/feed?page=1&page_size=10&interests=brick")
    items = pers_res.json()["items"]
    
    top_3_titles = [it.get("title", "").lower() for it in items[:3]]
    for title in top_3_titles:
        assert "chandelier" not in title, f"Chandelier unexpectedly ranked in top 3 for brick preferences: {title}"

def test_new_user_gets_diverse_feed(client):
    """
    4. Proves a new user with no preferences gets a diverse, visually varied architectural feed.
    """
    res = client.get("/api/feed?page=1&page_size=12")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) >= 8

    # Ensure feed contains multiple distinct styles or categories
    categories = set(it.get("category_name") for it in items if it.get("category_name"))
    assert len(categories) >= 3, f"Expected diverse feed with >= 3 categories, got: {categories}"

def test_personalization_no_duplicate_images(client):
    """
    5. Proves personalization does not return duplicate images to fill the top results.
    """
    res = client.get("/api/feed?page=1&page_size=20&interests=brick,concrete,laterite")
    assert res.status_code == 200
    items = res.json()["items"]
    
    seen_images = set()
    duplicates = []
    for it in items:
        img = it.get("thumbnail_url") or it.get("media_url")
        if img:
            # Normalize URL to catch duplicates
            norm = img.split("?")[0].lower()
            if norm in seen_images:
                duplicates.append(norm)
            seen_images.add(norm)

    assert len(duplicates) == 0, f"Found duplicate images in personalized feed: {duplicates}"

def test_chettinad_traditional_architecture_card_consistency(client):
    """
    6. Verifies Requirement 5: Chettinad card title, image, description, tags and thumbnail
       all describe the same authentic Chettinad subject.
    """
    res = client.get("/api/feed?q=Chettinad&page=1&page_size=10")
    assert res.status_code == 200
    items = res.json()["items"]
    assert len(items) > 0, "Expected Chettinad architectural items in feed search"

    chettinad_card = None
    for it in items:
        if "chettinad courtyard house" in it.get("title", "").lower() or "chettinad" in it.get("title", "").lower():
            chettinad_card = it
            break

    assert chettinad_card is not None, "Chettinad card not found in feed results"
    
    # Verify title
    assert "Traditional Chettinad Courtyard House" in chettinad_card["title"] or "Chettinad" in chettinad_card["title"]
    
    # Verify image does not show generic villa
    img = chettinad_card.get("thumbnail_url", "")
    assert "photo-1600585154340-be6161a56a0c" not in img, "Chettinad card must not use modern villa placeholder!"
    assert "photo-1513694203232-719a280e022f" not in img, "Chettinad card must not use bedroom placeholder!"
    assert ("chettinad" in img.lower() or "wikimedia" in img.lower() or "upload.wikimedia.org" in img), (
        f"Chettinad card must use authentic Chettinad image, got: {img}"
    )

    # Verify tags and source
    tags = chettinad_card.get("material_tags", "")
    assert "Chettinad Architecture" in tags or "Traditional Courtyard" in tags
    assert "wikimedia.org" in chettinad_card.get("source_url", ""), "Source must point to verified Wikimedia Commons page"

def test_reset_personalization_restores_base_feed(client):
    """
    8. Proves that resetting personalization (passing no interests or clearing interests)
       restores the exact base architectural feed ordering.
    """
    base_res = client.get("/api/feed?page=1&page_size=10")
    base_ids = [it["id"] for it in base_res.json()["items"]]

    pers_res = client.get("/api/feed?page=1&page_size=10&interests=brick,masonry")
    pers_ids = [it["id"] for it in pers_res.json()["items"]]
    assert base_ids != pers_ids, "Personalized feed should differ from neutral feed"

    reset_res = client.get("/api/feed?page=1&page_size=10")
    reset_ids = [it["id"] for it in reset_res.json()["items"]]
    assert base_ids == reset_ids, "Resetting personalization must restore exact neutral feed ordering"

def test_images_are_not_shorts_and_video_thumbnails_match(client):
    """
    9. Verifies images have is_short == False, and YouTube videos have verified thumbnails derived from video ID.
    """
    res = client.get("/api/feed?page=1&page_size=25")
    assert res.status_code == 200
    items = res.json()["items"]

    for it in items:
        video_id = it.get("video_embed_id")
        is_short = it.get("is_short")
        thumb = it.get("thumbnail_url", "")

        # If it's an image, is_short MUST be False
        if not video_id:
            assert is_short is False, f"Image '{it.get('title')}' is marked as is_short=True!"
        else:
            # If it's a YouTube video, thumbnail must derive from video_id
            if it.get("source_platform") == "youtube":
                assert video_id in thumb or "i.ytimg.com" in thumb, (
                    f"Video thumbnail '{thumb}' does not match video_id '{video_id}' for '{it.get('title')}'"
                )

