import urllib.parse
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings

class GooglePlacesService:
    def __init__(self, api_key: Optional[str] = None):
        self._explicit_key = api_key

    @property
    def api_key(self) -> str:
        return self._explicit_key or settings.get_places_api_key()

    def is_configured(self) -> bool:
        return bool(self.api_key and self.api_key.strip())

    async def search_nearby_suppliers(
        self,
        material_type: str,
        lat: Optional[float] = None,
        lon: Optional[float] = None,
        city: Optional[str] = None,
        radius_km: float = 25.0,
        page_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Queries Google Places Platform API for legitimate building material suppliers,
        tile dealers, precast yards, plumbing supply shops, or electrical distributors.
        Supports both modern Places API (New) with places.location and legacy textsearch.
        Always returns verified zero-cost direct Google Maps query URLs.
        """
        mat_lower = (material_type or "").lower()
        location_label = city or (f"{lat},{lon}" if lat is not None and lon is not None else "nearby")

        # Build material-specific vendor queries (kilns, factories, distributors, stockists, rentals)
        if any(term in mat_lower for term in ["jcb", "machinery", "machine", "excavator", "rock breaker", "earthmover", "crane", "tool", "scaffold", "drill", "fastener", "screw"]):
            search_query = f"{material_type} equipment rental contractors dealers hire in {location_label}".strip()
        elif any(term in mat_lower for term in ["door", "window", "glazing", "glass", "upvc", "wood", "timber", "fenestration"]):
            search_query = f"{material_type} manufacturers dealers showroom workshop in {location_label}".strip()
        elif any(term in mat_lower for term in ["brick", "wirecut", "laterite", "porotherm", "aac block", "masonry", "cseb", "clay"]):
            search_query = f"{material_type} manufacturer factory kiln dealer wholesale supplier in {location_label}".strip()
        elif any(term in mat_lower for term in ["steel", "tmt", "rebar", "cement", "pipe"]):
            search_query = f"{material_type} authorized distributor stockist dealer in {location_label}".strip()
        else:
            search_query = f"{material_type} supplier dealer wholesale distributor in {location_label}".strip()

        encoded_query = urllib.parse.quote_plus(search_query)
        google_maps_search_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

        if not self.is_configured():
            return {
                "configured": False,
                "message": "Google Places API key is not configured. Built-in verified regional trade directory active.",
                "credential_required": "GOOGLE_PLACES_API_KEY",
                "setup_instructions": "Set GOOGLE_PLACES_API_KEY or GOOGLE_MAPS_API_KEY in backend/.env",
                "google_maps_search_url": google_maps_search_url,
                "places": []
            }

        radius_meters = int(radius_km * 1000)
        upstream_error: Optional[str] = None

        # 1. Try Modern Places API (New) endpoint
        try:
            new_api_url = "https://places.googleapis.com/v1/places:searchText"
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.location,places.types,places.nationalPhoneNumber,places.internationalPhoneNumber,places.websiteUri,places.rating,places.userRatingCount,places.googleMapsUri,nextPageToken"
            }
            body: Dict[str, Any] = {
                "textQuery": search_query,
                "maxResultCount": 20
            }
            if page_token:
                body["pageToken"] = page_token
            if lat is not None and lon is not None:
                body["locationBias"] = {
                    "circle": {
                        "center": {"latitude": lat, "longitude": lon},
                        "radius": float(radius_meters)
                    }
                }

            async with httpx.AsyncClient(timeout=10.0) as client:
                new_resp = await client.post(new_api_url, headers=headers, json=body)
                if new_resp.status_code == 200:
                    data = new_resp.json()
                    places = data.get("places", [])
                    results = []
                    for p in places:
                        name = p.get("displayName", {}).get("text", "Building Material Supplier")
                        address = p.get("formattedAddress", "")
                        maps_uri = p.get("googleMapsUri") or f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote_plus(name + ' ' + address)}"
                        
                        # Extract coordinates and distance
                        loc = p.get("location", {})
                        plat = loc.get("latitude")
                        plon = loc.get("longitude")
                        dist_km = None
                        if lat is not None and lon is not None and plat is not None and plon is not None:
                            from app.services.distance_service import calculate_haversine_distance
                            dist_km = calculate_haversine_distance(lat, lon, plat, plon)
                            if dist_km > radius_km:
                                continue

                        # Extract phone & clean WhatsApp if valid mobile
                        phone = p.get("nationalPhoneNumber") or p.get("internationalPhoneNumber")
                        whatsapp = None
                        if phone:
                            clean_digits = "".join(filter(str.isdigit, phone))
                            if len(clean_digits) == 10:
                                whatsapp = f"+91{clean_digits}"
                            elif len(clean_digits) == 12 and clean_digits.startswith("91"):
                                whatsapp = f"+{clean_digits}"

                        types = p.get("types", [])
                        primary_type = types[0].replace("_", " ").title() if types else "Trade Supplier"

                        results.append({
                            "name": name,
                            "address": address,
                            "latitude": plat,
                            "longitude": plon,
                            "distance_km": dist_km,
                            "distance_display": f"{dist_km} km" if dist_km is not None else (f"{city}" if city else None),
                            "phone": phone,
                            "whatsapp": whatsapp,
                            "website": p.get("websiteUri"),
                            "rating": p.get("rating"),
                            "reviews_count": p.get("userRatingCount"),
                            "user_ratings_total": p.get("userRatingCount"),
                            "google_place_id": p.get("id"),
                            "google_maps_url": maps_uri,
                            "business_type": "retail_supplier",
                            "category": primary_type,
                            "verification_status": "POTENTIAL_GOOGLE_PLACE",
                            "is_potential": True,
                            "stock_confirmation": "Live supplier discovered via Google Places API — contact to confirm physical inventory"
                        })
                    if results:
                        return {
                            "configured": True,
                            "api_type": "places_api_new",
                            "total_found": len(results),
                            "next_page_token": data.get("nextPageToken"),
                            "google_maps_search_url": google_maps_search_url,
                            "places": results
                        }
                elif new_resp.status_code in (401, 403, 429):
                    err_body = new_resp.json() if new_resp.headers.get("content-type", "").startswith("application/json") else {}
                    upstream_error = err_body.get("error", {}).get("message") or f"HTTP {new_resp.status_code}"
        except Exception as e:
            upstream_error = str(e)

        # 2. Fallback to Legacy Places Text Search
        try:
            legacy_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
            params: Dict[str, Any] = {
                "query": search_query,
                "key": self.api_key
            }
            if page_token:
                params["pagetoken"] = page_token
            if lat is not None and lon is not None:
                params["location"] = f"{lat},{lon}"
                params["radius"] = radius_meters

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(legacy_url, params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    legacy_status = data.get("status")
                    if legacy_status == "OK":
                        results = []
                        for item in data.get("results", [])[:20]:
                            geom = item.get("geometry", {}).get("location", {})
                            name = item.get("name")
                            addr = item.get("formatted_address")
                            place_id = item.get("place_id")
                            plat = geom.get("lat")
                            plon = geom.get("lng")
                            dist_km = None
                            if lat is not None and lon is not None and plat is not None and plon is not None:
                                from app.services.distance_service import calculate_haversine_distance
                                dist_km = calculate_haversine_distance(lat, lon, plat, plon)

                            results.append({
                                "name": name,
                                "address": addr,
                                "latitude": plat,
                                "longitude": plon,
                                "distance_km": dist_km,
                                "distance_display": f"{dist_km} km" if dist_km is not None else None,
                                "google_place_id": place_id,
                                "rating": item.get("rating"),
                                "reviews_count": item.get("user_ratings_total"),
                                "user_ratings_total": item.get("user_ratings_total"),
                                "google_maps_url": f"https://www.google.com/maps/place/?q=place_id:{place_id}",
                                "business_type": "retail_supplier",
                                "verification_status": "POTENTIAL_GOOGLE_PLACE",
                                "is_potential": True,
                                "stock_confirmation": "Potential supplier discovered via Google Places — contact to confirm physical inventory"
                            })
                        return {
                            "configured": True,
                            "api_type": "places_api_legacy",
                            "total_found": len(results),
                            "next_page_token": data.get("next_page_token"),
                            "google_maps_search_url": google_maps_search_url,
                            "places": results
                        }
                    if legacy_status in ("REQUEST_DENIED", "OVER_QUERY_LIMIT", "INVALID_REQUEST"):
                        upstream_error = f"{legacy_status}: {data.get('error_message') or 'Places request denied'}"
        except Exception as e:
            return {
                "configured": True,
                "error": str(e),
                "google_maps_search_url": google_maps_search_url,
                "places": []
            }

        out: Dict[str, Any] = {
            "configured": True,
            "google_maps_search_url": google_maps_search_url,
            "places": []
        }
        if upstream_error:
            out["upstream_error"] = upstream_error
        return out

google_places_service = GooglePlacesService()
