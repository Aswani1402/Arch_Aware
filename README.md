# Architect AI — Architectural Inspiration & Material Sourcing Platform

Architect AI is a full-stack architectural discovery and material sourcing platform that bridges the gap between visual architectural inspiration and physical building material procurement.

---

## 🌟 The Core Problem Architect AI Solves

Architects, interior designers, and landscape professionals should not be restricted to visiting a single local vendor or specifying only materials they see in nearby shops. When discovering inspiration across YouTube walkthroughs, Reddit discussions, Pinterest boards, and Instagram portfolios, architects need to:
1. **Identify the original manufacturer or brand** (e.g. *Asian Paints*, *Kajaria*, *Saint-Gobain*, *Marazzi*, *Kyoto Garden Stone Guild*) distinct from retail dealers.
2. **Compare multiple regional suppliers** selling that exact SKU with confirmed prices, stock levels, and delivery radii.
3. **Expand search dynamically** across 7 geographic scopes when a material is unavailable in the immediate locality.
4. **Dispatch quotation inquiries** directly to verified trade yards.

---

## 🏗️ Architecture & Sourcing Pipeline

```
ARCHITECTURAL INSPIRATION (YouTube, Reddit, Pinterest, Instagram, Catalogs)
        │
        ▼
DESIGN REFERENCES (Joinery, exposed masonry, breezeblocks, finishes)
        │
        ▼
BUILDING MATERIALS (Material specs, water absorption, thermal mass)
        │
        ▼
PRODUCT DISCOVERY (Original Manufacturer SKUs, official catalog PDFs)
        │
        ▼
SUPPLIER DISCOVERY (Distributors, authorized dealers, stone yards, importers)
        │
        ▼
7-LEVEL REGIONAL SOURCING FALLBACK
        ├── Level 0: Immediate Vicinity (<25 km)
        ├── Level 1: Extended Local Region (50 km)
        ├── Level 2: Regional Architectural Hubs (100 km)
        ├── Level 3: Selected State (Kerala)
        ├── Level 4: Neighbouring States (Tamil Nadu, Karnataka)
        ├── Level 5: South India Regional Corridor
        ├── Level 6: Pan-India Manufacturers & Freight
        └── Level 7: International Sourcing (Japan, Italy, Germany)
        │
        ▼
FORMAL QUOTATION REQUESTS & VENDOR LOGISTICS
```

---

## 🛠️ Technology Stack

- **Frontend**:
  - **Framework**: Next.js 14 (App Router)
  - **Language**: TypeScript
  - **Styling**: Tailwind CSS (Tailored architectural palette: Warm White `#FBFBF9`, Charcoal `#1A1A18`, Terracotta `#C86D51`)
  - **Icons**: Lucide React
  - **Typography**: Google Fonts (*Cormorant Garamond* & *Inter*)
- **Backend**:
  - **Framework**: Python 3.13 + FastAPI
  - **ORM & Database**: SQLAlchemy (SQLite for zero-config instant local dev + full PostgreSQL/PostGIS support via `DATABASE_URL`)
  - **Security & Tokens**: Bcrypt password hashing + PyJWT Bearer Authentication
  - **Spatial Logic**: Haversine Spherical Distance Algorithm
  - **HTTP & Connectors**: HTTPX async client
- **Testing**:
  - Pytest + Starlette TestClient (100% test pass rate across feed, fallback, auth, quotations, and admin)

---

## 🚀 Quick Start / Running Locally

### Prerequisites
- Python 3.10+ (Python 3.13 installed)
- Node.js 18+ (Node.js 24 installed) & npm

### 1. Start the Backend API (FastAPI)
Open a terminal in the root folder:
```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the FastAPI server
python backend\run.py
```
- **Backend API**: `http://127.0.0.1:8000`
- **Interactive OpenAPI Docs**: `http://127.0.0.1:8000/docs`
- **Health Check**: `http://127.0.0.1:8000/api/health`

*Note: Database tables and authentic architectural seed data are initialized automatically on startup.*

---

