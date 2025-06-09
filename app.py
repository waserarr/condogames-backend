from flask import Flask, jsonify
from flask_cors import CORS
from roblox_uploader import upload_game  # must return the game URL
import json
import os

app = Flask(__name__)
CORS(app, origins=["https://condogames.net"], supports_credentials=True)  # <-- Add this

LATEST_FILE = "latest.json"

@app.route("/latest-upload", methods=["GET"])
def get_latest_upload():
    if os.path.exists(LATEST_FILE):
        with open(LATEST_FILE, "r") as f:
            data = json.load(f)
        return jsonify(data)
    return jsonify({"url": None})

@app.route("/auto-upload", methods=["POST"])
def auto_upload():
    try:
        with open("cookies.txt", "r") as f:
            cookies = [line.strip() for line in f if line.strip()]
        
        for cookie in cookies:
            try:
                url = upload_game(cookie, "game.rbxl", place_name="Auto Condo")
                if url:
                    with open(LATEST_FILE, "w") as f:
                        json.dump({"url": url}, f)
                    return jsonify({"success": True, "url": url})
            except Exception:
                continue

        return jsonify({"success": False, "error": "All uploads failed."}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run()
