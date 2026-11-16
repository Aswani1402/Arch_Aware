from fastapi import APIRouter
from typing import List, Dict, Any, Optional

router = APIRouter(prefix="/locations", tags=["Locations & Geocoding"])

ARCHITECTURAL_HUBS = [
    {"city": "Kochi", "state": "Kerala", "latitude": 9.9312, "longitude": 76.2673, "pin_code": "682001", "label": "Kochi / Ernakulam (Kerala)", "aliases": ["ernakulam", "cochin", "kochi"]},
    {"city": "Calicut", "state": "Kerala", "latitude": 11.2588, "longitude": 75.7804, "pin_code": "673001", "label": "Kozhikode / Malabar (Kerala)", "aliases": ["kozhikode", "calicut", "malabar"]},
    {"city": "Trivandrum", "state": "Kerala", "latitude": 8.5241, "longitude": 76.9366, "pin_code": "695001", "label": "Thiruvananthapuram (Kerala)", "aliases": ["thiruvananthapuram", "trivandrum"]},
    {"city": "Bengaluru", "state": "Karnataka", "latitude": 12.9716, "longitude": 77.5946, "pin_code": "560001", "label": "Bengaluru (Karnataka)", "aliases": ["bangalore", "bengaluru"]},
    {"city": "Nagercoil", "state": "Tamil Nadu", "latitude": 8.1833, "longitude": 77.4119, "pin_code": "629001", "label": "Nagercoil / Kanyakumari (Tamil Nadu)", "aliases": ["nagercoil", "kanyakumari", "marthandam"]},
    {"city": "Chennai", "state": "Tamil Nadu", "latitude": 13.0827, "longitude": 80.2707, "pin_code": "600001", "label": "Chennai (Tamil Nadu)", "aliases": ["chennai", "madras"]},
    {"city": "Coimbatore", "state": "Tamil Nadu", "latitude": 11.0168, "longitude": 76.9558, "pin_code": "641001", "label": "Coimbatore (Tamil Nadu)", "aliases": ["coimbatore", "kovai"]},
    {"city": "Tirunelveli", "state": "Tamil Nadu", "latitude": 8.7139, "longitude": 77.7567, "pin_code": "627001", "label": "Tirunelveli (Tamil Nadu)", "aliases": ["tirunelveli", "nellai"]},
    {"city": "Madurai", "state": "Tamil Nadu", "latitude": 9.9252, "longitude": 78.1198, "pin_code": "625001", "label": "Madurai (Tamil Nadu)", "aliases": ["madurai"]},
    {"city": "Mumbai", "state": "Maharashtra", "latitude": 19.0760, "longitude": 72.8777, "pin_code": "400001", "label": "Mumbai (Maharashtra)", "aliases": ["mumbai", "bombay"]},
    {"city": "Hyderabad", "state": "Telangana", "latitude": 17.3850, "longitude": 78.4867, "pin_code": "500001", "label": "Hyderabad (Telangana)", "aliases": ["hyderabad", "secunderabad"]},
    {"city": "Delhi", "state": "Delhi", "latitude": 28.6139, "longitude": 77.2090, "pin_code": "110001", "label": "New Delhi / NCR", "aliases": ["delhi", "new delhi", "noida", "gurgaon", "gurugram"]},
]

@router.get("/reverse")
async def reverse_geocode_coords(lat: float, lon: float) -> Dict[str, Any]:
    """
    Reverse geocodes device GPS coordinates into a verified real locality / city name.
    """
    import httpx
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get(
                "https://nominatim.openstreetmap.org/reverse",
                params={"format": "json", "lat": lat, "lon": lon, "zoom": 12},
                headers={"User-Agent": "NivoraApp/1.0 (Specification & Sourcing)"}
            )
            if resp.status_code == 200:
                data = resp.json()
                addr = data.get("address", {})
                city = (
                    addr.get("city")
                    or addr.get("town")
                    or addr.get("municipality")
                    or addr.get("suburb")
                    or addr.get("district")
                    or addr.get("county")
                    or addr.get("state_district")
                )
                state = addr.get("state") or "India"
                country = addr.get("country") or "India"
                if city:
                    return {
                        "success": True,
                        "city": city,
                        "state": state,
                        "country": country,
                        "latitude": lat,
                        "longitude": lon,
                        "display_name": data.get("display_name"),
                        "source": "nominatim_reverse"
                    }
    except Exception:
        pass
    return {
        "success": False,
        "detail": "Could not reverse geocode coordinates."
    }


@router.get("/presets")
def get_location_presets() -> List[Dict[str, Any]]:
    return ARCHITECTURAL_HUBS

@router.get("/geocode")
async def geocode_city_or_pin(q: str) -> Dict[str, Any]:
    query = q.strip().lower()
    if not query:
        return {
            "success": False,
            "detail": "Please enter a city or pin code to search.",
            "city": None,
            "state": None,
            "latitude": None,
            "longitude": None,
            "pin_code": None,
            "source": "empty_query"
        }

    # 1. Match presets and their known regional aliases
    for hub in ARCHITECTURAL_HUBS:
        aliases = hub.get("aliases", [])
        if (
            query in hub["city"].lower()
            or query in hub["pin_code"]
            or query in hub["state"].lower()
            or any(query == a or query in a for a in aliases)
        ):
            return {
                "success": True,
                "city": hub["city"],
                "state": hub["state"],
                "latitude": hub["latitude"],
                "longitude": hub["longitude"],
                "pin_code": hub["pin_code"],
                "source": "preset_database"
            }

    # 2. Forward geocode via OpenStreetMap Nominatim for real locations outside presets
    import httpx
    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(
                "https://nominatim.openstreetmap.org/search",
                params={"q": q.strip(), "format": "json", "limit": 1, "addressdetails": 1},
                headers={"User-Agent": "NivoraApp/1.0 (Specification & Sourcing)"}
            )
            if resp.status_code == 200:
                results = resp.json()
                if results and len(results) > 0:
                    first = results[0]
                    addr = first.get("address", {})
                    found_city = (
                        addr.get("city")
                        or addr.get("town")
                        or addr.get("municipality")
                        or addr.get("suburb")
                        or addr.get("county")
                        or addr.get("state_district")
                        or first.get("name")
                    )
                    found_state = addr.get("state") or "India"
                    return {
                        "success": True,
                        "city": found_city or q.strip().title(),
                        "state": found_state,
                        "latitude": float(first["lat"]),
                        "longitude": float(first["lon"]),
                        "pin_code": addr.get("postcode", ""),
                        "source": "nominatim_forward"
                    }
    except Exception:
        pass

    # No silent Kochi fallback! Return clear unsuccessful response
    return {
        "success": False,
        "detail": f"Could not find location '{q}'. Please check spelling or select from regional presets.",
        "city": None,
        "state": None,
        "latitude": None,
        "longitude": None,
        "pin_code": None,
        "source": "not_found"
    }

@router.get("/google-places/search")
async def search_google_places_suppliers(
    query: str = "tiles stone materials",
    material: Optional[str] = None,
    city: Optional[str] = None,
    lat: float = 9.9312,
    lon: float = 76.2673,
    radius_km: float = 25.0
):
    from app.services.google_places_service import google_places_service
    search_term = material if material else query
    result = await google_places_service.search_nearby_suppliers(
        material_type=search_term,
        lat=lat,
        lon=lon,
        radius_km=radius_km
    )
    result["query"] = search_term
    result["city"] = city
    result["results"] = result.get("places", [])
    return result

