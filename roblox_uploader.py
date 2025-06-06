import aiohttp
import asyncio
import os

ROBLOSECURITY_COOKIES_FILE = "cookies.txt"
GAME_FILE = "game.rbxl"

ROBLOX_API_BASE = "https://games.roblox.com"

async def get_csrf_token(session):
    # Roblox requires a CSRF token sent in headers for POST/PUT requests
    # This endpoint returns a CSRF token in header 'x-csrf-token'
    url = "https://auth.roblox.com/v2/logout"  # Any POST request that triggers token return
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
            raise Exception(f"Failed to create universe: {resp.status} {text}")
        res = await resp.json()
        universe_id = res.get("universeId")
        if not universe_id:
            raise Exception("Universe ID missing in response")
        return universe_id

async def create_place(session, csrf_token, universe_id):
    url = f"{ROBLOX_API_BASE}/universes/{universe_id}/places"
    headers = {
        "x-csrf-token": csrf_token,
        "Content-Type": "application/json"
    }
    data = {
        "name": "Main Place",
        "description": "Main place for condo game"
    }
    async with session.post(url, json=data, headers=headers) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"Failed to create place: {resp.status} {text}")
        res = await resp.json()
        place_id = res.get("placeId")
        if not place_id:
            raise Exception("Place ID missing in response")
        return place_id

async def upload_place_file(session, csrf_token, place_id, game_bytes):
    # Upload endpoint
    url = f"https://data.roblox.com/Data/Upload.ashx?assetid={place_id}&isPlaceFile=true"
    headers = {
        "x-csrf-token": csrf_token,
        "Content-Type": "application/octet-stream"
    }
    async with session.post(url, headers=headers, data=game_bytes) as resp:
        if resp.status != 200:
            text = await resp.text()
            raise Exception(f"Failed to upload place file: {resp.status} {text}")

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
            raise Exception(f"Failed to configure universe: {resp.status} {text}")

async def upload_condo_game() -> int:
    if not os.path.exists(ROBLOSECURITY_COOKIES_FILE):
        raise Exception(f"{ROBLOSECURITY_COOKIES_FILE} not found")

    with open(ROBLOSECURITY_COOKIES_FILE, "r") as f:
        cookies = [line.strip() for line in f if line.strip()]
    if not cookies:
        raise Exception("No cookies in cookies.txt")

    cookie = cookies[0]  # Use the first cookie, or random.choice(cookies) if you want

    if not os.path.exists(GAME_FILE):
        raise Exception(f"{GAME_FILE} not found")

    with open(GAME_FILE, "rb") as f:
        game_bytes = f.read()

    jar = aiohttp.CookieJar()
    jar.update_cookies({".ROBLOSECURITY": cookie})

    async with aiohttp.ClientSession(cookie_jar=jar) as session:
        # Get CSRF token
        csrf_token = await get_csrf_token(session)

        # Create Universe
        universe_id = await create_universe(session, csrf_token)

        # Create Place inside Universe
        place_id = await create_place(session, csrf_token, universe_id)

        # Upload the game.rbxl file to the Place
        await upload_place_file(session, csrf_token, place_id, game_bytes)

        # Activate and configure universe
        await activate_universe(session, csrf_token, universe_id)

        return universe_id

# Test the uploader locally
if __name__ == "__main__":
    asyncio.run(upload_condo_game())
