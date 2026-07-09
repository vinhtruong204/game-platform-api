# Player Service - Implementation Plan

## Status: IMPLEMENTED

All 7 tables with full CRUD APIs are implemented and ready.

## Architecture

```
Request → Router → Service → Repository → Model (SQLAlchemy) → PostgreSQL
```

## Tables (7)

| Table | PK | Endpoints |
|-------|-----|-----------|
| player_profile | player_id (auto-inc) | `/api/v1/players/` |
| player_stats | (player_id, mode) | `/api/v1/player-stats/` |
| player_currency | (player_id, currency_type) | `/api/v1/player-currencies/` |
| player_inventory | (player_id, item_id, item_type) | `/api/v1/player-inventory/` |
| player_equipment | (player_id, slot_type) | `/api/v1/player-equipment/` |
| player_selected_character | player_id (1:1) | `/api/v1/player-selected-characters/` |
| player_achievement | (player_id, achievement_id) | `/api/v1/player-achievements/` |

## Enums

- `GameMode`: normal, rank
- `CurrencyType`: gold, diamond
- `ItemType`: weapon, character
- `SlotType`: primary, secondary, melee, grenade, character

## Running

```bash
# Install deps
pip install -r requirements.txt

# Apply migration (requires running PostgreSQL)
alembic upgrade head

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Swagger docs at http://localhost:8000/docs
```
