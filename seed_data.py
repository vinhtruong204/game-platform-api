"""
Seed script for all 4 microservices.
Deletes existing data (FK-safe order), then inserts ~221 test records.

Usage:
    pip install httpx
    python seed_data.py

Expects services running on:
    player-service  -> http://localhost:8000
    config-service  -> http://localhost:8001
    economy-service -> http://localhost:8002
    match-service   -> http://localhost:8003
"""

import httpx
import random
from datetime import datetime, timedelta, timezone

PLAYER = "http://localhost:8000/api/v1"
CONFIG = "http://localhost:8001/api/v1"
ECONOMY = "http://localhost:8002/api/v1"
MATCH = "http://localhost:8003/api/v1"

client = httpx.Client(timeout=30, follow_redirects=True)

_auth_token: str | None = None

SEED_PLAYER_NAMES = [
    "SeedBot", "DragonSlayer99", "NightOwl", "PixelWarrior", "SilentStorm",
    "BlazeMaster", "IcePhoenix", "ThunderBolt", "CyberNinja",
    "GhostRider", "SteelWolf",
]


def authenticate():
    global _auth_token
    r = client.post(f"{PLAYER}/auth/dev-login", json={"name": "SeedBot"})
    r.raise_for_status()
    _auth_token = r.json()["session_token"]
    print(f"  Authenticated as SeedBot (token: {_auth_token[:20]}...)")


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


def put(url: str, data: dict) -> dict:
    r = client.put(url, json=data, headers=auth_headers())
    if r.status_code >= 400:
        print(f"  ERROR {r.status_code} on PUT {url}")
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


# ── Phase 0: Delete existing data ──────────────────────────────────────────

def delete_all():
    print("Deleting existing data...")

    # Identify seed players (skip real users like Google/Apple sign-ins)
    all_players = get_list(f"{PLAYER}/players")
    seed_players = [p for p in all_players if p["name"] in SEED_PLAYER_NAMES]
    seed_player_ids = {p["player_id"] for p in seed_players}
    print(f"  Found {len(seed_players)} seed players to delete (preserving {len(all_players) - len(seed_players)} real players)")

    # player-service children — only delete sub-entities belonging to seed players
    for a in get_list(f"{PLAYER}/player-achievements"):
        if a["player_id"] in seed_player_ids:
            delete(f"{PLAYER}/player-achievements/{a['player_id']}/{a['achievement_id']}")
    for sc in get_list(f"{PLAYER}/player-selected-characters"):
        if sc["player_id"] in seed_player_ids:
            delete(f"{PLAYER}/player-selected-characters/{sc['player_id']}")
    for eq in get_list(f"{PLAYER}/player-equipment"):
        if eq["player_id"] in seed_player_ids:
            delete(f"{PLAYER}/player-equipment/{eq['player_id']}/{eq['slot_type']}")
    for inv in get_list(f"{PLAYER}/player-inventory"):
        if inv["player_id"] in seed_player_ids:
            delete(f"{PLAYER}/player-inventory/{inv['player_id']}/{inv['item_id']}/{inv['item_type']}")
    for c in get_list(f"{PLAYER}/player-currencies"):
        if c["player_id"] in seed_player_ids:
            delete(f"{PLAYER}/player-currencies/{c['player_id']}/{c['currency_type']}")
    for s in get_list(f"{PLAYER}/player-stats"):
        if s["player_id"] in seed_player_ids:
            delete(f"{PLAYER}/player-stats/{s['player_id']}/{s['mode']}")
    for p in seed_players:
        delete(f"{PLAYER}/players/{p['player_id']}")

    # match-service history/config. Modes are preserved and upserted by seed_modes().
    for mp in get_list(f"{MATCH}/match-players"):
        delete(f"{MATCH}/match-players/{mp['match_id']}/{mp['player_id']}")
    for m in get_list(f"{MATCH}/matches"):
        delete(f"{MATCH}/matches/{m['match_id']}")
    for ma in get_list(f"{MATCH}/maps"):
        delete(f"{MATCH}/maps/{ma['map_id']}")
    # economy-service
    for sh in get_list(f"{ECONOMY}/shops"):
        delete(f"{ECONOMY}/shops/{sh['shop_id']}")

    # config-service
    for w in get_list(f"{CONFIG}/weapons"):
        delete(f"{CONFIG}/weapons/{w['weapon_id']}")
    for ch in get_list(f"{CONFIG}/characters"):
        delete(f"{CONFIG}/characters/{ch['character_id']}")
    for ac in get_list(f"{CONFIG}/achievements"):
        delete(f"{CONFIG}/achievements/{ac['achievement_id']}")
    for lc in get_list(f"{CONFIG}/level-configs"):
        delete(f"{CONFIG}/level-configs/{lc['level_id']}")

    print("All seed data deleted.\n")


