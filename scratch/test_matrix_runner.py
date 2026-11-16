import re
from typing import Tuple, Dict, Any, List, Optional
from enum import Enum

class InspirationRelevanceTierEnum(str, Enum):
    TIER_1_EXACT = "EXACT_METADATA_MATCH"
    TIER_2_ALIAS = "VERIFIED_CATALOGUE_ALIAS"
    TIER_3_CONTEXTUAL = "SUPPORTED_CONTEXTUAL_MATCH"
    TIER_4_AMBIGUOUS = "AMBIGUOUS_MATCH"
    TIER_5_REJECTED = "REJECTED_UNRELATED"

APPROVED_MATERIAL_ALIASES = {
    "flyash bricks": {"canonical": "fly ash brick", "standard": "IS 12894:2002 Cl. 1.1 & 3.1, CPWD Specs 2019 Cl. 3.2", "bidirectional": True},
    "flyash brick": {"canonical": "fly ash brick", "standard": "IS 12894:2002 Cl. 1.1 & 3.1, CPWD Specs 2019 Cl. 3.2", "bidirectional": True},
    "fly ash bricks": {"canonical": "fly ash brick", "standard": "IS 12894:2002 Cl. 1.1 & 3.1, CPWD Specs 2019 Cl. 3.2", "bidirectional": True},
    "wirecut clay brick": {"canonical": "wire-cut brick", "standard": "IS 1077:1992, IS 2117:1991 Cl. 4.2", "bidirectional": True},
    "wirecut brick": {"canonical": "wire-cut brick", "standard": "IS 1077:1992, IS 2117:1991 Cl. 4.2", "bidirectional": True},
    "wire cut brick": {"canonical": "wire-cut brick", "standard": "IS 1077:1992, IS 2117:1991 Cl. 4.2", "bidirectional": True},
    "autoclaved aerated concrete block": {"canonical": "aac block", "standard": "IS 2185 Pt. 3 Cl. 2.1, ASTM C1693", "bidirectional": True},
    "autoclaved aerated concrete": {"canonical": "aac block", "standard": "IS 2185 Pt. 3 Cl. 2.1, ASTM C1693", "bidirectional": True},
    "kota limestone": {"canonical": "kota stone", "standard": "GSI Rajasthan Mineral Directory, IS 1130 / ASTM C568", "bidirectional": True},
    "italian statuario floor": {"canonical": "italian marble flooring", "standard": "ASTM C503 / UNI EN 12407", "bidirectional": False, "sub_variety": True},
    "statuario marble floor": {"canonical": "italian marble flooring", "standard": "ASTM C503 / UNI EN 12407", "bidirectional": False, "sub_variety": True},
    "statuario floor": {"canonical": "italian marble flooring", "standard": "ASTM C503 / UNI EN 12407", "bidirectional": False, "sub_variety": True},
    "mangalore pattern tiles": {"canonical": "mangalore clay roof tile", "standard": "IS 654:1992 Cl. 1", "bidirectional": False, "conditional": True},
    "mangalore tiles": {"canonical": "mangalore clay roof tile", "standard": "IS 654:1992 Cl. 1", "bidirectional": False, "conditional": True},
    "teak wood main door": {"canonical": "teakwood entrance door", "standard": "CPWD Specs 2019 Cl. 9.1, IS 1003 Pt. 1", "bidirectional": True},
    "teak main door": {"canonical": "teakwood entrance door", "standard": "CPWD Specs 2019 Cl. 9.1, IS 1003 Pt. 1", "bidirectional": True},
    "spider glazing brackets": {"canonical": "glass spider fitting", "standard": "ASTM A351 / A276, GANA Glazing Manual", "bidirectional": True},
    "spider glazing bracket": {"canonical": "glass spider fitting", "standard": "ASTM A351 / A276, GANA Glazing Manual", "bidirectional": True},
    "precast boundary wall": {"canonical": "precast compound wall panel", "standard": "CPWD Specs 2019 Cl. 4.14", "bidirectional": True},
    "precast boundary wall panel": {"canonical": "precast compound wall panel", "standard": "CPWD Specs 2019 Cl. 4.14", "bidirectional": True},
}

CONDITIONAL_OR_AMBIGUOUS_ALIASES = {
    "hollow blocks": {
        "status": InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS,
        "reason": "Umbrella trade term ambiguous between concrete hollow block (IS 2185 Pt 1) and clay hollow block (IS 3952)."
    },
    "hollow block": {
        "status": InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS,
        "reason": "Umbrella trade term ambiguous between concrete hollow block (IS 2185 Pt 1) and clay hollow block (IS 3952)."
    }
}

