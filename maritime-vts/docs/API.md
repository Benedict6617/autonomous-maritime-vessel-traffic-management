# API Reference

Interactive Swagger UI is available at `/docs` once the server is running
(`http://localhost:8000/docs`). This document summarizes the endpoints by capability.

## Health

- `GET /` — service status and configured port name
- `GET /health` — liveness check

## Vessels & tracking

- `GET /vessels` — all known vessels (static particulars)
- `GET /vessels/{mmsi}` — a single vessel's particulars
- `GET /vessels/track/current` — current fused AIS position picture
- `GET /vessels/{mmsi}/collision-risk` — CPA/TCPA risk for one vessel against nearby traffic

## Berths

- `GET /berths` — all berths and current occupancy
- `GET /berths/{berth_id}` — a single berth
- `GET /berths/forecast` — 72-hour availability forecast, all berths

## Weather

- `GET /weather/buoys` — latest readings from all weather buoys

## Anchorage queue

- `POST /anchorage/queue` — add a vessel to the anchorage queue (`{mmsi, loa_m, cargo_category, is_emergency}`)
- `DELETE /anchorage/queue/{mmsi}` — remove a vessel from the queue
- `GET /anchorage/queue` — current queue, ordered by priority

## Pilots

- `GET /pilots` — all pilots and duty/rest status
- `GET /pilots/assign/{mmsi}` — recommended pilot for a given vessel

## Tugboats

- `GET /tugboats` — all tugboats and status
- `GET /tugboats/assign/{mmsi}` — recommended tug assignment for a given vessel

## Tides

- `GET /tides/height?at=<ISO8601>` — predicted tide height at a given time (defaults to now)
- `GET /tides/window?charted_depth_m=&vessel_draft_m=&min_required_ukc_m=&search_hours=` —
  safe transit windows over the forecast horizon

## Emergencies

- `POST /emergencies/divert` — compute diversion options and notification list
  (`{mmsi, severity, lat, lon}`)

## Manifests / customs

- `GET /manifests` — all crew manifests
- `GET /manifests/{mmsi}` — advance-notice and clearance compliance check for one vessel

## IMO compliance

- `GET /compliance/{mmsi}` — pre-arrival regulatory checklist status