# ── Phase 1: Config data ───────────────────────────────────────────────────

def seed_weapons() -> list[dict]:
    weapons_data = [
        {"name": "AK-47", "weapon_type": "assault_rifle", "damage": 36, "fire_rate": 10.0, "ammo": 30},
        {"name": "M4A1", "weapon_type": "assault_rifle", "damage": 33, "fire_rate": 11.0, "ammo": 30},
        {"name": "AWP", "weapon_type": "sniper", "damage": 115, "fire_rate": 1.5, "ammo": 5},
        {"name": "Desert Eagle", "weapon_type": "pistol", "damage": 53, "fire_rate": 4.0, "ammo": 12},
        {"name": "P90", "weapon_type": "smg", "damage": 26, "fire_rate": 15.0, "ammo": 50},
        {"name": "Shotgun XM1014", "weapon_type": "shotgun", "damage": 80, "fire_rate": 3.0, "ammo": 8},
        {"name": "MP5", "weapon_type": "smg", "damage": 27, "fire_rate": 13.0, "ammo": 50},
        {"name": "SCAR-L", "weapon_type": "assault_rifle", "damage": 35, "fire_rate": 9.5, "ammo": 30},
        {"name": "Combat Knife", "weapon_type": "melee", "damage": 55, "fire_rate": 2.0, "ammo": 0},
        {"name": "Frag Grenade", "weapon_type": "grenade", "damage": 98, "fire_rate": 0.5, "ammo": 0},
    ]
    results = []
    for w in weapons_data:
        results.append(post(f"{CONFIG}/weapons", w))
    print(f"  Created {len(results)} weapons")
    return results


def seed_characters() -> list[dict]:
    characters_data = [
        {"name": "Shadow", "character_type": "assault", "hp": 100, "run_speed": 5.5, "avatar_image": "shadow.png"},
        {"name": "Blaze", "character_type": "tank", "hp": 150, "run_speed": 4.0, "avatar_image": "blaze.png"},
        {"name": "Phantom", "character_type": "recon", "hp": 80, "run_speed": 6.5, "avatar_image": "phantom.png"},
        {"name": "Viper", "character_type": "support", "hp": 90, "run_speed": 5.0, "avatar_image": "viper.png"},
        {"name": "Titan", "character_type": "tank", "hp": 180, "run_speed": 3.5, "avatar_image": "titan.png"},
    ]
    results = []
    for c in characters_data:
        results.append(post(f"{CONFIG}/characters", c))
    print(f"  Created {len(results)} characters")
    return results


def seed_achievements() -> list[dict]:
    achievements_data = [
        {"name": "First Blood", "image": "first_blood.png", "requirement": "Get the first kill in a match"},
        {"name": "Sharpshooter", "image": "sharpshooter.png", "requirement": "Get 100 headshots"},
        {"name": "Survivor", "image": "survivor.png", "requirement": "Win 50 matches"},
        {"name": "Veteran", "image": "veteran.png", "requirement": "Play 200 matches"},
        {"name": "Collector", "image": "collector.png", "requirement": "Own 10 different weapons"},
    ]
    results = []
    for a in achievements_data:
        results.append(post(f"{CONFIG}/achievements", a))
    print(f"  Created {len(results)} achievements")
    return results


def seed_level_configs() -> list[dict]:
    results = []
    for i in range(10):
        lc = {
            "min_exp": i * 1000,
            "max_exp": (i + 1) * 1000,
            "reward_gold": 100 + i * 50,
            "reward_diamond": 10 + i * 5,
        }
        results.append(post(f"{CONFIG}/level-configs", lc))
    print(f"  Created {len(results)} level configs")
    return results


# ── Phase 2: Match standalone data ─────────────────────────────────────────

def seed_maps() -> list[dict]:
    maps_data = [
        {"name": "Dust II", "image": "dust2.png"},
        {"name": "Inferno", "image": "inferno.png"},
        {"name": "Mirage", "image": "mirage.png"},
        {"name": "Nuke", "image": "nuke.png"},
    ]
    results = []
    for m in maps_data:
        results.append(post(f"{MATCH}/maps", m))
    print(f"  Created {len(results)} maps")
    return results


