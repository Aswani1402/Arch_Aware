import sys
import os
sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import SessionLocal
from app.models.models import ArchitecturalReference
from app.services.keyword_library import expand_search_query_with_synonyms
from app.services.relevance_service import relevance_service
from sqlalchemy import or_

db = SessionLocal()
search_query = "Different types of bricks for a house"
synonym_phrases = expand_search_query_with_synonyms(search_query)
all_terms = set([w.strip().lower() for w in search_query.split() if len(w.strip()) >= 2])
for syn in synonym_phrases:
    for sw in syn.split():
        if len(sw.strip()) >= 3:
            all_terms.add(sw.strip().lower())

print(f"all_terms: {all_terms}")
word_conditions = []
for w in all_terms:
    w_term = f"%{w}%"
    word_conditions.append(
        or_(
            ArchitecturalReference.title.ilike(w_term),
            ArchitecturalReference.material_tags.ilike(w_term),
            ArchitecturalReference.description.ilike(w_term),
            ArchitecturalReference.location_context.ilike(w_term),
            ArchitecturalReference.country.ilike(w_term),
            ArchitecturalReference.region.ilike(w_term),
            ArchitecturalReference.architectural_style.ilike(w_term),
            ArchitecturalReference.architect_name.ilike(w_term),
            ArchitecturalReference.creator_name.ilike(w_term),
            ArchitecturalReference.search_keyword.ilike(w_term)
        )
    )

query = db.query(ArchitecturalReference).filter(or_(*word_conditions))
print("Querying candidates...")
candidates = query.all()
print(f"Candidates count: {len(candidates)}")

print("Ranking candidates...")
ranked_results = relevance_service.rank_and_filter_feed(
    candidates,
    query=search_query,
    user_interests=None,
    category_slug=None
)
print(f"Ranked results count: {len(ranked_results)}")

db.close()

