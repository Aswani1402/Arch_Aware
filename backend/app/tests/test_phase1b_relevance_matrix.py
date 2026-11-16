"""
MATERIQ — Phase 1B / Stage 1 55-Case Material Relevance Matrix Test Suite.
Tests the 5-Layer Query Matcher and Gate 0 Precedence engine deterministically.
Asserts exact metadata matching (Tier 1), verified catalogue aliases (Tier 2),
supported contextual matching (Tier 3), generic/conditional abstention (Tier 4),
and conflicting substrate / negative exclusions rejection (Tier 5).
"""

import pytest
from app.schemas.discovery import (
    InspirationRelevanceTierEnum,
    MediaStatusEnum,
    ProvenanceEnum,
)
from app.services.relevance_service import (
    relevance_matcher,
    APPROVED_MATERIAL_ALIASES,
    CONDITIONAL_OR_AMBIGUOUS_ALIASES,
    GENERIC_PARENT_NOUNS,
    normalize_relevance_text,
)


# ==============================================================================
# 11.1 POSITIVE MATCHING TEST CASES (20 Cases)
# ==============================================================================

POSITIVE_TEST_CASES = [
    # POS-01: Fly ash brick (ASTM C869 / IS 12894)
    ("POS-01", "Fly ash brick", "Fly ash brick masonry wall construction ASTM C869 compliance",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-02: Wire-cut brick (IS 1077 / IS 2117)
    ("POS-02", "Wire-cut brick", "Exposed red clay wire-cut brick facade architecture",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-03: Laterite block (Vernacular masonry)
    ("POS-03", "Laterite block", "Dressed natural laterite stone blocks for vernacular masonry walling",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_3_CONTEXTUAL]),

    # POS-04: Concrete hollow block (IS 2185 Pt 1)
    ("POS-04", "Concrete hollow block", "2-core load-bearing concrete hollow block masonry units CMU",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-05: AAC block (IS 2185 Pt 3 / ASTM C1693)
    ("POS-05", "AAC block", "Autoclaved aerated concrete AAC blocks for thermal insulation walling",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-06: Kota stone (GSI Rajasthan / IS 1130)
    ("POS-06", "Kota stone", "Honed greenish-grey Kota stone flooring slabs in courtyard",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-07: Italian marble flooring (ASTM C503)
    ("POS-07", "Italian marble flooring", "Bookmatched Italian marble flooring in residential villa",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-08: Black granite
    ("POS-08", "Black granite", "Flamed absolute black granite slab paving for outdoor walkway",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-09: Mangalore clay roof tile (IS 654:1992)
    ("POS-09", "Mangalore clay roof tile", "Terracotta interlocking Mangalore clay roof tile on timber rafters",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-10: Wood-wool acoustic panel
    ("POS-10", "Wood-wool acoustic panel", "Cement-bonded wood-wool acoustic panel boards for ceiling baffles",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-11: Teakwood entrance door (CPWD 2019 Cl 9.1 / IS 1003)
    ("POS-11", "Teakwood entrance door", "Solid teakwood entrance door with traditional brass fittings",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-12: Glass curtain wall
    ("POS-12", "Glass curtain wall", "Structural unitized glass curtain wall system on modern facade",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-13: Elastomeric exterior paint
    ("POS-13", "Elastomeric exterior paint", "Weatherproof flexible elastomeric exterior paint coating",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-14: Steel pipe pile
    ("POS-14", "Steel pipe pile", "Driven structural steel pipe pile foundation casing",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-15: Glass spider fitting (ASTM A351 / GANA)
    ("POS-15", "Glass spider fitting", "4-way stainless steel point-supported glass spider fitting",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-16: Drip irrigation pipe
    ("POS-16", "Drip irrigation pipe", "Inline pressure-compensating drip irrigation pipe lateral tubing",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-17: Western water closet
    ("POS-17", "Western water closet", "Wall-hung ceramic western water closet dual flush WC",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-18: Concrete paver block
    ("POS-18", "Concrete paver block", "Interlocking concrete paver block driveway paving",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-19: Precast compound wall panel (CPWD 2019 Cl 4.14)
    ("POS-19", "Precast compound wall panel", "Modular precast compound wall panel planks and columns",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # POS-20: Glass block
    ("POS-20", "Glass block", "Translucent patterned glass block masonry partition wall",
     [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
]

@pytest.mark.parametrize("case_id, query, candidate_title, allowed_tiers", POSITIVE_TEST_CASES)
def test_positive_matching_cases(case_id, query, candidate_title, allowed_tiers):
    tier, reason = relevance_matcher.classify(query, candidate_title)
    assert tier in allowed_tiers, f"{case_id} failed: Query '{query}' got {tier} ({reason}), expected one of {allowed_tiers}"


# ==============================================================================
# 11.2 NEGATIVE / MISLEADING MATCHING TEST CASES (20 Cases)
# ==============================================================================

NEGATIVE_TEST_CASES = [
    # NEG-01: Fly ash brick vs Red clay kiln brick
    ("NEG-01", "Fly ash brick", "Traditional red clay kiln-fired brick masonry wall"),

    # NEG-02: Wire-cut brick vs Wire mesh fencing
    ("NEG-02", "Wire-cut brick", "Galvanized wire mesh fencing panel and security boundary"),

    # NEG-03: Laterite block vs CSEB
    ("NEG-03", "Laterite block", "Compressed stabilized earth block CSEB wall construction"),

    # NEG-04: Concrete hollow block vs Solid block
    ("NEG-04", "Concrete hollow block", "Dense concrete solid block heavy foundation wall"),

    # NEG-05: AAC block vs Dense concrete block
    ("NEG-05", "AAC block", "Dense cement concrete block high density masonry"),

    # NEG-06: Kota stone vs Glazed porcelain tile with Kota print
    ("NEG-06", "Kota stone", "Glazed porcelain tile with Kota print pattern ceramic"),

    # NEG-07: Italian marble flooring vs Terrazzo with marble chips
    ("NEG-07", "Italian marble flooring", "Terrazzo flooring with marble chips composite cement"),

    # NEG-08: Black granite vs Black slate wall cladding
    ("NEG-08", "Black granite", "Natural black slate wall cladding tiles"),

    # NEG-09: Mangalore clay roof tile vs Corrugated metal roofing sheet
    ("NEG-09", "Mangalore clay roof tile", "Corrugated metal roofing sheet galvanized steel"),

    # NEG-10: Wood-wool acoustic panel vs Fiberglass insulation roll
    ("NEG-10", "Wood-wool acoustic panel", "Fiberglass insulation roll glasswool thermal batt"),

    # NEG-11: Teakwood entrance door vs PVC flush door with teak sticker
    ("NEG-11", "Teakwood entrance door", "PVC laminated flush door with teak sticker decal"),

    # NEG-12: Glass curtain wall vs Aluminum sliding window
    ("NEG-12", "Glass curtain wall", "Standard aluminum sliding window punched opening"),

    # NEG-13: Elastomeric exterior paint vs Interior distemper/emulsion
    ("NEG-13", "Elastomeric exterior paint", "Interior distemper emulsion paint for bedroom walls"),

    # NEG-14: Steel pipe pile vs PVC plumbing drainage pipe
    ("NEG-14", "Steel pipe pile", "PVC plumbing drainage pipe underground sewer"),

    # NEG-15: Glass spider fitting vs Plastic shower glass bracket
    ("NEG-15", "Glass spider fitting", "Plastic shower glass bracket bathroom fitting"),

    # NEG-16: Drip irrigation pipe vs Garden hose reel
    ("NEG-16", "Drip irrigation pipe", "Flexible garden hose reel watering kit"),

    # NEG-17: Western water closet vs Squat toilet / Indian pan
    ("NEG-17", "Western water closet", "Squat toilet ceramic Indian pan squatting WC"),

    # NEG-18: Concrete paver block vs Asphalt / bitumen road surfacing
    ("NEG-18", "Concrete paver block", "Asphalt bitumen road surfacing macadam pavement"),

    # NEG-19: Precast compound wall panel vs Brick boundary wall with plaster
    ("NEG-19", "Precast compound wall panel", "Traditional brick boundary wall with plaster wet masonry"),

    # NEG-20: Glass block vs Clear acrylic bathroom shelf
    ("NEG-20", "Glass block", "Clear acrylic bathroom shelf polymer rack"),
]

@pytest.mark.parametrize("case_id, query, candidate_title", NEGATIVE_TEST_CASES)
def test_negative_matching_cases(case_id, query, candidate_title):
    tier, reason = relevance_matcher.classify(query, candidate_title)
    assert tier == InspirationRelevanceTierEnum.TIER_5_REJECTED, (
        f"{case_id} failed: Expected TIER_5_REJECTED for conflicting pair, but got {tier} ({reason})"
    )


# ==============================================================================
# 11.3 ALIAS & SPELLING-VARIATION TEST CASES (10 Cases)
# ==============================================================================

def test_ali_01_flyash_bricks():
    # ALI-01: "Flyash bricks" -> [168] Fly ash brick (IS 12894:2002 Cl. 1.1 & 3.1)
    tier, reason = relevance_matcher.classify("Flyash bricks", "Fly ash brick manufacturing ASTM standard")
    assert tier == InspirationRelevanceTierEnum.TIER_2_ALIAS
    assert "IS 12894" in reason

def test_ali_02_wirecut_clay_brick():
    # ALI-02: "Wirecut clay brick" -> [166] Wire-cut brick (IS 1077 / IS 2117)
    tier, reason = relevance_matcher.classify("Wirecut clay brick", "Wire-cut brick architectural facade")
    assert tier == InspirationRelevanceTierEnum.TIER_2_ALIAS
    assert "IS 1077" in reason

def test_ali_03_hollow_blocks_abstention():
    # ALI-03: "Hollow blocks" -> Umbrella term without confirmed substrate (IS 2185 Pt 1 vs IS 3952)
    tier, reason = relevance_matcher.classify("Hollow blocks", "Generic hollow blocks supply")
    assert tier == InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS
    assert "Umbrella trade term" in reason

def test_ali_04_aac_block_expansion():
    # ALI-04: "Autoclaved aerated concrete block" -> [171] AAC block (IS 2185 Pt 3 / ASTM C1693)
    tier, reason = relevance_matcher.classify("Autoclaved aerated concrete block", "AAC block masonry lightweight")
    assert tier == InspirationRelevanceTierEnum.TIER_2_ALIAS
    assert "IS 2185 Pt. 3" in reason

def test_ali_05_kota_limestone():
    # ALI-05: "Kota limestone" -> [80] Kota stone (GSI Rajasthan / IS 1130)
    tier, reason = relevance_matcher.classify("Kota limestone", "Kota stone polished flooring")
    assert tier == InspirationRelevanceTierEnum.TIER_2_ALIAS
    assert "kota stone" in reason.lower()

def test_ali_06_italian_statuario_floor():
    # ALI-06: "Italian statuario floor" -> [1353] Italian marble flooring (ASTM C503, one-way)
    tier, reason = relevance_matcher.classify("Italian statuario floor", "Italian marble flooring living room")
    assert tier == InspirationRelevanceTierEnum.TIER_2_ALIAS

def test_ali_07_mangalore_pattern_tiles():
    # ALI-07: "Mangalore pattern tiles" -> Conditional on clay + roofing context
    tier_pos, _ = relevance_matcher.classify("Mangalore pattern tiles", "Mangalore clay roof tile sloped roofing")
    assert tier_pos == InspirationRelevanceTierEnum.TIER_2_ALIAS

    tier_amb, _ = relevance_matcher.classify("Mangalore pattern tiles", "Mangalore pattern floor tiles ceramic")
    assert tier_amb == InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS

def test_ali_08_teak_wood_main_door():
    # ALI-08: "Teak wood main door" -> [350] Teakwood entrance door (CPWD 2019 Cl 9.1 / IS 1003)
    tier, reason = relevance_matcher.classify("Teak wood main door", "Teakwood entrance door hand-carved")
    assert tier == InspirationRelevanceTierEnum.TIER_2_ALIAS
    assert "CPWD Specs 2019" in reason

def test_ali_09_spider_glazing_brackets():
    # ALI-09: "Spider glazing brackets" -> [6186] Glass spider fitting (ASTM A351 / GANA)
    tier, reason = relevance_matcher.classify("Spider glazing brackets", "Glass spider fitting 316 stainless steel")
    assert tier == InspirationRelevanceTierEnum.TIER_2_ALIAS
    assert "ASTM A351" in reason

def test_ali_10_precast_boundary_wall():
    # ALI-10: "Precast boundary wall" -> [570] Precast compound wall panel (CPWD 2019 Cl 4.14)
    tier, reason = relevance_matcher.classify("Precast boundary wall", "Precast compound wall panel boundary system")
    assert tier == InspirationRelevanceTierEnum.TIER_2_ALIAS
    assert "CPWD Specs 2019" in reason


# ==============================================================================
# 11.4 AMBIGUOUS CASES REQUIRING UNCERTAINTY HANDLING (5 Cases)
# ==============================================================================

AMBIGUOUS_TEST_CASES = [
    ("AMB-01", "Stone flooring", "Natural stone flooring variety in modern courtyard"),
    ("AMB-02", "Bricks", "Bricks for construction projects"),
    ("AMB-03", "Wall cladding", "Exterior wall cladding design ideas"),
    ("AMB-04", "Concrete block", "Concrete block selection for building site"),
    ("AMB-05", "Wood door", "Wood door models for contemporary home"),
]

@pytest.mark.parametrize("case_id, query, candidate_title", AMBIGUOUS_TEST_CASES)
def test_ambiguous_parent_noun_queries(case_id, query, candidate_title):
    tier, reason = relevance_matcher.classify(query, candidate_title)
    assert tier == InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS, (
        f"{case_id} failed: Expected TIER_4_AMBIGUOUS for parent noun '{query}', got {tier} ({reason})"
    )


# ==============================================================================
# GATE 0 PRECEDENCE & PROTOCOL INTEGRITY TESTS
# ==============================================================================

def test_gate_0_primary_subject_exclusion_wallpaper():
    """Gate 0 rejects toy/sticker/wallpaper products even if the material keyword is present."""
    tier, reason = relevance_matcher.classify("Exposed brick", "Brick pattern peel and stick wallpaper for accent wall")
    assert tier == InspirationRelevanceTierEnum.TIER_5_REJECTED
    assert "Gate 0 Excluded" in reason

def test_gate_0_secondary_mention_preservation():
    """Secondary mention preservation: teak door with decorative glass must not be rejected."""
    tier, reason = relevance_matcher.classify("Teakwood entrance door", "Teakwood entrance door with decorative glass panel")
    assert tier in [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]

def test_gate_0_negation_phrase_preservation():
    """Negation preservation: 'without wallpaper' or 'without pvc pipe' must not trigger exclusions."""
    tier1, reason1 = relevance_matcher.classify("Modern villa", "Modern villa with exposed brick and without wallpaper")
    assert tier1 in [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_3_CONTEXTUAL]

    tier2, reason2 = relevance_matcher.classify("Steel pipe pile", "Driven steel pipe pile without pvc pipe lining")
    assert tier2 in [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_3_CONTEXTUAL]


# ==============================================================================
# STAGE 4 MANDATORY RELEVANCE TESTS
# ==============================================================================

def test_stage4_aac_blocks_vs_red_clay_brick_rejection():
    """AAC blocks query must reject red clay brick metadata."""
    tier, reason = relevance_matcher.classify("AAC block", "Exposed red clay brick masonry wall facade")
    assert tier == InspirationRelevanceTierEnum.TIER_5_REJECTED
    assert "Gate 0 Contradiction" in reason or "conflict" in reason.lower()

def test_stage4_generic_stone_not_treated_as_specific_stone():
    """Generic 'stone' query must abstain to Tier 4 ambiguous, never asserted as Kota stone."""
    tier, reason = relevance_matcher.classify("Stone", "Natural stone landscaping paving ideas")
    assert tier == InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS
    assert "Generic parent query" in reason

    tier_nat, reason_nat = relevance_matcher.classify("Natural stone", "Selection of natural stone floor slabs")
    assert tier_nat == InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS

def test_stage4_wood_interior_with_brick_accent_kept():
    """Wood interior with brick accent must be preserved for brick query."""
    tier, reason = relevance_matcher.classify(
        "Wire-cut brick",
        "Contemporary residence featuring warm teak wood interior and exposed wire-cut brick accent wall"
    )
    assert tier in [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS, InspirationRelevanceTierEnum.TIER_3_CONTEXTUAL]
    assert tier != InspirationRelevanceTierEnum.TIER_5_REJECTED

def test_stage4_fly_ash_vs_clay_brick_not_confused():
    """Fly ash brick vs clay brick must not be confused by metadata alone."""
    tier_fa, reason_fa = relevance_matcher.classify("Fly ash brick", "Handmade red clay burnt brick wall")
    assert tier_fa == InspirationRelevanceTierEnum.TIER_5_REJECTED

    tier_clay, reason_clay = relevance_matcher.classify("Clay brick", "High performance fly ash block masonry construction")
    assert tier_clay == InspirationRelevanceTierEnum.TIER_5_REJECTED

