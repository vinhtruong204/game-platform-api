"""
Fill missing mock data for all players.
Adds data to fill gaps WITHOUT deleting or modifying anything.

Usage:
    pip install httpx
    python seed_missing_data.py

Expects services running on:
    player-service  -> http://localhost:8000
    match-service   -> http://localhost:8003
"""

import httpx
import random
import time
from datetime import datetime, timedelta, timezone

PLAYER = "http://localhost:8000/api/v1"
MATCH = "http://localhost:8003/api/v1"

client = httpx.Client(timeout=30, follow_redirects=True)
_auth_token: str | None = None


def authenticate():
    global _auth_token
    r = client.post(f"{PLAYER}/auth/dev-login", json={"name": "SeedBot"})
    r.raise_for_status()
    _auth_token = r.json()["session_token"]
    print(f"  Authenticated as SeedBot (token: {_auth_token[:20]}...)")


def auth_headers() -> dict:
    return {"Authorization": f"Bearer {_auth_token}"}


def post(url: str, data: dict) -> dict | None:
    r = client.post(url, json=data, headers=auth_headers())
    if r.status_code >= 400:
        print(f"  SKIP/ERROR {r.status_code}: {url} -> {r.text[:120]}")
        return None
    return r.json()


def put(url: str, data: dict) -> dict | None:
    r = client.put(url, json=data, headers=auth_headers())
    if r.status_code >= 400:
        print(f"  SKIP/ERROR {r.status_code}: {url} -> {r.text[:120]}")
        return None
    return r.json()


def get_list(url: str) -> list:
    # Ensure trailing slash to avoid redirect (which strips auth headers)
    if not url.endswith("/"):
        url += "/"
    r = client.get(url, headers=auth_headers())
    r.raise_for_status()
    return r.json()


def find_by_prefix(players: list, prefix: str) -> str:
    """Find player UUID by its short prefix."""
    for p in players:
        if p["player_id"].startswith(prefix):
            return p["player_id"]
    raise ValueError(f"Player with prefix '{prefix}' not found")


# ── Data definitions (from plan) ─────────────────────────────────────────────

# Short UUID prefixes for all 15 players (from plan audit)
PLAYER_PREFIXES = {
    "BlazeMaster": "a5f317cd",
    "Chiec Guong": "5ab18f71",
    "CyberNinja": "ae9fa4ba",
    "DragonSlayer99": "3180bc64",
    "GhostRider": "9b8bd664",
    "IcePhoenix": "44d61797",
    "NightOwl": "53ee6944",
    "PixelWarrior": "9b4aeba0",
    "SeedBot": "a4f1a0d4",
    "SilentStorm": "129b15dd",
    "SteelWolf": "58ea3f8d",
    "ThunderBolt": "13ac4abc",
    "Truong Quang Vinh": "9d9ef068",
    "Vinh_a5d5": "a5d5fc83",
    "Vinh_75e2": "75e2abcf",
}


MODE_DEFINITIONS = [
    {"name": "Free For All", "type": "normal", "code": "free_for_all", "players_per_team": 1, "selection_weight": 0},
    {"name": "Search & Destroy", "type": "normal", "code": "search_destroy", "players_per_team": 1, "selection_weight": 0},
    {"name": "Ranked Free For All", "type": "rank", "code": "ranked_free_for_all", "players_per_team": 1, "selection_weight": 20},
    {"name": "Ranked Search & Destroy", "type": "rank", "code": "ranked_search_destroy", "players_per_team": 1, "selection_weight": 80},
]


def get_player_map(all_players: list) -> dict[str, str]:
    """Return a dict of short-name -> full UUID for all 15 players."""
    return {key: find_by_prefix(all_players, prefix) for key, prefix in PLAYER_PREFIXES.items()}


