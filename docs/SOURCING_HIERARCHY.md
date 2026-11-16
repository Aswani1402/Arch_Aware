# Hierarchical Regional Sourcing & Fallback Logic

## 1. The Core Sourcing Problem
When an architect in Kochi, Calicut, or Bengaluru specifies an architectural material (such as *Machine-cut laterite blocks*, *Kiln-fired terracotta jaali screens*, or *Kyoto andesite stepping stones*), searching only a narrow 5 km radius might yield zero results.

However, an architect should not abandon a design simply because no local retail shop stocks it. The material might be stocked:
- 30 km away in an industrial hub (Aluva / Kalamassery)
- 70 km away in a specialty stone quarry (Thrissur / Ollur)
- 140 km away in an adjacent state corridor (Coimbatore, Tamil Nadu)
- 350 km away in a major national distribution center (Bengaluru, Karnataka)
- Or directly from an artisanal craft exporter overseas (Kyoto, Japan)

Architect AI implements a backend search orchestration service that executes a **7-tier progressive hierarchical fallback**.

---

## 2. The 7 Hierarchical Levels

| Tier | Level Name | Geographic Scope | Typical Transit / Logistics |
|---|---|---|---|
| **Level 0** | Immediate Vicinity | Within user selected initial radius (Default: **25 km**) | Same-day site delivery, local truck dispatch |
| **Level 1** | Extended Local Region | **25 km to 50 km** radius | Regional delivery van / tempo dispatch |
| **Level 2** | Regional Architectural Hubs | **50 km to 100 km** radius | Inter-district freight, medium truck |
| **Level 3** | Selected State | Entire project state (e.g., **Kerala**) | State-wide logistics network, quarry flatbed |
| **Level 4** | Neighbouring States | Bordering states (e.g. for Kerala: **Tamil Nadu, Karnataka**) | Inter-state transport, multi-axle freight |
| **Level 5** | South India Regional Corridor | **Kerala, Tamil Nadu, Karnataka, Andhra Pradesh, Telangana, Goa** | Regional logistics corridor, 2–4 days transit |
| **Level 6** | Pan-India Manufacturers | All Indian states (e.g. Mumbai, Delhi, Gujarat tile belts) | Containerized freight, rail cargo, 4–7 days |
| **Level 7** | International Sourcing | Global craft studios & exporters (e.g. **Japan, Italy, Germany**) | Sea freight to Cochin / Nhava Sheva Port, customs clearance |

---

## 3. Strict Deduplication Guarantee
A supplier appears **only once** in the results. If a supplier qualifies for Level 0 (<25 km), it is claimed by Level 0 and is **never repeated** in Levels 1 through 7. This ensures clean, non-redundant presentation for architects comparing vendors.

---

## 4. Distance Calculation Algorithm
Distances are computed using the **Haversine formula**, which calculates the great-circle distance between two coordinate pairs on a spherical Earth:

$$\Delta\text{lat} = \text{lat}_2 - \text{lat}_1$$
$$\Delta\text{lon} = \text{lon}_2 - \text{lon}_1$$
$$a = \sin^2\left(\frac{\Delta\text{lat}}{2}\right) + \cos(\text{lat}_1)\cos(\text{lat}_2)\sin^2\left(\frac{\Delta\text{lon}}{2}\right)$$
$$c = 2 \cdot \text{atan2}(\sqrt{a}, \sqrt{1-a})$$
$$d = R \cdot c \quad (R = 6371\text{ km})$$

Implemented in `backend/app/services/distance_service.py` to run universally on both SQLite and PostgreSQL.

---

## 5. Potential Suppliers vs. Confirmed Stock
- If a supplier was discovered via Google Places or directory indexation but has not confirmed physical stock of the exact SKU, it is tagged:
  `POTENTIAL_GOOGLE_PLACE`: *"Potential supplier — contact to confirm"*.
- If a supplier has an active dealer agreement or confirmed inventory record with prices and MOQs, it is tagged:
  `VERIFIED`: *"Manufacturer Confirmed Stock"*.
