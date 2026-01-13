...existing code...
# Webhook Ingestion System

Production-style FastAPI backend for a webhook ingestion system.

## Overview

This project provides a small FastAPI service that ingests webhook payloads and persists them to SQLite. It exposes endpoints to ingest webhooks, list stored messages, and retrieve basic stats.

Key components:
- [`app.main`](main.py) — application entrypoints and HTTP handlers.
- [`app.storage.Storage`](app/storage.py) — persistence helpers for messages.
- [`app.models.init_db`](app/models.py) — SQLAlchemy models and DB initialization.
- [`app.db.get_db`](app/db.py) — DB engine and session management.
- [`app.schemas.WebhookPayload`](app/schemas.py) — strict Pydantic schema used for payload validation (where applicable).
- Config provided by [`app.core.config.Settings`](app/core/config.py).

See the files:
- [main.py](main.py)
- [app/storage.py](app/storage.py)
- [app/models.py](app/models.py)
- [app/db.py](app/db.py)
- [app/schemas.py](app/schemas.py)
- [app/core/config.py](app/core/config.py)
- [Dockerfile](Dockerfile)
- [docker-compose.yml](docker-compose.yml)
- [Makefile](Makefile)

## Requirements

- Python 3.11
- pip
- (Optional) Docker & docker-compose

## Quick start — local (virtualenv)

1. Create and activate a virtual environment:
```sh
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:
```sh
pip install -r requirements.txt
```

3. Initialize the database and run the app:
```sh
# Create DB directory and start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# Or use the Makefile:
make run
```

4. Open the API docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Notes:
- DB initialization is handled by [`app.models.init_db`](app/models.py) on application startup.
- The DB engine and sessions are provided by [`app.db`](app/db.py).

## Using Docker

Build and run the image:
```sh
docker build -t webhook-ingestor .
docker run -p 8000:8000 --env-file .env webhook-ingestor
```

Using docker-compose:
```sh
docker-compose up --build
```
The provided [docker-compose.yml](docker-compose.yml) maps port 8000 and mounts a host SQLite file.

## Environment variables

Configuration is read from [`app.core.config.Settings`](app/core/config.py). By default it uses an on-disk SQLite DB.

If you need to override DB location, set the env var used by the config. (See [`app/core/config.py`](app/core/config.py) and [`app/db.py`](app/db.py) for how the DB path/URL is constructed.)

## API (brief)

- POST /webhook
  - Ingest a webhook payload (expects at least `message_id` and `sender` keys in the JSON body).
  - Example:
    ```sh
    curl -X POST http://localhost:8000/webhook \
      -H "Content-Type: application/json" \
      -d '{"message_id":"msg-1","sender":"+1234567890","text":"hello"}'
    ```

- GET /messages
  - List stored messages. Query params: `sender`, `q`, `limit`, `offset`.

- GET /stats
  - Basic statistics (total messages and per-sender counts).

The handlers are implemented in [`main.py`](main.py).

## Tests

Run the test suite (if present):
```sh
make test
# or
pytest
```

## Notes for developers

- Persistence is implemented with SQLAlchemy models in [`app.models`](app/models.py) and sessions in [`app.db`](app/db.py).
- The ingestion endpoint in [`main.py`](main.py) currently performs a simple payload presence check; the stricter Pydantic model is available in [`app.schemas.WebhookPayload`](app/schemas.py) for validation.
- If you plan to run multiple writers/readers concurrently against SQLite, review the PRAGMA settings in [`app.db`](app/db.py).

## License

MIT
