# Architect AI — REST API Documentation

The backend REST API is built with **FastAPI** and runs at `http://127.0.0.1:8000/api`.
Interactive OpenAPI documentation is automatically available at `http://127.0.0.1:8000/docs`.

---

## 1. Authentication Endpoints

### Register User
`POST /api/auth/register`
```json
{
  "email": "architect@studio.com",
  "password": "password123",
  "full_name": "Aswini Ayappan",
  "role": "user"
}
```

### Login
`POST /api/auth/login`
```json
{
  "email": "architect@studio.com",
  "password": "password123"
}
```
**Response**: Returns JWT bearer access token and user profile.

### Current User Profile
`GET /api/auth/me`
Header: `Authorization: Bearer <token>`

---

## 2. Discovery Feed & References

### Continuous Architectural Feed
`GET /api/feed`
Query Parameters:
- `page`: Integer (default 1)
- `page_size`: Integer (default 12)
- `q`: Search keyword across title, material tags, or description
- `category`: Category slug (`tiles`, `natural-stone`, `paints-and-finishes`, `flooring`, `garden-materials`, `doors-and-windows`)
- `platform`: `youtube`, `reddit`, `pinterest`, `instagram`, `catalog`

### Architectural Reference Detail
`GET /api/references/{id_or_slug}`
Returns reference details, authorized preview or YouTube embed ID, creator attribution, and list of linked manufacturer products with match confidence.

### Submit Manual Reference
`POST /api/references`
Allows architects to submit an external Pinterest or Instagram reference link with material tags.

---

## 3. Products & Catalogs

### List Products
`GET /api/products`
Query Parameters: `category`, `material`, `manufacturer`, `q`

### Product Detail
`GET /api/products/{id_or_slug}`
Returns:
- Product technical specifications (finish, dimensions, performance metrics)
- Original Manufacturer / Brand details (website, official catalog PDF)
- Multi-vendor comparison list of suppliers selling this SKU with confirmed prices, currency, availability, and delivery scopes.

---

## 4. Location-Based Sourcing & 7-Level Regional Fallback

### Hierarchical Sourcing Search
`GET /api/sourcing/search`
Query Parameters:
- `q`: Material or style keyword (e.g. `Japanese Stone`, `Laterite`, `Apex Ultima`)
- `product_id`: Direct product ID filter
- `category`: Category slug filter
- `city`: Project location city (default: `Kochi`)
- `state`: Project location state (default: `Kerala`)
- `lat`: GPS latitude coordinate
- `lon`: GPS longitude coordinate
- `radius`: Initial radius in km (default: `25.0`)

**Response**: Returns `HierarchicalSourcingResponse` with all 8 traversed levels (Level 0 through Level 7) with deduplicated suppliers, calculated distances, contact telephone numbers, and Google Maps links.

---

## 5. Suppliers & Vendor Onboarding

### List Suppliers
`GET /api/suppliers`
Query Parameters: `city`, `state`, `country`, `business_type`, `q`

### Supplier Profile & Catalog
`GET /api/suppliers/{id_or_slug}`
Returns supplier business credentials, address, verified status, delivery radius, and all products stocked by this supplier.

### Supplier Self-Registration
`POST /api/suppliers/register`
```json
{
  "name": "Malabar Natural Stone Depot",
  "business_type": "authorized_dealer",
  "address": "NH 66 Bypass, Edappally",
  "city": "Kochi",
  "state": "Kerala",
  "pin_code": "682024",
  "phone": "+91 484 253 4810",
  "email": "orders@malabarstone.com",
  "website": "https://malabarstone.in",
  "delivery_radius_km": 100.0
}
```

---

## 6. Quotation Inquiries Workflow

### Submit Quotation Request
`POST /api/quotations`
Header: `Authorization: Bearer <token>`
```json
{
  "product_id": 1,
  "supplier_id": 1,
  "quantity": "25 Drums (500L)",
  "dimensions": "Standard 20L containers",
  "project_location": "Fort Kochi Heritage Villa Project",
  "city": "Kochi",
  "state": "Kerala",
  "pin_code": "682001",
  "delivery_urgency": "standard",
  "additional_notes": "Phased delivery required."
}
```

### List User Quotations
`GET /api/quotations`

### Respond to Quotation (Vendor Portal)
`POST /api/quotations/{request_id}/respond`
```json
{
  "quoted_price": 118750.0,
  "currency": "INR",
  "estimated_delivery_days": 3,
  "delivery_terms": "Door delivery via flatbed truck.",
  "response_message": "Ready stock in Edappally depot."
}
```

---

## 7. Saved Items & Moodboards

### Toggle Bookmark
`POST /api/saved/toggle`
```json
{
  "item_type": "reference",
  "reference_id": 1,
  "project_collection": "Moodboard"
}
```

### List Saved Items
`GET /api/saved`

---

## 8. Source Connectors & Admin Dashboard

### List Connectors
`GET /api/connectors`

### Trigger Ingestion Sync
`POST /api/connectors/{platform}/sync`
Platforms: `youtube`, `reddit`, `pinterest`, `instagram`, `catalog`

### Admin Metrics
`GET /api/admin/stats`

### Update Supplier Verification
`PUT /api/admin/suppliers/{id}/verify`
Body: `{"status": "VERIFIED"}`
