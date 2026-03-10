# app.py (Deploy this to your Render service)
from flask import Flask, request, jsonify
from supabase import create_client

app = Flask(__name__)
# Replace these with your actual Supabase credentials
supabase = create_client("https://iwxstkhfvfpfaxcniegt.supabase.co", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml3eHN0a2hmdmZwZmF4Y25pZWd0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MzA3ODY1NCwiZXhwIjoyMDg4NjU0NjU0fQ.8xAOZd2XSG6O575OZ3z6K9LarcnzdsGGVxYmSWewFtk")

@app.route('/api/learn', methods=['POST'])
def learn():
    data = request.get_json()
    # Save the mine positions to Supabase
    supabase.table("game_logs").insert({"mines": data['mines']}).execute()
    return jsonify({"status": "learned"}), 200

@app.route('/api/predict', methods=['GET'])
def predict():
    # Fetch last 500 games
    response = supabase.table("game_logs").select("mines").order("id", desc=True).limit(500).execute()
    games = response.data
    
    # Calculate bomb frequency per tile (0-24)
    counts = [0] * 25
    for game in games:
        for mine_index in game['mines']:
            counts[mine_index] += 1
            
    # Return the 5 tiles with the lowest bomb frequency
    indexed_counts = list(enumerate(counts))
    safe_tiles = sorted(indexed_counts, key=lambda x: x[1])[:5]
    return jsonify([tile[0] for tile in safe_tiles])
