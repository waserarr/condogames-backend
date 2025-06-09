import requests
import time

ROBLOX_API_BASE = "https://apis.roblox.com/universes/v1"
UPLOAD_ENDPOINT = "https://data.roblox.com/Data/Upload.ashx"

HEADERS = {
    "User-Agent": "RobloxUploader/1.0"
}

def get_csrf_token(cookie):
    res = requests.post("https://auth.roblox.com/v2/logout", headers={"Cookie": f".ROBLOSECURITY={cookie}"})
    return res.headers.get("x-csrf-token", "")

def create_universe(cookie, csrf, name):
    headers = {
        "Cookie": f".ROBLOSECURITY={cookie}",
        "x-csrf-token": csrf,
        "Content-Type": "application/json"
    }
    data = {
        "name": name,
        "description": "Uploaded via CondoGames.Net",
        "universeAvatarType": "R6"
    }
    res = requests.post("https://apis.roblox.com/universes/v1/universes", headers=headers, json=data)
    if res.ok:
        return res.json().get("universeId")
    return None

def create_place(cookie, csrf, universe_id, name):
    headers = {
        "Cookie": f".ROBLOSECURITY={cookie}",
        "x-csrf-token": csrf,
        "Content-Type": "application/json"
    }
    data = {
        "name": name,
        "description": "Uploaded from CondoGames.Net",
        "universeId": universe_id
    }
    res = requests.post("https://apis.roblox.com/universes/v1/places", headers=headers, json=data)
    if res.ok:
        return res.json().get("placeId")
    return None

def upload_file(cookie, csrf, place_id, file_path):
    headers = {
        "Cookie": f".ROBLOSECURITY={cookie}",
        "x-csrf-token": csrf
    }
    with open(file_path, "rb") as f:
        files = {
            "request": (None, f'{{"targetPlaceId":{place_id},"versionType":"Published"}}', "application/json"),
            "file": ("game.rbxl", f, "application/octet-stream")
        }
        res = requests.post(UPLOAD_ENDPOINT, headers=headers, files=files)
    return res.ok

def make_public(cookie, csrf, universe_id):
    headers = {
        "Cookie": f".ROBLOSECURITY={cookie}",
        "x-csrf-token": csrf,
        "Content-Type": "application/json"
    }
    data = {"isArchived": False, "isActive": True}
    res = requests.patch(f"{ROBLOX_API_BASE}/{universe_id}/configuration", headers=headers, json=data)
    return res.ok

def upload_game(cookie, file_path="game.rbxl", place_name="Auto Condo"):
    try:
        csrf = get_csrf_token(cookie)
        if not csrf:
            raise Exception("Failed to get CSRF token")

        universe_id = create_universe(cookie, csrf, place_name)
        if not universe_id:
            raise Exception("Failed to create universe")

        place_id = create_place(cookie, csrf, universe_id, place_name)
        if not place_id:
            raise Exception("Failed to create place")

        uploaded = upload_file(cookie, csrf, place_id, file_path)
        if not uploaded:
            raise Exception("File upload failed")

        public = make_public(cookie, csrf, universe_id)
        if not public:
            raise Exception("Failed to make game public")

        return f"https://www.roblox.com/games/{place_id}/{place_name.replace(' ', '-')}"
    except Exception as e:
        print(f"[Upload Error] {e}")
        return None