GENERIC_PARENT_NOUNS = {
    "stone flooring", "stone floor", "natural stone flooring",
    "bricks", "brick", "wall cladding", "cladding",
    "concrete block", "concrete blocks", "wood door", "wooden door",
    "doors", "door", "tiles", "tile", "flooring"
}

CONFLICTING_MATERIAL_PAIRS = [
    ("fly ash", ["red clay", "ordinary clay", "burnt clay", "kiln fired", "kiln-fired", "traditional clay"]),
    ("flyash", ["red clay", "ordinary clay", "burnt clay", "kiln fired", "kiln-fired", "traditional clay"]),
    ("wire-cut", ["wire mesh", "chain link", "fencing mesh", "welded mesh", "fencing panel", "chicken wire"]),
    ("wirecut", ["wire mesh", "chain link", "fencing mesh", "welded mesh", "fencing panel", "chicken wire"]),
    ("wire cut", ["wire mesh", "chain link", "fencing mesh", "welded mesh", "fencing panel", "chicken wire"]),
    ("laterite", ["cseb", "compressed stabilized earth", "compressed earth block"]),
    ("concrete hollow block", ["solid block", "dense concrete solid block", "solid concrete block"]),
    ("hollow block", ["solid block", "solid concrete block"]),
    ("aac block", ["dense concrete", "dense cement", "solid concrete", "heavyweight block"]),
    ("autoclaved aerated", ["dense concrete", "dense cement", "solid concrete"]),
    ("kota stone", ["porcelain", "glazed porcelain", "ceramic tile", "kota print", "vitrified tile", "digital print"]),
    ("kota limestone", ["porcelain", "glazed porcelain", "ceramic tile", "kota print", "vitrified tile", "digital print"]),
    ("italian marble", ["terrazzo", "marble chips", "cement tile", "quartz print", "composite marble"]),
    ("statuario", ["terrazzo", "marble chips", "cement tile"]),
    ("black granite", ["slate", "slate stone", "schist", "black slate", "slate wall"]),
    ("mangalore clay", ["corrugated", "metal sheet", "tin sheet", "asbestos", "polycarbonate sheet", "galvanized steel"]),
    ("mangalore pattern", ["corrugated", "metal sheet", "tin sheet", "asbestos"]),
    ("wood-wool", ["fiberglass", "glasswool", "mineral wool", "rockwool", "insulation roll"]),
    ("teakwood entrance door", ["pvc", "flush door with teak sticker", "laminated flush", "particleboard", "teak sticker", "pvc wrap", "pvc laminated"]),
    ("teak wood", ["teak sticker", "pvc wrap", "pvc laminated flush door", "pvc laminate"]),
    ("teakwood", ["teak sticker", "pvc wrap", "pvc laminated flush door", "pvc laminate"]),
    ("glass curtain wall", ["sliding window", "casement window", "punched window", "standard window"]),
    ("elastomeric exterior paint", ["distemper", "interior emulsion", "lime wash", "chalk paint", "interior paint"]),
    ("elastomeric paint", ["distemper", "interior emulsion", "lime wash", "chalk paint", "interior paint"]),
    ("steel pipe pile", ["pvc pipe", "drainage pipe", "plastic pipe", "cpvc pipe", "plumbing pipe", "sewer"]),
    ("glass spider fitting", ["plastic shower", "shower bracket", "acrylic bracket", "bathroom bracket"]),
    ("spider glazing", ["plastic shower", "shower bracket", "acrylic bracket", "bathroom bracket"]),
    ("drip irrigation pipe", ["hose reel", "garden hose", "sprinkler pipe", "flexible hose"]),
    ("western water closet", ["squat toilet", "indian pan", "squat pan", "orissa pan"]),
    ("concrete paver block", ["asphalt", "bitumen", "tar road", "macadam", "road surfacing"]),
    ("precast compound wall panel", ["brick boundary wall", "brick wall with plaster", "rubble wall", "wet masonry"]),
    ("precast boundary wall", ["brick boundary wall", "brick wall with plaster", "rubble wall", "wet masonry"]),
    ("glass block", ["acrylic", "polymer shelf", "plastic sheet", "plexiglass", "bathroom shelf"]),
]

