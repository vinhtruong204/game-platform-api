# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the API layer of a multiplayer game platform, structured as four independent FastAPI microservices, each with its own PostgreSQL database:

| Service | Port | Database | Purpose |
|---------|------|----------|---------|
| `player-service` | 8000 | `player_db` | Player profiles, stats, inventory, equipment, achievements, currency, character selection, leaderboard, rank, purchases, lucky-wheel spins, auth/sessions |
| `config-service` | 8001 | `config_db` | Game config: weapons, characters, achievements, level progression, rank config |
| `economy-service` | 8002 | `economy_db` | Shop listings and lucky wheel slot configuration |
| `match-service` | 8003 | `match_db` | Match history, match players, maps, modes, matchmaking |

Each service is self-contained with its own `.env`, `requirements.txt`, Alembic migrations, Dockerfile, virtual environment (`.venv`), and per-service `CLAUDE.md`.

## Commands

All commands must be run from within a specific service directory (e.g., `cd player-service`).

```bash
# Run dev server
uvicorn main:app --reload --port 8000   # player-service
uvicorn main:app --reload --port 8001   # config-service
uvicorn main:app --reload --port 8002   # economy-service
uvicorn main:app --reload --port 8003   # match-service

# Database migrations
alembic upgrade head                              # apply all migrations
alembic revision --autogenerate -m "description"  # create new migration
alembic downgrade -1                              # rollback one migration

# Install dependencies
pip install -r requirements.txt

# Docker
docker build -t <service-name> .
docker run -p <port>:<port> <service-name>
```

## Architecture

All four services follow identical layered architecture:

**Request flow:** Router → Service → Repository → DB

- **`main.py`** (root) — imports `app` from `app.main` (required for `uvicorn main:app`)
- **`app/api/`** — aggregates routers under `/api/v1` prefix
- **`app/routers/`** — FastAPI endpoints, injects `AsyncSession` via `Depends(get_db)`
- **`app/services/`** — business logic, raises `HTTPException(404)` on not found
- **`app/repositories/`** — async CRUD queries using `flush()`/`refresh()` (never `commit()`)
- **`app/models/`** — SQLAlchemy 2.0 declarative (`Mapped`/`mapped_column`)
- **`app/schemas/`** — Pydantic v2 with `Create`/`Update`/`Response` pattern
- **`app/db/session.py`** — `get_db()` yields `AsyncSession` with auto-commit/rollback
- **`app/core/config.py`** — `pydantic-settings` loads `.env`; `async_database_url` property converts `postgresql://` to `postgresql+asyncpg://`

## Key Conventions

**Adding a new entity:** Create model → schema → repository → service → router, then register the router in `app/api/<service>.py` and import the model in `app/models/__init__.py`.

**Session management:** Repositories call `flush()` + `refresh()` but never `commit()`. The `get_db()` dependency handles commit on success and rollback on exception.

**Partial updates:** Update schemas make all fields optional. Services use `data.model_dump(exclude_unset=True)` so only provided fields are changed.

**Enums** (economy-service, match-service): Defined as `(str, enum.Enum)`. PostgreSQL enum types are created automatically by `sa.Enum` in Alembic migrations — do NOT add manual `op.execute("CREATE TYPE ...")` as it causes `DuplicateObjectError`.

**Composite primary keys** (player-service stats/currency/inventory/equipment, match-service `match_player`): Uses multiple `primary_key=True` columns. Repository `get_by_id` takes all key parts. Router paths use `/{key1}/{key2}` etc.

**Model circular imports:** Use forward references (`Mapped["ClassName"]`) for relationships with bottom-of-file imports to resolve them. `datetime` must be imported at the top of the file (not as a forward ref).

**Alembic autogenerate caveat:** Review generated migrations for unrelated tables from other services sharing the same database and remove those operations.

## Authentication (player-service only)

- Auth providers: Google OAuth, Apple, guest, and dev (dev-login only available when `DEV_MODE=true`)
- Google OAuth via `httpx.AsyncClient` calling `https://oauth2.googleapis.com/tokeninfo`
- JWT session tokens created via `PyJWT`; sessions stored in `player_session` table
- Session refresh creates a new session and revokes the old one (no in-place renewal)
- Protected routes use `Depends(get_current_player)` from `app/core/dependencies.py` which validates the Bearer token and checks the session is not revoked
- Additional env vars: `GOOGLE_CLIENT_ID`, `JWT_SECRET_KEY`, `JWT_EXPIRATION_DAYS`, `DEV_MODE`

## Inter-Service Communication

Services are fully decoupled — no HTTP calls between them. Each service manages its own database with no cross-DB references. The only external HTTP call is player-service → Google OAuth API.

## Data Seeding

`seed_data.py` (repo root) seeds all four services via HTTP using `httpx`. Run it with all four services running on their respective ports (8000–8003):

```bash
python seed_data.py
```

It uses dev-login (`/api/v1/auth/dev-login`) to obtain a session token, deletes existing seed data first (respecting FK order, preserves real players), then creates records across all services using deterministic random seed (42).

Additional standalone seed scripts at repo root are **additive/idempotent** (do not delete existing data) and are intended to be run after `seed_data.py`:

- `seed_additional.py` — adds 10 weapons + 5 characters, plus shop/lucky-wheel entries (skips existing rows)
- `seed_lucky_wheel.py` — seeds lucky wheel items from existing weapon/character data
- `seed_missing_data.py` — fills gaps in per-player data (stats/currency/inventory/etc.) without modifying existing rows
- `seed_search_destroy_modes.py` — adds Search & Destroy match modes

## Database Engine

`app/db/engine.py` configures `create_async_engine` with pool size 20, max overflow 10, echo disabled. Alembic migrations use `NullPool`.

## Environment

Each service needs a `.env` file with:
- `DATABASE_URL=postgresql://user:password@host:port/database_name`
- `SENTRY_DSN` (optional, for error tracking)
- player-service additionally needs: `GOOGLE_CLIENT_ID`, `JWT_SECRET_KEY`, `JWT_EXPIRATION_DAYS`, `DEV_MODE`

## Other Notes

- Each service exposes `/health` (returns `{"status": "ok"}`) and `/` (service description)
- No CORS middleware configured
- No test suite or CI/CD pipeline exists
- `docker-compose.yml` at repo root builds and runs all four services with correct port mappings
- Each Dockerfile hardcodes its correct port in CMD (8000–8003 respectively)
- Sentry is conditionally initialized only when `SENTRY_DSN` is set

## Tech Stack

- Python 3.11, FastAPI 0.128, Uvicorn
- SQLAlchemy 2.0 (async) + asyncpg
- Pydantic v2 + pydantic-settings
- Alembic (async migrations)
- Sentry SDK, PyJWT, httpx
