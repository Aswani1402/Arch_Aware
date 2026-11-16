import re
from typing import List, Optional, Dict, Any, Set, Tuple
from app.models.models import ArchitecturalReference
from app.schemas.discovery import (
    ProvenanceEnum,
    InspirationRelevanceTierEnum,
    MediaStatusEnum,
)

# ==============================================================================
# PHASE 1B / STAGE 1: VERIFIED ALIASES, STANDARDS GROUNDING & GATE 0 DATA
# ==============================================================================

APPROVED_MATERIAL_ALIASES: Dict[str, Dict[str, Any]] = {
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

CONDITIONAL_OR_AMBIGUOUS_ALIASES: Dict[str, Dict[str, Any]] = {
    "hollow blocks": {
        "status": InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS,
        "reason": "Umbrella trade term ambiguous between concrete hollow block (IS 2185 Pt 1) and clay hollow block (IS 3952)."
    },
    "hollow block": {
        "status": InspirationRelevanceTierEnum.TIER_4_AMBIGUOUS,
        "reason": "Umbrella trade term ambiguous between concrete hollow block (IS 2185 Pt 1) and clay hollow block (IS 3952)."
    }
}

GENERIC_PARENT_NOUNS: Set[str] = {
    "stone flooring", "stone floor", "natural stone flooring",
    "stone", "natural stone",
    "bricks", "brick", "wall cladding", "cladding",
    "concrete block", "concrete blocks", "wood door", "wooden door",
    "doors", "door", "tiles", "tile", "flooring"
}

CONFLICTING_MATERIAL_PAIRS: List[Tuple[str, List[str]]] = [
    ("fly ash", ["red clay", "ordinary clay", "burnt clay", "kiln fired", "kiln-fired", "traditional clay"]),
    ("flyash", ["red clay", "ordinary clay", "burnt clay", "kiln fired", "kiln-fired", "traditional clay"]),
    ("wire-cut", ["wire mesh", "chain link", "fencing mesh", "welded mesh", "fencing panel", "chicken wire"]),
    ("wirecut", ["wire mesh", "chain link", "fencing mesh", "welded mesh", "fencing panel", "chicken wire"]),
    ("wire cut", ["wire mesh", "chain link", "fencing mesh", "welded mesh", "fencing panel", "chicken wire"]),
    ("clay brick", ["fly ash", "flyash", "aac block", "autoclaved aerated"]),
    ("red clay", ["fly ash", "flyash", "aac block", "autoclaved aerated"]),
    ("laterite", ["cseb", "compressed stabilized earth", "compressed earth block"]),
    ("concrete hollow block", ["solid block", "dense concrete solid block", "solid concrete block"]),
    ("hollow block", ["solid block", "solid concrete block"]),
    ("aac block", ["dense concrete", "dense cement", "solid concrete", "heavyweight block", "red clay brick", "clay brick", "burnt clay"]),
    ("autoclaved aerated", ["dense concrete", "dense cement", "solid concrete", "red clay brick", "clay brick", "burnt clay"]),
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

PRIMARY_SUBJECT_EXCLUSIONS: Set[str] = {
    "wallpaper", "wall paper", "peel and stick", "decal", "sticker", "stickers",
    "toy", "toys", "lego", "puzzle", "puzzles", "t-shirt", "shirt", "apparel",
    "costume", "keychain", "phone case", "poster", "wall art print", "miniature", "miniatures"
}

def normalize_relevance_text(text: str) -> str:
    if not text:
        return ""
    clean = re.sub(r"[\-_/]", " ", text.lower())
    clean = re.sub(r"[^\w\s]", "", clean)
    return " ".join(clean.split())

class LayeredQueryMatcher:
    """
    MATERIQ 5-Layer Inspiration Query Matcher with Gate 0 Precedence.
    Enforces material relevance without claiming supplier inventory or fabrication capabilities.
    """
    def __init__(self):
        pass

    def evaluate_gate_0(self, query: str, title: str, description: str = "", tags: str = "") -> Tuple[bool, str]:
        q_norm = normalize_relevance_text(query)
        title_norm = normalize_relevance_text(title)
        desc_norm = normalize_relevance_text(description)
        tags_norm = normalize_relevance_text(tags)
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
            q_pat_norm = normalize_relevance_text(q_pattern)
            if q_pat_norm in q_norm:
                for c_token in conflicting_tokens:
                    c_token_norm = normalize_relevance_text(c_token)
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
        q_norm = normalize_relevance_text(query)
        title_norm = normalize_relevance_text(title)
        desc_norm = normalize_relevance_text(description)
        tags_norm = normalize_relevance_text(tags)
        tax_norm = normalize_relevance_text(f"{category} {subcategory}")
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
            canonical = normalize_relevance_text(alias_info["canonical"])
            if canonical in content_norm:
                return InspirationRelevanceTierEnum.TIER_2_ALIAS, f"Approved alias '{query}' -> canonical '{canonical}' ({alias_info['standard']})"

        # Reverse check: query is canonical, candidate contains approved alias
        for alias_phrase, alias_info in APPROVED_MATERIAL_ALIASES.items():
            canonical = normalize_relevance_text(alias_info["canonical"])
            if canonical == q_norm:
                if alias_info.get("bidirectional", False):
                    alias_norm = normalize_relevance_text(alias_phrase)
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

        # Architectural concept & token overlap matching for multi-word contextual queries
        stopwords = {"the", "and", "or", "for", "with", "from", "types", "different", "best", "used", "house", "room"}
        q_substantive = [w for w in q_norm.split() if len(w) >= 3 and w not in stopwords]
        matched_tokens = [
            w for w in q_substantive
            if (w in content_norm or (w.endswith("s") and len(w) > 3 and w[:-1] in content_norm))
        ]
        if matched_tokens and len(q_substantive) > 0:
            overlap_ratio = len(matched_tokens) / len(q_substantive)
            if overlap_ratio >= 0.5 or len(matched_tokens) >= 2:
                return InspirationRelevanceTierEnum.TIER_3_CONTEXTUAL, f"Supported contextual architectural match: {', '.join(matched_tokens)}"

        # LAYER 5: Inconclusive / Rejected
        return InspirationRelevanceTierEnum.TIER_5_REJECTED, "No exact, alias, or supported contextual match"

relevance_matcher = LayeredQueryMatcher()

# Core Architectural & Construction Taxonomy
CIVIL_CONSTRUCTION_TERMS = {
    "brick", "bricks", "clay brick", "porotherm", "masonry", "mortar", "pointing",
    "cement", "concrete", "rcc", "precast", "drainage", "drain", "slab", "slabs",
    "u-drain", "culvert", "steel", "tmt", "rebar", "reinforcement", "structural steel",
    "foundation", "beam", "column", "lintel", "walling", "partition", "drywall",
    "roofing", "roof tile", "waterproofing", "damp proofing", "sand", "aggregate",
    "civil engineering", "construction", "excavation", "site work", "boundary wall",
    "retaining wall", "aac block", "concrete block", "plaster"
}

INTERIOR_DESIGN_TERMS = {
    "interior", "interiors", "living room", "bedroom", "dining room", "kitchen",
    "kitchen design", "bathroom", "bathroom renovation", "dressing room", "wardrobe",
    "closet", "furniture", "sofa", "bed", "dining table", "lighting", "chandelier",
    "chandeliers", "ceiling", "false ceiling", "cove lighting", "wall panel", "fluted panel",
    "wallpaper", "paint", "texture paint", "terrazzo", "flooring", "wood veneer",
    "laminate", "home transformation", "room redesign", "renovation", "loft", "decor",
    "architectural lighting", "sconce"
}

ARCHITECTURAL_PRODUCT_TERMS = {
    "door", "doors", "carved door", "teak door", "window", "windows", "upvc", "aluminium",
    "sliding door", "glass", "facade", "cladding", "jaali", "tile", "tiles", "porcelain",
    "vitrified", "granite", "marble", "kota stone", "athangudi", "laterite", "pipe", "pipes",
    "cpvc", "plumbing", "drainage channel", "manhole cover", "switchboard", "electrical",
    "conduit", "hardware", "handle", "hinge", "fittings", "pergola", "landscape stone",
    "paver", "pavers", "stepping stones", "paving"
}

LANDSCAPE_AND_DECOR_TERMS = {
    "garden", "pathway", "garden pathway", "walkway", "stepping stone", "waterfall",
    "garden waterfall", "water feature", "fountain", "pond", "pots", "decorative pots",
    "planter", "planters", "indoor pots", "outdoor planters", "vertical garden",
    "terrace garden", "courtyard landscaping", "sculpture", "vase", "mirror", "wall art",
    "boundary wall", "pergola", "outdoor seating", "patio", "landscaping"
}

ALL_ARCHITECTURAL_TERMS = CIVIL_CONSTRUCTION_TERMS | INTERIOR_DESIGN_TERMS | ARCHITECTURAL_PRODUCT_TERMS | LANDSCAPE_AND_DECOR_TERMS

class RelevanceRankingService:
    def __init__(self):
        self.min_relevance_threshold = 0.12
        self.matcher = relevance_matcher

    def tokenize(self, text: Optional[str]) -> Set[str]:
        if not text:
            return set()
        # Split on all non-alphanumeric characters (spaces, hyphens, underscores, punctuation)
        clean = re.sub(r"[^a-zA-Z0-9]", " ", text.lower())
        tokens = set()
        stop_words = {"the", "a", "an", "and", "or", "in", "on", "at", "to", "for", "of", "with", "is", "by", "from", "video", "shorts", "short"}
        for word in clean.split():
            if len(word) >= 3 and word not in stop_words:
                tokens.add(word)
                # Add singular form if plural (e.g. bricks -> brick, tiles -> tile, pots -> pot)
                if word.endswith("s") and len(word) > 3:
                    tokens.add(word[:-1])
                # Architectural root stemming
                if word.endswith("age") and len(word) > 5:
                    tokens.add(word[:-3])  # drainage -> drain
                elif word.endswith("ing") and len(word) > 5:
                    tokens.add(word[:-3])  # flooring -> floor, lighting -> light
                elif word == "drain":
                    tokens.add("drainage")
                elif word == "floor":
                    tokens.add("flooring")
                elif word == "light":
                    tokens.add("lighting")
                elif word == "pave" or word == "paver":
                    tokens.add("paving")
                    tokens.add("pavers")
        return tokens

    def compute_query_relevance(self, ref: ArchitecturalReference, query: str) -> float:
        """
        Evaluates title, material tags, description, architect/creator, and channel identity
        against the user search query. Returns a normalized score between 0.0 and 1.0.
        Tags serve as supporting evidence, with primary weight on accurate titles and descriptions.
        """
        if not query or not query.strip():
            setattr(ref, "inspiration_relevance_tier", InspirationRelevanceTierEnum.TIER_1_EXACT.value)
            return 1.0

        # Stage 1: Evaluate Gate 0 and 5-layer classification
        tier, reason = self.matcher.classify(
            query=query,
            title=ref.title or "",
            description=ref.description or "",
            tags=ref.material_tags or "",
            category=ref.category.name if ref.category else "",
            subcategory=ref.category.slug if ref.category else ""
        )
        setattr(ref, "inspiration_relevance_tier", tier.value)

        # Immediate rejection on Gate 0 exclusion or conflicting substrate
        if tier == InspirationRelevanceTierEnum.TIER_5_REJECTED:
            return 0.0

        q_clean = query.strip().lower()
        q_tokens = self.tokenize(q_clean)
        if not q_tokens:
            return 1.0

        title_tokens = self.tokenize(ref.title)
        tag_tokens = self.tokenize(ref.material_tags)
        desc_tokens = self.tokenize(ref.description)
        creator_tokens = self.tokenize(ref.creator_name or ref.architect_name)
        cat_tokens = self.tokenize((ref.category.slug + " " + ref.category.name) if ref.category else "")

        title_lower = (ref.title or "").lower()
        tag_lower = (ref.material_tags or "").lower()
        desc_lower = (ref.description or "").lower()
        all_item_text = f"{title_lower} {tag_lower} {desc_lower} {ref.category.name.lower() if ref.category else ''}"

        # Disambiguate 'pots' / 'decorative pots' vs cookware/cooking
        if "pot" in q_tokens or "pots" in q_clean:
            if any(cook in all_item_text for cook in ["cooking pot", "pressure cooker", "cookware", "culinary"]):
                return 0.0

        # Domain negative exclusions to prevent concept contamination
        NEGATIVE_EXCLUSIONS = {
            "drainage": ["chandelier", "bedroom", "living room sofa", "residence with brick", "waterfall", "garden pond"],
            "bedroom": ["drainage", "bridge", "tmt rebar", "sewer", "stormwater", "u-drain"],
            "cement": ["bedroom loft", "chandelier"],
            "lighting": ["drainage slab", "concrete channel", "tmt bar", "rebar"],
            "marble": ["brick arch", "drainage channel", "tmt rebar"],
            "garden waterfall": ["bedroom", "chandelier", "tmt bar", "cooking"],
            "decorative pots": ["cooking pot", "pressure cooker", "drainage slab", "bridge"],
            "garden pathway": ["chandelier", "false ceiling", "rebar"],
            "bathroom renovation": ["bridge", "drainage channel", "tmt bar"],
            "kitchen design": ["bathroom shower", "drainage channel", "rebar"],
            "boundary wall": ["chandelier", "bedroom wardrobe", "bathroom shower"],
            "switchboard": ["chandelier", "sconce", "table lamp", "garden lighting"],
            "waterproofing": ["wall painting", "emulsion paint", "decorative paint"],
            "retaining wall": ["bedroom wardrobe", "living room sofa", "interior wall"],
            "rammed earth": ["rebar", "tmt bar", "chandelier", "drainage"],
            "exterior lighting": ["drainage slab", "concrete channel", "u-drain"],
            "rainwater drainage": ["bedroom", "chandelier", "living room sofa"],
            "kitchen storage": ["bathroom shower", "rebar", "tmt bar"],
            "tropical": ["bridge without pillars", "pillar-free bridge"],
            "wood-look": ["waterfall", "garden pond", "chandelier", "drain", "drainage"]
        }
        for term, forbidden in NEGATIVE_EXCLUSIONS.items():
            if term in q_clean or term in q_tokens:
                if any(fb in all_item_text for fb in forbidden):
                    return 0.0

        if "exterior lighting" in q_clean:
            has_light = any(k in all_item_text for k in ["light", "lighting", "lamp", "sconce", "chandelier", "luminaire"])
            has_ext = any(k in all_item_text for k in ["exterior", "facade"])
            if not (has_light and has_ext):
                return 0.0
        if "rainwater drainage" in q_clean:
            if not any(k in all_item_text for k in ["drain", "drainage", "stormwater", "culvert"]):
                return 0.0

        # Conversational intent words and query modifiers
        INTENT_MODIFIERS = {
            "different", "types", "type", "kind", "kinds", "used", "best", "good",
            "how", "what", "where", "which", "make", "create", "ideas", "idea",
            "alternatives", "alternative", "modern", "design", "designs", "home", "house",
            "building", "construction", "stays", "stay", "cooler", "cool", "summer", "warm",
            "provide", "provides", "using", "beside", "for", "with", "walkthrough", "site"
        }

        # Multi-word query validation:
        # Separate core architectural subject tokens from conversational framing
        core_tokens = {t for t in q_tokens if t not in INTENT_MODIFIERS}
        effective_head_tokens = core_tokens if core_tokens else q_tokens

        # Morphological concept grouping:
        # Group singular and plural/stem variants into single concept requirements
        # e.g. {'brick', 'bricks'} -> concept 'brick'
        concept_groups: Dict[str, Set[str]] = {}
        for tok in effective_head_tokens:
            stem = tok[:-1] if (tok.endswith("s") and len(tok) > 3) else tok
            if stem not in concept_groups:
                concept_groups[stem] = set()
            concept_groups[stem].add(tok)
            # Architectural synonyms for common stems
            if stem in ["stormwater"]:
                concept_groups[stem].update(["stormwater", "drainage", "drain", "runoff"])
            elif stem in ["exterior", "facade"]:
                concept_groups[stem].update(["exterior", "facade", "outdoor", "elevation"])
            elif stem in ["small", "compact"]:
                concept_groups[stem].update(["small", "compact", "tiny", "mini", "space-saving"])

        item_content_tokens = title_tokens | tag_tokens | desc_tokens
        item_text_lower = f"{title_lower} {tag_lower} {desc_lower}"

        exact_phrase_match = (q_clean in title_lower) or (q_clean in tag_lower) or (q_clean in desc_lower)

        # Count matched concepts from concept groups
        matched_concepts_count = sum(
            1 for variants in concept_groups.values()
            if bool(variants & item_content_tokens) or any(bool(re.search(rf"\b{re.escape(v)}\b", item_text_lower)) for v in variants)
        )
        total_concepts = max(1, len(concept_groups))

        # Check specific architectural subject matches:
        # If the query contains specific subject terms alongside generic context words (e.g. 'decorative pots', 'garden pathway', 'exposed brick wall'),
        # require that at least one of the specific non-generic architectural concepts matches.
        GENERIC_CONTEXT_WORDS = {
            "garden", "wall", "walls", "decorative", "interior", "flooring",
            "floor", "small", "tropical", "modern", "traditional", "style", "idea",
            "ideas", "design", "designs", "before", "after", "storage",
            "space", "home", "house", "room", "rooms", "side", "sides", "front",
            "rear", "back", "top", "bottom", "left", "right", "electrical",
            "look", "looks"
        }
        matched_specific_concept = False
        has_specific_concepts_in_query = False
        for stem_key, variants in concept_groups.items():
            if stem_key not in GENERIC_CONTEXT_WORDS:
                has_specific_concepts_in_query = True
                if bool(variants & item_content_tokens) or any(bool(re.search(rf"\b{re.escape(v)}\b", item_text_lower)) for v in variants):
                    matched_specific_concept = True
                    break

        if has_specific_concepts_in_query and not matched_specific_concept and not exact_phrase_match:
            return 0.0

        # Verify direct match existence in the item's actual content
        has_direct_match = (
            exact_phrase_match or
            (matched_concepts_count > 0) or
            bool(effective_head_tokens & item_content_tokens) or
            any(bool(re.search(rf"\b{re.escape(t)}\b", item_text_lower)) for t in effective_head_tokens)
        )
        if not has_direct_match:
            return 0.0

        title_matches = len(q_tokens & title_tokens)
        tag_matches = len(q_tokens & tag_tokens)
        desc_matches = len(q_tokens & desc_tokens)
        creator_matches = len(q_tokens & creator_tokens)
        cat_matches = len(q_tokens & cat_tokens)

        substantive_match = (
            (title_matches > 0) or
            (desc_matches > 0) or
            (tag_matches > 0) or
            (q_clean in title_lower) or
            (q_clean in desc_lower) or
            (matched_concepts_count > 0)
        )
        if not substantive_match:
            return 0.0

        score = 0.0

        # Exact phrase match in title (Highest relevance signal)
        if q_clean in title_lower:
            score += 0.65
        # Exact phrase in description
        elif q_clean in desc_lower:
            score += 0.45
        # Exact phrase in tags
        elif q_clean in tag_lower:
            score += 0.35

        # Concept coverage bonus (proportional to how many core concepts matched)
        concept_coverage = matched_concepts_count / total_concepts
        score += concept_coverage * 0.35

        title_overlap = title_matches / max(1, len(q_tokens))
        tag_overlap = tag_matches / max(1, len(q_tokens))
        desc_overlap = desc_matches / max(1, len(q_tokens))

        # Weighting across title, tags and description
        score += title_overlap * 0.30
        score += desc_overlap * 0.15
        score += tag_overlap * 0.15

        if creator_matches > 0:
            score += 0.08

        # Category alignment boost (e.g. searching 'drainage' when category is 'drainage-precast')
        if cat_matches > 0:
            score += 0.25

        # Architectural domain boost (only applied if item already matches query substantively)
        matched_arch_terms = (title_tokens | tag_tokens) & ALL_ARCHITECTURAL_TERMS
        if matched_arch_terms and substantive_match:
            score += min(len(matched_arch_terms) * 0.04, 0.10)

        # Verified status bonus (small trust signal)
        if ref.verification_status in ["VERIFIED", "MANUFACTURER_CONFIRMED"]:
            score += 0.05

        return min(max(score, 0.0), 1.0)

    def compute_personalization_boost(
        self,
        ref: ArchitecturalReference,
        user_interests: Optional[List[str]] = None
    ) -> float:
        """
        Boosts items matching user's recently liked or saved material tags / categories (+0.0 to +0.80).
        """
        if not user_interests:
            return 0.0

        ref_text = f"{ref.title} {ref.material_tags or ''} {ref.description or ''} {ref.category.slug if ref.category else ''} {ref.category.name if ref.category else ''}"
        ref_tokens = self.tokenize(ref_text)
        if not ref_tokens:
            return 0.0

        matches = 0
        for interest in user_interests:
            if not interest or not interest.strip():
                continue
            i_tokens = self.tokenize(interest)
            if i_tokens & ref_tokens:
                matches += len(i_tokens & ref_tokens)

        if matches == 0:
            return 0.0

        # Substantial boost (+0.35 to +0.80) to visibly prioritize liked materials at top of feed
        return min(0.35 + (matches * 0.15), 0.80)

    def rank_and_filter_feed(
        self,
        candidates: List[ArchitecturalReference],
        query: Optional[str] = None,
        user_interests: Optional[List[str]] = None,
        category_slug: Optional[str] = None,
        min_threshold: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Filters out irrelevant content, applies strict image-level deduplication,
        and ranks candidates according to architectural relevance and personalized interest profile.
        """
        threshold = min_threshold if min_threshold is not None else (self.min_relevance_threshold if query else 0.0)
        ranked_items = []
        seen_keys: Set[str] = set()
        seen_images: Set[str] = set()

        for ref in candidates:
            # 1. Deduplication by video ID or slug or title
            dedup_key = ref.video_embed_id or ref.slug or ref.title.lower().strip()
            if dedup_key in seen_keys:
                continue

            # 2. Strict YouTube Thumbnail & Embed Integrity Validation
            if ref.source_platform == "youtube":
                if not ref.video_embed_id or len(ref.video_embed_id.strip()) < 5:
                    continue
                ref.thumbnail_url = f"https://i.ytimg.com/vi/{ref.video_embed_id}/hqdefault.jpg"
                ref.media_url = f"https://i.ytimg.com/vi/{ref.video_embed_id}/hqdefault.jpg"

            # 3. Category match check if category_slug is given
            if category_slug and ref.category and ref.category.slug != category_slug:
                cat_tokens = self.tokenize(category_slug)
                ref_tags = self.tokenize(f"{ref.material_tags} {ref.category.name if ref.category else ''}")
                if not (cat_tokens & ref_tags):
                    continue

            # 4. Calculate Relevance Score FIRST so irrelevant items don't mask relevant items
            query_score = self.compute_query_relevance(ref, query) if query else 1.0

            # Filter out irrelevant results below threshold when a search query is active
            if query and query_score < threshold:
                continue

            # 5. Genuine Duplicate Prevention:
            # Different products or distinct architectural subjects must NOT be discarded merely because they share a stock/catalog image URL.
            # Preserve genuine duplicate prevention using canonical post URLs and image + title concept matching.
            raw_img = (ref.inspiration_image_url or ref.thumbnail_url or ref.media_url or "").strip().lower()
            if raw_img and not ref.video_embed_id:
                normalized_img = re.sub(r"\?.*$", "", raw_img)
                unsplash_id_match = re.search(r"photo-[a-zA-Z0-9-]+", normalized_img)
                img_identifier = unsplash_id_match.group(0) if unsplash_id_match else normalized_img

                # Canonical post source URL check (e.g. duplicate Pinterest pin or Instagram reel)
                if ref.source_url:
                    m_pin = re.search(r"pinterest\.com/pin/([0-9]+)", ref.source_url)
                    m_insta = re.search(r"instagram\.com/(?:p|reel)/([A-Za-z0-9_-]+)", ref.source_url)
                    canon_id = None
                    if m_pin:
                        canon_id = f"pin:{m_pin.group(1)}"
                    elif m_insta:
                        canon_id = f"insta:{m_insta.group(1)}"

                    if canon_id:
                        if canon_id in seen_keys:
                            continue
                        seen_keys.add(canon_id)

                # If personalized feed is requested without specific query, enforce visual image uniqueness to avoid repeating images
                if user_interests and not query:
                    if img_identifier in seen_images:
                        continue
                    seen_images.add(img_identifier)
                else:
                    # In product/keyword discovery, allow distinct products sharing a catalog/stock image,
                    # while preventing genuine duplicate content with matching title/subject tokens
                    title_tokens = tuple(sorted(list(self.tokenize(ref.title))[:2]))
                    img_subject_key = (img_identifier, title_tokens)
                    if img_subject_key in seen_images:
                        continue
                    seen_images.add(img_subject_key)

            seen_keys.add(dedup_key)

            # 6. Personalization score
            pers_boost = self.compute_personalization_boost(ref, user_interests)

            # 7. Provenance, media status, and relevance tier defaults for ArchitecturalReference
            if not getattr(ref, "provenance", None):
                setattr(ref, "provenance", ProvenanceEnum.CURATED_ARCHIVE.value)
            has_media = bool(ref.inspiration_image_url or ref.thumbnail_url or ref.media_url or ref.video_embed_id)
            if not getattr(ref, "media_status", None):
                setattr(ref, "media_status", MediaStatusEnum.MEDIA_READY.value if has_media else MediaStatusEnum.MEDIA_UNUSABLE.value)
            if not getattr(ref, "inspiration_relevance_tier", None):
                setattr(ref, "inspiration_relevance_tier", InspirationRelevanceTierEnum.TIER_1_EXACT.value)

            # 8. Overall Composite Score
            base_score = (query_score * 0.70) if query else 0.70
            final_score = base_score + pers_boost + (0.10 if ref.verification_status == "VERIFIED" else 0.0)

            ranked_items.append({
                "reference": ref,
                "relevance_score": round(final_score, 3),
                "is_personalized": pers_boost > 0
            })

        # Sort by final score descending
        ranked_items.sort(key=lambda x: x["relevance_score"], reverse=True)
        return ranked_items

relevance_service = RelevanceRankingService()
