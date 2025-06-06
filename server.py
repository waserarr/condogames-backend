import os
from flask import Flask, request, jsonify, redirect, session
from functools import wraps
from roblox_uploader import upload_condo_game
import secrets
import requests
import asyncio

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", secrets.token_hex(16))

DISCORD_CLIENT_ID = os.environ.get("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.environ.get("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.environ.get("DISCORD_REDIRECT_URI")

VALID_KEYS = {
    "key1-abc123", "key2-def456", "key3-ghi789", "key4-jkl012", "key5-mno345",
    "key6-pqr678", "key7-stu901", "key8-vwx234", "key9-yza567", "key10-bcd890",
    "key11-efg123", "key12-hij456", "key13-klm789", "key14-nop012", "key15-qrs345",
    "key16-tuv678", "key17-wxy901", "key18-zab234", "key19-cde567", "key20-fgh890",
    "key21-ijk123", "key22-lmn456", "key23-opq789", "key24-rst012", "key25-uvw345",
    "key26-xyz678", "key27-abc901", "key28-def234", "key29-ghi567", "key30-jkl890",
}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'discord_token' not in session:
            return jsonify({"error": "Unauthorized, login required"}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def home():
    return redirect("/condorequestor.html")


@app.route("/login")
def login():
    discord_oauth_url = (
        f"https://discord.com/api/oauth2/authorize"
        f"?client_id={DISCORD_CLIENT_ID}"
        f"&redirect_uri={DISCORD_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope=identify"
        f"&prompt=consent"
    )
    return redirect(discord_oauth_url)


@app.route("/callback")
def callback():
    code = request.args.get('code')
    if not code:
        return "No code provided", 400

    data = {
        "client_id": DISCORD_CLIENT_ID,
        "client_secret": DISCORD_CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": DISCORD_REDIRECT_URI,
        "scope": "identify",
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    r = requests.post("https://discord.com/api/oauth2/token", data=data, headers=headers)
    r.raise_for_status()
    tokens = r.json()
    session['discord_token'] = tokens['access_token']

    user_req = requests.get(
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    user_req.raise_for_status()
    user = user_req.json()
    session['discord_user'] = user

    return redirect("https://condogames.net/condorequestor.html?status=success")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/upload-condo", methods=["POST"])
@login_required
def upload_condo():
    key = request.form.get("key")
    if not key or key not in VALID_KEYS:
        return jsonify({"error": "Invalid or missing key"}), 400

    try:
        universe_id = asyncio.run(upload_condo_game())
    except Exception as e:
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

    game_url = f"https://www.roblox.com/games/{universe_id}/Uploaded-Condo-Game"
    return jsonify({"success": True, "url": game_url})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
