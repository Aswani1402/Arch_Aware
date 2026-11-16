import math
from typing import List, Tuple, Dict, Optional, Union

# Geographic aliases mapping variations and vernacular spellings to canonical location keys
CITY_DISTRICT_ALIASES: Dict[str, str] = {
    "trivandrum": "thiruvananthapuram",
    "thiruvananthapuram": "thiruvananthapuram",
    "tvm": "thiruvananthapuram",
    "cochin": "kochi",
    "ernakulam": "kochi",
    "kochi": "kochi",
    "calicut": "kozhikode",
    "kozhikode": "kozhikode",
    "trichur": "thrissur",
    "thrissur": "thrissur",
    "alleppey": "alappuzha",
    "alappuzha": "alappuzha",
    "quilon": "kollam",
    "kollam": "kollam",
    "palghat": "palakkad",
    "palakkad": "palakkad",
    "cannur": "kannur",
    "cannanore": "kannur",
    "kannur": "kannur",
    "bangalore": "bengaluru",
    "bengaluru": "bengaluru",
    "madras": "chennai",
    "chennai": "chennai"
}

def normalize_location_name(name: Optional[str]) -> str:
    """Normalizes city and district aliases to canonical keys."""
    if not name:
        return ""
    cleaned = name.strip().lower()
    return CITY_DISTRICT_ALIASES.get(cleaned, cleaned)


# Verified boundary polygon coordinates for Thiruvananthapuram District
# Perimeter points from Kappil/Varkala coast to Poovar/Parassala and the Western Ghats Agasthyamala ridge.
TVM_DISTRICT_POLYGON: List[Tuple[float, float]] = [
    (8.790, 76.690),  # Kappil / Kollam coastal border
    (8.740, 76.695),  # Varkala coast
    (8.615, 76.810),  # Perumathura / Kadinamkulam
    (8.550, 76.850),  # Kazhakkoottam / Menamkulam
    (8.480, 76.900),  # Shanghumukham
    (8.390, 76.970),  # Kovalam
    (8.360, 76.995),  # Vizhinjam
    (8.300, 77.060),  # Poovar / Pozhiyoor coastal border
    (8.320, 77.160),  # Parassala / Kaliyakkavilai
    (8.380, 77.210),  # Kunnathukal / TN border
    (8.440, 77.240),  # Vellarada / Chittar border
    (8.615, 77.260),  # Agasthyamala peak / Ghats ridge
    (8.700, 77.200),  # Bonacaud
    (8.770, 77.120),  # Ponmudi
    (8.840, 77.045),  # Madathara border
    (8.815, 76.930),  # Kilimanoor / Kollam border
    (8.800, 76.780),  # Navaikulam / Parippally border
]

DISTRICT_BOUNDARIES: Dict[str, List[Tuple[float, float]]] = {
    "thiruvananthapuram": TVM_DISTRICT_POLYGON,
}


def is_point_in_polygon(lat: float, lon: float, polygon: List[Tuple[float, float]]) -> bool:
    """
    Standard Ray-casting algorithm to test whether (lat, lon) is inside a closed polygon.
    """
    n = len(polygon)
    if n < 3:
        return False
    inside = False
    p1_lat, p1_lon = polygon[0]
    for i in range(1, n + 1):
        p2_lat, p2_lon = polygon[i % n]
        if min(p1_lon, p2_lon) < lon <= max(p1_lon, p2_lon):
            if lat <= max(p1_lat, p2_lat):
                if p1_lon != p2_lon:
                    xinters = (lon - p1_lon) * (p2_lat - p1_lat) / (p2_lon - p1_lon) + p1_lat
                if p1_lat == p2_lat or lat <= xinters:
                    inside = not inside
        p1_lat, p1_lon = p2_lat, p2_lon
    return inside


def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth in kilometers
    using the Haversine formula.
    """
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    distance = R * c
    return round(distance, 2)


def distance_point_to_segment(p_lat: float, p_lon: float, a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    """
    Calculate minimum distance from point P to line segment AB in kilometers.
    Uses local equirectangular projection for regional accuracy.
    """
    lat_mid = math.radians((a_lat + b_lat + p_lat) / 3.0)
    kx = math.cos(lat_mid) * 111.195
    ky = 111.195

    ax = a_lon * kx
    ay = a_lat * ky
    bx = b_lon * kx
    by = b_lat * ky
    px = p_lon * kx
    py = p_lat * ky

    dx = bx - ax
    dy = by - ay
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq < 1e-9:
        return calculate_haversine_distance(p_lat, p_lon, a_lat, a_lon)

    t = ((px - ax) * dx + (py - ay) * dy) / seg_len_sq
    t = max(0.0, min(1.0, t))
    closest_lon = a_lon + t * (b_lon - a_lon)
    closest_lat = a_lat + t * (b_lat - a_lat)
    return calculate_haversine_distance(p_lat, p_lon, closest_lat, closest_lon)


def distance_to_district_boundary(lat: float, lon: float, district_or_polygon: Union[str, List[Tuple[float, float]]]) -> float:
    """
    Calculate shortest distance from (lat, lon) to a district perimeter.
    Returns 0.0 if the point is inside the district perimeter.
    Otherwise returns distance in kilometers to the nearest boundary segment.
    """
    if isinstance(district_or_polygon, str):
        canonical = normalize_location_name(district_or_polygon)
        polygon = DISTRICT_BOUNDARIES.get(canonical)
        if not polygon:
            return 999999.0
    else:
        polygon = district_or_polygon

    if is_point_in_polygon(lat, lon, polygon):
        return 0.0

    min_dist = float('inf')
    n = len(polygon)
    for i in range(n):
        p1 = polygon[i]
        p2 = polygon[(i + 1) % n]
        d = distance_point_to_segment(lat, lon, p1[0], p1[1], p2[0], p2[1])
        if d < min_dist:
            min_dist = d
    return round(min_dist, 2)


def is_in_district_or_buffer(
    lat: float,
    lon: float,
    district_name: str,
    buffer_km: float = 60.0
) -> Tuple[bool, float, str]:
    """
    Evaluates whether a point is inside a district or within its ~60 km perimeter buffer.
    Returns:
        (is_within_boundary_or_buffer: bool, distance_km: float, scope_label: str)
    """
    canonical = normalize_location_name(district_name)
    polygon = DISTRICT_BOUNDARIES.get(canonical)
    if not polygon:
        return False, 999999.0, f"No boundary geometry for {district_name}"

    if is_point_in_polygon(lat, lon, polygon):
        return True, 0.0, f"Inside {canonical.title()} District"

    dist = distance_to_district_boundary(lat, lon, polygon)
    if dist <= buffer_km:
        return True, dist, f"District Buffer Corridor ({dist} km from {canonical.title()} border)"
    return False, dist, f"Outside District Buffer ({dist} km from {canonical.title()} border)"
