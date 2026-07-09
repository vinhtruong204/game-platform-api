# Knockback — Game Platform API

The backend API layer for **[Knockback](https://github.com/vinhtruong204/knockback-godot)**, a networked multiplayer 2D action game. Built as **four independent FastAPI microservices**, each with its own PostgreSQL database. Services are fully decoupled — there are no HTTP calls between them, and each owns its own schema and migrations.

> **Game client:** the Godot 4.6 client that consumes this API lives in **[knockback-godot](https://github.com/vinhtruong204/knockback-godot)**. See [Related Repositories](#related-repositories).

## Services

| Service | Port | Database | Purpose |
|---------|------|----------|---------|
| `player-service` | 8000 | `player_db` | Player profiles, stats, inventory, equipment, achievements, currency, character selection, leaderboard, rank, purchases, lucky-wheel spins, auth/sessions |
| `config-service` | 8001 | `config_db` | Game config: weapons, characters, achievements, level progression, rank config |
| `economy-service` | 8002 | `economy_db` | Shop listings and lucky-wheel slot configuration |
| `match-service` | 8003 | `match_db` | Match history, match players, maps, modes, matchmaking |

## Tech Stack

- **Python 3.11**, **FastAPI 0.128**, **Uvicorn**
- **SQLAlchemy 2.0** (async) + **asyncpg**
- **Pydantic v2** + **pydantic-settings**
- **Alembic** (async migrations)
- **PyJWT**, **httpx**, **Sentry SDK**

## Architecture

Every service follows the same layered request flow:

```
Router → Service → Repository → DB
```

- **`main.py`** (root) — re-exports `app` from `app.main` so `uvicorn main:app` works
- **`app/api/`** — aggregates routers under the `/api/v1` prefix
- **`app/routers/`** — FastAPI endpoints; inject `AsyncSession` via `Depends(get_db)`
- **`app/services/`** — business logic; raise `HTTPException(404)` on not found
- **`app/repositories/`** — async CRUD using `flush()`/`refresh()` (never `commit()`)
- **`app/models/`** — SQLAlchemy 2.0 declarative models (`Mapped`/`mapped_column`)
- **`app/schemas/`** — Pydantic v2 with the `Create`/`Update`/`Response` pattern
- **`app/db/session.py`** — `get_db()` yields an `AsyncSession` with auto-commit/rollback
- **`app/core/config.py`** — loads `.env`; converts `postgresql://` → `postgresql+asyncpg://`

Each service exposes `GET /health` (`{"status": "ok"}`) and `GET /` (service description).

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL (a separate database per service)

### Setup (per service)

Run these from within each service directory (e.g. `cd player-service`):

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment (see below), then apply migrations
alembic upgrade head

# Run the dev server
uvicorn main:app --reload --port 8000   # use 8001/8002/8003 for the others
```

Interactive API docs for each running service are available at `http://localhost:<port>/docs`.

### Environment

Create a `.env` file in each service directory (these are **not** committed):

```env
DATABASE_URL=postgresql://user:password@host:port/database_name
SENTRY_DSN=            # optional, for error tracking
```

`player-service` additionally requires:

```env
GOOGLE_CLIENT_ID=
JWT_SECRET_KEY=
JWT_EXPIRATION_DAYS=
DEV_MODE=true          # enables the dev-login auth provider
```

### Database Migrations

```bash
alembic upgrade head                              # apply all migrations
alembic revision --autogenerate -m "description"  # create a new migration
alembic downgrade -1                              # roll back one migration
```

## Running with Docker

`docker-compose.yml` builds and runs all four services with correct port mappings (8000–8003):

```bash
docker compose up --build
```

Each service reads its config from its own `./<service>/.env` via `env_file`.

## Authentication (player-service)

- Auth providers: **Google OAuth**, **Apple**, **guest**, and **dev** (dev-login is only available when `DEV_MODE=true`).
- Google OAuth is verified via `https://oauth2.googleapis.com/tokeninfo`.
- JWT session tokens are issued with PyJWT; sessions are stored in the `player_session` table.
- Refreshing a session creates a new session and revokes the old one (no in-place renewal).
- Protected routes use `Depends(get_current_player)`, which validates the Bearer token and checks that the session is not revoked.

## Data Seeding

With all four services running on ports 8000–8003:

```bash
python seed_data.py
```

`seed_data.py` seeds all four services over HTTP (using dev-login for auth), deleting existing seed data first in FK-safe order while preserving real players, using a deterministic random seed (42).

Additional **additive/idempotent** seed scripts (run after `seed_data.py`):

- `seed_additional.py` — adds weapons, characters, and shop / lucky-wheel entries (skips existing rows)
- `seed_lucky_wheel.py` — seeds lucky-wheel items from existing weapon/character data
- `seed_missing_data.py` — fills gaps in per-player data without modifying existing rows
- `seed_search_destroy_modes.py` — adds Search & Destroy match modes

## Conventions

- **Adding an entity:** model → schema → repository → service → router, then register the router in `app/api/<service>.py` and import the model in `app/models/__init__.py`.
- **Sessions:** repositories `flush()`/`refresh()` but never `commit()`; `get_db()` commits on success and rolls back on exception.
- **Partial updates:** update schemas make all fields optional; services use `model_dump(exclude_unset=True)`.
- **Enums** (economy/match services): declared as `(str, enum.Enum)`; `sa.Enum` creates the PostgreSQL types in migrations — do not add manual `CREATE TYPE`.
- **Composite primary keys:** repository `get_by_id` takes all key parts; router paths use `/{key1}/{key2}`.

## Project Layout

```
.
├── player-service/     # profiles, stats, inventory, auth, leaderboard, purchases, spins
├── config-service/     # weapons, characters, achievements, level & rank config
├── economy-service/    # shop, lucky-wheel slots
├── match-service/      # matches, players, maps, modes, matchmaking
├── seed_data.py        # primary cross-service seeder
├── seed_*.py           # additional idempotent seeders
└── docker-compose.yml  # runs all four services
```

## Related Repositories

| Repository | Role |
|------------|------|
| **[knockback-godot](https://github.com/vinhtruong204/knockback-godot)** | The **game client** — a Godot 4.6 (Mobile renderer) multiplayer 2D action game that consumes this API for auth, profiles, config, economy, and match data. |
| **game-platform-api** *(this repo)* | The **backend** — four FastAPI microservices on ports 8000–8003. |

The client maps to the services as follows: its `PlayerApi` → `player-service` (8000), `ConfigApi` → `config-service` (8001), `EconomyApi` → `economy-service` (8002), and `MatchApi` → `match-service` (8003). See the client's [README](https://github.com/vinhtruong204/knockback-godot#backend-api) for details.

## Notes

- No CORS middleware is configured.
- No automated test suite or CI/CD pipeline exists yet.
- Sentry is initialized only when `SENTRY_DSN` is set.
