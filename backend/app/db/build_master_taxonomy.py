"""
Nivora — Master Keyword Explorer Taxonomy Builder (Phase 5)
Constructs the complete 14-category Master Architectural & Construction Taxonomy
incorporating Sections A-M and 5-14.
"""

import json
import os

def build_taxonomy():
    categories = [
        # ==============================================================================
        # 1. ARCHITECTURE
        # ==============================================================================
        {
            "id": 1,
            "name": "Architecture",
            "slug": "architecture",
            "icon": "🏛️",
            "description": "Architectural typologies, vernacular traditions, residential & commercial master designs, and documentation.",
            "supplier_category": "Architectural Design & Turnkey Planning",
            "subcategories": [
                {
                    "name": "Residential Architecture",
                    "items": [
                        {
                            "name": "Modern Villas",
                            "variants": [
                                "Minimalist Flat Roof Villa",
                                "Cantilevered Luxury Villa",
                                "Tropical Courtyard Villa",
                                "Double-Height Glass Villa",
                                "Biophilic Garden Villa"
                            ]
                        },
                        {
                            "name": "Bungalows & Single Storey",
                            "variants": [
                                "Single-Storey Contemporary Bungalow",
                                "Colonial Wrap-Around Porch Bungalow",
                                "Sloped Roof Timber Bungalow",
                                "L-Shaped Courtyard Bungalow"
                            ]
                        },
                        {
                            "name": "Duplex Houses",
                            "variants": [
                                "Open Plan Duplex Residence",
                                "Mezzanine Floor Duplex",
                                "Corner Plot Duplex House",
                                "Split-Level Contemporary Duplex"
                            ]
                        },
                        {
                            "name": "Compact Homes",
                            "variants": [
                                "Small House Designs Under 1200 sqft",
                                "Narrow Plot Townhouse",
                                "Micro-Living Urban House",
                                "Low-Cost Sustainable Cottage"
                            ]
                        },
                        {
                            "name": "Apartments & Penthouses",
                            "variants": [
                                "Penthouse with Sky Terrace",
                                "Duplex Luxury Apartment",
                                "High-Rise Glass Balcony Residence"
                            ]
                        },
                        {
                            "name": "Farmhouse Designs",
                            "variants": [
                                "Rustic Timber Farmhouse",
                                "Courtyard Retreat Farmhouse",
                                "Modern Barn House"
                            ]
                        }
                    ]
                },
                {
                    "name": "Traditional & Vernacular Architecture",
                    "items": [
                        {
                            "name": "Kerala Traditional Architecture",
                            "variants": [
                                "Nalukettu Traditional Courtyard House",
                                "Ettukettu Heritage Residence",
                                "Tharavadu Ancestral Home",
                                "Charupady Built-in Wooden Verandah Benches",
                                "Padippura Entrance Gateway",
                                "Sloped Clay Tile Roof Architecture"
                            ]
                        },
                        {
                            "name": "Chettinad Architecture",
                            "variants": [
                                "Chettinad Courtyard Mansion",
                                "Athangudi Tiled Living Hall",
                                "Burma Teak Pillar Verandahs"
                            ]
                        },
                        {
                            "name": "Regional Heritage Typologies",
                            "variants": [
                                "Rajasthani Haveli with Jharokha Balconies",
                                "Goan Portuguese Heritage Villa",
                                "Colonial Planter Bungalow",
                                "Alpine Sloped Timber Chalet"
                            ]
                        }
                    ]
                },
                {
                    "name": "Commercial & Institutional Architecture",
                    "items": [
                        {
                            "name": "Office & Commercial Buildings",
                            "variants": [
                                "Corporate Headquarters Complex",
                                "Boutique Commercial Studio",
                                "Glass Curtain-Wall Office Building",
                                "Co-Working Office Architecture"
                            ]
                        },
                        {
                            "name": "Hospitality & Resort Architecture",
                            "variants": [
                                "Eco-Resort Timber Cottages",
                                "Boutique Heritage Hotel",
                                "Water Villa Resort Architecture",
                                "Cliffside Pavilion Resort"
                            ]
                        },
                        {
                            "name": "Retail & Public Buildings",
                            "variants": [
                                "Shopping Mall Architecture",
                                "High-Street Retail Showrooms",
                                "Cultural & Community Center",
                                "School & University Campus"
                            ]
                        }
                    ]
                },
                {
                    "name": "Architectural Drawings & Documentation",
                    "items": [
                        {
                            "name": "Floor Plans & Master Layouts",
                            "variants": [
                                "Architectural Working Floor Plans",
                                "Conceptual Space Layouts",
                                "Measured Site Plans",
                                "Master Layout Plans"
                            ]
                        },
                        {
                            "name": "Elevations, Sections & Joinery Details",
                            "variants": [
                                "Front & Side Elevation Drawings",
                                "Structural Cross-Sections",
                                "Door and Window Schedules",
                                "Joinery & Staircase Detail Drawings"
                            ]
                        },
                        {
                            "name": "CAD, BIM & 3D Visualisations",
                            "variants": [
                                "Standard 2D CAD Blocks & Symbols",
                                "Revit BIM Families & Objects",
                                "SketchUp 3D Architectural Models",
                                "High-Resolution 3D Architectural Renders"
                            ]
                        },
                        {
                            "name": "BOQ, Cost Estimation & Specification Sheets",
                            "variants": [
                                "Bill of Quantities BOQ",
                                "Detailed Construction Cost Estimates",
                                "Technical Specification Sheets",
                                "Material Test Reports & Standards"
                            ]
                        }
                    ]
                },
                {
                    "name": "Sustainable Architecture & Passive Design",
                    "items": [
                        {
                            "name": "Passive Climate Design",
                            "variants": [
                                "Courtyard Stack Ventilation",
                                "Solar Shading & Sun Path Orientation",
                                "Thermal Mass Wall Systems",
                                "Wind-Catcher Ventilation Towers"
                            ]
                        },
                        {
                            "name": "Green Building Systems",
                            "variants": [
                                "Net-Zero Energy Homes",
                                "Living Green Roof Buildings",
                                "Earth-Sheltered Structures",
                                "Rainwater Harvesting Master Design"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 2. EXTERIOR & FACADE
        # ==============================================================================
        {
            "id": 2,
            "name": "Exterior & Facade",
            "slug": "exterior-facade",
            "icon": "🏢",
            "description": "Building envelopes, exterior elevations, cladding systems, sun-control louvers, and roofing.",
            "supplier_category": "Facade & Exterior Cladding Contractors",
            "subcategories": [
                {
                    "name": "Elevation & Facade Systems",
                    "items": [
                        {
                            "name": "Modern House Elevations",
                            "variants": [
                                "Contemporary Geometric Front Elevation",
                                "Minimalist Box Elevation",
                                "Double-Height Entrance Portico",
                                "Cantilevered Canopy Elevation"
                            ]
                        },
                        {
                            "name": "Double-Skin & Commercial Facades",
                            "variants": [
                                "Double-Skin Ventilated Curtain Wall",
                                "Dynamic Motorized Kinetic Facade",
                                "Structural Glazed Curtain Wall",
                                "Precast Concrete Facade Panels"
                            ]
                        }
                    ]
                },
                {
                    "name": "Exterior Wall Cladding",
                    "items": [
                        {
                            "name": "Natural Stone Cladding",
                            "variants": [
                                "Teakwood Sandstone Wall Cladding",
                                "Natural Slate Stone Veneer",
                                "Flamed Granite Facade Slabs",
                                "Travertine Exterior Tiles"
                            ]
                        },
                        {
                            "name": "Engineered & Composite Cladding",
                            "variants": [
                                "WPC Fluted Exterior Cladding Louvers",
                                "Aluminium Composite Panel ACP Cladding",
                                "Fiber Cement Exterior Siding Boards",
                                "Terracotta Rain-Screen Tiles"
                            ]
                        },
                        {
                            "name": "Exposed Brick & Traditional Facades",
                            "variants": [
                                "Exposed Wirecut Brick Cladding",
                                "Porotherm Exterior Facade",
                                "Dressed Laterite Stone Facade"
                            ]
                        }
                    ]
                },
                {
                    "name": "Sun Shading, Louvers & Metalwork",
                    "items": [
                        {
                            "name": "Architectural Louver Systems",
                            "variants": [
                                "Aluminium Aerofoil Sun Louvers",
                                "Motorized Exterior Sun-Control Louvers",
                                "Vertical Wooden Louver Screens"
                            ]
                        },
                        {
                            "name": "Decorative Screens & Jali",
                            "variants": [
                                "CNC Cut Aluminium Jali Panels",
                                "Terracotta Clay Breeze Blocks",
                                "Laser-Cut Corten Steel Screens"
                            ]
                        }
                    ]
                },
                {
                    "name": "Balcony, Porch & Terrace Features",
                    "items": [
                        {
                            "name": "Balcony Railings & Barriers",
                            "variants": [
                                "Frameless Glass Balcony Railings",
                                "Stainless Steel Cable Balustrades",
                                "Stainless Steel Invisible Safety Grilles"
                            ]
                        },
                        {
                            "name": "Terrace & Balcony Drainage",
                            "variants": [
                                "Rainwater Drainage Scuppers",
                                "Parapet Drainage Spouts",
                                "Balcony Floor Drain Weep Holes"
                            ]
                        },
                        {
                            "name": "Sit-outs, Verandahs & Canopies",
                            "variants": [
                                "Covered Front Sit-outs",
                                "Glass & Steel Entrance Canopies",
                                "Tensile Fabric Car Parking Shade Canopies",
                                "Terrace Pergolas"
                            ]
                        }
                    ]
                },
                {
                    "name": "Roofing Systems & Rainwater Drainage",
                    "items": [
                        {
                            "name": "Traditional & Pitched Roofing",
                            "variants": [
                                "Mangalore Clay Roof Tiles",
                                "Flat Ceramic Roof Tiles",
                                "Natural Slate Roofing Shingles"
                            ]
                        },
                        {
                            "name": "Metal & Polycarbonate Roofing",
                            "variants": [
                                "Standing Seam Metal Roofing Sheets",
                                "Insulated Sandwich PUF Roofing Panels",
                                "Multi-Wall Polycarbonate Skylight Sheets",
                                "Corrugated UPVC Roofing Sheets"
                            ]
                        },
                        {
                            "name": "Roof Drainage Accessories",
                            "variants": [
                                "Seamless Aluminium Rainwater Gutters",
                                "PVC Downspout Pipes",
                                "Leaf Guards & Rainwater Collector Boxes"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 3. INTERIOR SPACES
        # ==============================================================================
        {
            "id": 3,
            "name": "Interior Spaces",
            "slug": "interior-spaces",
            "icon": "🛋️",
            "description": "Residential & commercial interior spaces, room typologies, staircases, and specialized living areas.",
            "supplier_category": "Interior Fitout & Modular Contractors",
            "subcategories": [
                {
                    "name": "Living & Dining Spaces",
                    "items": [
                        {
                            "name": "Living Room Spaces",
                            "variants": [
                                "Double-Height Formal Living Room",
                                "Contemporary Open Plan Living Space",
                                "Mezzanine Lounge",
                                "Sunken Living Room Pit"
                            ]
                        },
                        {
                            "name": "Dining & Entertaining Spaces",
                            "variants": [
                                "Formal Dining Area",
                                "Open Dining with Kitchen Island",
                                "Built-in Breakfast Bar Counter",
                                "Home Wine & Cocktail Bar"
                            ]
                        }
                    ]
                },
                {
                    "name": "Kitchens & Utility Areas",
                    "items": [
                        {
                            "name": "Modular Kitchen Spaces",
                            "variants": [
                                "Island Modular Kitchen Layout",
                                "L-Shaped Ergonomic Kitchen",
                                "Parallel Galley Kitchen",
                                "Open Kitchen with Breakfast Counter"
                            ]
                        },
                        {
                            "name": "Utility & Laundry Rooms",
                            "variants": [
                                "Heavy-Duty Stainless Steel Utility Scrub Sinks",
                                "Integrated Granite Drainboards",
                                "Washing Machine & Dryer Stacking Cabinets",
                                "Retractable Ceiling-Mounted Drying Racks",
                                "Broom & Cleaning Utility Cupboards",
                                "Built-in Ironing Board Storage",
                                "Laundry Quartz Countertops"
                            ]
                        },
                        {
                            "name": "Pantry & Food Storage",
                            "variants": [
                                "Walk-in Butler's Pantry",
                                "Tall Unit Pull-Out Larder",
                                "Corner Magic Carousel Storage"
                            ]
                        }
                    ]
                },
                {
                    "name": "Bedrooms & Dressing Suites",
                    "items": [
                        {
                            "name": "Master Bedrooms",
                            "variants": [
                                "Luxury Master Bedroom Suite",
                                "Minimalist Platform Bedroom",
                                "Bedroom with Private Balcony Sit-out"
                            ]
                        },
                        {
                            "name": "Wardrobes & Dressing Areas",
                            "variants": [
                                "Walk-in Dressing Closet with Island",
                                "Floor-to-Ceiling Built-in Wardrobes",
                                "Dressing Vanity Table with Backlit Mirror"
                            ]
                        },
                        {
                            "name": "Kids & Guest Bedrooms",
                            "variants": [
                                "Kids Bedroom with Bunk Beds",
                                "Compact Guest Bedroom Suite"
                            ]
                        }
                    ]
                },
                {
                    "name": "Bathrooms & Powder Rooms",
                    "items": [
                        {
                            "name": "Ensuite Bathrooms",
                            "variants": [
                                "Master Bathroom with Freestanding Soak Tub",
                                "Walk-in Rain Shower with Glass Partition",
                                "Floating Double Vanity Washroom"
                            ]
                        },
                        {
                            "name": "Powder Rooms & Restrooms",
                            "variants": [
                                "Compact Powder Room with Statement Mirror",
                                "Guest Restroom with Wall-Hung Commode"
                            ]
                        }
                    ]
                },
                {
                    "name": "Staircases & Vertical Circulation",
                    "items": [
                        {
                            "name": "Staircase Architectural Types & Layouts",
                            "variants": [
                                "Floating Cantilever Staircase",
                                "Spiral Staircase",
                                "Helical Curved Luxury Staircase",
                                "Dog-Legged Half-Turn Staircase",
                                "Mono-Stringer Steel Staircase",
                                "Open-Riser Modern Staircase",
                                "Straight Flight Staircase",
                                "Modular Prefabricated Staircase",
                                "Loft Pull-Down Ladders",
                                "Spiral Metal Fire Escapes"
                            ]
                        },
                        {
                            "name": "Staircase Treads, Risers & Step Materials",
                            "variants": [
                                "Solid Teak Wood Stair Treads",
                                "Italian Marble Treads & Risers",
                                "Flamed Black Granite Anti-Skid Steps",
                                "Toughened Structural Glass Steps",
                                "Steel Checkered Plate Industrial Treads",
                                "Anti-Slip Stair Nosing Profiles",
                                "Staircase Skirting & Cladding"
                            ]
                        },
                        {
                            "name": "Staircase Railings & Balustrades",
                            "variants": [
                                "Frameless Glass Balustrades with Base Shoe",
                                "Stainless Steel Tension Cable Railing",
                                "Wrought Iron Ornate Balusters",
                                "Continuous Round Wooden Handrails",
                                "Minimalist Matte Black MS Railings",
                                "Railing Base Clamps & Glass Spigots"
                            ]
                        },
                        {
                            "name": "Staircase Structural Hardware & Step Lighting",
                            "variants": [
                                "Concealed Heavy-Duty Wall Anchors",
                                "Heavy Structural Steel Stringer Beams",
                                "Recessed LED Step Lights",
                                "Undermount Handrail LED Channel",
                                "Heavy-Duty Handrail Wall Brackets"
                            ]
                        }
                    ]
                },
                {
                    "name": "Specialized Residential Spaces",
                    "items": [
                        {
                            "name": "Spiritual & Cultural Spaces",
                            "variants": [
                                "Traditional Carved Wooden Pooja Mandir",
                                "Minimalist Marble Pooja Room",
                                "Meditative Courtyard"
                            ]
                        },
                        {
                            "name": "Leisure, Entertainment & Wellness",
                            "variants": [
                                "Home Cinema Theatre with Acoustic Paneling",
                                "Home Gym & Yoga Studio",
                                "Reading Nook & Library Bookshelf Wall",
                                "Indoor Landscaped Light Courtyard"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 4. CONSTRUCTION MATERIALS
        # ==============================================================================
        {
            "id": 4,
            "name": "Construction Materials",
            "slug": "construction-materials",
            "icon": "🧱",
            "description": "Structural steel, cement, bricks, blocks, precast, scaffolding, civil engineering, and construction machinery.",
            "supplier_category": "Building Materials Stockyards & Manufacturers",
            "subcategories": [
                {
                    "name": "Structural Steel & Rebar",
                    "items": [
                        {
                            "name": "TMT Steel Rebar",
                            "variants": [
                                "TMT Rebar 6 mm Stirrup Wire",
                                "TMT Rebar 8 mm",
                                "TMT Rebar 10 mm",
                                "TMT Rebar 12 mm",
                                "TMT Rebar 16 mm",
                                "TMT Rebar 20 mm",
                                "TMT Rebar 25 mm",
                                "Fe 500D Grade Rebar",
                                "Fe 550D Corrosion Resistant Rebar"
                            ]
                        },
                        {
                            "name": "Structural Steel Sections",
                            "variants": [
                                "Structural Steel I-Beams",
                                "H-Columns",
                                "MS Channels",
                                "Equal Angles",
                                "Square Hollow Sections SHS",
                                "Rectangular Hollow Sections RHS"
                            ]
                        },
                        {
                            "name": "Steel Reinforcement Accessories",
                            "variants": [
                                "Mechanical Rebar Couplers",
                                "Rebar Plastic Spacers",
                                "High-Strength Concrete Cover Blocks",
                                "Annealed GI Binding Wire"
                            ]
                        }
                    ]
                },
                {
                    "name": "Cement, Concrete & Mortar",
                    "items": [
                        {
                            "name": "Standard Bagged Cement",
                            "variants": [
                                "OPC 53 Grade High Strength Cement",
                                "PPC Portland Pozzolana Cement",
                                "High Alumina White Cement",
                                "Masonry Cement"
                            ]
                        },
                        {
                            "name": "Ready-Mix & Specialized Concrete",
                            "variants": [
                                "Ready-Mix Concrete RMC M25 M30 M40",
                                "Microcement Decorative Floor Coating",
                                "Self-Leveling Underlayment Screed",
                                "Non-Shrink Precision Grout"
                            ]
                        },
                        {
                            "name": "Sustainable & Low-Carbon Cements",
                            "variants": [
                                "Geopolymer Slag-Based Cement",
                                "Low-Carbon Blended Limestone Calcined Cement"
                            ]
                        }
                    ]
                },
                {
                    "name": "Bricks, Blocks & Masonry",
                    "items": [
                        {
                            "name": "Clay Bricks & Masonry Units",
                            "variants": [
                                "Wirecut Red Clay Bricks",
                                "Porotherm Clay Cavity Wall Blocks",
                                "Terracotta Perforated Bricks"
                            ]
                        },
                        {
                            "name": "Lightweight & Concrete Blocks",
                            "variants": [
                                "AAC Autoclaved Aerated Concrete Lightweight Blocks",
                                "Solid Precast Concrete Blocks",
                                "Fly Ash High-Strength Bricks",
                                "Natural Dressed Laterite Stone Blocks",
                                "Compressed Stabilized Earth Blocks CSEB"
                            ]
                        }
                    ]
                },
                {
                    "name": "Precast, Prefabrication & Civil Engineering",
                    "items": [
                        {
                            "name": "Precast Concrete Structural Elements",
                            "variants": [
                                "Precast Hollow-Core Floor Slabs",
                                "Precast RCC Beams & Columns",
                                "Precast Boundary Wall Panels",
                                "Precast Concrete Staircase Flights"
                            ]
                        },
                        {
                            "name": "Prefabricated Building Systems",
                            "variants": [
                                "Structural Steel Roof Trusses",
                                "Welded Space Frames",
                                "Tensile Fabric Membrane Canopies",
                                "PUF Insulated Sandwich Wall Panels",
                                "Modular Light Gauge Steel Frame LGSF Buildings"
                            ]
                        },
                        {
                            "name": "Foundations & Geotechnical Systems",
                            "variants": [
                                "RCC Bored Pile Foundations",
                                "Raft Slabs",
                                "Biaxial Soil Stabilization Geogrids",
                                "Non-Woven Geotextile Membrane",
                                "Galvanized Wire Gabion Retaining Walls"
                            ]
                        },
                        {
                            "name": "Civil Infrastructure & Drainage Products",
                            "variants": [
                                "Precast Concrete Box Culverts",
                                "Precast U-Shaped Drainage Channels",
                                "Precast Road Kerb Stones",
                                "Bituminous Hot-Mix Asphalt",
                                "Structural Bridge Expansion Joints & Neoprene Bearings"
                            ]
                        }
                    ]
                },
                {
                    "name": "Construction Tools, Machinery & Site Supplies",
                    "items": [
                        {
                            "name": "Hand Construction Tools",
                            "variants": [
                                "Laser Precision Levels",
                                "Spirit Levels",
                                "Manual Ceramic Tile Cutters",
                                "Plastic Tile Leveling Clips & Wedges",
                                "Notched Masonry Trowels",
                                "Putty Knives",
                                "Heavy-Duty Caulking Guns",
                                "Steel Measuring Tapes"
                            ]
                        },
                        {
                            "name": "Power Tools & Cutting Equipment",
                            "variants": [
                                "SDS-Plus Rotary Hammer Drills",
                                "Demolition Breaker Hammers",
                                "Variable-Speed Angle Grinders",
                                "Heavy-Duty Circular Saws",
                                "Wall Chasers with Dust Extraction",
                                "Airless Paint Sprayer Guns"
                            ]
                        },
                        {
                            "name": "Heavy Construction Machinery",
                            "variants": [
                                "Hydraulic Crawler Excavators",
                                "Backhoe Loaders",
                                "Tower Cranes",
                                "Portable Concrete Mixers",
                                "Concrete Boom Delivery Pumps",
                                "Transit Mixer Trucks",
                                "Plate Soil Compactors",
                                "Electric Scissor Lifts"
                            ]
                        },
                        {
                            "name": "Formwork & Scaffolding Systems",
                            "variants": [
                                "Aluminium Mivan Formwork Panels",
                                "Heavy-Duty Adjustable Steel Props",
                                "Cuplock Scaffolding Systems",
                                "Film-Faced Shuttering Plywood",
                                "Formwork Chemical Release Agent"
                            ]
                        },
                        {
                            "name": "Fasteners, Anchors & PPE Safety",
                            "variants": [
                                "Chemical Epoxy Capsule Anchors",
                                "Metallic Expansion Wedge Bolts",
                                "Stainless Steel Self-Drilling Screws",
                                "Construction Safety Helmets",
                                "Full-Body Safety Harnesses",
                                "Debris Safety Netting",
                                "Heavy Waterproof Tarpaulins"
                            ]
                        }
                    ]
                },
                {
                    "name": "Sustainable, Eco-Friendly & Alternative Materials",
                    "items": [
                        {
                            "name": "Bio-Based Structural Materials",
                            "variants": [
                                "Treated Structural Bamboo Poles",
                                "Engineered Bamboo Beams",
                                "Reclaimed Antique Teak Timber",
                                "Recycled Plastic Lumber Planks"
                            ]
                        },
                        {
                            "name": "Earth & Natural Wall Construction",
                            "variants": [
                                "Rammed Earth Monolithic Walls",
                                "Cob Earthen Construction",
                                "Straw Bale Insulated Walls",
                                "Hempcrete Bio-Composite Blocks"
                            ]
                        },
                        {
                            "name": "Eco-Insulation & Coatings",
                            "variants": [
                                "Jute & Coir Acoustic Baffles",
                                "Recycled Denim Textile Insulation",
                                "Natural Expanded Cork Floor Sheets",
                                "Cool Roof Heat-Reflective Solar Paint"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 5. PLUMBING & SANITARYWARE
        # ==============================================================================
        {
            "id": 5,
            "name": "Plumbing & Sanitaryware",
            "slug": "plumbing-sanitaryware",
            "icon": "🚿",
            "description": "Piping networks, drainage systems, sanitaryware, luxury bath fittings, pumps, water tanks, and purification.",
            "supplier_category": "Plumbing, Sanitaryware & Bath Showrooms",
            "subcategories": [
                {
                    "name": "Pipes, Fittings & Drainage Systems",
                    "items": [
                        {
                            "name": "Potable Water Supply Piping",
                            "variants": [
                                "CPVC SDR 11 Hot & Cold Pipes",
                                "Brass Threaded CPVC Fittings",
                                "UPVC Schedule 40 Cold Water Pipes",
                                "Multi-Layer Composite PEX Pipes"
                            ]
                        },
                        {
                            "name": "Drainage, Soil & Waste Piping",
                            "variants": [
                                "SWR Drainage Pipes with Rubber Ring Joint",
                                "SWR Double Socket Bends & Tees",
                                "Underground HDPE Double-Wall Corrugated Pipes",
                                "Cast Iron Hubless Soil Pipes"
                            ]
                        },
                        {
                            "name": "Floor Drains & Traps",
                            "variants": [
                                "Stainless Steel 304 Tile-Insert Floor Drains",
                                "Linear Walk-in Shower Drains",
                                "Heavy-Duty Driveway Trench Drains with Grates",
                                "PVC Multi-Inlet Floor Traps"
                            ]
                        }
                    ]
                },
                {
                    "name": "Sanitaryware & Toilets",
                    "items": [
                        {
                            "name": "Water Closets & Commodes",
                            "variants": [
                                "Wall-Hung Rimless Water Closet",
                                "Concealed Dual-Flush In-Wall Cistern",
                                "Floor-Mounted One-Piece EWC",
                                "Smart Electronic Toilet with Heated Bidet"
                            ]
                        },
                        {
                            "name": "Washbasins & Vanities",
                            "variants": [
                                "Tabletop Ceramic Vessel Basins",
                                "Undercounter Seamless Vanity Basins",
                                "Freestanding Monolith Pedestal Basins",
                                "Heavy-Duty Stainless Steel Utility Scrub Sinks"
                            ]
                        },
                        {
                            "name": "Bathtubs & Shower Enclosures",
                            "variants": [
                                "Freestanding High-Gloss Acrylic Soaking Tubs",
                                "Air-Jet Jacuzzi Whirlpool Bathtubs",
                                "10mm Toughened Fluted Glass Shower Cubicles"
                            ]
                        }
                    ]
                },
                {
                    "name": "Bath Fittings, Faucets & Showers",
                    "items": [
                        {
                            "name": "Mixers & Diverters",
                            "variants": [
                                "Concealed Thermostatic Shower Diverters with Body Jets",
                                "Tall Single-Lever Basin Mixers",
                                "Wall-Mounted Waterfall Basin Spouts",
                                "Infrared Touchless Sensor Faucets"
                            ]
                        },
                        {
                            "name": "Showers & Handsets",
                            "variants": [
                                "Ceiling-Mounted Multi-Flow Rain Showers",
                                "Multi-Function Handheld Showers with Slide Rail",
                                "Heavy-Duty Solid Brass Health Faucets"
                            ]
                        }
                    ]
                },
                {
                    "name": "Water Storage, Pumps & Treatment",
                    "items": [
                        {
                            "name": "Water Storage Tanks",
                            "variants": [
                                "Overhead 4-Layer Antibacterial Polyethylene Tanks",
                                "Underground Stainless Steel 304 Water Tanks",
                                "Modular Bolted GRP Panel Tanks"
                            ]
                        },
                        {
                            "name": "Pumps & Water Automation",
                            "variants": [
                                "Automatic Multi-Stage Pressure Booster Pumps",
                                "Submersible Deep-Well Borewell Pumps",
                                "Sump Dewatering Drainage Pumps",
                                "Automatic Digital Water Level Controllers"
                            ]
                        },
                        {
                            "name": "Water Treatment & Purification",
                            "variants": [
                                "Automatic Water Softeners with Brine Tank",
                                "Whole-House Central Carbon Water Filters",
                                "Under-Sink Commercial RO UV Water Purifiers",
                                "Packaged Sewage Treatment Plants STP",
                                "Greywater Recycling Filtration Units"
                            ]
                        },
                        {
                            "name": "Water Heaters & Geysers",
                            "variants": [
                                "Evacuated Tube Collector ETC Solar Water Heaters",
                                "Instant Electric Tankless Water Geysers",
                                "Heavy-Duty Electric Storage Geysers",
                                "Air-Source Heat Pump Water Heaters"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 6. ELECTRICAL & LIGHTING
        # ==============================================================================
        {
            "id": 6,
            "name": "Electrical & Lighting",
            "slug": "electrical-lighting",
            "icon": "💡",
            "description": "Architectural luminaires, chandeliers, smart automation, HVAC systems, fire safety, and renewable energy.",
            "supplier_category": "Electrical & Lighting Studios",
            "subcategories": [
                {
                    "name": "Architectural & Feature Lighting",
                    "items": [
                        {
                            "name": "Recessed & Track Systems",
                            "variants": [
                                "Low-Voltage Magnetic Track Lighting Systems",
                                "Deep-Recessed Anti-Glare Architectural Downlights",
                                "Trimless Miniature COB Spotlights",
                                "Surface & Recessed Aluminium LED Profile Extrusions"
                            ]
                        },
                        {
                            "name": "Decorative Chandeliers & Pendants",
                            "variants": [
                                "Hand-Cut Luxury Crystal Chandeliers",
                                "Double-Height Living Room Statement Pendants",
                                "Contemporary Brushed Brass Ring Chandeliers",
                                "Linear Dining Table Pendants",
                                "Minimalist Wall Sconces"
                            ]
                        },
                        {
                            "name": "Linear, Strip & Accent Lighting",
                            "variants": [
                                "High-CRI COB Flexible LED Strip Lights",
                                "Under-Cabinet Diffused Kitchen Lighting",
                                "Wardrobe Recessed Sensor Strip Lights",
                                "False Ceiling Concealed Cove Indirect Lights"
                            ]
                        }
                    ]
                },
                {
                    "name": "Outdoor, Landscape & Facade Lighting",
                    "items": [
                        {
                            "name": "Landscape Luminaires",
                            "variants": [
                                "Heavy-Duty In-Ground Walkover Uplights",
                                "Cast Aluminium Bollard Pathway Lights",
                                "Waterproof IP67 Garden Spike Spotlights",
                                "Staircase Recessed Step Lights",
                                "Solar Powered LED Streetlights"
                            ]
                        }
                    ]
                },
                {
                    "name": "Wiring, Cables & Power Distribution",
                    "items": [
                        {
                            "name": "Conductors & Conduits",
                            "variants": [
                                "FRLS Multi-Strand Pure Copper House Wires",
                                "Armoured Underground Power Cables",
                                "Heavy-Duty Rigid PVC Electrical Conduits",
                                "Fire-Survival High-Temperature Cables"
                            ]
                        },
                        {
                            "name": "Distribution Boards & Switchgear",
                            "variants": [
                                "Distribution Boards with Transparent Acrylic Doors",
                                "Miniature Circuit Breakers MCB",
                                "Residual Current Circuit Breakers RCCB",
                                "Type 2 Surge Protection Devices SPD"
                            ]
                        }
                    ]
                },
                {
                    "name": "Modular Switches & Smart Home Automation",
                    "items": [
                        {
                            "name": "Switches & Sockets",
                            "variants": [
                                "Modular Push-Button Switches",
                                "Toughened Glass Switch Front Plates",
                                "Universal Multi-Pin Power Sockets with USB-C",
                                "Rotary Step Fan Regulators"
                            ]
                        },
                        {
                            "name": "Smart Home Automation",
                            "variants": [
                                "Zigbee Smart Touch Keypads",
                                "Wi-Fi Motorized Curtain Controllers",
                                "Smart Occupancy & Motion Sensors",
                                "Smart Gateway Hubs"
                            ]
                        }
                    ]
                },
                {
                    "name": "HVAC, Climate Control & Ventilation",
                    "items": [
                        {
                            "name": "Air Conditioning Systems",
                            "variants": [
                                "High-Efficiency 5-Star Inverter Split ACs",
                                "4-Way Compact Ceiling Cassette ACs",
                                "VRF VRV Central Multi-Zone AC Systems",
                                "Ducted Chilled Water Concealed Fan Coil Units FCU"
                            ]
                        },
                        {
                            "name": "Ventilation & Fresh-Air Systems",
                            "variants": [
                                "Continuous Low-Noise Bathroom Exhaust Fans",
                                "Fresh-Air Energy Recovery Ventilators ERV",
                                "Galvanized Steel Spiral Ventilation Ducts",
                                "Aerofoil Volume Control Dampers"
                            ]
                        },
                        {
                            "name": "Air Quality & Accessories",
                            "variants": [
                                "Wi-Fi Smart Learning Thermostats",
                                "Central In-Duct Air Purifiers",
                                "Commercial Dehumidifiers",
                                "Decorative BLDC Motor Ceiling Fans",
                                "Weatherproof Architectural Ventilation Louvers"
                            ]
                        }
                    ]
                },
                {
                    "name": "Fire Safety & Building Security Systems",
                    "items": [
                        {
                            "name": "Fire Protection Equipment",
                            "variants": [
                                "ABC Dry Powder Fire Extinguishers",
                                "Carbon Dioxide CO2 Fire Extinguishers",
                                "Fire Hydrant Valves & Canvas Hose Reels",
                                "Automatic Glass Bulb Sprinklers",
                                "Addressable Smoke Detectors & Alarm Panels",
                                "Fire-Rated Wooden Doors 60 Min",
                                "Fire-Stop Silicone Sealants"
                            ]
                        },
                        {
                            "name": "Security & Access Control",
                            "variants": [
                                "CCTV 4K IP Dome & Bullet Surveillance Cameras",
                                "Video Door Phones with Mobile App Connectivity",
                                "Smart Fingerprint Biometric Door Locks",
                                "Wireless Intrusion Alarm Motion Sensors",
                                "Motorized Automatic Sliding Security Gates"
                            ]
                        }
                    ]
                },
                {
                    "name": "Solar PV & Clean Energy Systems",
                    "items": [
                        {
                            "name": "Solar Power Generation",
                            "variants": [
                                "High-Efficiency Monocrystalline Bifacial Solar PV Panels",
                                "Hybrid On-Grid & Off-Grid Solar Inverters",
                                "Lithium Iron Phosphate LiFePO4 Energy Storage Batteries",
                                "Anodized Aluminium Rooftop Solar Mounting Racks"
                            ]
                        },
                        {
                            "name": "Electric Vehicle Charging",
                            "variants": [
                                "Wallbox 7.4 kW Level 2 Electric Vehicle EV Chargers",
                                "22 kW Dual-Gun Commercial EV Charging Stations"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 7. FLOORING & STONE
        # ==============================================================================
        {
            "id": 7,
            "name": "Flooring & Stone",
            "slug": "flooring-stone",
            "icon": "💎",
            "description": "Imported marbles, granites, regional limestones, vitrified slabs, heritage Athangudi tiles, wood, and pavers.",
            "supplier_category": "Stone Quarries, Marble Yards & Tile Showrooms",
            "subcategories": [
                {
                    "name": "Natural Marble & Translucent Stones",
                    "items": [
                        {
                            "name": "Imported Italian Marble",
                            "variants": [
                                "Statuario White Polished Italian Marble",
                                "Botticino Classico Beige Marble",
                                "Carrara White Marble Slabs",
                                "Black Marquina Veined Marble"
                            ]
                        },
                        {
                            "name": "Indian Marble & Translucent Onyx",
                            "variants": [
                                "Makrana Pure White Marble",
                                "Rainforest Green Serpentine Marble",
                                "Honey Onyx Translucent Backlit Slabs",
                                "Engineered Quartz Composite Marble"
                            ]
                        }
                    ]
                },
                {
                    "name": "Granite & Regional Building Stones",
                    "items": [
                        {
                            "name": "Polished & Flamed Granite",
                            "variants": [
                                "Black Galaxy Granite with Gold Flecks",
                                "Kashmir White Granite",
                                "Steel Grey Granite",
                                "Flamed Black Granite Anti-Skid Steps",
                                "Leather-Finish Granite Kitchen Slabs"
                            ]
                        },
                        {
                            "name": "Heritage Limestones & Sandstone",
                            "variants": [
                                "Kadappa Natural Black Limestone Slabs",
                                "Blue Kota Stone Mirror-Polished",
                                "Jaisalmer Yellow Golden Limestone",
                                "Teakwood Veined Sandstone Paving Slabs"
                            ]
                        }
                    ]
                },
                {
                    "name": "Vitrified & Ceramic Tile Slabs",
                    "items": [
                        {
                            "name": "Large Format Porcelain Slabs",
                            "variants": [
                                "Continuous Book-Matched Porcelain Slabs 8x4 ft",
                                "Glazed Vitrified Tiles PGVT High Gloss",
                                "Full-Body Matte Porcelain Slabs"
                            ]
                        },
                        {
                            "name": "Specialized Flooring Tiles",
                            "variants": [
                                "Anti-Skid Matte R10 Bathroom Floor Tiles",
                                "Wood-Plank Porcelain Vitrified Tiles",
                                "Moroccan Mosaic Glazed Tiles"
                            ]
                        }
                    ]
                },
                {
                    "name": "Heritage & Handcrafted Tiles",
                    "items": [
                        {
                            "name": "Artisanal Cement & Terrazzo",
                            "variants": [
                                "Athangudi Traditional Handcrafted Chettinad Cement Tiles",
                                "Geometric Moroccan Encaustic Cement Tiles",
                                "Custom Cast Terrazzo Floor Tiles with Brass Dividers"
                            ]
                        }
                    ]
                },
                {
                    "name": "Wood, Laminate & Resilient Flooring",
                    "items": [
                        {
                            "name": "Hardwood & Engineered Wood",
                            "variants": [
                                "Solid Teak Wood Tongue-and-Groove Flooring",
                                "Multi-Layer Engineered Oak Wood Flooring",
                                "Chevron Pattern Hardwood Parquet"
                            ]
                        },
                        {
                            "name": "Resilient Waterproof Flooring",
                            "variants": [
                                "SPC Stone Plastic Composite Luxury Vinyl Planks",
                                "Heavy-Duty Commercial Heterogeneous Vinyl Rolls"
                            ]
                        }
                    ]
                },
                {
                    "name": "Outdoor Pavers & Landscape Stone",
                    "items": [
                        {
                            "name": "Driveway & Pathway Pavers",
                            "variants": [
                                "Heavy-Duty Interlocking Concrete Pavers 80mm",
                                "Permeable Grass Pavers",
                                "Tumbled Volcanic Basalt Cobblestones",
                                "Dressed Granite Stepping Stones"
                            ]
                        },
                        {
                            "name": "Decorative Landscape Stones",
                            "variants": [
                                "Snow White Polished River Pebbles",
                                "Natural River Gravel",
                                "Black Basalt River Stones"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 8. DOORS, WINDOWS & GLASS
        # ==============================================================================
        {
            "id": 8,
            "name": "Doors, Windows & Glass",
            "slug": "doors-windows-glass",
            "icon": "🚪",
            "description": "Solid timber doors, UPVC/Aluminium fenestration, structural glazing, architectural hardware, and specialized shutters.",
            "supplier_category": "Doors, Windows & Architectural Glass Fabricators",
            "subcategories": [
                {
                    "name": "Doors & Entryway Systems",
                    "items": [
                        {
                            "name": "Solid Timber & Veneer Doors",
                            "variants": [
                                "Solid Burma Teak Main Entrance Doors",
                                "Teak Veneer Solid-Core Flush Doors",
                                "Traditional Carved Kerala Double Entrance Doors"
                            ]
                        },
                        {
                            "name": "Waterproof & Security Doors",
                            "variants": [
                                "WPC Water-Proof Foam Core Bathroom Doors",
                                "Galvanized Steel Security Entrance Doors",
                                "Fire-Rated Steel Doors 120 Min BS Compliance"
                            ]
                        },
                        {
                            "name": "Modern Architectural Door Systems",
                            "variants": [
                                "Extra-Large Pivot Entrance Doors with Offset Hinges",
                                "Concealed Sliding Pocket Doors",
                                "Exterior Folding Bi-fold Patio Doors",
                                "Acoustic Soundproof Studio Doors"
                            ]
                        }
                    ]
                },
                {
                    "name": "Windows & Fenestration Systems",
                    "items": [
                        {
                            "name": "UPVC Window Systems",
                            "variants": [
                                "Multi-Chamber UPVC 3-Track Sliding Windows with Mosquito Mesh",
                                "UPVC Casement Windows with Multi-Point Locking",
                                "Tilt-and-Turn Energy-Saving Windows"
                            ]
                        },
                        {
                            "name": "Aluminium Window Systems",
                            "variants": [
                                "Thermal-Break Minimalist Slim-Profile Sliding Windows",
                                "Fixed Floor-to-Ceiling Panoramic Glass Picture Windows",
                                "Aluminium Top-Hung Awning Windows"
                            ]
                        }
                    ]
                },
                {
                    "name": "Architectural Glass & Glazing",
                    "items": [
                        {
                            "name": "Safety & Performance Glass",
                            "variants": [
                                "Toughened Clear Tempered Safety Glass",
                                "Acoustic PVB Laminated Double Glazed Units DGU",
                                "Low-E Solar Heat Reflective Glass"
                            ]
                        },
                        {
                            "name": "Decorative & Patterned Glass",
                            "variants": [
                                "Fluted Reeded Vertical Textured Glass",
                                "Frosted Acid-Etched Privacy Glass",
                                "Architectural Tinted Grey Bronze Glass Panels"
                            ]
                        }
                    ]
                },
                {
                    "name": "Hardware, Locks & Architectural Fittings",
                    "items": [
                        {
                            "name": "Door Locks & Latches",
                            "variants": [
                                "Heavy-Duty Mortise Door Locks with Solid Brass Handles",
                                "Digital Smart Biometric Fingerprint Locks",
                                "Night Latches with Brass Deadbolt"
                            ]
                        },
                        {
                            "name": "Hinges & Precision Runners",
                            "variants": [
                                "Stainless Steel 304 Concealed Hinges with Soft Close",
                                "Telescopic Soft-Close Undermount Drawer Runners",
                                "Heavy-Duty Overhead Sliding Door Tracks"
                            ]
                        },
                        {
                            "name": "Glass Hardware & Accessories",
                            "variants": [
                                "Heavy-Duty Hydraulic Floor Springs 120kg",
                                "Stainless Steel Patch Fittings for Glass Doors",
                                "4-Arm Stainless Steel Spider Glazing Brackets",
                                "600mm Architectural Stainless Steel Pull Handles"
                            ]
                        }
                    ]
                },
                {
                    "name": "Specialty Shutters & Movable Partitions",
                    "items": [
                        {
                            "name": "Industrial & Garage Shutters",
                            "variants": [
                                "Motorized Polyurethane Insulated Rolling Shutters",
                                "Overhead Motorized Sectional Garage Doors",
                                "Fire-Rated Rolling Shutters"
                            ]
                        },
                        {
                            "name": "Movable Walls & Inspection Access",
                            "variants": [
                                "Ceiling & Floor Flush Access Inspection Hatches",
                                "Movable Acoustic Operable Glass Partition Walls"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 9. FURNITURE
        # ==============================================================================
        {
            "id": 9,
            "name": "Furniture",
            "slug": "furniture",
            "icon": "🪑",
            "description": "Bedroom, dining, living, modular kitchen cabinetry, ergonomic office, and all-weather outdoor furniture.",
            "supplier_category": "Furniture Showrooms & Custom Joinery Studios",
            "subcategories": [
                {
                    "name": "Bedroom Furniture",
                    "items": [
                        {
                            "name": "Beds & Sleep Systems",
                            "variants": [
                                "Platform Minimalist Hardwood Beds",
                                "Upholstered Fabric Headboard King Beds",
                                "Hydraulic Storage Under-Bed Mechanism",
                                "Solid Wood Bunk Beds with Guardrails",
                                "Space-Saving Murphy Wall Beds"
                            ]
                        },
                        {
                            "name": "Wardrobes & Closet Storage",
                            "variants": [
                                "Modular Hinged Wardrobes with Soft-Close Shutters",
                                "Floor-to-Ceiling Sliding Wardrobes with Mirror",
                                "Walk-in Dressing Closet Systems with Accessory Island"
                            ]
                        },
                        {
                            "name": "Bedroom Storage & Accents",
                            "variants": [
                                "Dual-Drawer Nightstands & Bedside Tables",
                                "Dressing Vanity Tables with Backlit LED Mirror",
                                "Six-Drawer Wooden Chest of Drawers",
                                "Upholstered End-of-Bed Benches"
                            ]
                        }
                    ]
                },
                {
                    "name": "Dining Room Furniture",
                    "items": [
                        {
                            "name": "Dining Tables",
                            "variants": [
                                "Solid Teak Wood 8-Seater Dining Tables",
                                "Italian Marble Top Dining Tables with Brass Base",
                                "Extendable Solid Oak Dining Tables"
                            ]
                        },
                        {
                            "name": "Dining Chairs & Benches",
                            "variants": [
                                "Ergonomic Upholstered Dining Chairs",
                                "Solid Wood Dining Benches",
                                "High-Back Counter Bar Stools",
                                "Swivel Breakfast Stools"
                            ]
                        },
                        {
                            "name": "Dining Cabinets & Storage",
                            "variants": [
                                "Glass-Door Crockery Display Cabinets",
                                "Low-Profile Buffet Sideboards",
                                "Built-in Wine & Bar Cabinets"
                            ]
                        }
                    ]
                },
                {
                    "name": "Living Room Furniture",
                    "items": [
                        {
                            "name": "Sofas & Seating",
                            "variants": [
                                "L-Shaped Modular Fabric Sectional Sofas",
                                "Motorized Leather Recliner Armchairs",
                                "Tufted Chesterfield Sofas",
                                "Contemporary Fabric Ottomans & Poufs"
                            ]
                        },
                        {
                            "name": "Living Room Tables & Media Units",
                            "variants": [
                                "Round Marble-Top Coffee Tables",
                                "Solid Wood Nesting Side Tables",
                                "Minimalist Console Tables for Entryway",
                                "Floating TV Entertainment Media Units"
                            ]
                        }
                    ]
                },
                {
                    "name": "Kitchen Furniture & Modular Cabinetry",
                    "items": [
                        {
                            "name": "Kitchen Cabinets & Units",
                            "variants": [
                                "Modular Base & Wall Cabinets with Tandem Drawers",
                                "Anti-Scratch Acrylic Finished Kitchen Shutters",
                                "Tall Kitchen Pantry Larder Pull-Out Units",
                                "Movable Wooden Island Utility Trolleys"
                            ]
                        }
                    ]
                },
                {
                    "name": "Office & Commercial Furniture",
                    "items": [
                        {
                            "name": "Workstations & Desks",
                            "variants": [
                                "Executive Solid Wood Desks with Cable Management",
                                "Dual-Motor Height-Adjustable Standing Desks",
                                "Multi-Pod Collaborative Workstation Cubicles"
                            ]
                        },
                        {
                            "name": "Office Seating & Storage",
                            "variants": [
                                "Ergonomic High-Back Mesh Chairs with Lumbar Support",
                                "Conference & Boardroom Boat-Shaped Tables",
                                "Commercial Reception Desks with LED Kick-Plate",
                                "Steel Heavy-Duty Vertical Filing Cabinets"
                            ]
                        }
                    ]
                },
                {
                    "name": "Outdoor & Patio Furniture",
                    "items": [
                        {
                            "name": "All-Weather Garden Furniture",
                            "variants": [
                                "Synthetic All-Weather Wicker Sofa Sets",
                                "Solid Teak Wood Garden Park Benches",
                                "Adjustable Aluminium Sun Loungers",
                                "Teak Outdoor Dining Sets with Umbrella Hole",
                                "Poolside Polypropylene Recliners"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 10. DECOR & FURNISHINGS
        # ==============================================================================
        {
            "id": 10,
            "name": "Decor & Furnishings",
            "slug": "decor-furnishings",
            "icon": "🖼️",
            "description": "Curtains, blinds, rugs, soft furnishings, fine wall art, sculptural mirrors, and curated accents.",
            "supplier_category": "Furnishing Galleries & Home Decor Studios",
            "subcategories": [
                {
                    "name": "Window Coverings & Blinds",
                    "items": [
                        {
                            "name": "Curtains & Drapes",
                            "variants": [
                                "Translucent Linen Sheer Drapery Curtains",
                                "100% Light-Blocking Velvet Blackout Curtains",
                                "Floor-to-Ceiling Wave Pleat Curtains"
                            ]
                        },
                        {
                            "name": "Window Blinds",
                            "variants": [
                                "Motorized Smart Roller Blinds",
                                "Solid Basswood Venetian Blinds with Tape",
                                "Folded Roman Fabric Blinds",
                                "Perforated Vertical Office Blinds"
                            ]
                        }
                    ]
                },
                {
                    "name": "Rugs, Carpets & Floor Textiles",
                    "items": [
                        {
                            "name": "Handmade & Area Rugs",
                            "variants": [
                                "Hand-Tufted 100% Pure Woolen Area Rugs",
                                "Modern Geometric Low-Pile Area Rugs",
                                "Natural Hand-Braided Jute & Hemp Dhurries"
                            ]
                        },
                        {
                            "name": "Commercial Carpeting",
                            "variants": [
                                "Heavy-Duty Nylon Modular Carpet Tiles",
                                "Wall-to-Wall Cut-Pile Hotel Carpets"
                            ]
                        }
                    ]
                },
                {
                    "name": "Soft Furnishings & Bedding",
                    "items": [
                        {
                            "name": "Cushions & Throws",
                            "variants": [
                                "Embroidered Velvet Decorative Cushion Covers",
                                "Knitted Cotton Textured Throw Blankets"
                            ]
                        },
                        {
                            "name": "Bedding & Linens",
                            "variants": [
                                "400 Thread Count Pure Cotton Bedsheet Sets",
                                "Lightweight Microfiber Duvet Comforters",
                                "Breathable Quilted Mattress Protectors",
                                "Ergonomic Memory Foam Contour Pillows"
                            ]
                        }
                    ]
                },
                {
                    "name": "Wall Art, Mirrors & Sculptures",
                    "items": [
                        {
                            "name": "Wall Art & Prints",
                            "variants": [
                                "Hand-Painted Canvas Oil Paintings",
                                "Framed Architectural Black-and-White Photography Prints",
                                "Hand-Hammered Brass Metal Wall Sculptures"
                            ]
                        },
                        {
                            "name": "Mirrors",
                            "variants": [
                                "Full-Length Arch Metal-Framed Floor Mirrors",
                                "Round LED Backlit Anti-Fog Vanity Mirrors",
                                "Decorative Sunburst Beveled Wall Mirrors"
                            ]
                        }
                    ]
                },
                {
                    "name": "Decorative Accessories & Planters",
                    "items": [
                        {
                            "name": "Tabletop & Shelf Accents",
                            "variants": [
                                "Ceramic Matte Texture Vases",
                                "Sculptural Solid Brass Candle Holders",
                                "Polished Marble Decorative Trays",
                                "Minimalist Metal Wall Clocks"
                            ]
                        },
                        {
                            "name": "Indoor Planters & Botanical Decor",
                            "variants": [
                                "Terracotta Handcrafted Floor Planters",
                                "Brushed Brass Indoor Plant Stands",
                                "Preserved Fiddle Leaf Fig Indoor Plants",
                                "Bonsai & Artificial Orchid Arrangements"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 11. CEILING, WALLS & FINISHES
        # ==============================================================================
        {
            "id": 11,
            "name": "Ceiling, Walls & Finishes",
            "slug": "ceiling-walls-finishes",
            "icon": "🎨",
            "description": "False ceilings, decorative paneling, luxury paints, textures, acoustic treatments, and waterproofing.",
            "supplier_category": "Ceiling, Wall Paneling & Paint Distributors",
            "subcategories": [
                {
                    "name": "False Ceiling Systems",
                    "items": [
                        {
                            "name": "Gypsum & Plaster Ceilings",
                            "variants": [
                                "Tapered-Edge Gypsum Board False Ceiling",
                                "Plaster of Paris POP Decorative Moldings & Cornices",
                                "Seamless Acoustic Perforated Gypsum Board"
                            ]
                        },
                        {
                            "name": "Modular & Baffle Ceilings",
                            "variants": [
                                "T-Grid Modular Mineral Fiber Acoustic Ceiling Tiles",
                                "Extruded Aluminium Wood-Finish Ceiling Baffles",
                                "Suspended PVC Ceiling Panels"
                            ]
                        }
                    ]
                },
                {
                    "name": "Wall Paneling & Cladding",
                    "items": [
                        {
                            "name": "Decorative Louvers & Veneer",
                            "variants": [
                                "Charcoal & WPC Interior Fluted Wall Louvers",
                                "Natural Reconstituted Wood Veneer Sheets",
                                "3D Textured Gypsum Wall Tiles"
                            ]
                        },
                        {
                            "name": "Acoustic Wall Systems",
                            "variants": [
                                "Fabric-Wrapped High-Density Acoustic Wall Panels",
                                "Slotted Acoustic Wooden Wall Cladding",
                                "Polyester Fiber Sound-Absorbing Baffles"
                            ]
                        }
                    ]
                },
                {
                    "name": "Interior & Exterior Paints & Textures",
                    "items": [
                        {
                            "name": "Interior Paints",
                            "variants": [
                                "Low-VOC Luxury Silk Interior Emulsion Paint",
                                "Washable Anti-Bacterial Acrylic Paint",
                                "Super-Matte Interior Ceiling Paint"
                            ]
                        },
                        {
                            "name": "Exterior Paints & Stucco",
                            "variants": [
                                "Silicon Weatherproof Exterior Acrylic Emulsion",
                                "Traditional Slaked Lime Plaster & Stucco",
                                "Italian Venetian Marble Plaster",
                                "Metallic Textured Designer Wall Finish"
                            ]
                        }
                    ]
                },
                {
                    "name": "Waterproofing & Protective Chemicals",
                    "items": [
                        {
                            "name": "Surface Waterproofing",
                            "variants": [
                                "Elastomeric Polymer-Modified Roof Waterproofing Membrane",
                                "Heavy-Duty SBS Bituminous Torch-on Membrane",
                                "Deep Penetrating Crystalline Capillary Sealers"
                            ]
                        },
                        {
                            "name": "Construction Chemicals & Additives",
                            "variants": [
                                "Two-Component Epoxy Tile Grout",
                                "SBR Latex Bonding Agent for Concrete Repair",
                                "Organosilicon Water-Repellent Impregnation",
                                "Anti-Termite Chlorpyrifos Soil Pre-Treatment"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 12. LANDSCAPE & OUTDOOR
        # ==============================================================================
        {
            "id": 12,
            "name": "Landscape & Outdoor",
            "slug": "landscape-outdoor",
            "icon": "🌿",
            "description": "Landscape architecture, decorative stones, decking, pergolas, pools, waterfalls, turf, and irrigation.",
            "supplier_category": "Landscape Architects, Nurseries & Outdoor Living Suppliers",
            "subcategories": [
                {
                    "name": "Landscape Typologies & Garden Design",
                    "items": [
                        {
                            "name": "Garden Styles",
                            "variants": [
                                "Tropical Courtyard Garden with Ferns",
                                "Zen Japanese Minimalist Rock Garden",
                                "Rooftop Terrace Sky Garden",
                                "Exterior Vertical Living Green Wall"
                            ]
                        }
                    ]
                },
                {
                    "name": "Natural & Decorative Landscape Stones",
                    "items": [
                        {
                            "name": "Pebbles & Aggregates",
                            "variants": [
                                "Snow White Polished Natural River Pebbles",
                                "Natural Grey River Stones",
                                "Black Polished Basalt Decorative Pebbles",
                                "Decomposed Granite Gravel"
                            ]
                        },
                        {
                            "name": "Boulders & Stepping Stones",
                            "variants": [
                                "Natural Granite Landscape Boulders",
                                "Dressed Sandstone Stepping Stones",
                                "Volcanic Basalt Cobblestone Pavers"
                            ]
                        }
                    ]
                },
                {
                    "name": "Outdoor Decking, Pergolas & Structures",
                    "items": [
                        {
                            "name": "Decking Systems",
                            "variants": [
                                "Grooved Anti-Slip WPC Composite Outdoor Decking",
                                "Weatherproof Natural Teak Decking Planks on Joists"
                            ]
                        },
                        {
                            "name": "Outdoor Shelters & Structures",
                            "variants": [
                                "Powder-Coated Aluminium Motorized Louver Pergolas",
                                "Solid Teak Garden Gazebos & Cabanas",
                                "Metal Garden Trellises & Arches"
                            ]
                        }
                    ]
                },
                {
                    "name": "Water Features & Swimming Pools",
                    "items": [
                        {
                            "name": "Garden Water Features",
                            "variants": [
                                "Natural Stone Cascading Garden Waterfalls",
                                "Slate Stone Water Wall Fountains",
                                "Concrete Koi Reflection Ponds"
                            ]
                        },
                        {
                            "name": "Swimming Pool Systems",
                            "variants": [
                                "Glass Mosaic Swimming Pool Tiles",
                                "Variable-Speed Pool Filtration Circulation Pumps",
                                "Stainless Steel Solar Pool Showers"
                            ]
                        }
                    ]
                },
                {
                    "name": "Turf, Soil & Irrigation Systems",
                    "items": [
                        {
                            "name": "Lawns & Groundcover",
                            "variants": [
                                "Natural Bermuda & Mexican Grass Sod Rolls",
                                "40mm Monofilament UV-Stabilized Artificial Turf",
                                "Rich Organic Potting Mix Soil with Compost"
                            ]
                        },
                        {
                            "name": "Automated Irrigation",
                            "variants": [
                                "Pressure-Compensating Drip Irrigation Pipes",
                                "Pop-Up Lawn Gear-Driven Sprinklers",
                                "Multi-Station Digital Automatic Irrigation Controllers"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 13. MANUFACTURERS & SUPPLIERS
        # ==============================================================================
        {
            "id": 13,
            "name": "Manufacturers & Suppliers",
            "slug": "manufacturers-suppliers",
            "icon": "🏭",
            "description": "Factories, stockists, showrooms, architects, builders, contractors, and specialized trade fabricators.",
            "supplier_category": "Direct Factories, Trade Yards & Professional Practices",
            "subcategories": [
                {
                    "name": "Material Manufacturers & Factories",
                    "items": [
                        {
                            "name": "Heavy Material Factories",
                            "variants": [
                                "Portland Cement Manufacturing Plants",
                                "Secondary Steel Rolling Mills & Rebar Plants",
                                "Large-Format Vitrified Tile Factories"
                            ]
                        },
                        {
                            "name": "Processing & Finishing Plants",
                            "variants": [
                                "Automated Architectural Glass Processing & Toughening Units",
                                "Exterior Architectural Paint Manufacturing Plants",
                                "Aluminium Extrusion & Powder-Coating Plants"
                            ]
                        }
                    ]
                },
                {
                    "name": "Distributors, Stockists & Wholesalers",
                    "items": [
                        {
                            "name": "Bulk Trade Stockyards",
                            "variants": [
                                "Authorized Regional TMT Rebar Stockyards",
                                "Wholesale Imported Timber & Plywood Merchants",
                                "Primary Marble & Granite Stone Stockists",
                                "Plumbing Pipes & Industrial Sanitaryware Distributors"
                            ]
                        }
                    ]
                },
                {
                    "name": "Showrooms & Design Studios",
                    "items": [
                        {
                            "name": "Experience Centers",
                            "variants": [
                                "Curated Architectural Tile & Marble Surface Studios",
                                "Luxury European Modular Kitchen Studios",
                                "High-End Architectural Lighting Experience Centers",
                                "Complete Architectural Hardware Display Centers"
                            ]
                        }
                    ]
                },
                {
                    "name": "Architects & Design Studios",
                    "items": [
                        {
                            "name": "Architecture Firms",
                            "variants": [
                                "Contemporary Residential Villa Architects",
                                "Sustainable Biophilic Architects",
                                "Heritage Conservation Architectural Firms",
                                "Commercial Architectural Studios"
                            ]
                        },
                        {
                            "name": "Interior Design Studios",
                            "variants": [
                                "Luxury Residential Interior Design Studios",
                                "Turnkey Commercial Office Interior Designers"
                            ]
                        }
                    ]
                },
                {
                    "name": "Builders & General Contractors",
                    "items": [
                        {
                            "name": "Residential Builders",
                            "variants": [
                                "Turnkey Luxury Villa Construction Builders",
                                "Residential House Contractors",
                                "Design-and-Build Construction Companies"
                            ]
                        },
                        {
                            "name": "Engineering Contractors",
                            "variants": [
                                "Structural RCC Framing Contractors",
                                "Commercial Civil Infrastructure Contractors",
                                "Mechanical Electrical Plumbing MEP Contractors"
                            ]
                        }
                    ]
                },
                {
                    "name": "Specialized Fabricators & Skilled Trades",
                    "items": [
                        {
                            "name": "Fabricators",
                            "variants": [
                                "Custom Architectural Staircase & Railing Fabricators",
                                "Structural Steel Shed & Truss Fabricators",
                                "Architectural Glass & Aluminium Window Fabricators"
                            ]
                        },
                        {
                            "name": "Skilled Trade Artisans",
                            "variants": [
                                "Master Carpenters & Fine Cabinet Makers",
                                "Italian Marble Polishers & Stone Cutters",
                                "Certified Applicators for Waterproofing"
                            ]
                        }
                    ]
                }
            ]
        },

        # ==============================================================================
        # 14. BRANDS
        # ==============================================================================
        {
            "id": 14,
            "name": "Brands",
            "slug": "brands",
            "icon": "🏷️",
            "description": "Verified Indian, European, and global manufacturing brands across all architectural building categories.",
            "supplier_category": "Official Brand Showrooms & Authorized Distributors",
            "subcategories": [
                {
                    "name": "Cement & Structural Steel Brands",
                    "items": [
                        {
                            "name": "Cement Brands",
                            "variants": [
                                "UltraTech Cement",
                                "Dalmia Cement",
                                "Ramco Cement",
                                "ACC Cement",
                                "Ambuja Cement"
                            ]
                        },
                        {
                            "name": "Steel Brands",
                            "variants": [
                                "Tata Tiscon",
                                "JSW Neosteel",
                                "Jindal Steel & Power",
                                "Vizag Steel RINL",
                                "Agni Steels",
                                "Tirumala TMT"
                            ]
                        }
                    ]
                },
                {
                    "name": "Sanitaryware, Bath & Plumbing Brands",
                    "items": [
                        {
                            "name": "Bath & Sanitaryware Brands",
                            "variants": [
                                "Jaquar",
                                "Hindware",
                                "Cera",
                                "Kohler",
                                "Grohe",
                                "TOTO"
                            ]
                        },
                        {
                            "name": "Pipes & Water Systems Brands",
                            "variants": [
                                "Astral Pipes",
                                "Supreme Industries",
                                "Ashirvad Pipes",
                                "Finolex Pipes",
                                "Sintex Water Tanks"
                            ]
                        }
                    ]
                },
                {
                    "name": "Tiles, Marble & Surface Brands",
                    "items": [
                        {
                            "name": "Ceramic & Vitrified Tile Brands",
                            "variants": [
                                "Kajaria Ceramics",
                                "Somany Ceramics",
                                "Nitco Tiles",
                                "RAK Ceramics",
                                "AGL Asian Granito",
                                "Simpolo Ceramics"
                            ]
                        }
                    ]
                },
                {
                    "name": "Paints, Textures & Waterproofing Brands",
                    "items": [
                        {
                            "name": "Coatings & Chemicals Brands",
                            "variants": [
                                "Asian Paints",
                                "Berger Paints",
                                "Kansai Nerolac",
                                "Dr. Fixit Pidilite",
                                "Fosroc Construction Chemicals",
                                "Sika"
                            ]
                        }
                    ]
                },
                {
                    "name": "Electrical, Lighting & Automation Brands",
                    "items": [
                        {
                            "name": "Electrical & Smart Brands",
                            "variants": [
                                "Legrand",
                                "Schneider Electric",
                                "Havells",
                                "Philips Lighting",
                                "Wipro Lighting",
                                "Anchor by Panasonic",
                                "L&T Electrical"
                            ]
                        }
                    ]
                },
                {
                    "name": "Architectural Hardware, Wood & Glass Brands",
                    "items": [
                        {
                            "name": "Hardware, Wood & Glass Brands",
                            "variants": [
                                "Häfele Hardware",
                                "Hettich Hardware",
                                "Godrej Locks",
                                "Dormakaba",
                                "Saint-Gobain Glass",
                                "Greenply Industries",
                                "CenturyPly"
                            ]
                        }
                    ]
                }
            ]
        }
    ]

    # Flatten keywords for every subcategory
    for cat in categories:
        for sub in cat["subcategories"]:
            kws = []
            for item in sub["items"]:
                if item["name"] not in kws:
                    kws.append(item["name"])
                for v in item.get("variants", []):
                    if v not in kws:
                        kws.append(v)
            sub["keywords"] = kws

    return categories

if __name__ == "__main__":
    cats = build_taxonomy()
    print(f"Built {len(cats)} categories.")
    total_subs = sum(len(c["subcategories"]) for c in cats)
    total_items = sum(sum(len(s["items"]) for s in c["subcategories"]) for c in cats)
    total_vars = sum(sum(sum(len(it["variants"]) for it in s["items"]) for s in c["subcategories"]) for c in cats)
    print(f"Total Subcategories: {total_subs}")
    print(f"Total Items: {total_items}")
    print(f"Total Variants: {total_vars}")

