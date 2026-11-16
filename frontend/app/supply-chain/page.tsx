"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import {
  GitFork, ArrowRight, ShieldCheck, CheckCircle2, AlertTriangle,
  Factory, Mountain, Truck, Building2, HardHat, FileText,
  Compass, ExternalLink, Info, Check, RefreshCw, Leaf
} from 'lucide-react';

interface SupplyChainStage {
  step: number;
  name: string;
  role: string;
  description: string;
  typicalEntities: string;
  qualityCheck: string;
}

interface MaterialSupplyChain {
  id: string;
  title: string;
  category: string;
  primaryOrigin: string;
  environmentalNotes: string;
  standardCompliance: string;
  stages: SupplyChainStage[];
}

const MATERIAL_CHAINS: MaterialSupplyChain[] = [
  {
    id: "stone",
    title: "Natural Stone & Laterite Masonry",
    category: "Masonry & Structural Stone",
    primaryOrigin: "Malappuram & Kannur (Laterite), Kota (Rajasthan Limestone), Salem (Granite)",
    environmentalNotes: "Low embodied carbon when locally sourced; minimal chemical processing required. Extraction requires regulated quarry permits.",
    standardCompliance: "IS 1121 (Compressive Strength), IS 1124 (Water Absorption < 12%)",
    stages: [
      {
        step: 1,
        name: "Raw Source / Quarry",
        role: "Quarry Producer",
        description: "Extraction of raw stone blocks using wire-saws or mechanical cutters from licensed geological formations.",
        typicalEntities: "Malappuram Laterite Quarries, Makrana Marble Pits, Kota Stone Beds",
        qualityCheck: "Visual density inspection, absence of clay pockets or cleavage fissures."
      },
      {
        step: 2,
        name: "Primary Processing",
        role: "Stone Dressing & Cutting Mill",
        description: "Block gang-saw slabbing, calibration to standard thickness (20mm, 30mm), surface honing or flamed bush-hammering.",
        typicalEntities: "Regional stone processing yards, dressing units",
        qualityCheck: "Dimensional tolerance check (±1mm), edge straightness, uniform calibration."
      },
      {
        step: 3,
        name: "Manufacturer / Finisher",
        role: "Finishing Facility",
        description: "Surface texturing, anti-stain impregnating sealers, chamfering, and custom architectural cut-to-size dressing.",
        typicalEntities: "Architectural stone specialists",
        qualityCheck: "Water absorption testing, surface slip resistance testing."
      },
      {
        step: 4,
        name: "Regional Distributor",
        role: "State / Regional Depot",
        description: "Consolidated freight transport from quarry states (e.g. Rajasthan to Kerala / Tamil Nadu) to central warehouse hubs.",
        typicalEntities: "Wholesale interstate stone logistics hubs",
        qualityCheck: "Crate packing integrity, transit shock inspection."
      },
      {
        step: 5,
        name: "Dealer / Stockist Yard",
        role: "Local Stockist Yard",
        description: "Display showroom and physical inventory yard where architects and contractors inspect current lot colors and textures.",
        typicalEntities: "City stone yards (Kochi, Kozhikode, Thiruvananthapuram, Chennai)",
        qualityCheck: "Lot shade consistency, physical count and batch matching."
      },
      {
        step: 6,
        name: "Contractor Procurement",
        role: "Masonry Contractor / Builder",
        description: "Purchase order against architectural bill of quantities, jobsite delivery scheduling, and crane unloading.",
        typicalEntities: "Civil engineering contractor, stone setting specialist",
        qualityCheck: "On-site mock-up dry lay for architect approval before installation."
      },
      {
        step: 7,
        name: "Jobsite Installation",
        role: "Construction Site",
        description: "Bedding in polymer-modified stone adhesive or lime-cement mortar with stainless steel mechanical ties where required.",
        typicalEntities: "Active project site",
        qualityCheck: "Post-installation plumb alignment, expansion joints, protective breathable sealer."
      }
    ]
  },
  {
    id: "steel",
    title: "Reinforcement Steel (TMT Rebars)",
    category: "Structural Steel",
    primaryOrigin: "Jamshedpur, Bellary (Karnataka), Salem (Tamil Nadu), Angul (Odisha)",
    environmentalNotes: "High initial embodied carbon; fully recyclable via Electric Arc Furnace (EAF) processing using recycled scrap content.",
    standardCompliance: "IS 1786:2008 (High Strength Deformed Steel Bars - Fe 500D / Fe 550D)",
    stages: [
      {
        step: 1,
        name: "Raw Source / Feedstock",
        role: "Mining / Scrap Recycler",
        description: "Iron ore extraction or certified heavy melting steel scrap recycling.",
        typicalEntities: "Mining leases or industrial metal recyclers",
        qualityCheck: "Chemical purity and carbon/sulfur/phosphorus limits."
      },
      {
        step: 2,
        name: "Primary Smelting",
        role: "Integrated Steel Plant (Blast Furnace / DRI)",
        description: "Smelting iron ore into liquid pig iron and refining in Basic Oxygen Furnace to exact structural metallurgy.",
        typicalEntities: "Tata Steel, JSW Steel, SAIL",
        qualityCheck: "Spectrometer metallurgical test report (MTC)."
      },
      {
        step: 3,
        name: "Hot Rolling & Thermo-Mechanical Treatment",
        role: "TMT Rolling Mill",
        description: "Hot billet rolling followed by rapid water-quenching (Tempcore process) producing tough tempered martensite rim and ductile ferrite-pearlite core.",
        typicalEntities: "Primary Steel Producers & Licensed TMT Mills",
        qualityCheck: "Yield strength, ultimate tensile strength, elongation > 16% (D grade)."
      },
      {
        step: 4,
        name: "Distributor & Logistics",
        role: "National / State Distributor",
        description: "Rail rake and multi-axle trailer haulage of standardized 12-meter bundles to regional stockyards.",
        typicalEntities: "Authorized Primary Steel Distributors",
        qualityCheck: "Bundle tagging, mill test certificate matching heat number."
      },
      {
        step: 5,
        name: "Authorized Stockist",
        role: "District / City Stockist",
        description: "Retail stockist with weighbridge facility, stock tracking by grade (Fe 500D) and diameter (8mm to 32mm).",
        typicalEntities: "City steel stockyards across Kerala and South India",
        qualityCheck: "Physical diameter, rib pattern, absence of corrosive pitting."
      },
      {
        step: 6,
        name: "Bar Bending & Procurement",
        role: "Cut & Bend Yard / Contractor",
        description: "Processing structural bar-bending schedule (BBS), cutting, and automated stirrup bending.",
        typicalEntities: "Central cut & bend facility or jobsite bar benders",
        qualityCheck: "Bend test and re-bend test compliance without micro-cracks."
      },
      {
        step: 7,
        name: "Rebar Cage Placement",
        role: "Construction Site",
        description: "Tying column, beam, and slab reinforcement with 18-gauge binding wire and non-conductive cover blocks before concrete pour.",
        typicalEntities: "Project foundation / RCC framework",
        qualityCheck: "Pre-pour structural engineer inspection: clear cover, lap length, stirrup spacing."
      }
    ]
  },
  {
    id: "clay",
    title: "Terracotta Clay Roofing Tiles & Bricks",
    category: "Envelope & Masonry",
    primaryOrigin: "Feroke (Kozhikode, Kerala), Thrissur, Mangalore (Karnataka)",
    environmentalNotes: "All-natural alluvial clay; high thermal mass; 100+ year durability; reusable upon demolition. Kiln fuel efficiency governs carbon intensity.",
    standardCompliance: "IS 654 (Clay Roofing Tiles), IS 1077 (Common Burnt Clay Building Bricks)",
    stages: [
      {
        step: 1,
        name: "Alluvial Clay Extraction",
        role: "Clay Deposit Excavation",
        description: "Harvesting naturally weathered silt and alluvial clay from riverbed and designated agrarian valley basins.",
        typicalEntities: "Chaliyar River Valley, Feroke Clay Basins",
        qualityCheck: "Plasticity index, absence of gravel and excessive organic peat."
      },
      {
        step: 2,
        name: "Pug Mill Aging & De-Airing",
        role: "Clay Processing Plant",
        description: "Mechanical pugging, crushing, water blending, and vacuum de-airing to achieve homogenous clay paste.",
        typicalEntities: "Feroke & Thrissur Tile Works",
        qualityCheck: "Moisture consistency, vacuum de-airing efficiency."
      },
      {
        step: 3,
        name: "Hydraulic Pressing & Firing",
        role: "Tile / Brick Manufacturer",
        description: "Extrusion and high-tonnage hydraulic pressing of interlocking tile profile, slow chamber drying, and Hoffman kiln firing at 950°C - 1050°C.",
        typicalEntities: "Commonwealth Tile Works, Pioneer Tile Factories",
        qualityCheck: "Metallic ringing sound when struck, flexural breaking load > 1.0 kN."
      },
      {
        step: 4,
        name: "Packing & Freight",
        role: "Regional Logistics",
        description: "Interleaved straw/corrugated cushioned truck transport to prevent edge chipping during transit.",
        typicalEntities: "Kerala & South India regional freight carriers",
        qualityCheck: "Breakage percentage audit (< 1.5% target)."
      },
      {
        step: 5,
        name: "Local Building Material Dealer",
        role: "Roofing & Brick Depot",
        description: "Local yard maintaining buffer stock of standard ridge tiles, valley tiles, and field tiles.",
        typicalEntities: "District roofing supply depots",
        qualityCheck: "Lot color uniformity and interlocking fit verification."
      },
      {
        step: 6,
        name: "Roofing Subcontractor",
        role: "Specialist Carpentry / Steel Fabricator",
        description: "Fabrication of timber or GI purlin sub-structure at specified tile batten pitch (typically 320mm - 340mm).",
        typicalEntities: "Roofing contractor",
        qualityCheck: "Sub-structure slope verification (> 22° for tropical monsoon drainage)."
      },
      {
        step: 7,
        name: "Interlocking Installation",
        role: "Construction Site",
        description: "Dry-laying interlocking tiles from eaves to ridge, mechanical screw anchoring on wind-exposed hips and ridges.",
        typicalEntities: "Finished roof envelope",
        qualityCheck: "Water hose spray test to verify zero capillary water ingress."
      }
    ]
  },
  {
    id: "timber",
    title: "Structural Timber & Architectural Teak",
    category: "Woodwork & Framing",
    primaryOrigin: "Nilambur (Kerala Teak), Malabar Plantations, Certified Sustainable Forestry (FSC)",
    environmentalNotes: "Net carbon sequestering material when sourced from FSC-certified sustainable plantations or government forest department auctions.",
    standardCompliance: "IS 883 (Design of Structural Timber in Building), IS 1141 (Seasoning Code)",
    stages: [
      {
        step: 1,
        name: "Sustainable Plantation / Forest",
        role: "Forestry Reserve / Plantation",
        description: "Regulated harvest of mature hardwood (Nilambur Teak, Anjili, Rosewood) via Forest Department auctions.",
        typicalEntities: "Kerala Forest Development Corporation (KFDC), Certified Tree Farms",
        qualityCheck: "Legal chain-of-custody pass, girth measurement, tree maturity > 30-50 years."
      },
      {
        step: 2,
        name: "Sawmill Conversion",
        role: "Primary Sawmill",
        description: "Debarking and bandsaw quarter-sawing or plain-sawing into architectural scantlings, planks, and beams.",
        typicalEntities: "Licensed Sawmills (Kallai, Kozhikode, Perumbavoor)",
        qualityCheck: "Heartwood to sapwood ratio, straightness of grain, absence of rot."
      },
      {
        step: 3,
        name: "Kiln Seasoning & Preservation",
        role: "Seasoning Facility",
        description: "Controlled dehumidification seasoning down to 10-12% equilibrium moisture content (EMC) and borate vacuum pressure impregnation (VPI).",
        typicalEntities: "Timber treatment units",
        qualityCheck: "Moisture meter test across core (< 12%), insect bore hole resistance."
      },
      {
        step: 4,
        name: "Timber Wholesaler",
        role: "Wholesale Timber Depot",
        description: "Grading and stocking certified timber lots by species and cross-section.",
        typicalEntities: "State timber trade depots",
        qualityCheck: "Dimensional verification, warp / cup / twist tolerances."
      },
      {
        step: 5,
        name: "Joinery Workshop / Dealer",
        role: "Architectural Joinery Yard",
        description: "CNC profiling, precision mortise-and-tenon joinery, sanding, and customized architectural components.",
        typicalEntities: "Modular joinery works, traditional master carpenters",
        qualityCheck: "Tolerance of joinery joints, grain orientation."
      },
      {
        step: 6,
        name: "Finishing & Site Delivery",
        role: "Finisher / Contractor",
        description: "Application of natural oil, polyurethane, or micro-porous exterior weather sealers before installation.",
        typicalEntities: "Finishing contractors",
        qualityCheck: "Moisture seal integrity on all end-grains."
      },
      {
        step: 7,
        name: "Structural / Joinery Installation",
        role: "Construction Site",
        description: "Securing into masonry with non-ferrous anchors, isolating from direct damp concrete via bitumen felt / damp-proof barrier.",
        typicalEntities: "Door/window frames, rafters, ceilings",
        qualityCheck: "Expansion clearance check, plumb and true alignment."
      }
    ]
  }
];

