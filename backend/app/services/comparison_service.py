"""
Comparative Architectural Material Engine for Architect AI (Category 27: Material Comparisons & Selection Guides).
Provides objective, evidence-based side-by-side matrices separating building science principles from commercial claims.
"""

from typing import Dict, List, Any, Optional

MATERIAL_COMPARISONS: Dict[str, Dict[str, Any]] = {
    "clay-brick-vs-aac-block": {
        "id": "clay-brick-vs-aac-block",
        "title": "Clay Brick vs. Autoclaved Aerated Concrete (AAC) Block",
        "category": "Bricks & Blocks (Masonry)",
        "summary": "Clay bricks provide superior thermal mass and high compressive strength for load-bearing walls, whereas AAC blocks offer rapid construction, 60% lower structural dead-load, and significantly higher thermal insulation value (R-value).",
        "material_a": {
            "name": "Traditional Burnt Clay / Wire-Cut Brick",
            "material_type": "Fired Red Clay Unit (IS 1077)",
            "compressive_strength": "7.5 – 10.5 N/mm² (Grade 7.5/10)",
            "dry_density": "1600 – 1900 kg/m³",
            "thermal_conductivity": "0.70 – 0.90 W/m·K (High Thermal Mass, stores daytime heat)",
            "fire_rating": "Up to 4 hours depending on thickness",
            "water_absorption": "12% – 18% by weight",
            "cost_index": "Moderate (₹8 – ₹14 per brick, plus mortar and plaster)",
            "installation_speed": "Standard (approx. 25–30 m² per mason week)",
            "mortared_joints": "10–12 mm cement-sand mortar joints",
            "advantages": [
                "Exceptional compressive strength suitable for multi-storey load-bearing masonry without RCC columns",
                "High thermal mass delays diurnal heat penetration in hot, arid zones",
                "Can be left exposed without plaster (e.g. Laurie Baker rat-trap bond)"
            ],
            "limitations": [
                "Heavy dead weight increases foundation and RCC frame sizing",
                "Requires thick sand-cement plastering on both faces unless wire-cut",
                "Higher mortar consumption and extended curing time"
            ],
            "standards": "IS 1077, IS 2212"
        },
        "material_b": {
            "name": "Autoclaved Aerated Concrete (AAC) Block",
            "material_type": "Cellular Precast Concrete (IS 2185 Part 3)",
            "compressive_strength": "3.5 – 4.5 N/mm² (Non-load-bearing or framed infill)",
            "dry_density": "550 – 650 kg/m³ (approx. 1/3 weight of red brick)",
            "thermal_conductivity": "0.16 – 0.22 W/m·K (3x higher thermal insulation than clay brick)",
            "fire_rating": "Up to 4 hours (non-combustible porous structure)",
            "water_absorption": "High capillary surface suction; requires specialized polymer thin-bed adhesive",
            "cost_index": "Economical in framed structures (reduces steel reinforcement & concrete costs by 12–15%)",
            "installation_speed": "Fast (larger modular size speeds wall laying by 40%)",
            "mortared_joints": "2–3 mm thin-bed polymer adhesive",
            "advantages": [
                "Outstanding thermal insulation reduces air conditioning load in tropical and warm climates",
                "Lightweight structure significantly reduces dead load on columns and footings",
                "Requires minimal joint mortar and thin skim plastering instead of 15mm sand plaster"
            ],
            "limitations": [
                "Not recommended for primary load-bearing walls above 2 storeys without structural RCC frame",
                "Prone to hairline shrinkage cracking if laid with ordinary cement mortar instead of polymer adhesive",
                "Requires specialized wall plugs (nylon anchor expansion plugs) for heavy wall-mounted cabinets"
            ],
            "standards": "IS 2185 Part 3, IS 6041"
        },
        "climate_guidance": "In hot tropical zones (Kerala, Tamil Nadu, Karnataka), AAC blocks provide lower heat ingress through framed exterior walls. For vernacular homes emphasizing exposed masonry and passive breeze ventilation, wire-cut clay bricks in rat-trap bonding remain the standard."
    },
    "marble-vs-granite": {
        "id": "marble-vs-granite",
        "title": "Natural Marble vs. Granite Slabs & Flooring",
        "category": "Natural Stone & Flooring",
        "summary": "Marble is a metamorphic calcite stone prized for translucent veining and luxurious soft warmth, but is vulnerable to acidic staining. Granite is an igneous silica-dense stone offering extreme scratch resistance, zero porosity, and superior performance for high-traffic and kitchen worktops.",
        "material_a": {
            "name": "Natural Marble (Italian / Makrana)",
            "material_type": "Metamorphic Recrystallized Calcite / Dolomite (IS 1130)",
            "hardness": "3 – 4 on Mohs scale (Relatively soft, prone to micro-scratches)",
            "porosity": "0.5% – 2.0% (Porous; susceptible to lemon, vinegar, turmeric acids)",
            "heat_resistance": "Moderate (sudden extreme thermal shock can cause surface discoloration)",
            "finish_options": "Mirror Polish, Satin Honed, Leathered, Antique Brushed",
            "cost_index": "Premium (₹180 – ₹2,500+ / sq.ft depending on quarry and veining)",
            "maintenance": "Requires annual penetrating fluoropolymer sealer; avoid acidic cleaning agents",
            "advantages": [
                "Distinctive organic veining capable of symmetrical bookmatching",
                "Soft tactile warmth under bare feet, ideal for master bedrooms and living areas",
                "Can be re-polished multiple times over decades to restore factory luster"
            ],
            "limitations": [
                "Easily stained and etched by citrus acids, curry oils, and harsh household chemicals",
                "Soft surface shows wear in outdoor or heavy shoe-traffic entrances"
            ],
            "standards": "IS 1130"
        },
        "material_b": {
            "name": "Natural Granite Slabs",
            "material_type": "Igneous Quartz-Feldspar Crystalline Stone (IS 3316)",
            "hardness": "6 – 7 on Mohs scale (Extremely hard, knife-blade scratch-proof)",
            "porosity": "0.1% – 0.5% (Very low porosity; highly stain resistant)",
            "heat_resistance": "High (tolerates hot cookware placed directly on kitchen counters)",
            "finish_options": "High Polish, Flamed (Anti-Skid Outdoor), Lapato, Bush-Hammered",
            "cost_index": "Moderate to High (₹85 – ₹450 / sq.ft for South Indian varieties)",
            "maintenance": "Very low maintenance; cleans with plain water and mild detergent",
            "advantages": [
                "Virtually scratch-proof and impervious to kitchen food stains",
                "Ideal for kitchen countertops, staircase treads, door jambs, and outdoor paving",
                "Flamed finish delivers certified R11 slip-resistance around swimming pools"
            ],
            "limitations": [
                "Heavy and rigid; requires sturdy base cabinetry and diamond wet-cutting tools",
                "Uniform speckled or crystalline pattern lacks the translucent organic veining of marble"
            ],
            "standards": "IS 3316"
        },
        "climate_guidance": "For kitchen countertops and outdoor wet verandahs, Granite is vastly superior in durability and chemical resistance. For formal indoor living areas and air-conditioned suites where luxury veining is desired, Marble delivers unmatched visual warmth."
    },
    "aluminium-vs-upvc-windows": {
        "id": "aluminium-vs-upvc-windows",
        "title": "Aluminium Windows vs. uPVC Window Systems",
        "category": "Windows & Doors (Building Envelope)",
        "summary": "Aluminium profiles provide ultra-slim sightlines, high structural wind-load capacity for high-rises, and modern powder-coated colors. uPVC window frames provide superior thermal acoustic insulation and zero corrosion in saline coastal environments.",
        "material_a": {
            "name": "Thermally-Broken Aluminium Windows",
            "material_type": "Extruded Aluminium Alloy 6063-T6 (IS 733 / IS 1081)",
            "frame_profile_width": "Ultra-slim sightlines (35mm – 50mm profile interlock)",
            "thermal_insulation": "Requires polyamide thermal-break strip to prevent heat conduction",
            "acoustic_reduction": "28 – 35 dB with laminated DGU glass",
            "coastal_resistance": "Requires marine-grade PVDF or 25-micron architectural anodizing in coastal areas",
            "structural_strength": "High tensile strength; supports floor-to-ceiling glass spans exceeding 3 meters",
            "cost_index": "Moderate to High (₹450 – ₹1,200 / sq.ft)",
            "advantages": [
                "Minimalist architectural sightlines maximizing natural glass daylight area",
                "High wind-load resistance for high-rise apartments and coastal gale exposures",
                "100% recyclable metal framing"
            ],
            "limitations": [
                "Without a thermal-break barrier, metal frames conduct outdoor heat directly indoors",
                "Improperly treated hardware can experience galvanic corrosion if dissimilar metals contact"
            ],
            "standards": "IS 733, IS 1948"
        },
        "material_b": {
            "name": "Unplasticized Polyvinyl Chloride (uPVC) Windows",
            "material_type": "Multi-Chambered uPVC Extrusion with Galvanized Steel Core (IS 14856)",
            "frame_profile_width": "Standard profile width (60mm – 75mm profile depth)",
            "thermal_insulation": "Excellent natural non-conductor (U-value 1.8 – 2.4 W/m²K)",
            "acoustic_reduction": "32 – 40 dB with double-glazed EPDM gaskets",
            "coastal_resistance": "Completely immune to salt air corrosion, humidity, and coastal efflorescence",
            "structural_strength": "Reinforced with concealed galvanized steel channel inside chambers",
            "cost_index": "Economical to Moderate (₹380 – ₹850 / sq.ft)",
            "advantages": [
                "Completely maintenance-free; will not rust, rot, warp, or peel in high humidity",
                "Fusion-welded corner joints and multi-point locking deliver high acoustic soundproofing",
                "High thermal resistance keeps conditioned indoor air cool in tropical climates"
            ],
            "limitations": [
                "Bulkier frame sightlines compared to slimline aluminium",
                "Requires high-grade titanium dioxide (TiO2) UV stabilizers to prevent yellowing under intense tropical sun"
            ],
            "standards": "IS 14856, EN 12608"
        },
        "climate_guidance": "For coastal areas (Kanyakumari, Kochi, Chennai, Mumbai), uPVC is the benchmark choice against salt corrosion. For panoramic floor-to-ceiling sliding glass walls where minimal frame visibility is paramount, thermally-broken Aluminium is preferred."
    },
    "solid-wood-vs-wood-tiles": {
        "id": "solid-wood-vs-wood-tiles",
        "title": "Solid Natural Hardwood vs. Wood-Look Vitrified Tiles",
        "category": "Flooring Materials",
        "summary": "Solid hardwood delivers authentic organic warmth, acoustic softness, and natural patina, but requires seasonal humidity control and termite vigilance. Wood-look vitrified porcelain tiles offer 100% waterproof performance, zero maintenance, and total termite immunity while mimicking wood grain aesthetics.",
        "material_a": {
            "name": "Solid Natural Hardwood (Teak / Oak)",
            "material_type": "Kiln-Dried Natural Timber Planks",
            "water_resistance": "Low to Moderate; vulnerable to standing water and seasonal swelling",
            "termite_resistance": "Requires chemical anti-termite treatment unless dense seasoned teak",
            "scratch_repair": "Can be sanded down and re-varnished or oiled multiple times",
            "tactile_feel": "Warm, resilient, organically soft under bare feet",
            "cost_index": "High (₹350 – ₹1,200 / sq.ft including sub-base & PU polish)",
            "advantages": [
                "Genuine organic wood grain with natural character and acoustic warmth",
                "Increases property value and develops an attractive heritage patina",
                "Comfortable to walk on throughout all seasons without thermal chill"
            ],
            "limitations": [
                "Unsuitable for bathrooms, kitchens, semi-outdoor verandahs, or damp basements",
                "Requires careful humidity expansion gap detailing around room perimeters"
            ],
            "standards": "IS 1141, IS 1708"
        },
        "material_b": {
            "name": "Wood-Look Vitrified Porcelain Planks",
            "material_type": "High-Density Sintered Porcelain / Vitrified Tile (IS 15622)",
            "water_resistance": "100% Waterproof (<0.05% water absorption)",
            "termite_resistance": "100% Termite-proof and rot-proof",
            "scratch_repair": "High surface hardness (PEI IV/V); cannot be sanded if chipped",
            "tactile_feel": "Hard and cool to touch; can be installed over underfloor heating",
            "cost_index": "Economical to Moderate (₹65 – ₹220 / sq.ft)",
            "advantages": [
                "Completely impervious to moisture, spills, bathroom steam, and pet claws",
                "Zero maintenance; requires no waxing, sanding, or chemical polish",
                "Can be used seamlessly from indoor living rooms out onto open balconies and verandahs"
            ],
            "limitations": [
                "Lacks the resilient organic softness and acoustic dampening of real wood",
                "Repeats pattern every 6–8 tiles unless choosing high-end multi-face printing"
            ],
            "standards": "IS 15622 / ISO 13006"
        },
        "climate_guidance": "In high-humidity coastal monsoon zones, wood-look vitrified tiles prevent warped floorboards and termite infestation. In climate-controlled dry bedrooms, authentic hardwood offers incomparable comfort."
    }
}

def get_all_comparisons() -> List[Dict[str, Any]]:
    return list(MATERIAL_COMPARISONS.values())

def get_comparison_by_id(comp_id: str) -> Optional[Dict[str, Any]]:
    return MATERIAL_COMPARISONS.get(comp_id)
