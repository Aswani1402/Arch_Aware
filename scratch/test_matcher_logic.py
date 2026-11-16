import re
from typing import Optional, Dict, Any, Tuple, List, Set
from enum import Enum

class InspirationRelevanceTierEnum(str, Enum):
    TIER_1_EXACT = "EXACT_METADATA_MATCH"
    TIER_2_ALIAS = "VERIFIED_CATALOGUE_ALIAS"
    TIER_3_CONTEXTUAL = "SUPPORTED_CONTEXTUAL_MATCH"
    TIER_4_AMBIGUOUS = "AMBIGUOUS_MATCH"
    TIER_5_REJECTED = "REJECTED_UNRELATED"

class MediaStatusEnum(str, Enum):
    MEDIA_READY = "MEDIA_READY"
    MEDIA_UNUSABLE = "MEDIA_UNUSABLE"
    TEXT_DISCUSSION = "TEXT_DISCUSSION"

APPROVED_MATERIAL_ALIASES = {
    "flyash bricks": {"canonical": "fly ash brick", "standard": "IS 12894:2002", "bidirectional": True},
    "flyash brick": {"canonical": "fly ash brick", "standard": "IS 12894:2002", "bidirectional": True},
    "fly ash bricks": {"canonical": "fly ash brick", "standard": "IS 12894:2002", "bidirectional": True},
    "wirecut clay brick": {"canonical": "wire-cut brick", "standard": "IS 1077:1992 / IS 2117:1991", "bidirectional": True},
    "wirecut brick": {"canonical": "wire-cut brick", "standard": "IS 1077:1992 / IS 2117:1991", "bidirectional": True},
    "wire cut brick": {"canonical": "wire-cut brick", "standard": "IS 1077:1992 / IS 2117:1991", "bidirectional": True},
    "autoclaved aerated concrete block": {"canonical": "aac block", "standard": "IS 2185 Pt 3:1984", "bidirectional": True},
    "autoclaved aerated concrete": {"canonical": "aac block", "standard": "IS 2185 Pt 3:1984", "bidirectional": True},
    "kota limestone": {"canonical": "kota stone", "standard": "GSI Rajasthan Directory / IS 1130", "bidirectional": True},
    "italian statuario floor": {"canonical": "italian marble flooring", "standard": "ASTM C503 / UNI EN 12407", "bidirectional": False, "sub_variety": True},
    "statuario marble floor": {"canonical": "italian marble flooring", "standard": "ASTM C503 / UNI EN 12407", "bidirectional": False, "sub_variety": True},
    "mangalore pattern tiles": {"canonical": "mangalore clay roof tile", "standard": "IS 654:1992", "bidirectional": False, "conditional": True},
    "mangalore tiles": {"canonical": "mangalore clay roof tile", "standard": "IS 654:1992", "bidirectional": False, "conditional": True},
    "teak wood main door": {"canonical": "teakwood entrance door", "standard": "CPWD 2019 Cl 9.1 / IS 1003", "bidirectional": True},
    "teak main door": {"canonical": "teakwood entrance door", "standard": "CPWD 2019 Cl 9.1 / IS 1003", "bidirectional": True},
    "spider glazing brackets": {"canonical": "glass spider fitting", "standard": "ASTM A351 / GANA Manual", "bidirectional": True},
    "spider glazing bracket": {"canonical": "glass spider fitting", "standard": "ASTM A351 / GANA Manual", "bidirectional": True},
    "precast boundary wall": {"canonical": "precast compound wall panel", "standard": "CPWD 2019 Cl 4.14", "bidirectional": True},
    "precast boundary wall panel": {"canonical": "precast compound wall panel", "standard": "CPWD 2019 Cl 4.14", "bidirectional": True},
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
    ("solid block", ["hollow", "cavity", "cellular"]),
    ("hollow block", ["solid block", "solid concrete"]),
    ("fly ash", ["red clay", "ordinary clay", "burnt clay", "kiln fired", "kiln-fired"]),
    ("wire-cut", ["wire mesh", "chain link", "fencing mesh", "welded mesh", "fencing panel"]),
    ("wirecut", ["wire mesh", "chain link", "fencing mesh", "welded mesh", "fencing panel"]),
    ("laterite", ["cseb", "compressed stabilized earth", "fly ash", "clay brick"]),
    ("aac block", ["dense concrete", "dense cement", "solid concrete"]),
    ("kota stone", ["porcelain", "ceramic", "glazed tile", "kota print", "vitrified tile"]),
    ("italian marble", ["terrazzo", "marble chips", "cement tile", "quartz print"]),
    ("black granite", ["slate", "slate stone", "schist", "black slate"]),
    ("mangalore clay", ["corrugated", "metal sheet", "tin sheet", "asbestos", "polycarbonate"]),
    ("mangalore", ["corrugated", "metal sheet", "tin sheet"]),
    ("wood-wool", ["fiberglass", "glasswool", "mineral wool", "rockwool"]),
    ("teakwood entrance door", ["pvc", "flush door with teak sticker", "laminated flush", "particleboard", "teak sticker"]),
    ("teakwood", ["pvc sticker", "pvc laminated", "flush door with sticker", "teak sticker"]),
    ("glass curtain wall", ["sliding window", "casement window", "punched window"]),
    ("elastomeric", ["interior distemper", "interior emulsion", "lime wash", "chalk paint"]),
    ("steel pipe pile", ["pvc pipe", "drainage pipe", "plastic pipe", "cpvc"]),
    ("glass spider fitting", ["plastic shower", "shower bracket", "acrylic bracket"]),
    ("drip irrigation pipe", ["hose reel", "garden hose", "sprinkler pipe"]),
    ("western water closet", ["squat toilet", "indian pan", "squat pan", "orissa pan"]),
    ("concrete paver block", ["asphalt", "bitumen", "tar road", "macadam"]),
    ("precast compound wall panel", ["brick boundary wall", "brick wall with plaster", "rubble wall", "wet masonry"]),
    ("glass block", ["acrylic", "polymer shelf", "plastic sheet", "plexiglass"]),
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

def evaluate_gate_0(query: str, title: str, description: str, tags: str = "") -> Tuple[bool, str]:
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
            # Check for negation: e.g. "without wallpaper", "no wallpaper"
            if bool(re.search(rf"\b(without|no|zero|free of)\s+{re.escape(excl)}\b", content_norm)):
                continue
            return False, f"Primary subject excluded: '{excl}' detected in title"

    # 2. Conflicting Material Contradiction Check
    for q_pattern, conflicting_tokens in CONFLICTING_MATERIAL_PAIRS:
        if q_pattern in q_norm:
            for c_token in conflicting_tokens:
                if bool(re.search(rf"\b{re.escape(c_token)}\b", content_norm)):
                    # Allow comparison / discussion: e.g. "fly ash vs clay brick"
                    if " vs " in content_norm or "versus" in content_norm or "comparison" in content_norm:
                        continue
                    return False, f"Conflicting substrate/system contradiction: '{c_token}' conflicts with query '{q_pattern}'"

    return True, "PASSED"

def classify_relevance(
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
    content_norm = f"{title_norm} {desc_norm} {tags_norm}"

    # GATE 0 PRECEDENCE
    passed_gate_0, gate_reason = evaluate_gate_0(query, title, description, tags)
    if not passed_gate_0:
        return InspirationRelevanceTierEnum.TIER_5_REJECTED, f"Gate 0: {gate_reason}"

    # Comparison / discussion check
    is_comparison = " vs " in content_norm or "versus" in content_norm or "comparison" in content_norm or "review" in content_norm

    # Check for Ambiguous / Generic Parent Noun queries
    if q_norm in GENERIC_PARENT_NOUNS:
        return InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS, f"Generic parent query '{query}' requires sub-type disambiguation"

    # Check conditional / unconfirmed alias queries
    if q_norm in CONDITIONAL_OR_AMBIGUOUS_ALIASES:
        meta = CONDITIONAL_OR_AMBIGUOUS_ALIASES[q_norm]
        # Check if substrate is confirmed in content
        if "requires_substrate" in meta:
            has_sub = any(s in content_norm for s in meta["requires_substrate"])
            if not has_sub:
                return meta["status"], meta["reason"]

    # Layer 1: Normalized Exact Phrase Match
    if q_norm in title_norm or q_norm in tags_norm or q_norm in desc_norm:
        if is_comparison:
            return InspirationRelevanceTierEnum.TIER_3_CONTEXTUAL, "Exact phrase in comparative/discussion context"
        return InspirationRelevanceTierEnum.TIER_1_EXACT, "Exact phrase match in candidate metadata"

    # Layer 2: Approved Technical Alias Match
    # Check if query matches an approved alias
    if q_norm in APPROVED_MATERIAL_ALIASES:
        alias_info = APPROVED_MATERIAL_ALIASES[q_norm]
        canonical = alias_info["canonical"]
        if canonical in content_norm:
            return InspirationRelevanceTierEnum.TIER_2_ALIAS, f"Approved alias '{query}' -> canonical '{canonical}' ({alias_info['standard']})"

    # Check if content matches an approved alias of the query
    for alias_phrase, alias_info in APPROVED_MATERIAL_ALIASES.items():
        if alias_info["canonical"] == q_norm:
            if alias_phrase in content_norm:
                return InspirationRelevanceTierEnum.TIER_2_ALIAS, f"Candidate matches approved alias '{alias_phrase}' ({alias_info['standard']})"

    # Layer 3: Core Material Noun Stemming & Supported Context
    # Core noun must be present + category/subcategory or contextual support
    core_nouns = ["brick", "block", "stone", "marble", "granite", "tile", "door", "panel", "pipe", "fitting", "wc", "closet", "paint", "paver", "wall"]
    found_core = None
    for cn in core_nouns:
        if cn in q_norm:
            found_core = cn
            break

    if found_core and found_core in content_norm:
        # Check taxonomy or description support
        tax_str = f"{category} {subcategory}".lower()
        if found_core in tax_str or any(w in content_norm for w in q_norm.split() if len(w) > 3):
            return InspirationRelevanceTierEnum.TIER_3_CONTEXTUAL, f"Core noun stem '{found_core}' with supported context"

    # Layer 4: Inconclusive
    return InspirationRelevanceTierEnum.TIER_5_REJECTED, "No exact, alias, or supported contextual match"

print("Matcher logic loaded successfully.")

