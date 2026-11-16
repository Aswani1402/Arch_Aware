# Architect AI — System Architecture & Design Philosophy

## 1. Overview & Vision
Architect AI is a dedicated architectural inspiration and building material sourcing platform designed specifically for architects, interior designers, landscape architects, and design studios.

### The Problem It Solves
Traditional architects are often restricted to the limited stock of one or two local vendors. When designing a facade, courtyard, or minimalist interior, discovering who originally manufactures a material (e.g., Asian Paints, Kajaria, Saint-Gobain, Marazzi, Japanese stone ateliers) and which regional suppliers actually stock or distribute it is fragmented across social media, PDF catalogs, and manual telephone inquiries.

Architect AI connects the entire journey:
```
ARCHITECTURAL INSPIRATION (YouTube, Reddit, Pinterest, Instagram, Curated Portfolios)
        │
        ▼
DESIGN REFERENCES (Visual context, architectural details, joinery, masonry)
        │
        ▼
BUILDING MATERIALS (Material composition, finishes, performance ratings)
        │
        ▼
PRODUCT DISCOVERY (Original Manufacturer SKUs, official catalogs, dimensions)
        │
        ▼
SUPPLIER DISCOVERY (Distributors, authorized dealers, stone yards, importers)
        │
        ▼
LOCATION-BASED SOURCING (7-Tier hierarchical fallback from local yard to global craft studios)
        │
        ▼
CONTACT & FORMAL QUOTATION REQUESTS
```

---

## 2. Core Architectural Principles

### 2.1 Distinction Between Original Manufacturer vs. Vendor/Supplier
One of the most important architectural rules of the system:
- **Original Manufacturer / Brand Owner**: The company that engineered, quarried, or manufactured the material (e.g. *Asian Paints*, *Kajaria Ceramics*, *Marazzi Group*, *Kyoto Garden Stone Guild*).
- **Supplier / Dealer / Distributor / Retailer**: The vendor selling or stocking the product (e.g. *Malabar Paint & Decor*, *Coastal Surfaces Ernakulam*, *Deccan Builders Coimbatore*).
- **One Product, Multiple Suppliers**: A single SKU (e.g., *Apex Ultima Protek 20L*) exists once in the product catalog and is linked to multiple regional suppliers with distinct prices, lead times, and freight terms.
- **One Supplier, Many Products**: A supplier maintains an independent catalog of multiple brands and categories.

### 2.2 Material & Product Identification Verification Levels
Never infer country of origin or manufacturer identity from visual resemblance alone:
1. `VERIFIED_EXACT` / `MANUFACTURER_CONFIRMED`: The manufacturer or distributor has confirmed the exact product identity, technical specifications, and official catalog URL.
2. `VISUALLY_SIMILAR`: The material resembles the architectural inspiration reference but is not confirmed to be the identical product.
3. `ALTERNATIVE_REVIEW`: A different product that may satisfy the design intent or monsoonal durability requirements.
4. `POTENTIAL_GOOGLE_PLACE`: Discovered via business listing directories (e.g., Google Places) without confirmed live stock. Clearly labeled: *"Potential supplier — contact to confirm"*.
5. `UNVERIFIED`: Original source or manufacturer unconfirmed.

---

## 3. Modular Source Connector Architecture
Architect AI is decoupled from individual social platforms. Every external ingestion source implements `BaseSourceConnector`:

```
BaseSourceConnector (app/connectors/base.py)
   ├── YouTubeConnector (Official YouTube Data API v3 + permitted video embedding)
   ├── RedditConnector (Reddit API / JSON public index with community attribution)
   ├── PinterestConnector (Authorized pin reference metadata)
   ├── InstagramConnector (Graph API reference handler preserving creator handles)
   └── CatalogConnector (Direct manufacturer specification sheet parser)
```

Each connector is responsible for:
1. Respecting platform API rate limits.
2. Ingesting only permitted previews and URLs (no illegal downloading or copyright republishing).
3. Normalizing data into `NormalizedReference`.
4. Storing provenance notes and recording synchronization health logs.
5. Providing an authentic offline/demo fallback mode when third-party API keys are not yet configured.

---

## 4. Frontend Design Aesthetics
- **Palette**: Architectural warm white backgrounds (`#FBFBF9`), dark charcoal typography (`#1A1A18`), restrained terracotta earthy accents (`#C86D51`), and subtle stone borders (`#E8E6E0`).
- **Typography**: Editorial architectural elegance with *Cormorant Garamond* for titles and *Inter* for clean technical specifications.
- **Continuous Scrolling**: Responsive multi-column masonry grid with lazy image loading and position preservation when opening reference modals.
- **Media Controls**: Embedded YouTube video players strictly respect user context — stopping playback upon closing modals or scrolling away, with audio autoplay disabled.
