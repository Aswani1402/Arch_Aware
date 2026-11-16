import pytest
from app.services.vision_service import identify_materials_from_image, analyze_video_keyframes, _VISION_CACHE
from app.core.config import settings
from app.models.models import Supplier

def test_supplier_is_demo_flag_breakdown():
    """Verify that Gate G5 demo classification accurately marks 36 demo and 42 real suppliers in architect_ai.db."""
    import sqlite3
    con = sqlite3.connect("backend/architect_ai.db")
    cur = con.cursor()
    cur.execute("SELECT count(*) FROM suppliers")
    total = cur.fetchone()[0]
    assert total == 78

    cur.execute("SELECT count(*) FROM suppliers WHERE is_demo = 1")
    demo_count = cur.fetchone()[0]
    cur.execute("SELECT count(*) FROM suppliers WHERE is_demo = 0")
    real_count = cur.fetchone()[0]
    con.close()

    assert demo_count == 36, f"Expected 36 demo suppliers, got {demo_count}"
    assert real_count == 42, f"Expected 42 real suppliers, got {real_count}"

def test_vision_material_identification_tiers(db):
    """Vision AI distinguishes observed vs inferred (Tier 4) vs uncertain, and includes disclaimer."""
    img_url = "https://images.example.com/brick-villa-facade.jpg"
    res = identify_materials_from_image(image_url=img_url, title="Modern Brick Villa", db=db)
    
    assert res["status"] == "success"
    assert "disclaimer" in res
    assert "Visual AI detection is for design guidance only" in res["disclaimer"]
    
    all_detected = res["observed_materials"] + res["inferred_materials"] + res["uncertain_materials"]
    assert len(all_detected) >= 1
    
    for item in all_detected:
        assert "confidence" in item
        assert "evidence" in item
        assert item["tier"] in (4, 5)

def test_vision_caching():
    """Verify that identical image queries hit cache to avoid repeat costs."""
    img_url = "https://images.example.com/cached-facade.jpg"
    res1 = identify_materials_from_image(image_url=img_url, title="Cached Facade")
    assert res1["from_cache"] is False

    res2 = identify_materials_from_image(image_url=img_url, title="Cached Facade")
    assert res2["from_cache"] is True

def test_vision_kill_switch():
    """Vision kill switch immediately blocks external calls and returns disabled status."""
    img_url = "https://images.example.com/blocked-facade.jpg"
    original_switch = settings.VISION_KILL_SWITCH
    try:
        settings.VISION_KILL_SWITCH = True
        res = identify_materials_from_image(image_url=img_url, title="Blocked Facade")
        assert res["status"] == "disabled"
    finally:
        settings.VISION_KILL_SWITCH = original_switch

def test_video_keyframe_extraction():
    """Video analysis extracts 6-8 keyframes with timestamps, scenes, and material evidence."""
    video_url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
    res = analyze_video_keyframes(video_url=video_url, title="Contemporary Courtyard House Tour", duration_seconds=240)
    
    assert res["status"] == "success"
    assert 6 <= res["total_keyframes"] <= 8
    
    for kf in res["keyframes"]:
        assert "timestamp" in kf
        assert "seconds" in kf
        assert "scene_description" in kf
        assert "detected_material" in kf
        assert "evidence" in kf
        assert kf["tier"] == 4
