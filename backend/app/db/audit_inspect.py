import sys
import os
sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from app.services.socialcrawl_service import ARCHITECTURAL_CATEGORIES
from app.services.keyword_library import (
    MASTER_KEYWORD_CATEGORIES,
    CONTENT_CLASSIFICATIONS,
    SEARCH_EXPANSION_DIMENSIONS,
    INSTAGRAM_DISCOVERY_INTENTS,
    SOURCE_SPECIFIC_QUERY_TEMPLATES,
    FILTER_METADATA_GROUPS,
    STOCK_INVENTORY_SPECS,
    SYNONYM_DICT,
    search_keyword_library,
    expand_search_query_with_synonyms
)

print(f"Count of SocialCrawl ARCHITECTURAL_CATEGORIES: {len(ARCHITECTURAL_CATEGORIES)}")
for idx, c in enumerate(ARCHITECTURAL_CATEGORIES, 1):
    print(f"  {idx:2d}. {c['id']}: {c['name']} (domain: {c.get('domain')})")

print("\n" + "=" * 60)
print(f"Count of Metadata CONTENT_CLASSIFICATIONS: {len(CONTENT_CLASSIFICATIONS)}")
for idx, c in enumerate(CONTENT_CLASSIFICATIONS, 1):
    print(f"  {idx:2d}. {c['code']}: {c['name']} - {c.get('description', '')}")
