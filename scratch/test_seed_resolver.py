import os
import sys

# Test resolving seed path
backend_dir = os.path.abspath("backend")
root_dir = os.path.dirname(backend_dir)
default_db = os.path.join(backend_dir, "architect_ai.db")

def _is_seed_catalogue_path(db_path: str) -> bool:
    try:
        norm = os.path.abspath(db_path).lower()
        seed_norm = os.path.abspath(os.path.join(backend_dir, "seed_catalogue.sqlite")).lower()
        return norm == seed_norm or os.path.basename(norm).lower() == "seed_catalogue.sqlite"
    except Exception:
        return False

def _resolve_seed_path(seed_candidate: str = None) -> str:
    if seed_candidate:
        candidates = [
            seed_candidate,
            os.path.join(backend_dir, seed_candidate),
            os.path.join(backend_dir, os.path.basename(seed_candidate)),
            os.path.join(root_dir, seed_candidate),
        ]
        for c in candidates:
            if os.path.exists(c):
                return os.path.normpath(os.path.abspath(c))
        return os.path.normpath(os.path.abspath(seed_candidate))

    if os.path.exists(default_db):
        return os.path.normpath(os.path.abspath(default_db))

    sanitized = os.path.join(backend_dir, "seed_catalogue.sqlite")
    if os.path.exists(sanitized):
        return os.path.normpath(os.path.abspath(sanitized))

    return os.path.normpath(os.path.abspath(default_db))

print("Testing _resolve_seed_path:")
print("1. None (local):", _resolve_seed_path(None))
print("2. 'backend/seed_catalogue.sqlite':", _resolve_seed_path("backend/seed_catalogue.sqlite"))
print("3. 'seed_catalogue.sqlite':", _resolve_seed_path("seed_catalogue.sqlite"))
print("4. Non-existent candidate:", _resolve_seed_path("missing.db"))
print("5. _is_seed_catalogue_path('backend/seed_catalogue.sqlite'):", _is_seed_catalogue_path("backend/seed_catalogue.sqlite"))
print("6. _is_seed_catalogue_path('seed_catalogue.sqlite'):", _is_seed_catalogue_path("seed_catalogue.sqlite"))
print("7. _is_seed_catalogue_path('other.db'):", _is_seed_catalogue_path("other.db"))

