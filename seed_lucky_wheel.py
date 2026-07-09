"""
Standalone script to seed lucky wheel items using existing weapon/character data.
Does not delete or modify any other data.

Usage:
    python seed_lucky_wheel.py
"""

import httpx

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
    print(f"Authenticated (token: {_auth_token[:20]}...)")


def headers():
    return {"Authorization": f"Bearer {_auth_token}"}


def main():
    authenticate()

    # Fetch existing config data
    weapons = client.get(f"{CONFIG}/weapons", headers=headers()).json()
    characters = client.get(f"{CONFIG}/characters", headers=headers()).json()
    print(f"Found {len(weapons)} weapons, {len(characters)} characters")

    weapon_map = {w["weapon_id"]: w for w in weapons}
    char_map = {c["character_id"]: c for c in characters}
    weapon_ids = sorted(weapon_map.keys())
    character_ids = sorted(char_map.keys())

    # Delete existing wheel items
    existing = client.get(f"{ECONOMY}/lucky-wheel", headers=headers()).json()
    for item in existing:
        client.delete(f"{ECONOMY}/lucky-wheel/{item['id']}", headers=headers())
    print(f"Deleted {len(existing)} existing wheel items")

    items = []

    # ── Gold Wheel (16 slots) ──
    gold_weapons = weapon_ids[:6]
    for i, wid in enumerate(gold_weapons):
        w = weapon_map[wid]
        items.append({
            "wheel_type": "gold", "slot_index": i,
            "item_id": wid, "item_type": "weapon",
            "shop_price": 3000 + i * 500,
            "weight": 80 if i != 2 else 20,
            "display_name": w["name"], "image": w.get("image", ""),
        })
    for i, cid in enumerate(character_ids[:2]):
        c = char_map[cid]
        items.append({
            "wheel_type": "gold", "slot_index": 6 + i,
            "item_id": cid, "item_type": "character",
            "shop_price": 5000,
            "weight": 50,
            "display_name": c["name"], "image": c.get("texture", c.get("avatar_image", "")),
        })
    rare_wid = weapon_ids[7] if len(weapon_ids) > 7 else weapon_ids[-1]
    rw = weapon_map[rare_wid]
    items.append({
        "wheel_type": "gold", "slot_index": 8,
        "item_id": rare_wid, "item_type": "weapon",
        "shop_price": 6000, "weight": 15,
        "display_name": rw["name"], "image": rw.get("image", ""),
    })
    for i, (amount, w) in enumerate(zip(
        [200, 300, 500, 800, 1000, 1500, 2000],
        [200, 180, 150, 120, 100, 80, 50],
    )):
        items.append({
            "wheel_type": "gold", "slot_index": 9 + i,
            "currency_reward": amount, "weight": w,
            "display_name": f"{amount} Gold", "image": "gold.png",
        })

    # ── Diamond Wheel (16 slots) ──
    diamond_weapons = weapon_ids[2:7] if len(weapon_ids) >= 7 else weapon_ids[:5]
    for i, wid in enumerate(diamond_weapons):
        w = weapon_map[wid]
        items.append({
            "wheel_type": "diamond", "slot_index": i,
            "item_id": wid, "item_type": "weapon",
            "shop_price": 100 + i * 30,
            "weight": 80,
            "display_name": w["name"], "image": w.get("image", ""),
        })
    for i, cid in enumerate(character_ids[:4]):
        c = char_map[cid]
        items.append({
            "wheel_type": "diamond", "slot_index": 5 + i,
            "item_id": cid, "item_type": "character",
            "shop_price": 200, "weight": 60,
            "display_name": c["name"], "image": c.get("texture", c.get("avatar_image", "")),
        })
    rare_cid = character_ids[-1]
    rc = char_map[rare_cid]
    items.append({
        "wheel_type": "diamond", "slot_index": 9,
        "item_id": rare_cid, "item_type": "character",
        "shop_price": 300, "weight": 30,
        "display_name": rc["name"], "image": rc.get("texture", rc.get("avatar_image", "")),
    })
    for i, (amount, w) in enumerate(zip(
        [10, 20, 30, 50, 80, 100],
        [200, 180, 150, 120, 80, 50],
    )):
        items.append({
            "wheel_type": "diamond", "slot_index": 10 + i,
            "currency_reward": amount, "weight": w,
            "display_name": f"{amount} Diamond", "image": "diamond.png",
        })

    # Insert all items
    for item in items:
        r = client.post(f"{ECONOMY}/lucky-wheel", json=item, headers=headers())
        if r.status_code >= 400:
            print(f"  ERROR: {r.status_code} - {r.text}")
        r.raise_for_status()

    print(f"Created {len(items)} lucky wheel items (16 gold + 16 diamond)")


if __name__ == "__main__":
    main()
