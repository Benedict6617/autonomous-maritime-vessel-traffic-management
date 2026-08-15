"""Loads sample JSON data from data/ into the in-memory DataStore."""
import json
from pathlib import Path

from app.db.database import store
from app.utils.logger import get_logger

logger = get_logger(__name__)
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


def _load(filename: str):
    path = DATA_DIR / filename
    with open(path, "r") as f:
        return json.load(f)


def seed():
    store.vessels = {v["mmsi"]: v for v in _load("sample_vessels.json")}
    store.ais_feed = _load("sample_ais_feed.json")
    store.weather_buoys = _load("sample_weather_buoys.json")
    store.berths = {b["berth_id"]: b for b in _load("sample_berths.json")}
    store.pilots = {p["pilot_id"]: p for p in _load("sample_pilots.json")}
    store.tugboats = {t["tug_id"]: t for t in _load("sample_tugboats.json")}
    store.manifests = {m["mmsi"]: m for m in _load("sample_manifests.json")}
    store.port_schedule = _load("sample_port_schedule.json")

    logger.info(
        "Seeded store: %d vessels, %d AIS reports, %d buoys, %d berths, %d pilots, %d tugs, %d manifests, %d schedule entries",
        len(store.vessels),
        len(store.ais_feed),
        len(store.weather_buoys),
        len(store.berths),
        len(store.pilots),
        len(store.tugboats),
        len(store.manifests),
        len(store.port_schedule),
    )


if __name__ == "__main__":
    seed()
