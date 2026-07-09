# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Start dev server (from match-service root)
uvicorn main:app --reload --port 8003

# Alembic migrations
alembic revision --autogenerate -m "description"
alembic upgrade head
alembic downgrade -1

# Install dependencies (venv already exists at .venv)
.venv\Scripts\pip.exe install -r requirements.txt
```

## Architecture

Async FastAPI service with layered CRUD architecture targeting the `match_db` PostgreSQL database. Mirrors the sibling `player-service` exactly.

**Request flow:** Router → Service → Repository → DB (async SQLAlchemy + asyncpg)

- **`app/api/match.py`** — aggregates all routers under `/api/v1` prefix
- **`app/routers/`** — FastAPI endpoints, injects `AsyncSession` via `Depends(get_db)`
- **`app/services/`** — business logic, raises `HTTPException(404)` when not found
- **`app/repositories/`** — async CRUD using `flush()`/`refresh()` (session commits in `get_db`)
- **`app/schemas/`** — Pydantic v2 with Create/Update/Response pattern; Update schemas use `Optional` fields + `exclude_unset=True`
- **`app/models/`** — SQLAlchemy 2.0 declarative (`Mapped`/`mapped_column`); `__init__.py` declares `Base` and imports all models (required for Alembic detection)
- **`app/db/session.py`** — `get_db()` dependency handles commit/rollback automatically
- **`app/core/config.py`** — `pydantic-settings` reads `.env`; `async_database_url` property converts to `postgresql+asyncpg://`

## Authentication

All endpoints require JWT Bearer token via `Depends(get_current_player_id)` (`app/core/dependencies.py`). This decodes the token using `HS256` + `JWT_SECRET_KEY` and extracts `player_id` (UUID) from the payload. Tokens are issued by `player-service` — this service only validates them.

**Env vars:** `JWT_SECRET_KEY` (required), `DATABASE_URL`, `SENTRY_DSN` (optional).

## Matchmaking System

The matchmaking module (`app/services/matchmaking_service.py`) implements a rank-based queue with dynamic matching:

**Tuning constants:**
- `POINT_RANGE = 500` — initial rank tolerance for candidate matching
- `POINT_RANGE_RELAXED = 1000` — expanded tolerance after 60s wait
- `WAIT_THRESHOLD_SECS = 30` — minimum wait before allowing 2-player (1v1) matches
- `RELAX_THRESHOLD_SECS = 60` — triggers relaxed rank range
- `STALE_TIMEOUT_MINS = 10` — auto-cleanup for abandoned queue entries

**Matching algorithm (in `try_match`):**
1. Player joins queue → `matchmaking_queue` entry with `status=waiting`
2. Find candidates within rank point range (uses `SELECT ... FOR UPDATE` lock)
3. If 4+ candidates → create 2v2 match; if 2+ and anyone waited 30s+ → create 1v1
4. Team assignment alternates high/low rank for balance
5. Stale entries (>10 min) are auto-cleaned on each join

**Queue status flow:** `none` → `queued`/`waiting` → `match_found`/`matched`

**Endpoints** (`/api/v1/matchmaking`):
- `POST /join` — join queue (body: `rank_point`); triggers matching attempt
- `GET /status` — poll queue/match state
- `DELETE /leave` — leave queue

**Error:** `HTTPException(409)` if player already in queue.

## Key Patterns

**Composite primary keys** (`match_player`): uses two `primary_key=True` columns. Repository `get_by_id` takes both keys. Router paths use `/{match_id}/{player_id}`. `player_id` has no FK constraint (references external player-service).

**Enums**: Defined as `(str, enum.Enum)` in model files (`MatchStatus`, `MatchResult`, `QueueStatus`). PostgreSQL types created automatically by `sa.Enum` in Alembic migrations — do NOT add manual `op.execute("CREATE TYPE ...")` as it causes `DuplicateObjectError`. Downgrade needs explicit `DROP TYPE IF EXISTS`.

**Model circular imports**: Forward references (`Mapped["ClassName"]`) for relationships, with bottom-of-file imports to resolve them (e.g., `from app.models.match_history import MatchHistory  # noqa: E402`).

**`datetime` in models**: Must be imported at the top of the file (not as a forward ref) since SQLAlchemy resolves `Mapped[datetime]` at class creation time.

## Database Tables

| Table | PK | FKs |
|-------|-----|-----|
| `map` | `map_id` (auto) | — |
| `mode` | `mode_id` (auto) | — |
| `match_history` | `match_id` (auto) | `map_id` → map, `mode_id` → mode |
| `match_player` | (`match_id`, `player_id`) composite | `match_id` → match_history |
| `matchmaking_queue` | `queue_id` (auto) | `matched_match_id` → match_history; `player_id` UNIQUE |
