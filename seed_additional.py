"""
Additive seed script: adds 10 new weapons + 5 new characters, plus shop entries
and lucky wheel slot replacements. Non-destructive and idempotent — safe to run
repeatedly. Skips any row whose name (weapons/characters) or (item_id, item_type)
(shop) already exists. Wheel slots are only replaced if the target slot still
holds a currency reward (not another item).

Usage:
    pip install httpx
    python seed_additional.py

Expects services running on:
    player-service  -> http://localhost:8000
    config-service  -> http://localhost:8001
    economy-service -> http://localhost:8002
"""

import httpx
from datetime import datetime, timedelta, timezone

PLAYER = "http://localhost:8000/api/v1"
CONFIG = "http://localhost:8001/api/v1"
ECONOMY = "http://localhost:8002/api/v1"

client = httpx.Client(timeout=30, follow_redirects=True)
_auth_token: str | None = None


def authenticate():
    global _auth_token
    r = client.post(f"{PLAYER}/auth/dev-login", json={"name": "SeedBot"})
    r.raise_for_status()
    _auth_token = r.json()["session_token"]
    print(f"  Authenticated (token: {_auth_token[:20]}...)")


def auth_headers() -> dict:
    return {"Authorization": f"Bearer {_auth_token}"}


def post(url: str, data: dict) -> dict:
    r = client.post(url, json=data, headers=auth_headers())
    if r.status_code >= 400:
        print(f"  ERROR {r.status_code} on POST {url}")
        print(f"  Request: {data}")
        print(f"  Response: {r.text}")
    r.raise_for_status()
    return r.json()


def get_list(url: str) -> list:
    r = client.get(url, headers=auth_headers())
    r.raise_for_status()
    return r.json()


def delete(url: str):
    r = client.delete(url, headers=auth_headers())
    if r.status_code not in (204, 200, 404):
        r.raise_for_status()


NEW_WEAPONS = [
    {"name": "Plasma Rifle",    "weapon_type": "primary",   "damage": 42, "fire_rate": 9.0,  "image": "plasma-rifle.png"},
    {"name": "Vortex Carbine",  "weapon_type": "primary",   "damage": 38, "fire_rate": 10.5, "image": "vortex-carbine.png"},
    {"name": "Phoenix Pistol",  "weapon_type": "secondary", "damage": 48, "fire_rate": 5.5,  "image": "phoenix-pistol.png"},
    {"name": "Shadow Revolver", "weapon_type": "secondary", "damage": 65, "fire_rate": 2.8,  "image": "shadow-revolver.png"},
    {"name": "Ion Blaster",     "weapon_type": "secondary", "damage": 40, "fire_rate": 6.5,  "image": "ion-blaster.png"},
    {"name": "Katana",          "weapon_type": "melee",     "damage": 60, "fire_rate": 2.2,  "image": "katana.png"},
    {"name": "Plasma Sword",    "weapon_type": "melee",     "damage": 75, "fire_rate": 1.6,  "image": "plasma-sword.png"},
    {"name": "War Hammer",      "weapon_type": "melee",     "damage": 85, "fire_rate": 1.0,  "image": "war-hammer.png"},
    {"name": "Sticky Bomb",     "weapon_type": "grenade",   "damage": 90, "fire_rate": 0.6,  "image": "sticky-bomb.png"},
    {"name": "Flash Grenade",   "weapon_type": "grenade",   "damage": 45, "fire_rate": 1.0,  "image": "flash-grenade.png"},
]

NEW_CHARACTERS = [
    {"name": "Raven",   "character_type": "recon",   "hp": 85,  "run_speed": 6.0, "texture": "raven.png"},
    {"name": "Onyx",    "character_type": "assault", "hp": 110, "run_speed": 5.2, "texture": "onyx.png"},
    {"name": "Ember",   "character_type": "assault", "hp": 95,  "run_speed": 5.8, "texture": "ember.png"},
    {"name": "Crimson", "character_type": "tank",    "hp": 160, "run_speed": 3.8, "texture": "crimson.png"},
    {"name": "Mystic",  "character_type": "support", "hp": 100, "run_speed": 4.9, "texture": "mystic.png"},
]


def seed_weapons_additional() -> dict[str, int]:
    existing = {w["name"]: w["weapon_id"] for w in get_list(f"{CONFIG}/weapons")}
    result: dict[str, int] = {}
    added = 0
    for w in NEW_WEAPONS:
        if w["name"] in existing:
            result[w["name"]] = existing[w["name"]]
            continue
        created = post(f"{CONFIG}/weapons", w)
        result[w["name"]] = created["weapon_id"]
        added += 1
    print(f"  Weapons: added {added}, skipped {len(NEW_WEAPONS) - added} (already present)")
    return result


def seed_characters_additional() -> dict[str, int]:
    existing = {c["name"]: c["character_id"] for c in get_list(f"{CONFIG}/characters")}
    result: dict[str, int] = {}
    added = 0
    for c in NEW_CHARACTERS:
        if c["name"] in existing:
            result[c["name"]] = existing[c["name"]]
            continue
        created = post(f"{CONFIG}/characters", c)
        result[c["name"]] = created["character_id"]
        added += 1
    print(f"  Characters: added {added}, skipped {len(NEW_CHARACTERS) - added} (already present)")
    return result