def seed_modes() -> list[dict]:
    modes_data = [
        {"name": "Free For All", "type": "normal", "code": "free_for_all", "players_per_team": 1, "selection_weight": 0},
        {"name": "Search & Destroy", "type": "normal", "code": "search_destroy", "players_per_team": 1, "selection_weight": 0},
        {"name": "Ranked Free For All", "type": "rank", "code": "ranked_free_for_all", "players_per_team": 1, "selection_weight": 20},
        {"name": "Ranked Search & Destroy", "type": "rank", "code": "ranked_search_destroy", "players_per_team": 1, "selection_weight": 80},
    ]
    existing = get_list(f"{MATCH}/modes")
    results = []
    added = 0
    updated = 0
    skipped = 0
    for desired in modes_data:
        current = next(
            (
                m for m in existing
                if m.get("code") == desired["code"]
                or (
                    str(m.get("name", "")).strip().lower() == desired["name"].strip().lower()
                    and m.get("type") == desired["type"]
                    and int(m.get("players_per_team", 1)) == desired["players_per_team"]
                )
            ),
            None,
        )
        if current is None:
            created = post(f"{MATCH}/modes", desired)
            existing.append(created)
            results.append(created)
            added += 1
            continue

        patch = {
            key: desired[key]
            for key in ["name", "type", "code", "players_per_team", "selection_weight"]
            if current.get(key) != desired[key]
        }
        if patch:
            current = put(f"{MATCH}/modes/{current['mode_id']}", patch)
            updated += 1
        else:
            skipped += 1
        results.append(current)

    print(f"  Modes: added {added}, updated {updated}, skipped {skipped}")
    return results


# ── Phase 3: Player profiles ───────────────────────────────────────────────

def seed_players(level_configs: list[dict]) -> list[dict]:
    player_names = [
        "DragonSlayer99", "NightOwl", "PixelWarrior", "SilentStorm",
        "BlazeMaster", "IcePhoenix", "ThunderBolt", "CyberNinja",
        "GhostRider", "SteelWolf",
    ]
    results = []
    for i, name in enumerate(player_names):
        level_idx = min(i, len(level_configs) - 1)
        lc = level_configs[level_idx]
        p = {
            "name": name,
            "slogan": f"{name}'s battle cry!",
            "current_level_id": lc["level_id"],
            "current_exp": random.randint(lc["min_exp"], lc["max_exp"] - 1),
        }
        results.append(post(f"{PLAYER}/players", p))
    print(f"  Created {len(results)} players")
    return results


# ── Phase 4: Player sub-entities ────────────────────────────────────────────

def seed_player_stats(player_ids: list[str]):
    count = 0
    for pid in player_ids:
        for mode in ["normal", "rank"]:
            data = {
                "player_id": pid,
                "mode": mode,
                "current_point": random.randint(0, 2000) if mode == "rank" else None,
                "total_game": random.randint(10, 500),
                "number_games_win": random.randint(5, 250),
                "kill": random.randint(50, 5000),
                "dead": random.randint(30, 3000),
                "assists": random.randint(20, 2000),
            }
            post(f"{PLAYER}/player-stats", data)
            count += 1
    print(f"  Created {count} player stats")


def seed_player_currencies(player_ids: list[str]):
    count = 0
    for pid in player_ids:
        for ctype in ["gold", "diamond"]:
            amount = random.randint(100, 50000) if ctype == "gold" else random.randint(10, 500)
            data = {"player_id": pid, "currency_type": ctype, "amount": amount}
            post(f"{PLAYER}/player-currencies", data)
            count += 1
    print(f"  Created {count} player currencies")


def seed_player_inventory(player_ids: list[str], weapon_ids: list[int], character_ids: list[int]):
    count = 0
    for i, pid in enumerate(player_ids):
        # Each player owns 3-7 weapons
        num_weapons = random.randint(3, min(7, len(weapon_ids)))
        owned_weapons = random.sample(weapon_ids, num_weapons)
        for wid in owned_weapons:
            data = {"player_id": pid, "item_id": wid, "item_type": "weapon", "quantity": 1}
            post(f"{PLAYER}/player-inventory", data)
            count += 1
        # Each player owns 1-2 characters
        num_chars = random.randint(1, min(2, len(character_ids)))
        owned_chars = random.sample(character_ids, num_chars)
        for cid in owned_chars:
            data = {"player_id": pid, "item_id": cid, "item_type": "character", "quantity": 1}
            post(f"{PLAYER}/player-inventory", data)
            count += 1
    print(f"  Created {count} inventory items")


