"""
Add Search & Destroy mode data without deleting existing rows.

Usage:
    pip install httpx
    python seed_search_destroy_modes.py

Expects services running on:
    player-service  -> http://localhost:8000
    match-service   -> http://localhost:8003
"""

import httpx

PLAYER = "http://localhost:8000/api/v1"
MATCH = "http://localhost:8003/api/v1"

client = httpx.Client(timeout=30, follow_redirects=True)
_auth_token: str | None = None


MODES = [
    {
        "name": "Free For All",
        "type": "normal",
        "code": "free_for_all",
        "players_per_team": 1,
        "selection_weight": 0,
    },
    {
        "name": "Search & Destroy",
        "type": "normal",
        "code": "search_destroy",
        "players_per_team": 1,
        "selection_weight": 0,
    },
    {
        "name": "Ranked Free For All",
        "type": "rank",
        "code": "ranked_free_for_all",
        "players_per_team": 1,
        "selection_weight": 20,
    },
    {
        "name": "Ranked Search & Destroy",
        "type": "rank",
        "code": "ranked_search_destroy",
        "players_per_team": 1,
        "selection_weight": 80,
    },
]


def authenticate() -> None:
    global _auth_token
    r = client.post(f"{PLAYER}/auth/dev-login", json={"name": "SeedBot"})
    r.raise_for_status()
    _auth_token = r.json()["session_token"]
    print(f"Authenticated (token: {_auth_token[:20]}...)")


def auth_headers() -> dict:
    return {"Authorization": f"Bearer {_auth_token}"}


def get_modes() -> list[dict]:
    r = client.get(f"{MATCH}/modes", headers=auth_headers())
    r.raise_for_status()
    return r.json()


def post_mode(data: dict) -> dict:
    r = client.post(f"{MATCH}/modes", json=data, headers=auth_headers())
    r.raise_for_status()
    return r.json()


def update_mode(mode_id: int, data: dict) -> dict:
    r = client.put(f"{MATCH}/modes/{mode_id}", json=data, headers=auth_headers())
    r.raise_for_status()
    return r.json()


def mode_matches(row: dict, desired: dict) -> bool:
    code = row.get("code")
    if code:
        return code == desired["code"]
    return (
        str(row.get("name", "")).strip().lower() == desired["name"].strip().lower()
        and row.get("type") == desired["type"]
        and int(row.get("players_per_team", 1)) == desired["players_per_team"]
    )


def main() -> None:
    print("ADD SEARCH & DESTROY MODES (non-destructive)")
    authenticate()

    existing = get_modes()
    added = 0
    updated = 0
    skipped = 0

    for desired in MODES:
        current = next((row for row in existing if mode_matches(row, desired)), None)
        if current is None:
            created = post_mode(desired)
            existing.append(created)
            added += 1
            print(f"  Added {desired['code']}")
            continue

        patch = {}
        for key in ["name", "type", "code", "players_per_team", "selection_weight"]:
            if current.get(key) != desired[key]:
                patch[key] = desired[key]
        if patch:
            update_mode(int(current["mode_id"]), patch)
            updated += 1
            print(f"  Updated {desired['code']}")
        else:
            skipped += 1

    print(f"Done. added={added}, updated={updated}, skipped={skipped}")


if __name__ == "__main__":
    main()