### 2. Start the Frontend (Next.js)
Open a second terminal in the `frontend` folder:
```powershell
cd frontend
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

## 🧪 Running the Test Suite
To verify the entire backend test suite:
```powershell
.\venv\Scripts\python.exe -m pytest backend\app\tests -v
```
All 10 tests will execute:
- ✅ `test_feed_endpoint`: Feed listing and pagination
- ✅ `test_feed_category_filter`: Category filtering (tiles, stone, paints, etc.)
- ✅ `test_feed_platform_filter`: Platform filtering (YouTube, Reddit, Instagram, etc.)
- ✅ `test_reference_detail`: Reference detail & verified product matches
- ✅ `test_hierarchical_sourcing_kochi`: 7-level regional fallback starting from Kochi, Kerala
- ✅ `test_international_sourcing_kyoto`: International sourcing fallback to Kyoto, Japan
- ✅ `test_deduplication_across_levels`: Zero duplicate vendors across geographic tiers
- ✅ `test_login_flow`: JWT authentication and password hashing
- ✅ `test_quotation_workflow`: Quotation submission & supplier response
- ✅ `test_admin_stats`: Curator dashboard statistics

---

## 🔑 External API Integrations & Credentials Guide

The platform is architected to run out of the box in **Permitted Demo Mode** with authentic architectural content (genuine YouTube video IDs, real manufacturer catalogs, and genuine coordinate grids). External API keys are entirely optional:

| Integration | Environment Variable | Purpose | Fallback Behavior When Missing |
|---|---|---|---|
| **SocialCrawl Discovery API** | `SOCIALCRAWL_API_KEY` | Live unified discovery across Pinterest, Instagram Reels, YouTube, Reddit, Google Shopping & Twitter/X | Curated architectural database with genuine high-resolution references |
| **YouTube Data API v3** | `YOUTUBE_API_KEY` | Direct YouTube architectural video search fallback | Loads curated architectural walkthroughs with genuine YouTube video embeds |
| **Reddit API** | `REDDIT_CLIENT_ID`<br>`REDDIT_CLIENT_SECRET` | Live ingestion from `r/architecture` & `r/InteriorDesign` | Ingests curated community discussions preserving author attribution & permalinks |
| **Pinterest API** | `PINTEREST_API_KEY` | Ingestion of architectural pins & boards | Curated architectural pinboards and user reference URLs |
| **Instagram Graph API** | `INSTAGRAM_APP_ID` | Ingestion from architectural studio profiles | Curated references preserving creator handles and URLs |
| **Google Maps / Places** | `GOOGLE_PLACES_API_KEY`<br>`CUSTOM_SEARCH_API_KEY` | Google Places trade yard discovery & architectural image search | Built-in architectural hub geocoder covering Kochi, Calicut, Trivandrum, Bengaluru, Chennai, Mumbai, Delhi |

---

## 👤 Instant Demo Accounts

You can test role-based capabilities instantly using the fast-switch buttons on the `/login` page:

| Role | Email | Password | Capabilities |
|---|---|---|---|
| **Architect** | `architect@studio.com` | `password123` | Browse feed, save moodboards, submit quotation inquiries |
| **Supplier** | `supplier@malabarpaints.com` | `supplier123` | Manage catalog inventory, respond to quotation inquiries |
| **Curator Admin** | `admin@architect.ai` | `adminpassword123` | Verify suppliers, approve products, trigger connector syncs |

---

## 📁 Repository Structure

```
Architect_AI/
├── backend/
│   ├── app/
│   │   ├── api/             # FastAPI REST endpoints (feed, sourcing, products, admin, quotations)
│   │   ├── connectors/      # Modular connectors (YouTube, Reddit, Pinterest, Instagram, Catalog)
│   │   ├── core/            # Config, database engine, security & JWT utilities
│   │   ├── db/              # Initializer & authentic architectural seed data
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── schemas/         # Pydantic validation schemas
│   │   ├── services/        # 7-level sourcing service, Haversine distance, quotations
│   │   └── tests/           # Full pytest test suite
│   ├── requirements.txt
│   └── run.py               # Backend runner entrypoint
├── frontend/
│   ├── app/
│   │   ├── layout.tsx       # Root layout with fonts & Navbar
│   │   ├── page.tsx         # Continuous Architectural Discovery Feed
│   │   ├── reference/[id]/  # Standalone Reference Detail Page
│   │   ├── product/[id]/    # Product Detail (Manufacturer vs Multiple Vendors)
│   │   ├── supplier/[id]/   # Supplier Profile & Catalog
│   │   ├── manufacturer/[id]/# Official Brand Catalog
│   │   ├── sourcing/        # 7-Level Regional Sourcing Engine
│   │   ├── saved/           # Curated Moodboards & Material Specs
│   │   ├── quotations/      # Quotation Inquiries & Supplier Responses
│   │   ├── suppliers/register/# Supplier Onboarding Page
│   │   ├── admin/           # Curator Verification Dashboard
│   │   └── login/           # Auth Portal & Demo Role Switcher
│   ├── components/          # Reusable UI components (FeedCard, Modal, YouTubeEmbed, Badges)
│   ├── lib/                 # API client & Auth/Location Context
│   └── types/               # TypeScript interfaces
├── docs/
│   ├── ARCHITECTURE.md
│   ├── SOURCING_HIERARCHY.md
│   └── API_DOCUMENTATION.md
├── docker-compose.yml
├── .env.example
└── README.md
```
#
