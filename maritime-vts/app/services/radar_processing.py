"""Fuses radar tracks with AIS tracks into a single vessel picture.

Association is done by nearest-neighbor proximity within a configurable
gate distance, which is a standard simplified approach for track-to-track
fusion when a full Kalman/JPDA tracker isn't warranted (e.g. small VTS
coverage areas with light traffic).
"""
from dataclasses import dataclass

from app.models.vessel import VesselTrack
from app.utils.geo import haversine_nm

DEFAULT_ASSOCIATION_GATE_NM = 0.25


@dataclass
class FusedTrack:
    mmsi: str
    lat: float
    lon: float
    sog_kt: float
    cog_deg: float
    sources: list[str]


def fuse_tracks(
    ais_tracks: list[VesselTrack],
    radar_tracks: list[dict],
    gate_nm: float = DEFAULT_ASSOCIATION_GATE_NM,
) -> list[FusedTrack]:
    """Associate unlabeled radar returns with known AIS tracks by proximity.

    Radar tracks that cannot be associated with any AIS track within the
    gate distance are still returned as unidentified fused tracks (mmsi=None
    equivalent handled by caller) — in coastal VTS this commonly represents
    small craft without a transponder, which is operationally significant.
    """
    fused: list[FusedTrack] = []
    unmatched_radar = list(radar_tracks)

    for ais in ais_tracks:
        best_match = None
        best_dist = gate_nm
        for radar in unmatched_radar:
            dist = haversine_nm(ais.lat, ais.lon, radar["lat"], radar["lon"])
            if dist <= best_dist:
                best_dist = dist
                best_match = radar

        sources = ["ais"]
        lat, lon, sog, cog = ais.lat, ais.lon, ais.sog_kt, ais.cog_deg
        if best_match:
            sources.append("radar")
            unmatched_radar.remove(best_match)

        fused.append(
            FusedTrack(mmsi=ais.mmsi, lat=lat, lon=lon, sog_kt=sog, cog_deg=cog, sources=sources)
        )

    for i, radar in enumerate(unmatched_radar):
        fused.append(
            FusedTrack(
                mmsi=f"UNIDENTIFIED-{radar.get('track_id', i)}",
                lat=radar["lat"],
                lon=radar["lon"],
                sog_kt=radar.get("sog", 0.0),
                cog_deg=radar.get("cog", 0.0),
                sources=["radar"],
            )
        )

    return fused