export default function SupplyChainPage() {
  const [selectedChainId, setSelectedChainId] = useState<string>("stone");
  const activeChain = MATERIAL_CHAINS.find((c) => c.id === selectedChainId) || MATERIAL_CHAINS[0];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Editorial Header */}
      <div className="max-w-3xl">
        <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-arch-terracotta/10 text-arch-terracotta border border-arch-terracotta/20 mb-3">
          <GitFork className="w-3.5 h-3.5" />
          Material Provenance & Logistics Architecture
        </span>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-arch-charcoal tracking-tight">
          Architectural Material Supply Chain
        </h1>
        <p className="mt-2 text-sm text-stone-600 leading-relaxed font-sans">
          Understand where construction materials originate, how they are processed, and how they reach the jobsite. Distinguish typical generic supply chain routes from verified vendor relationships with environmental traceability.
        </p>
      </div>

      {/* 7-Stage Architecture Overview Banner */}
      <div className="bg-white rounded-3xl border border-arch-border p-6 shadow-2xs space-y-4">
        <h2 className="font-serif text-lg font-bold text-arch-charcoal flex items-center gap-2">
          <span>The 7-Stage Architectural Sourcing Pipeline</span>
          <span className="text-xs font-normal text-stone-400 font-sans">Standard Construction Logistics Model</span>
        </h2>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-2 text-xs">
          {[
            { step: 1, name: "Raw Source", icon: Mountain, role: "Quarry / Mine / Scrap" },
            { step: 2, name: "Primary Processing", icon: Factory, role: "Smelting / Slicing" },
            { step: 3, name: "Manufacturer", icon: Building2, role: "Branded Production" },
            { step: 4, name: "Distributor / Importer", icon: Truck, role: "Regional Depot" },
            { step: 5, name: "Dealer / Stockist", icon: Building2, role: "Local Showroom" },
            { step: 6, name: "Contractor Procurement", icon: HardHat, role: "Tender / Purchase" },
            { step: 7, name: "Construction Site", icon: Building2, role: "Final Installation" },
          ].map((st) => {
            const Icon = st.icon;
            return (
              <div key={st.step} className="p-3 rounded-2xl bg-stone-50 border border-stone-200/80 flex flex-col justify-between">
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="w-5 h-5 rounded-full bg-arch-terracotta text-white flex items-center justify-center font-bold text-xs">
                      {st.step}
                    </span>
                    <Icon className="w-3.5 h-3.5 text-stone-400" />
                  </div>
                  <div className="font-bold text-arch-charcoal text-xs leading-snug">{st.name}</div>
                </div>
                <div className="text-xs text-stone-500 mt-2 font-mono">{st.role}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Material Selector Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto scrollbar-none pb-1">
        {MATERIAL_CHAINS.map((chain) => (
          <button
            key={chain.id}
            onClick={() => setSelectedChainId(chain.id)}
            className={`px-4 py-2 rounded-2xl text-xs font-semibold whitespace-nowrap transition-all ${
              selectedChainId === chain.id
                ? 'bg-arch-dark text-white shadow-xs'
                : 'bg-white hover:bg-stone-100 text-stone-700 border border-arch-border'
            }`}
          >
            {chain.title}
          </button>
        ))}
      </div>

      {/* Detailed Material Case Study */}
      <div className="bg-white rounded-3xl border border-arch-border p-6 sm:p-10 shadow-sm space-y-8">
        {/* Dossier Header */}
        <div className="space-y-3 pb-6 border-b border-stone-100">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-bold bg-stone-100 text-stone-700 font-mono uppercase">
              {activeChain.category}
            </span>
            <span className="text-xs text-stone-500 font-mono">
              Standards: <strong className="text-stone-800">{activeChain.standardCompliance}</strong>
            </span>
          </div>

          <h2 className="font-serif text-2xl sm:text-3xl font-bold text-arch-charcoal">
            {activeChain.title}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 text-xs">
            <div className="p-3.5 rounded-xl bg-stone-50 border border-stone-200/80 space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-stone-400 block">
                Primary Regional Extraction / Origin
              </span>
              <p className="font-semibold text-arch-charcoal">{activeChain.primaryOrigin}</p>
            </div>

            <div className="p-3.5 rounded-xl bg-emerald-50/60 border border-emerald-200 space-y-1">
              <span className="text-xs font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1">
                <Leaf className="w-3 h-3 text-emerald-600" />
                <span>Environmental & Embodied Carbon Impact</span>
              </span>
              <p className="text-emerald-950 text-xs leading-relaxed">{activeChain.environmentalNotes}</p>
            </div>
          </div>
        </div>

        {/* Chronological Stages Timeline */}
        <div className="space-y-6">
          <h3 className="font-serif text-xl font-bold text-arch-charcoal">
            Detailed Step-by-Step Supply & Quality Verification Path
          </h3>

          <div className="space-y-4">
            {activeChain.stages.map((st) => (
              <div
                key={st.step}
                className="p-5 rounded-2xl bg-stone-50 border border-stone-200/90 hover:border-arch-terracotta/40 transition-all flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                <div className="flex items-start gap-4">
                  <div className="w-8 h-8 rounded-full bg-arch-dark text-white font-serif font-bold text-sm flex items-center justify-center shrink-0 mt-0.5">
                    {st.step}
                  </div>
                  <div className="space-y-1 text-xs">
                    <div className="flex flex-wrap items-center gap-2">
                      <h4 className="font-serif text-base font-bold text-arch-charcoal">
                        {st.name}
                      </h4>
                      <span className="text-xs font-mono text-arch-terracotta uppercase font-bold bg-arch-terracotta/10 px-2 py-0.5 rounded-md">
                        {st.role}
                      </span>
                    </div>

                    <p className="text-stone-600 leading-relaxed">
                      {st.description}
                    </p>

                    <div className="text-xs text-stone-500 pt-1">
                      Typical Entities: <strong className="text-stone-700">{st.typicalEntities}</strong>
                    </div>
                  </div>
                </div>

                {/* Quality Check on this Stage */}
                <div className="md:w-72 shrink-0 p-3 rounded-xl bg-white border border-stone-200 text-xs space-y-1">
                  <div className="flex items-center gap-1 font-bold text-xs uppercase tracking-wider text-emerald-800">
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    <span>Architectural Quality Gate</span>
                  </div>
                  <p className="text-xs text-stone-600 leading-snug">
                    {st.qualityCheck}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Callout */}
        <div className="pt-6 border-t border-stone-100 flex flex-wrap items-center justify-between gap-4">
          <div className="text-xs text-stone-500">
            Need to source this material locally? Check the regional directory for verified stockists.
          </div>
          <Link
            href={`/sourcing?q=${encodeURIComponent(activeChain.title.split(' ')[0])}`}
            className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-arch-dark hover:bg-arch-terracotta text-white font-semibold text-xs transition-colors shadow-2xs"
          >
            <span>Locate Verified Regional Suppliers</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      </div>
    </div>
  );
}
