"""SQLAlchemy engine/session setup, plus lightweight in-memory data stores.

For the core reference/operational entities (vessels, berths, pilots,
tugboats, weather, manifests) this platform uses simple in-process stores
seeded from data/*.json, since a small port's fleet, berth, and staffing
lists change infrequently and don't need full relational modeling to get
a production-quality MVP running. The SQLAlchemy engine is wired up and
ready for teams that want to move these into real tables (see
docs/ARCHITECTURE.md) — swap DataStore for ORM-backed repositories without
changing the service layer or API contracts.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if settings.database_url.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DataStore:
    """A minimal in-memory data store keyed by ID, loaded from JSON at startup."""

    def __init__(self):
        self.vessels: dict[str, dict] = {}
        self.ais_feed: list[dict] = []
        self.weather_buoys: list[dict] = []
        self.berths: dict[str, dict] = {}
        self.pilots: dict[str, dict] = {}
        self.tugboats: dict[str, dict] = {}
        self.manifests: dict[str, dict] = {}
        self.port_schedule: list[dict] = []


store = DataStore()