def seed_player_equipment(player_ids: list[str], weapon_ids: list[int], character_ids: list[int]):
    count = 0
    weapon_slots = ["primary", "secondary", "melee", "grenade"]
    for pid in player_ids:
        # Not all players equip all slots
        num_slots = random.randint(1, len(weapon_slots))
        slots = random.sample(weapon_slots, num_slots)
        for slot in slots:
            wid = random.choice(weapon_ids)
            data = {"player_id": pid, "slot_type": slot, "weapon_id": wid}
            post(f"{PLAYER}/player-equipment", data)
            count += 1
    print(f"  Created {count} equipment items")


def seed_player_selected_characters(player_ids: list[str], character_ids: list[int]):
    count = 0
    for pid in player_ids:
        cid = random.choice(character_ids)
        data = {"player_id": pid, "character_id": cid}
        post(f"{PLAYER}/player-selected-characters", data)
        count += 1
    print(f"  Created {count} selected characters")


def seed_player_achievements(player_ids: list[str], achievement_ids: list[int]):
    count = 0
    for pid in player_ids:
        # Each player has 0-3 achievements
        num_achievements = random.randint(0, min(3, len(achievement_ids)))
        if num_achievements == 0:
            continue
        achieved = random.sample(achievement_ids, num_achievements)
        for aid in achieved:
            progress = random.randint(50, 100)
            unlock = datetime.now(timezone.utc).isoformat() if progress == 100 else None
            data = {
                "player_id": pid,
                "achievement_id": aid,
                "progress": progress,
                "unlock_at": unlock,
            }
            post(f"{PLAYER}/player-achievements", data)
            count += 1
    print(f"  Created {count} player achievements")


# ── Phase 5: Shop items ────────────────────────────────────────────────────

def seed_shop(weapon_ids: list[int], character_ids: list[int]):
    now = datetime.now(timezone.utc)
    shop_items = [
        {"item_id": weapon_ids[0], "item_type": "weapon", "price": 5000, "currency_type": "gold",
         "discount": 0.0, "is_today": True, "start_at": now.isoformat(), "end_at": (now + timedelta(days=7)).isoformat()},
        {"item_id": weapon_ids[1], "item_type": "weapon", "price": 4500, "currency_type": "gold",
         "discount": 0.1, "is_today": True, "start_at": now.isoformat(), "end_at": (now + timedelta(days=7)).isoformat()},
        {"item_id": weapon_ids[2], "item_type": "weapon", "price": 100, "currency_type": "diamond",
         "discount": 0.0, "is_today": False, "start_at": now.isoformat(), "end_at": (now + timedelta(days=30)).isoformat()},
        {"item_id": weapon_ids[4], "item_type": "weapon", "price": 3000, "currency_type": "gold",
         "discount": 0.2, "is_today": True, "start_at": now.isoformat(), "end_at": (now + timedelta(days=3)).isoformat()},
        {"item_id": weapon_ids[6], "item_type": "weapon", "price": 3500, "currency_type": "gold",
         "discount": 0.0, "is_today": False, "start_at": now.isoformat(), "end_at": (now + timedelta(days=14)).isoformat()},
        {"item_id": character_ids[0], "item_type": "character", "price": 200, "currency_type": "diamond",
         "discount": 0.0, "is_today": True, "start_at": now.isoformat(), "end_at": (now + timedelta(days=7)).isoformat()},
        {"item_id": character_ids[2], "item_type": "character", "price": 150, "currency_type": "diamond",
         "discount": 0.15, "is_today": False, "start_at": now.isoformat(), "end_at": (now + timedelta(days=14)).isoformat()},
        {"item_id": character_ids[4], "item_type": "character", "price": 300, "currency_type": "diamond",
         "discount": 0.0, "is_today": True, "start_at": now.isoformat(), "end_at": (now + timedelta(days=5)).isoformat()},
    ]
    results = []
    for item in shop_items:
        results.append(post(f"{ECONOMY}/shops", item))
    print(f"  Created {len(results)} shop items")
    return results