def seed_missing_modes():
    print("\nPhase 0: Match Modes...")
    modes = get_list(f"{MATCH}/modes")
    added = 0
    updated = 0
    skipped = 0
    for desired in MODE_DEFINITIONS:
        current = next(
            (
                m for m in modes
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
            if created:
                modes.append(created)
                added += 1
            continue

        patch = {
            key: desired[key]
            for key in ["name", "type", "code", "players_per_team", "selection_weight"]
            if current.get(key) != desired[key]
        }
        if patch:
            if put(f"{MATCH}/modes/{current['mode_id']}", patch):
                updated += 1
        else:
            skipped += 1
    print(f"  Modes: added {added}, updated {updated}, skipped {skipped}")


# ── Phase 1: Player Stats ────────────────────────────────────────────────────

def seed_missing_stats(pm: dict, existing_set: set):
    print("\nPhase 1: Player Stats...")
    count = 0
    stats_to_add = [
        # (player_key, mode, total_game, wins, kills, deaths, assists, current_point)
        ("Chiec Guong", "normal", 15, 8, 45, 30, 20, None),
        ("Chiec Guong", "rank", 10, 5, 30, 25, 15, 350),
        ("SeedBot", "normal", 5, 2, 10, 15, 5, None),
        ("SeedBot", "rank", 3, 1, 5, 10, 3, 100),
        ("Truong Quang Vinh", "normal", 20, 12, 60, 35, 25, None),
        ("Truong Quang Vinh", "rank", 15, 9, 50, 28, 22, 520),
        ("Vinh_a5d5", "normal", 30, 18, 90, 50, 40, None),
        ("Vinh_a5d5", "rank", 25, 15, 75, 40, 35, 780),
        ("Vinh_75e2", "normal", 12, 6, 35, 28, 18, None),
        ("Vinh_75e2", "rank", 8, 4, 22, 20, 12, 250),
    ]
    for key, mode, total, wins, kills, deaths, assists, points in stats_to_add:
        pid = pm[key]
        if (pid, mode) in existing_set:
            continue
        data = {
            "player_id": pid,
            "mode": mode,
            "total_game": total,
            "number_games_win": wins,
            "kill": kills,
            "dead": deaths,
            "assists": assists,
            "current_point": points,
        }
        if post(f"{PLAYER}/player-stats", data):
            count += 1
    print(f"  Created {count} player stats")


# ── Phase 2: Player Currency ─────────────────────────────────────────────────

def seed_missing_currencies(pm: dict, existing_set: set):
    print("\nPhase 2: Player Currency...")
    count = 0
    currencies_to_add = [
        # (player_key, gold, diamond)
        ("Chiec Guong", 5000, 50),
        ("SeedBot", 1000, 10),
        ("Truong Quang Vinh", 15000, 120),
        ("Vinh_a5d5", 25000, 200),
        ("Vinh_75e2", 3000, 30),
    ]
    for key, gold, diamond in currencies_to_add:
        pid = pm[key]
        for ctype, amount in [("gold", gold), ("diamond", diamond)]:
            if (pid, ctype) in existing_set:
                continue
            data = {"player_id": pid, "currency_type": ctype, "amount": amount}
            if post(f"{PLAYER}/player-currencies", data):
                count += 1
    print(f"  Created {count} player currencies")


# ── Phase 3: Player Inventory ────────────────────────────────────────────────

def seed_missing_inventory(pm: dict, existing_set: set):
    print("\nPhase 3: Player Inventory...")
    count = 0
    inventory_to_add = [
        # (player_key, item_id, item_type)
        ("Chiec Guong", 51, "weapon"),
        ("Chiec Guong", 55, "weapon"),
        ("Chiec Guong", 57, "weapon"),
        ("Chiec Guong", 26, "character"),
        ("SeedBot", 52, "weapon"),
        ("SeedBot", 54, "weapon"),
        ("SeedBot", 29, "character"),
        ("Truong Quang Vinh", 51, "weapon"),
        ("Truong Quang Vinh", 53, "weapon"),
        ("Truong Quang Vinh", 56, "weapon"),
        ("Truong Quang Vinh", 58, "weapon"),
        ("Truong Quang Vinh", 27, "character"),
        ("Truong Quang Vinh", 30, "character"),
        ("Vinh_a5d5", 52, "weapon"),
        ("Vinh_a5d5", 55, "weapon"),
        ("Vinh_a5d5", 59, "weapon"),
        ("Vinh_a5d5", 60, "weapon"),
        ("Vinh_a5d5", 28, "character"),
        ("Vinh_a5d5", 26, "character"),
        ("Vinh_75e2", 51, "weapon"),
        ("Vinh_75e2", 54, "weapon"),
        ("Vinh_75e2", 57, "weapon"),
        ("Vinh_75e2", 29, "character"),
    ]
    for key, item_id, item_type in inventory_to_add:
        pid = pm[key]
        if (pid, item_id, item_type) in existing_set:
            continue
        data = {"player_id": pid, "item_id": item_id, "item_type": item_type, "quantity": 1}
        if post(f"{PLAYER}/player-inventory", data):
            count += 1
    print(f"  Created {count} inventory items")


# ── Phase 4: Player Equipment ────────────────────────────────────────────────

def seed_missing_equipment(pm: dict, existing_set: set):
    print("\nPhase 4: Player Equipment...")
    count = 0
    equipment_to_add = [
        # (player_key, slot_type, weapon_id)
        ("Chiec Guong", "primary", 51),
        ("SeedBot", "primary", 52),
        ("Truong Quang Vinh", "primary", 58),
        ("Truong Quang Vinh", "secondary", 53),
        ("Truong Quang Vinh", "grenade", 56),
        ("Vinh_a5d5", "primary", 55),
        ("Vinh_a5d5", "secondary", 52),
        ("Vinh_a5d5", "melee", 59),
        ("Vinh_a5d5", "grenade", 60),
        ("Vinh_75e2", "primary", 51),
        ("Vinh_75e2", "secondary", 54),
    ]
    for key, slot, wid in equipment_to_add:
        pid = pm[key]
        if (pid, slot) in existing_set:
            continue
        data = {"player_id": pid, "slot_type": slot, "weapon_id": wid}
        if post(f"{PLAYER}/player-equipment", data):
            count += 1
    print(f"  Created {count} equipment items")


# ── Phase 5: Player Selected Character ───────────────────────────────────────

def seed_missing_selected_characters(pm: dict, existing_set: set):
    print("\nPhase 5: Selected Characters...")
    count = 0
    sel_chars = [
        ("Chiec Guong", 26),
        ("SeedBot", 29),
        ("Truong Quang Vinh", 27),
        ("Vinh_a5d5", 28),
        ("Vinh_75e2", 29),
    ]
    for key, char_id in sel_chars:
        pid = pm[key]
        if pid in existing_set:
            continue
        data = {"player_id": pid, "character_id": char_id}
        if post(f"{PLAYER}/player-selected-characters", data):
            count += 1
    print(f"  Created {count} selected characters")


# ── Phase 6: Player Achievements ─────────────────────────────────────────────

def seed_missing_achievements(pm: dict, existing_set: set):
    print("\nPhase 6: Player Achievements...")
    count = 0
    achievements_to_add = [
        # (player_key, achievement_id, progress)
        ("BlazeMaster", 26, 90),
        ("BlazeMaster", 28, 65),
        ("NightOwl", 27, 72),
        ("NightOwl", 30, 85),
        ("SteelWolf", 29, 60),
        ("ThunderBolt", 26, 95),
        ("ThunderBolt", 28, 55),
        ("Chiec Guong", 30, 40),
        # SeedBot gets none
        ("Truong Quang Vinh", 26, 78),
        ("Truong Quang Vinh", 27, 50),
        ("Vinh_a5d5", 28, 70),
        ("Vinh_a5d5", 29, 88),
        ("Vinh_75e2", 30, 35),
    ]
    for key, ach_id, progress in achievements_to_add:
        pid = pm[key]
        if (pid, ach_id) in existing_set:
            continue
        unlock = datetime.now(timezone.utc).isoformat() if progress == 100 else None
        data = {
            "player_id": pid,
            "achievement_id": ach_id,
            "progress": progress,
            "unlock_at": unlock,
        }
        if post(f"{PLAYER}/player-achievements", data):
            count += 1
    print(f"  Created {count} player achievements")


# ── Phase 7: Player Ranks ────────────────────────────────────────────────────

def seed_missing_ranks(pm: dict, existing_set: set):
    print("\nPhase 7: Player Ranks (Season 1)...")
    count = 0
    ranks_to_add = [
        # (player_key, season_id, rank_id, current_point)
        ("BlazeMaster", 1, 3, 1200),
        ("Chiec Guong", 1, 1, 350),
        ("CyberNinja", 1, 4, 1650),
        ("DragonSlayer99", 1, 2, 800),
        ("GhostRider", 1, 5, 2100),
        ("IcePhoenix", 1, 3, 1350),
        ("NightOwl", 1, 4, 1500),
        ("PixelWarrior", 1, 2, 950),
        ("SeedBot", 1, 1, 100),
        ("SilentStorm", 1, 3, 1100),
        ("SteelWolf", 1, 4, 1800),
        ("ThunderBolt", 1, 5, 2200),
        ("Truong Quang Vinh", 1, 2, 520),
        ("Vinh_a5d5", 1, 2, 780),
        ("Vinh_75e2", 1, 1, 250),
    ]
    for key, season, rank, points in ranks_to_add:
        pid = pm[key]
        if (pid, season) in existing_set:
            continue
        data = {
            "player_id": pid,
            "season_id": season,
            "rank_id": rank,
            "current_point": points,
        }
        if post(f"{PLAYER}/player-ranks", data):
            count += 1
    print(f"  Created {count} player ranks")


# ── Phase 8: Match History + Match Players ────────────────────────────────────

def seed_missing_matches(pm: dict):
    print("\nPhase 8: Match History + Match Players...")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    match_count = 0
    mp_count = 0

    matches_to_add = [
        # (map_id, mode_id, team1_keys, team2_keys)
        (22, 16,
         ["Chiec Guong", "Truong Quang Vinh", "DragonSlayer99", "BlazeMaster"],
         ["Vinh_a5d5", "Vinh_75e2", "SteelWolf", "NightOwl"]),
        (24, 17,
         ["Chiec Guong", "Vinh_a5d5", "GhostRider", "CyberNinja", "SilentStorm"],
         ["Truong Quang Vinh", "Vinh_75e2", "ThunderBolt", "PixelWarrior", "DragonSlayer99"]),
        (21, 18,
         ["SeedBot", "Chiec Guong", "Truong Quang Vinh", "IcePhoenix"],
         ["Vinh_a5d5", "Vinh_75e2", "BlazeMaster", "NightOwl"]),
        (23, 17,
         ["Chiec Guong", "Vinh_a5d5", "SteelWolf", "ThunderBolt", "GhostRider"],
         ["Truong Quang Vinh", "Vinh_75e2", "SeedBot", "CyberNinja", "SilentStorm"]),
        (22, 16,
         ["Vinh_a5d5", "DragonSlayer99", "PixelWarrior", "IcePhoenix"],
         ["Vinh_75e2", "Truong Quang Vinh", "Chiec Guong", "BlazeMaster"]),
    ]

    for i, (map_id, mode_id, team1_keys, team2_keys) in enumerate(matches_to_add):
        start = now - timedelta(hours=random.randint(1, 72))
        end = start + timedelta(minutes=random.randint(15, 45))
        season = 1 if mode_id == 17 else None  # ranked matches get season_id

        match_data = {
            "map_id": map_id,
            "mode_id": mode_id,
            "start_time": start.isoformat(),
            "end_time": end.isoformat(),
            "status": "finished",
            "season_id": season,
        }
        match_resp = post(f"{MATCH}/matches", match_data)
        if not match_resp:
            print(f"  Failed to create match #{i+1}, skipping")
            continue
        match_id = match_resp["match_id"]
        match_count += 1

        winning_team = random.choice([1, 2])

        for key in team1_keys:
            pid = pm[key]
            is_winner = winning_team == 1
            mp_data = {
                "match_id": match_id,
                "player_id": pid,
                "team_id": 1,
                "kill": random.randint(0, 25),
                "dead": random.randint(0, 18),
                "assists": random.randint(0, 12),
                "result": "win" if is_winner else "lose",
                "score": random.randint(500, 5000),
                "exp_earned": random.randint(50, 300),
                "reward_gold": random.randint(200, 500) if is_winner else random.randint(50, 150),
            }
            if post(f"{MATCH}/match-players", mp_data):
                mp_count += 1

        for key in team2_keys:
            pid = pm[key]
            is_winner = winning_team == 2
            mp_data = {
                "match_id": match_id,
                "player_id": pid,
                "team_id": 2,
                "kill": random.randint(0, 25),
                "dead": random.randint(0, 18),
                "assists": random.randint(0, 12),
                "result": "win" if is_winner else "lose",
                "score": random.randint(500, 5000),
                "exp_earned": random.randint(50, 300),
                "reward_gold": random.randint(200, 500) if is_winner else random.randint(50, 150),
            }
            if post(f"{MATCH}/match-players", mp_data):
                mp_count += 1

    print(f"  Created {match_count} matches, {mp_count} match players")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    random.seed(42)

    print("=" * 60)
    print("FILL MISSING DATA SCRIPT")
    print("=" * 60)

    # Authenticate
    print("\nAuthenticating...")
    authenticate()
    time.sleep(1)  # Wait for session commit (DB is remote)

    # Fetch all players and build name->UUID map
    print("\nFetching existing data...")
    all_players = get_list(f"{PLAYER}/players")
    print(f"  Found {len(all_players)} players")
    for p in all_players:
        name = p['name'].encode('ascii', 'replace').decode()
        print(f"    {name:25s} {p['player_id']}")

    pm = get_player_map(all_players)
    print(f"  Mapped {len(pm)} players")

    # Fetch existing sub-entities and build lookup sets
    existing_stats = get_list(f"{PLAYER}/player-stats")
    existing_currencies = get_list(f"{PLAYER}/player-currencies")
    existing_inventory = get_list(f"{PLAYER}/player-inventory")
    existing_equipment = get_list(f"{PLAYER}/player-equipment")
    existing_sel_chars = get_list(f"{PLAYER}/player-selected-characters")
    existing_achievements = get_list(f"{PLAYER}/player-achievements")
    existing_ranks = get_list(f"{PLAYER}/player-ranks")

    stats_set = {(s["player_id"], s["mode"]) for s in existing_stats}
    currency_set = {(c["player_id"], c["currency_type"]) for c in existing_currencies}
    inventory_set = {(i["player_id"], i["item_id"], i["item_type"]) for i in existing_inventory}
    equipment_set = {(e["player_id"], e["slot_type"]) for e in existing_equipment}
    sel_char_set = {sc["player_id"] for sc in existing_sel_chars}
    achievement_set = {(a["player_id"], a["achievement_id"]) for a in existing_achievements}
    rank_set = {(r["player_id"], r["season_id"]) for r in existing_ranks}

    print(f"  Existing: {len(stats_set)} stats, {len(currency_set)} currencies, "
          f"{len(inventory_set)} inventory, {len(equipment_set)} equipment, "
          f"{len(sel_char_set)} sel_chars, {len(achievement_set)} achievements, "
          f"{len(rank_set)} ranks")

    # Fill gaps
    seed_missing_modes()
    seed_missing_stats(pm, stats_set)
    seed_missing_currencies(pm, currency_set)
    seed_missing_inventory(pm, inventory_set)
    seed_missing_equipment(pm, equipment_set)
    seed_missing_selected_characters(pm, sel_char_set)
    seed_missing_achievements(pm, achievement_set)
    seed_missing_ranks(pm, rank_set)
    seed_missing_matches(pm)

    print("\n" + "=" * 60)
    print("FILL MISSING DATA COMPLETE!")
    print("=" * 60)


if __name__ == "__main__":
    main()
