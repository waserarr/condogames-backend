import aiohttp
import asyncio
import os
import random

ROBLOSECURITY_COOKIES_FILE = "cookies.txt"
ROBLOX_API_BASE = "https://games.roblox.com"

async def get_csrf_token(session):
    url = "https://auth.roblox.com/v2/logout"
    async with session.post(url) as resp:
        token = resp.headers.get("x-csrf-token")
        if not token:
            raise Exception("Failed to get CSRF token")
        return token

async def create_universe(session, csrf_token):
    url = f"{ROBLOX_API_BASE}/universes/create"
    headers = {
        "x-csrf-token": csrf_token,
        "Content-Type": "application/json"
    }
    data = {
        "name": "Uploaded Condo Game",
        "description": "Uploaded via API",
        "universeAvatarType": "Player"
    }
    async with session.post(url, json=data, headers=headers) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"❌ Create universe failed: {text}")
        res = await resp.json()
        return res.get("universeId")

async def create_place(session, csrf_token, universe_id):
    url = f"{ROBLOX_API_BASE}/universes/{universe_id}/places"
    headers = {
        "x-csrf-token": csrf_token,
        "Content-Type": "application/json"
    }
    data = {
        "name": "Main Place",
        "description": "Main place for game"
    }
    async with session.post(url, json=data, headers=headers) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"❌ Create place failed: {text}")
        res = await resp.json()
        return res.get("placeId")

async def upload_place_file(session, csrf_token, place_id, game_bytes):
    url = f"https://data.roblox.com/Data/Upload.ashx?assetid={place_id}&isPlaceFile=true"
    headers = {
        "x-csrf-token": csrf_token,
        "Content-Type": "application/octet-stream"
    }
    async with session.post(url, headers=headers, data=game_bytes) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"❌ Upload place failed: {text}")

async def activate_universe(session, csrf_token, universe_id):
    url = f"{ROBLOX_API_BASE}/universes/{universe_id}/configuration"
    headers = {
        "x-csrf-token": csrf_token,
        "Content-Type": "application/json"
    }
    data = {
        "universeId": universe_id,
        "maxPlayers": 20,
        "allowThirdPartySales": True,
        "universeAvatarType": "Player"
    }
    async with session.post(url, json=data, headers=headers) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"❌ Activate universe failed: {text}")

async def upload_condo_game(map_file: str) -> int:
    if not os.path.exists(ROBLOSECURITY_COOKIES_FILE):
        raise Exception("❌ cookies.txt not found")

    with open(ROBLOSECURITY_COOKIES_FILE, "r") as f:
        cookies = [line.strip() for line in f if line.strip()]
    if not cookies:
        raise Exception("❌ No .ROBLOSECURITY cookies found")

    cookie = random.choice(cookies)

    if not os.path.exists(map_file):
        raise Exception(f"❌ Map file not found: {map_file}")

    with open(map_file, "rb") as f:
        game_bytes = f.read()

    jar = aiohttp.CookieJar()
    jar.update_cookies({".ROBLOSECURITY": cookie})

    async with aiohttp.ClientSession(cookie_jar=jar) as session:
        csrf_token = await get_csrf_token(session)
        universe_id = await create_universe(session, csrf_token)
        place_id = await create_place(session, csrf_token, universe_id)
        await upload_place_file(session, csrf_token, place_id, game_bytes)
        await activate_universe(session, csrf_token, universe_id)
        return universe_id

if __name__ == "__main__":
    import sys
    map_arg = sys.argv[1] if len(sys.argv) > 1 else "game1.rbxl"
    asyncio.run(upload_condo_game(map_arg))