# ── Phase 5b: Lucky Wheel items ───────────────────────────────────────────

def seed_lucky_wheel(weapon_ids: list[int], character_ids: list[int], weapons: list[dict], characters: list[dict]):
    # Map weapon/character IDs to their data for display_name and image
    weapon_map = {w["weapon_id"]: w for w in weapons}
    char_map = {c["character_id"]: c for c in characters}

    # Delete existing wheel items
    for item in get_list(f"{ECONOMY}/lucky-wheel"):
        delete(f"{ECONOMY}/lucky-wheel/{item['id']}")

    items = []

    # ── Gold Wheel (16 slots) ──
    # Slots 0-5: weapons (common, gold-purchasable)
    gold_weapons = weapon_ids[:6]  # AK-47, M4A1, AWP, Desert Eagle, P90, Shotgun
    for i, wid in enumerate(gold_weapons):
        w = weapon_map[wid]
        items.append({
            "wheel_type": "gold", "slot_index": i,
            "item_id": wid, "item_type": "weapon",
            "shop_price": 3000 + i * 500,
            "weight": 80 if i != 2 else 20,  # AWP is rare
            "display_name": w["name"], "image": w.get("image", ""),
        })
    # Slots 6-7: characters
    for i, cid in enumerate(character_ids[:2]):
        c = char_map[cid]
        items.append({
            "wheel_type": "gold", "slot_index": 6 + i,
            "item_id": cid, "item_type": "character",
            "shop_price": 5000,
            "weight": 50,
            "display_name": c["name"], "image": c.get("texture", c.get("avatar_image", "")),
        })
    # Slot 8: rare weapon
    rare_wid = weapon_ids[7] if len(weapon_ids) > 7 else weapon_ids[-1]
    rw = weapon_map[rare_wid]
    items.append({
        "wheel_type": "gold", "slot_index": 8,
        "item_id": rare_wid, "item_type": "weapon",
        "shop_price": 6000,
        "weight": 15,
        "display_name": rw["name"], "image": rw.get("image", ""),
    })
    # Slots 9-15: gold currency rewards
    gold_rewards = [200, 300, 500, 800, 1000, 1500, 2000]
    gold_weights = [200, 180, 150, 120, 100, 80, 50]
    for i, (amount, w) in enumerate(zip(gold_rewards, gold_weights)):
        items.append({
            "wheel_type": "gold", "slot_index": 9 + i,
            "currency_reward": amount,
            "weight": w,
            "display_name": f"{amount} Gold", "image": "gold.png",
        })

    # ── Diamond Wheel (16 slots) ──
    # Slots 0-4: weapons (diamond-tier)
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
    # Slots 5-8: characters
    for i, cid in enumerate(character_ids[:4]):
        c = char_map[cid]
        items.append({
            "wheel_type": "diamond", "slot_index": 5 + i,
            "item_id": cid, "item_type": "character",
            "shop_price": 200,
            "weight": 60,
            "display_name": c["name"], "image": c.get("texture", c.get("avatar_image", "")),
        })
    # Slot 9: rare character
    rare_cid = character_ids[-1] if len(character_ids) > 4 else character_ids[-1]
    rc = char_map[rare_cid]
    items.append({
        "wheel_type": "diamond", "slot_index": 9,
        "item_id": rare_cid, "item_type": "character",
        "shop_price": 300,
        "weight": 30,
        "display_name": rc["name"], "image": rc.get("texture", rc.get("avatar_image", "")),
    })
    # Slots 10-15: diamond currency rewards
    diamond_rewards = [10, 20, 30, 50, 80, 100]
    diamond_weights = [200, 180, 150, 120, 80, 50]
    for i, (amount, w) in enumerate(zip(diamond_rewards, diamond_weights)):
        items.append({
            "wheel_type": "diamond", "slot_index": 10 + i,
            "currency_reward": amount,
            "weight": w,
            "display_name": f"{amount} Diamond", "image": "diamond.png",
        })

    results = []
    for item in items:
        results.append(post(f"{ECONOMY}/lucky-wheel", item))
    print(f"  Created {len(results)} lucky wheel items ({len([i for i in items if i['wheel_type'] == 'gold'])} gold, {len([i for i in items if i['wheel_type'] == 'diamond'])} diamond)")
    return results


# ── Phase 6: Match history + match players ──────────────────────────────────

