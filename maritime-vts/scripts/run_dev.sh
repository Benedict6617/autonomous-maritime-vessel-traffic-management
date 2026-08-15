#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."
python scripts/seed_data.py
uvicorn app.main:app --reload