def seed_shop_additional(weapon_ids: dict[str, int], character_ids: dict[str, int]):
    now = datetime.now(timezone.utc)
    plan = [
        {"name": "Plasma Rifle",   "kind": "weapon",    "price": 4000, "currency": "gold",    "discount": 0.0,  "is_today": True,  "days": 7},
        {"name": "Phoenix Pistol", "kind": "weapon",    "price": 3500, "currency": "gold",    "discount": 0.1,  "is_today": True,  "days": 7},
        {"name": "Katana",         "kind": "weapon",    "price": 120,  "currency": "diamond", "discount": 0.0,  "is_today": False, "days": 14},
        {"name": "Plasma Sword",   "kind": "weapon",    "price": 180,  "currency": "diamond", "discount": 0.0,  "is_today": True,  "days": 7},
        {"name": "Sticky Bomb",    "kind": "weapon",    "price": 5500, "currency": "gold",    "discount": 0.15, "is_today": True,  "days": 5},
        {"name": "Onyx",           "kind": "character", "price": 250,  "currency": "diamond", "discount": 0.0,  "is_today": True,  "days": 7},
        {"name": "Crimson",        "kind": "character", "price": 320,  "currency": "diamond", "discount": 0.1,  "is_today": False, "days": 14},
    ]
    existing_keys = {(s["item_id"], s["item_type"]) for s in get_list(f"{ECONOMY}/shops")}
    added = 0
    for entry in plan:
        ids = weapon_ids if entry["kind"] == "weapon" else character_ids
        item_id = ids.get(entry["name"])
        if item_id is None:
            print(f"  WARN: could not resolve {entry['kind']} '{entry['name']}' — skipping shop entry")
            continue
        if (item_id, entry["kind"]) in existing_keys:
            continue
        payload = {
            "item_id": item_id,
            "item_type": entry["kind"],
            "price": entry["price"],
            "currency_type": entry["currency"],
            "discount": entry["discount"],
            "is_today": entry["is_today"],
            "start_at": now.isoformat(),
            "end_at": (now + timedelta(days=entry["days"])).isoformat(),
        }
        post(f"{ECONOMY}/shops", payload)
        added += 1
    print(f"  Shop: added {added}, skipped {len(plan) - added} (already present or unresolved)")


def seed_wheel_replacements(weapon_ids: dict[str, int], character_ids: dict[str, int]):
    replacements = [
        # (wheel_type, slot_index, kind, name, shop_price, weight)
        ("gold",    14, "weapon",    "Vortex Carbine",  3500, 60),
        ("gold",    15, "character", "Raven",           6000, 30),
        ("diamond", 14, "weapon",    "Shadow Revolver", 150,  50),
        ("diamond", 15, "character", "Ember",           250,  30),
    ]
    wheel = get_list(f"{ECONOMY}/lucky-wheel")
    by_slot = {(row["wheel_type"], row["slot_index"]): row for row in wheel}

    added = 0
    skipped = 0
    for wheel_type, slot_index, kind, name, shop_price, weight in replacements:
        current = by_slot.get((wheel_type, slot_index))
        if current is None:
            print(f"  WARN: wheel slot {wheel_type}/{slot_index} not found — skipping")
            continue

        ids = weapon_ids if kind == "weapon" else character_ids
        item_id = ids.get(name)
        if item_id is None:
            print(f"  WARN: could not resolve {kind} '{name}' — skipping wheel slot")
            continue

        # Already replaced on a previous run? Skip.
        if current.get("item_id") == item_id and current.get("item_type") == kind:
            skipped += 1
            continue

        # Guard: only replace if current slot is still a currency reward
        # (item_id is NULL). Never clobber a slot that already holds an item.
        if current.get("item_id") is not None:
            print(f"  WARN: wheel slot {wheel_type}/{slot_index} already holds an item "
                  f"(id={current.get('item_id')}, type={current.get('item_type')}) — skipping")
            continue

        # Determine display_name + image for the new item
        if kind == "weapon":
            details = next((w for w in NEW_WEAPONS if w["name"] == name), None)
            image = details["image"] if details else ""
        else:
            details = next((c for c in NEW_CHARACTERS if c["name"] == name), None)
            image = details["texture"] if details else ""

        delete(f"{ECONOMY}/lucky-wheel/{current['id']}")
        payload = {
            "wheel_type": wheel_type,
            "slot_index": slot_index,
            "item_id": item_id,
            "item_type": kind,
            "shop_price": shop_price,
            "weight": weight,
            "display_name": name,
            "image": image,
        }
        post(f"{ECONOMY}/lucky-wheel", payload)
        added += 1

    print(f"  Wheel: replaced {added}, skipped {skipped} (already replaced)")


def main():
    print("=" * 60)
    print("ADDITIVE SEED (non-destructive)")
    print("=" * 60)

    print("\nAuthenticating...")
    authenticate()

    print("\nPhase 1: Weapons")
    weapon_ids = seed_weapons_additional()

    print("\nPhase 2: Characters")
    character_ids = seed_characters_additional()

    print("\nPhase 3: Shop")
    seed_shop_additional(weapon_ids, character_ids)

    print("\nPhase 4: Lucky wheel replacements")
    seed_wheel_replacements(weapon_ids, character_ids)

    print("\n" + "=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()