PRIMARY_SUBJECT_EXCLUSIONS = {
    "wallpaper", "wall paper", "peel and stick", "decal", "sticker", "stickers",
    "toy", "toys", "lego", "puzzle", "puzzles", "t-shirt", "shirt", "apparel",
    "costume", "keychain", "phone case", "poster", "wall art print", "miniature"
}

def normalize_text(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r"[\-_/]", " ", text.lower())
    clean = re.sub(r"[^\w\s]", "", clean)
    return " ".join(clean.split())

class LayeredQueryMatcher:
    def __init__(self):
        pass

    def evaluate_gate_0(self, query: str, title: str, description: str = "", tags: str = "") -> Tuple[bool, str]:
        q_norm = normalize_text(query)
        title_norm = normalize_text(title)
        desc_norm = normalize_text(description)
        tags_norm = normalize_text(tags)
        content_norm = f"{title_norm} {desc_norm} {tags_norm}"

        # 1. Primary Subject Negative Exclusions (e.g. Wallpaper, Sticker, Toy)
        for excl in PRIMARY_SUBJECT_EXCLUSIONS:
            if excl in q_norm:
                continue
            # Check if candidate primary subject is the excluded product
            if bool(re.search(rf"\b{re.escape(excl)}\b", title_norm)):
                # Negation phrase preservation: e.g. "without wallpaper", "no wallpaper"
                if bool(re.search(rf"\b(without|no|zero|free of)\s+{re.escape(excl)}\b", content_norm)):
                    continue
                return False, f"Gate 0 Excluded: Primary subject '{excl}' detected in title"

        # 2. Conflicting Substrate / Contradiction Check
        for q_pattern, conflicting_tokens in CONFLICTING_MATERIAL_PAIRS:
            q_pat_norm = normalize_text(q_pattern)
            if q_pat_norm in q_norm:
                for c_token in conflicting_tokens:
                    c_token_norm = normalize_text(c_token)
                    if bool(re.search(rf"\b{re.escape(c_token_norm)}\b", content_norm)):
                        # Negation phrase preservation: e.g. "without pvc pipe", "no pvc pipe", "non-pvc"
                        if bool(re.search(rf"\b(without|no|zero|free of|non)\s+{re.escape(c_token_norm)}\b", content_norm)):
                            continue
                        # Secondary mention preservation / comparison check: allow comparative discussions
                        if " vs " in content_norm or "versus" in content_norm or "comparison" in content_norm:
                            continue
                        return False, f"Gate 0 Contradiction: Candidate contains '{c_token}' which conflicts with query '{q_pattern}'"

        return True, "PASSED"

    def classify(
        self,
        query: str,
        title: str,
        description: str = "",
        tags: str = "",
        category: str = "",
        subcategory: str = ""
    ) -> Tuple[InspirationRelevanceTierEnum, str]:
        q_norm = normalize_text(query)
        title_norm = normalize_text(title)
        desc_norm = normalize_text(description)
        tags_norm = normalize_text(tags)
        tax_norm = normalize_text(f"{category} {subcategory}")
        content_norm = f"{title_norm} {desc_norm} {tags_norm}"

        # GATE 0 PRECEDENCE
        passed_gate_0, gate_reason = self.evaluate_gate_0(query, title, description, tags)
        if not passed_gate_0:
            return InspirationRelevanceTierEnum.TIER_5_REJECTED, gate_reason

        # Check for generic parent noun queries (must abstain to Tier 4)
        if q_norm in GENERIC_PARENT_NOUNS:
            return InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS, f"Generic parent query '{query}' requires sub-type disambiguation"

        # Check for conditional / unconfirmed alias queries
        if q_norm in CONDITIONAL_OR_AMBIGUOUS_ALIASES:
            meta = CONDITIONAL_OR_AMBIGUOUS_ALIASES[q_norm]
            return meta["status"], meta["reason"]

        if q_norm == "mangalore pattern tiles":
            # Must have roofing clay context to match Tier 2
            if "roof" in content_norm and ("clay" in content_norm or "terracotta" in content_norm):
                return InspirationRelevanceTierEnum.TIER_2_ALIAS, "Approved alias 'mangalore pattern tiles' -> 'mangalore clay roof tile' (IS 654:1992 Cl. 1)"
            else:
                return InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS, "Mangalore pattern tiles require roofing + fired clay substrate confirmation"

        # LAYER 1: Exact Phrase Match
        is_comparison = " vs " in content_norm or "versus" in content_norm or "comparison" in content_norm
        if q_norm in title_norm or q_norm in tags_norm or q_norm in desc_norm:
            if is_comparison:
                return InspirationRelevanceTierEnum.TIER_3_CONTEXTUAL, "Exact phrase in comparative/discussion context"
            return InspirationRelevanceTierEnum.TIER_1_EXACT, "Exact phrase match in candidate metadata"

        # LAYER 2: Approved Catalogue Alias Match
        if q_norm in APPROVED_MATERIAL_ALIASES:
            alias_info = APPROVED_MATERIAL_ALIASES[q_norm]
            canonical = normalize_text(alias_info["canonical"])
            if canonical in content_norm:
                return InspirationRelevanceTierEnum.TIER_2_ALIAS, f"Approved alias '{query}' -> canonical '{canonical}' ({alias_info['standard']})"

        # Reverse check: query is canonical, candidate contains approved alias
        for alias_phrase, alias_info in APPROVED_MATERIAL_ALIASES.items():
            canonical = normalize_text(alias_info["canonical"])
            if canonical == q_norm:
                if alias_info.get("bidirectional", False):
                    alias_norm = normalize_text(alias_phrase)
                    if alias_norm in content_norm:
                        return InspirationRelevanceTierEnum.TIER_2_ALIAS, f"Candidate matches approved alias '{alias_phrase}' ({alias_info['standard']})"

        # LAYER 3: Core Material Noun Stemming & Supported Context
        core_nouns = [
            "brick", "bricks", "block", "blocks", "stone", "marble", "granite",
            "tile", "tiles", "door", "doors", "panel", "panels", "pipe", "pipes",
            "fitting", "fittings", "paint", "paver", "pavers", "curtain wall", "closet"
        ]
        found_core = None
        for cn in core_nouns:
            if cn in q_norm.split():
                found_core = cn
                break

        if found_core:
            core_stem = found_core.rstrip("s")
            # If candidate mentions the core stem and at least one other word or taxonomy matches
            if core_stem in content_norm:
                q_words = [w for w in q_norm.split() if len(w) > 2 and w != found_core]
                if any(w in content_norm for w in q_words) or (tax_norm and any(w in tax_norm for w in q_words)):
                    return InspirationRelevanceTierEnum.TIER_3_CONTEXTUAL, f"Core noun stem '{core_stem}' with supported context"

        # LAYER 5: Inconclusive / Rejected
        return InspirationRelevanceTierEnum.TIER_5_REJECTED, "No exact, alias, or supported contextual match"

