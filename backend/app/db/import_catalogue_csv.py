"""
CLI entry point to idempotently import the 6,319-row Master Material Catalogue CSV into SQLite.
Usage:
  python -m app.db.import_catalogue_csv
"""

import json
import os
import sys

# Ensure backend directory is on sys.path when executed directly
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.core.database import SessionLocal
from app.services.catalogue_import_service import import_catalogue_csv


def main() -> None:
    db = SessionLocal()
    try:
        report = import_catalogue_csv(db)
        print(json.dumps(report, indent=2))
    finally:
        db.close()


if __name__ == "__main__":
    main()

