# Architecture

## Design goals

This platform is scoped for a **single coastal port or harbor authority** managing
tens (not thousands) of vessel movements per day — the traffic density and operational
footprint of a small-to-mid regional port, not a national VTS network. That scope shapes
several deliberate choices below.

## Data flow

1. **Ingestion** — `app/services/ais_ingestion.py` accepts decoded AIS position reports
   (JSON). A real deployment would sit this behind an actual AIS receiver decoder or a
   provider feed (Spire, MarineTraffic, exactEarth); the JSON contract is the seam.
2. **Fusion** — `app/services/radar_processing.py` associates radar returns with AIS
   tracks by nearest-neighbor proximity gating, producing a single fused vessel picture
   including untranspondered small craft.
3. **Risk screening** — `app/services/collision_avoidance.py` runs pairwise CPA/TCPA
   calculations across the fused picture on a rolling basis.
4. **Operational services** — berth forecasting, anchorage queueing, pilot/tug
   assignment, tidal windows, emergency diversion, and compliance checks are independent
   service modules with no cross-dependencies, so any one can be replaced or extended
   without touching the others.
5. **API layer** — FastAPI routes in `app/api/routes/` are thin: they fetch from the
   data store, call a service function, and serialize the result. Business logic lives
   in `app/services/`, not in route handlers, so it's independently testable (see `tests/`).

## Why an in-memory data store instead of full ORM models?

A small port's reference data — its fleet of expected vessels, berths, pilots, and tugs —
changes on the order of days, not seconds. `app/db/database.py` uses a lightweight
in-process `DataStore` seeded from `data/*.json` at startup, which keeps the reference
implementation simple to read, run, and test. The SQLAlchemy engine is already wired up
(`app/db/database.py`) for teams that want to move to persisted, multi-worker-safe
storage — the service layer functions take plain data in and return plain
dataclasses/pydantic models out, so swapping the store for real ORM-backed repositories
doesn't require changing service or route code.

## Known simplifications (and how to extend them)

| Area | Current approach | Production extension path |
|---|---|---|
| AIS decoding | Accepts pre-decoded JSON | Add a NMEA/AIVDM decoder upstream, or subscribe to a provider API |
| Radar fusion | Nearest-neighbor gating | Upgrade to a Kalman filter / JPDA tracker for denser traffic |
| Berth forecast | Deterministic timeline from known schedule | Add a probabilistic ETA model trained on historical AIS arrival data |
| Tidal model | 4-constituent harmonic model, example amplitudes | Replace `DEFAULT_CONSTITUENTS` with your station's published NOAA/hydrographic office table |
| Anchorage queue | Single-process in-memory queue | Move to a shared store (Postgres/Redis) for multi-worker deployments |
| Customs/immigration | Advance-notice timing/completeness check | Integrate with your jurisdiction's single-window filing system (e.g. CBP eNOA/D) |
| Pilot rest-hours | Simplified threshold rule | Replace with your pilotage authority's certified fatigue-management policy |

## Scaling notes

- The collision screening pass is O(n²) across active tracks — fine for the traffic
  density of one VTS sector, but should be spatially partitioned (grid/quadtree) before
  extending to a multi-sector or basin-wide deployment.
- Routes and services are stateless except for the anchorage queue; horizontal scaling
  requires only moving that queue to shared storage (see table above).
