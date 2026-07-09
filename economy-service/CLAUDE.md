# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Start dev server
uvicorn main:app --reload --port 8002

# Alembic migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Install dependencies (venv at .venv)
.venv\Scripts\pip.exe install -r requirements.txt
```

## Architecture

Async FastAPI microservice with layered CRUD architecture targeting the `economy_db` PostgreSQL database. Mirrors sibling `player-service` and `match-service`.

**Request flow:** Router → Service → Repository → DB (async SQLAlchemy + asyncpg)

- **`app/api/economy.py`** — aggregates all routers under `/api/v1` prefix
- **`app/routers/`** — FastAPI endpoints, injects `AsyncSession` via `Depends(get_db)`
- **`app/services/`** — business logic, raises `HTTPException(404)` when not found
- **`app/repositories/`** — async CRUD using `flush()`/`refresh()` (session commits in `get_db`)
- **`app/schemas/`** — Pydantic v2 with Create/Update/Response pattern; Update schemas use `Optional` fields + `exclude_unset=True`
- **`app/models/`** — SQLAlchemy 2.0 declarative (`Mapped`/`mapped_column`); `__init__.py` declares `Base` and imports all models (required for Alembic detection)
- **`app/db/session.py`** — `get_db()` dependency handles commit/rollback automatically
- **`app/core/config.py`** — `pydantic-settings` reads `.env`; `async_database_url` property converts to `postgresql+asyncpg://`

## Key Patterns

**Enums**: Defined as `(str, enum.Enum)` in model files (`ItemType`, `CurrencyType`). PostgreSQL enum types created automatically by `sa.Enum` in Alembic migrations — do NOT add manual `op.execute("CREATE TYPE ...")` as it causes `DuplicateObjectError`.

**Cross-DB references**: `item_id` in the `shop` table references weapons/characters in `economy_db` but has no FK constraint since they live in the same database as config tables. Stored as plain `int`.

**Partial updates**: `ShopUpdate` schema makes all fields optional. Service uses `data.model_dump(exclude_unset=True)` so only provided fields are changed.

**Query filters**: `ShopRepository.get_all()` supports optional `item_type`, `currency_type`, and `is_today` filters applied conditionally before pagination.

## Database

| Table | PK | Notes |
|-------|-----|-------|
| `shop` | `shop_id` (auto) | Enum columns: `item_type` (weapon/character), `currency_type` (gold/diamond) |

Other tables in `economy_db` managed by separate services: `achievement`, `character`, `level_config`, `weapon`.
