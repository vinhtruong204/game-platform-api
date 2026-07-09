# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Player-service is a FastAPI microservice managing player data (profiles, stats, inventory, achievements, currency, equipment, character selection) for a multiplayer game platform. It is one of several services in the system — others handle matches, economy, and game config (see `../../../docs/db-servives.md`).

## Commands

### Run locally
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Run via Docker
```bash
docker build -t player-service .
docker run -p 8000:8000 player-service
```

### Database migrations (Alembic)
```bash
alembic upgrade head        # apply all migrations
alembic revision --autogenerate -m "description"  # create migration
```

## Architecture

Layered structure under `app/`:

- **`main.py`** (root) — FastAPI app entry point with health check endpoints
- **`app/core/`** — Settings via Pydantic Settings, loaded from `.env`
- **`app/db/`** — SQLAlchemy engine and async session factory
- **`app/models/`** — SQLAlchemy ORM models (one file per table)
- **`app/schemas/`** — Pydantic v2 request/response models
- **`app/repositories/`** — Data access layer (DB queries)
- **`app/services/`** — Business logic
- **`app/routers/`** — FastAPI APIRouter definitions
- **`app/api/`** — Route registrations and endpoint grouping

Request flow: **Router → Service → Repository → Model**

## Database

- **PostgreSQL** database `player_db`, connection string in `.env` as `DATABASE_URL`
- **Alembic** for schema migrations (`alembic/` directory, `alembic.ini`)
- Ten tables: `player_profile`, `player_stats`, `player_currency`, `player_inventory`, `player_equipment`, `player_selected_character`, `player_achievement`, `player_rank`, `player_auth`, `player_session`

## Key Dependencies

- **FastAPI 0.128** + **Uvicorn** — web framework and ASGI server
- **Pydantic v2** + **pydantic-settings** — validation and config
- **SQLAlchemy** — ORM
- **Alembic** — migrations
- **Sentry SDK** — error tracking
- **python-dotenv** — env loading
