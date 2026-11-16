import sys
sys.path.insert(0, 'backend')
from app.services.keyword_library import expand_search_query_with_synonyms, SYNONYM_MAP

terms = [
    'fly ash brick',
    'hollow concrete block',
    'concrete hollow block',
    'marble flooring',
    'italian marble flooring',
    'laterite stone',
    'laterite block',
]

for t in terms:
    syns = expand_search_query_with_synonyms(t)
    print(f"Term: '{t}' -> Synonyms: {syns}")

print("\nDirect matches in SYNONYM_MAP:")
for k in list(SYNONYM_MAP.keys())[:20]:
    if any(x in k for x in ['brick', 'block', 'marble', 'stone', 'laterite', 'floor']):
        print(f"  {k} -> {SYNONYM_MAP[k]}")

