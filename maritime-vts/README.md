# Coastal Vessel Traffic Management System (VTS)

> **Before publishing:** add your own project description here. Suggested draft below — feel free to replace it entirely.
>
> *"An autonomous coastal Vessel Traffic Service that fuses AIS, radar, weather-buoy, and port-scheduling data to optimize ship arrivals, prevent collisions, and manage anchorage queues — built for regional ports and small harbor authorities that need enterprise-grade traffic coordination without an enterprise budget."*

---

## Overview

This system implements the core decision-support functions of a coastal Vessel Traffic Service (VTS):

- **Multi-source tracking** — fuses AIS transponder reports with radar tracks into a single vessel picture
- **Collision risk assessment** — real-time Closest Point of Approach (CPA) / Time to CPA (TCPA) calculations
- **Berth prediction** — 72-hour rolling forecast of berth availability from occupancy + schedule + ETA data
- **Anchorage queue management** — priority-scored waiting list for vessels with no assigned berth
- **Pilot assignment** — matches harbor pilots to vessels by license class, availability, and rest-hour rules
- **Tugboat coordination** — assigns tugs to vessel movements by required bollard pull and duty status
- **Tidal window calculation** — harmonic tide model for under-keel clearance and safe transit windows
- **Emergency diversion** — computes nearest safe anchorage/alternate port for distress or diversion events
- **Customs/immigration integration** — validates crew manifests against advance-notice requirements
- **IMO compliance checklist** — rule-based evaluator for pre-arrival regulatory obligations

This is designed as a **decision-support and coordination platform** for a small port authority or harbor
operations team — not a certified navigation, safety-of-life, or regulatory-filing system. See
[`docs/COMPLIANCE.md`](docs/COMPLIANCE.md) for scope and limitations.

## Who this is for

Small to mid-size port authorities, harbor masters' offices, terminal operators, and marine agency
companies that currently coordinate arrivals, pilots, tugs, and berths across spreadsheets, radio,
and email, and want a single operational picture with basic predictive tooling.

## Architecture

```
┌─────────────┐   ┌─────────────┐   ┌──────────────┐   ┌────────────────┐
│  AIS Feed   │   │ Radar Feed  │   │ Weather Buoys│   │ Port Schedule  │
└──────┬──────┘   └──────┬──────┘   └──────┬───────┘   └───────┬────────┘
       │                 │                 │                   │
       └────────┬────────┴─────────────────┴─────────┬─────────┘
                 ▼                                    ▼
        ┌─────────────────┐                 ┌──────────────────┐
        │ Track Fusion &   │                 │  Berth / Pilot /  │
        │ Collision Engine │                 │  Tug / Manifest    │
        │ (CPA/TCPA)       │                 │  Services           │
        └────────┬─────────┘                 └────────┬───────────┘
                 │                                     │
                 └───────────────┬─────────────────────┘
                                 ▼
                        ┌────────────────┐
                        │   FastAPI      │
                        │   REST API     │
                        └────────┬───────┘
                                 ▼
                        Ops dashboard / clients
```

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the full breakdown.

## Tech stack

- **Python 3.11+**, **FastAPI** for the API layer
- **SQLAlchemy** + SQLite (default) / PostgreSQL (production) for persistence
- **Pydantic v2** for data validation
- **pytest** for testing
- **Docker / docker-compose** for local & production deployment

## Project structure

```
maritime-vts/
├── app/
│   ├── main.py                # FastAPI app entrypoint
│   ├── config.py              # Environment-driven settings
│   ├── models/                # Pydantic + ORM data models
│   ├── services/               # Core business logic (one module per capability)
│   ├── api/routes/             # HTTP route handlers
│   ├── db/                     # Database session & seeding
│   └── utils/                  # Geo math, logging helpers
├── data/                       # Realistic sample datasets (JSON)
├── tests/                      # pytest unit tests for core algorithms
├── docs/                       # Architecture, API, deployment, compliance docs
├── scripts/                    # Dev/seed helper scripts
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

## Getting started

### Local (Python)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed_data.py      # loads sample data into the local DB
uvicorn app.main:app --reload
```

API docs (Swagger UI) will be available at `http://localhost:8000/docs`.

### Docker

```bash
docker-compose up --build
```

## Sample data

The `data/` directory contains realistic (fictional) sample data for a mid-size coastal port:
9 vessels across common types (container, bulk carrier, tanker, LNG carrier, RoRo), a live AIS
position feed, 5 weather buoys, 6 berths across 3 terminals, 5 licensed pilots, 4 tugboats, crew
manifests, and a rolling port schedule. `scripts/seed_data.py` loads this into the database so the
API is immediately usable out of the box.

## Testing

```bash
pytest -v
```

Tests cover the core algorithms: tidal height/under-keel clearance, CPA/TCPA collision risk,
berth availability prediction, and pilot assignment rules.

## API overview

Full endpoint reference in [`docs/API.md`](docs/API.md). Highlights:

| Endpoint | Purpose |
|---|---|
| `GET /vessels` | Current vessel picture (fused AIS + radar) |
| `GET /vessels/{mmsi}/collision-risk` | CPA/TCPA risk against nearby traffic |
| `GET /berths/forecast` | 72-hour berth availability forecast |
| `POST /anchorage/queue` | Add a vessel to the anchorage queue |
| `GET /pilots/assign/{mmsi}` | Recommended pilot assignment |
| `GET /tugboats/assign/{mmsi}` | Recommended tug assignment |
| `GET /tides/window` | Safe tidal transit window for a given draft |
| `POST /emergencies/divert` | Compute emergency diversion options |
| `GET /compliance/{mmsi}` | IMO pre-arrival compliance checklist |
| `GET /manifests/{mmsi}` | Crew manifest & customs advance-notice status |

## Roadmap

- [ ] WebSocket live vessel feed for dashboard clients
- [ ] Pluggable AIS decoder for real NMEA 0183 / AIVDM streams
- [ ] PostGIS-backed spatial queries for large port areas
- [ ] Role-based access control (harbor master, pilot, agent, customs)
- [ ] ML-based berth prediction (currently rule/heuristic-based)

## License

MIT — see [`LICENSE`](LICENSE).