# Run all test cases
matcher = LayeredQueryMatcher()
passed_count = 0
failed_cases = []

TEST_CASES = [
    # 11.1 Positive Matching Test Cases (20 cases)
    ("POS-01", "Fly ash brick", "Fly ash brick masonry wall construction ASTM C869", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-02", "Wire-cut brick", "Exposed red clay wire-cut brick facade architecture", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-03", "Laterite block", "Dressed natural laterite stone blocks for vernacular masonry walling", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS, InspirationRelevanceTierEnum.TIER_3_CONTEXTUAL]),
    ("POS-04", "Concrete hollow block", "2-core load-bearing concrete hollow block masonry units CMU", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-05", "AAC block", "Autoclaved aerated concrete AAC blocks for thermal walling", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-06", "Kota stone", "Honed greenish-grey Kota stone flooring slabs", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-07", "Italian marble flooring", "Bookmatched Italian marble flooring in residential villa", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-08", "Black granite", "Flamed absolute black granite slab paving", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-09", "Mangalore clay roof tile", "Terracotta interlocking Mangalore clay roof tile on timber rafters", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-10", "Wood-wool acoustic panel", "Cement-bonded wood-wool acoustic panel boards for ceiling", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-11", "Teakwood entrance door", "Solid teakwood entrance door with brass fittings", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-12", "Glass curtain wall", "Structural unitized glass curtain wall system modern facade", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-13", "Elastomeric exterior paint", "Weatherproof flexible elastomeric exterior paint coating", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-14", "Steel pipe pile", "Driven structural steel pipe pile foundation casing", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-15", "Glass spider fitting", "4-way stainless steel point-supported glass spider fitting", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-16", "Drip irrigation pipe", "Inline pressure-compensating drip irrigation pipe lateral", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-17", "Western water closet", "Wall-hung ceramic western water closet dual flush WC", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-18", "Concrete paver block", "Interlocking concrete paver block driveway paving", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-19", "Precast compound wall panel", "Modular precast compound wall panel planks and columns", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("POS-20", "Glass block", "Translucent patterned glass block masonry partition wall", [InspirationRelevanceTierEnum.TIER_1_EXACT, InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # 11.2 Negative / Misleading Matching Test Cases (20 cases)
    ("NEG-01", "Fly ash brick", "Traditional red clay kiln-fired brick masonry wall", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-02", "Wire-cut brick", "Galvanized wire mesh fencing panel and security boundary", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-03", "Laterite block", "Compressed stabilized earth block CSEB wall construction", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-04", "Concrete hollow block", "Dense concrete solid block heavy foundation wall", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-05", "AAC block", "Dense cement concrete block high density masonry", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-06", "Kota stone", "Glazed porcelain tile with Kota print pattern ceramic", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-07", "Italian marble flooring", "Terrazzo flooring with marble chips composite cement", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-08", "Black granite", "Natural black slate wall cladding tiles", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-09", "Mangalore clay roof tile", "Corrugated metal roofing sheet galvanized steel", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-10", "Wood-wool acoustic panel", "Fiberglass insulation roll glasswool thermal batt", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-11", "Teakwood entrance door", "PVC laminated flush door with teak sticker decal", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-12", "Glass curtain wall", "Standard aluminum sliding window punched opening", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-13", "Elastomeric exterior paint", "Interior distemper emulsion paint for bedroom walls", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-14", "Steel pipe pile", "PVC plumbing drainage pipe underground sewer", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-15", "Glass spider fitting", "Plastic shower glass bracket bathroom fitting", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-16", "Drip irrigation pipe", "Flexible garden hose reel watering kit", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-17", "Western water closet", "Squat toilet ceramic Indian pan squatting WC", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-18", "Concrete paver block", "Asphalt bitumen road surfacing macadam pavement", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-19", "Precast compound wall panel", "Traditional brick boundary wall with plaster wet masonry", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),
    ("NEG-20", "Glass block", "Clear acrylic bathroom shelf polymer rack", [InspirationRelevanceTierEnum.TIER_5_REJECTED]),

    # 11.3 Alias & Spelling-Variation Test Cases (10 cases)
    ("ALI-01", "Flyash bricks", "Fly ash brick manufacturing ASTM standard", [InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("ALI-02", "Wirecut clay brick", "Wire-cut brick architectural facade", [InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("ALI-03", "Hollow blocks", "Generic hollow blocks supply", [InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS]),
    ("ALI-04", "Autoclaved aerated concrete block", "AAC block masonry lightweight", [InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("ALI-05", "Kota limestone", "Kota stone polished flooring", [InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("ALI-06", "Italian statuario floor", "Italian marble flooring living room", [InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("ALI-07a", "Mangalore pattern tiles", "Mangalore clay roof tile sloped roofing", [InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("ALI-07b", "Mangalore pattern tiles", "Mangalore pattern floor tiles ceramic", [InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS]),
    ("ALI-08", "Teak wood main door", "Teakwood entrance door hand-carved", [InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("ALI-09", "Spider glazing brackets", "Glass spider fitting 316 stainless steel", [InspirationRelevanceTierEnum.TIER_2_ALIAS]),
    ("ALI-10", "Precast boundary wall", "Precast compound wall panel boundary system", [InspirationRelevanceTierEnum.TIER_2_ALIAS]),

    # 11.4 Ambiguous Cases (5 cases)
    ("AMB-01", "Stone flooring", "Natural stone flooring variety in modern courtyard", [InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS]),
    ("AMB-02", "Bricks", "Bricks for construction projects", [InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS]),
    ("AMB-03", "Wall cladding", "Exterior wall cladding design ideas", [InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS]),
    ("AMB-04", "Concrete block", "Concrete block selection for site", [InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS]),
    ("AMB-05", "Wood door", "Wood door models for home", [InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS]),
]

for case_id, query, title, expected_tiers in TEST_CASES:
    tier, reason = matcher.classify(query, title)
    if tier in expected_tiers:
        passed_count += 1
    else:
        failed_cases.append((case_id, query, title, tier, expected_tiers, reason))

print(f"RESULTS: {passed_count}/{len(TEST_CASES)} passed.")
if failed_cases:
    print("FAILED CASES:")
    for f in failed_cases:
        print(f"  {f[0]}: Q='{f[1]}' -> Got {f[3]} (expected {f[4]}). Reason: {f[5]}")
