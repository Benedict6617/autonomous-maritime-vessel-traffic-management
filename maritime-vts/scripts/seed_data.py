#!/usr/bin/env python3
"""Standalone script to seed/verify the sample dataset. Also runs automatically
on API startup."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.init_db import seed  # noqa: E402

if __name__ == "__main__":
    seed()
    print("Sample data loaded successfully.")
