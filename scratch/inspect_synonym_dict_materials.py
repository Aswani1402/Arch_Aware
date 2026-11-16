import sys
sys.path.insert(0, 'backend')
from app.services.keyword_library import SYNONYM_DICT, expand_search_query_with_synonyms

test_queries = [
    "Fly ash brick",
    "Hollow concrete block",
    "Marble flooring",
    "Laterite stone"
]

for q in test_queries:
    exp = expand_search_query_with_synonyms(q)
    print(f"\nQuery: '{q}'")
    print(f"  Expanded: {exp}")
    words = [w.lower() for w in q.split()]
    for w in words:
        if w in SYNONYM_DICT:
            print(f"  Word in SYNONYM_DICT: '{w}' -> {SYNONYM_DICT[w][:5]}")

print("\nAll keys in SYNONYM_DICT matching brick, block, marble, laterite, stone:")
for k in SYNONYM_DICT:
    if any(x in k for x in ['brick', 'block', 'marble', 'laterite', 'stone', 'floor']):
        print(f"  {k}: {SYNONYM_DICT[k][:3]}")

