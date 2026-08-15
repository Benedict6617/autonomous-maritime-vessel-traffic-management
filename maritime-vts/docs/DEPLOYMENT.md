# Deployment

## Local development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/seed_data.py
uvicorn app.main:app --reload
```

## Docker

```bash
docker-compose up --build
```

This builds the image, seeds sample data, and starts the API on port 8000.

## Production considerations

- **Database**: switch `DATABASE_URL` in `.env` to a managed PostgreSQL instance before
  going to production; the SQLAlchemy engine in `app/db/database.py` already supports it.
- **Anchorage queue state**: currently held in-process (see `app/api/routes/anchorage.py`).
  For more than one API worker/replica, move this to Postgres or Redis so all workers see
  the same queue.
- **Secrets**: never commit a populated `.env`; use your platform's secret manager
  (AWS Secrets Manager, Doppler, etc.) in production.
- **AIS/radar feeds**: this reference implementation ingests pre-decoded JSON. Point a
  real decoder (or provider webhook) at `app/services/ais_ingestion.py`'s input contract.
- **Reverse proxy / TLS**: run behind nginx or a managed load balancer with TLS
  termination; do not expose uvicorn directly to the internet.
- **Observability**: `app/utils/logger.py` provides structured logging; wire it to your
  log aggregator (CloudWatch, Datadog, etc.) via the `LOG_LEVEL` env var.

## CI

`.github/workflows/ci.yml` runs the test suite on every push/PR to `main` via GitHub
Actions. Extend it with linting (`ruff`/`black`) and a Docker build/push step as needed.
