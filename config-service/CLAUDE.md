# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run dev server
uvicorn main:app --reload --port 8001

# Alembic migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Install dependencies
pip install -r requirements.txt
```

## Architecture

FastAPI microservice providing CRUD APIs for game configuration data (weapons, characters, achievements, level progression, rank config). Targets the `config_db` PostgreSQL database on port 8001. Part of a four-service microservice system (player 8000, config 8001, economy 8002, match 8003) — all share identical architectural patterns.

**Layered request flow:** Router → Service → Repository → DB

- **Routers** (`app/routers/`) — Define endpoints, inject `AsyncSession` via `Depends(get_db)`, instantiate service per request
- **Services** (`app/services/`) — Business logic, raise `HTTPException(404)` on not found, use `model_dump(exclude_unset=True)` for partial updates
- **Repositories** (`app/repositories/`) — SQLAlchemy queries using `select/flush/refresh` pattern (no explicit `commit` — handled by `get_db` session wrapper)
- **Models** (`app/models/`) — SQLAlchemy 2.0 `Mapped`/`mapped_column` style. All models must be imported in `app/models/__init__.py` for Alembic to detect them
- **Schemas** (`app/schemas/`) — Pydantic v2. Each entity has `Create` (all required), `Update` (all optional), `Response` (includes PK, `from_attributes=True`)

**Current entities:** Weapon, Character, Achievement, LevelConfig, RankConfig

**API prefix:** All CRUD routes are mounted under `/api/v1` via `app/api/config.py`.

**DB session lifecycle** (`app/db/session.py`): `get_db()` yields an `AsyncSession` that auto-commits on success and rolls back on exception. Repositories call `flush()` + `refresh()` but never `commit()`.

## Authentication

All routes require a valid JWT Bearer token. The dependency `get_current_player_id` (`app/core/dependencies.py`) decodes the token using `JWT_SECRET_KEY` from settings and extracts the `player_id` claim. Tokens are issued by `player-service` — this service only validates them, it does not create them.

## Key Conventions

- Entry point: `main.py` imports `app` from `app.main` (required for `uvicorn main:app`)
- Config loaded via `pydantic-settings` from `.env` file (`app/core/config.py`); requires `DATABASE_URL` and `JWT_SECRET_KEY` (must match player-service)
- Async PostgreSQL via `asyncpg` — the `async_database_url` property converts `postgresql://` to `postgresql+asyncpg://`
- When adding a new entity: create model, schema, repository, service, router, then register router in `app/api/config.py` and import model in `app/models/__init__.py`
- All PKs use autoincrement integers (e.g., `weapon_id`, `rank_id`)
- After editing migration files, review for unrelated tables detected by autogenerate (e.g., tables from other services sharing the same database) and remove those operations
