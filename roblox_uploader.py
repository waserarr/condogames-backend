import random
import os
import requests

def get_random_cookie():
    with open("cookies.txt", "r") as f:
        cookies = f.read().splitlines()
    if not cookies:
        raise Exception("No cookies found.")
    return random.choice(cookies)


def get_csrf_token(session):
    r = session.post("https://auth.roblox.com/v2/logout")
    if "x-csrf-token" not in r.headers:
        raise Exception("Failed to get CSRF token.")
    return r.headers["x-csrf-token"]


def upload_condo_game(game_bytes):
    cookie = get_random_cookie()
    session = requests.Session()
    session.cookies[".ROBLOSECURITY"] = cookie

    csrf_token = get_csrf_token(session)
    headers = {
        "x-csrf-token": csrf_token,
    }

    # Step 1: Create universe
    create_universe = session.post(
        "https://apis.roblox.com/universes/v1/universes",
        json={"name": "Uploaded Condo"},
        headers=headers,
    )
    if not create_universe.ok:
        raise Exception(f"Create universe failed: {create_universe.text}")

    universe_id = create_universe.json()["universeId"]

    # Step 2: Upload place
    upload = session.post(
        f"https://data.roblox.com/Data/Upload.ashx?assetid=0&type=Model",
        files={"file": ("game.rbxl", game_bytes, "application/octet-stream")},
        headers=headers,
    )

    if not upload.ok:
        raise Exception(f"Upload failed: {upload.text}")

    return universe_id