def seed_matches(map_ids: list[int], mode_ids: list[int], player_ids: list[str]):
    now = datetime.now(timezone.utc).replace(tzinfo=None)  # naive datetime for TIMESTAMP WITHOUT TIME ZONE
    match_count = 0
    mp_count = 0

    for i in range(5):
        start = now - timedelta(hours=random.randint(1, 72))
        end = start + timedelta(minutes=random.randint(15, 45))
        match_data = {
            "map_id": random.choice(map_ids),
            "mode_id": random.choice(mode_ids),
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "status": "finished",
        }
        match_resp = post(f"{MATCH}/matches", match_data)
        match_id = match_resp["match_id"]
        match_count += 1

        # 4-10 players per match, split into 2 teams
        num_players = random.randint(4, min(10, len(player_ids)))
        match_players = random.sample(player_ids, num_players)
        half = num_players // 2
        team1 = match_players[:half]
        team2 = match_players[half:]
        winning_team = random.choice([1, 2])

        for pid in team1:
            is_winner = winning_team == 1
            mp = {
                "match_id": match_id,
                "player_id": pid,
                "team_id": 1,
                "kill": random.randint(0, 30),
                "dead": random.randint(0, 20),
                "assists": random.randint(0, 15),
                "result": "win" if is_winner else "lose",
                "score": random.randint(500, 5000),
                "exp_earned": random.randint(50, 300),
                "reward_gold": random.randint(200, 500) if is_winner else random.randint(50, 150),
            }
            post(f"{MATCH}/match-players", mp)
            mp_count += 1

        for pid in team2:
            is_winner = winning_team == 2
            mp = {
                "match_id": match_id,
                "player_id": pid,
                "team_id": 2,
                "kill": random.randint(0, 30),
                "dead": random.randint(0, 20),
                "assists": random.randint(0, 15),
                "result": "win" if is_winner else "lose",
                "score": random.randint(500, 5000),
                "exp_earned": random.randint(50, 300),
                "reward_gold": random.randint(200, 500) if is_winner else random.randint(50, 150),
            }
            post(f"{MATCH}/match-players", mp)
            mp_count += 1

    print(f"  Created {match_count} matches, {mp_count} match players")


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    random.seed(42)  # Reproducible randomness

    print("=" * 60)
    print("SEED DATA SCRIPT")
    print("=" * 60)

    # Authenticate before deleting (need auth for all endpoints)
    print("\nAuthenticating...")
    authenticate()

    # Phase 0: Clean slate
    delete_all()

    # Re-authenticate (SeedBot player was deleted above, need fresh token)
    print("Re-authenticating...")
    authenticate()

    # Phase 1: Config
    print("Phase 1: Seeding config-service...")
    weapons = seed_weapons()
    characters = seed_characters()
    achievements = seed_achievements()
    level_configs = seed_level_configs()

    weapon_ids = [w["weapon_id"] for w in weapons]
    character_ids = [c["character_id"] for c in characters]
    achievement_ids = [a["achievement_id"] for a in achievements]
    level_ids = [lc["level_id"] for lc in level_configs]

    # Phase 2: Match standalone
    print("\nPhase 2: Seeding match-service (maps, modes)...")
    maps = seed_maps()
    modes = seed_modes()
    map_ids = [m["map_id"] for m in maps]
    mode_ids = [m["mode_id"] for m in modes]

    # Phase 3: Players
    print("\nPhase 3: Seeding player profiles...")
    players = seed_players(level_configs)
    player_ids = [p["player_id"] for p in players]

    # Phase 4: Player sub-entities
    print("\nPhase 4: Seeding player sub-entities...")
    seed_player_stats(player_ids)
    seed_player_currencies(player_ids)
    seed_player_inventory(player_ids, weapon_ids, character_ids)
    seed_player_equipment(player_ids, weapon_ids, character_ids)
    seed_player_selected_characters(player_ids, character_ids)
    seed_player_achievements(player_ids, achievement_ids)

    # Phase 5: Shop
    print("\nPhase 5: Seeding economy-service (shop)...")
    seed_shop(weapon_ids, character_ids)

    # Phase 5b: Lucky Wheel
    print("\nPhase 5b: Seeding lucky wheel items...")
    seed_lucky_wheel(weapon_ids, character_ids, weapons, characters)

    # Phase 6: Matches
    print("\nPhase 6: Seeding match history...")
    seed_matches(map_ids, mode_ids, player_ids)

    print("\n" + "=" * 60)
    print("SEEDING COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
