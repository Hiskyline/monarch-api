from flask import Flask, request, jsonify
from supabase import create_client
import os

app = Flask(__name__)

# Credentials should be fetched from Environment Variables for security
SUPABASE_URL = os.environ.get("https://iwxstkhfvfpfaxcniegt.supabase.co", "https://iwxstkhfvfpfaxcniegt.supabase.co")
SUPABASE_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3eHN0a2hmdmZwZmF4Y25pZWd0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzA3ODY1NCwiZXh") # Ensure this is set in Render
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. Root route to prevent 404 Not Found
@app.route('/', methods=['GET'])
def home():
    return jsonify({"status": "online", "message": "Monarch API is live"}), 200

# 2. Learn route
@app.route('/api/learn', methods=['POST'])
def learn():
    try:
        data = request.get_json()
        supabase.table("game_logs").insert({"mines": data['mines']}).execute()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# 3. Predict route
@app.route('/api/predict', methods=['GET'])
def predict():
    try:
        response = supabase.table("game_logs").select("mines").order("id", desc=True).limit(500).execute()
        games = response.data
        
        counts = [0] * 25
        for game in games:
            for mine_index in game['mines']:
                counts[mine_index] += 1
                
        indexed_counts = list(enumerate(counts))
        # Return tiles with the lowest frequency (safest)
        safe_tiles = sorted(indexed_counts, key=lambda x: x[1])[:5]
        return jsonify([tile[0] for tile in safe_tiles])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
