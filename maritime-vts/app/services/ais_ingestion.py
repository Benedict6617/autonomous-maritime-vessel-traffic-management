"""Ingests AIS position reports (from a feed / file / simulated stream).

In production this would decode raw AIVDM/AIVDO NMEA sentences from an AIS
receiver or a provider such as Spire/MarineTraffic. For this platform we
accept pre-decoded JSON reports (see data/sample_ais_feed.json) so the rest
of the pipeline is provider-agnostic.
"""
from datetime import datetime
from typing import Iterable

from app.models.vessel import VesselTrack
from app.utils.logger import get_logger

logger = get_logger(__name__)


def parse_ais_report(raw: dict) -> VesselTrack:
    """Convert a raw decoded AIS JSON record into a VesselTrack."""
    return VesselTrack(
        mmsi=str(raw["mmsi"]),
        source="ais",
        lat=float(raw["lat"]),
        lon=float(raw["lon"]),
        sog_kt=float(raw.get("sog", 0.0)),
        cog_deg=float(raw.get("cog", 0.0)),
        heading_deg=raw.get("heading"),
        nav_status=raw.get("nav_status", "underway_using_engine"),
        timestamp=datetime.fromisoformat(raw["timestamp"]),
    )


def ingest_feed(raw_reports: Iterable[dict]) -> list[VesselTrack]:
    """Parse a batch of raw AIS reports, skipping malformed entries."""
    tracks: list[VesselTrack] = []
    for raw in raw_reports:
        try:
            tracks.append(parse_ais_report(raw))
        except (KeyError, ValueError) as exc:
            logger.warning("Dropping malformed AIS report %s: %s", raw.get("mmsi"), exc)
    logger.info("Ingested %d AIS tracks", len(tracks))
    return tracks
