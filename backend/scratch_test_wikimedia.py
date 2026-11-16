import asyncio
import httpx
from app.services.image_search_service import image_search_service

QUERIES = [
    "Chettinad traditional architecture",
    "Chettinad courtyard house",
    "Modern tropical houses in Kerala",
    "Exposed brick architecture",
    "Cement and concrete finishes",
    "Drainage and plumbing systems",
    "Bedroom interiors and lighting",
    "Tiles flooring doors windows and facades"
]

async def run_tests():
    print("=== WIKIMEDIA COMMONS API EMPIRICAL RELEVANCE TEST ===")
    for q in QUERIES:
        items = await image_search_service.wikimedia_adapter.search(q, limit=5)
        print(f"\n--- Query: '{q}' | Results: {len(items)} ---")
        for i, item in enumerate(items[:3], 1):
            print(f"[{i}] Title: {item.title}")
            print(f"    Image URL: {item.original_image_url[:85]}...")
            print(f"    Source: {item.source_page_url}")
            print(f"    Attribution: {item.attribution}")
            print(f"    License: {item.usage_license}")
            print(f"    Tags: {', '.join(item.material_tags)}")

if __name__ == "__main__":
    asyncio.run(run_tests())
