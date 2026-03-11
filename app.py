from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
import os
import random

app = Flask(__name__)
CORS(app)

# -------------------------
# Supabase Setup
# -------------------------

SUPABASE_URL = os.environ.get(
    "SUPABASE_URL",
    "https://iwxstkhfvfpfaxcniegt.supabase.co"
)

SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# Helpers
# -------------------------

GRID_SIZE = 25
SAFE_TILES = 5


def fetch_games(limit=1000):

    response = supabase.table("game_logs") \
        .select("mines") \
        .order("id", desc=True) \
        .limit(limit) \
        .execute()

    return response.data or []


def frequency_model(games):

    counts = [0] * GRID_SIZE

    for game in games:

        mines = game.get("mines", [])

        for m in mines:

            if 0 <= m < GRID_SIZE:
                counts[m] += 1

    indexed = list(enumerate(counts))

    safest = sorted(indexed, key=lambda x: x[1])[:SAFE_TILES]

    return [x[0] for x in safest]


def neural_pattern_model(games):

    pattern_score = [0] * GRID_SIZE

    for i, game in enumerate(games):

        weight = len(games) - i

        for mine in game.get("mines", []):

            pattern_score[mine] += weight

    indexed = list(enumerate(pattern_score))

    safest = sorted(indexed, key=lambda x: x[1])[:SAFE_TILES]

    return [x[0] for x in safest]


def quantum_model():

    tiles = list(range(GRID_SIZE))

    random.shuffle(tiles)

    return tiles[:SAFE_TILES]


# -------------------------
# Routes
# -------------------------

@app.route("/")
def home():

    return jsonify({
        "status": "online",
        "service": "Monarch AI Predictor"
    })


@app.route("/api/learn", methods=["POST"])
def learn():

    try:

        data = request.get_json()

        mines = data.get("mines")

        if not isinstance(mines, list):
            return jsonify({"error": "invalid mines"}), 400

        supabase.table("game_logs").insert({
            "mines": mines
        }).execute()

        return jsonify({"status": "stored"})

    except Exception as e:

        return jsonify({"error": str(e)}), 500


@app.route("/api/predict")
def predict():

    try:

        mode = request.args.get("mode", "ai")

        games = fetch_games()

        if mode == "ai":

            result = frequency_model(games)

        elif mode == "neural":

            result = neural_pattern_model(games)

        elif mode == "quantum":

            result = quantum_model()

        else:

            result = frequency_model(games)

        return jsonify(result)

    except Exception as e:

        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 10000))

    app.run(host="0.0.0.0", port=port)
