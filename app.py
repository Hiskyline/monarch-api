import os
import random
from flask import Flask, jsonify, request
from flask_cors import CORS
from supabase import create_client

app = Flask(__name__)
CORS(app)

# Connect to Supabase using the variables we'll set on Render
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

@app.route('/api/learn', methods=['POST'])
def learn():
    data = request.json
    # Saves the mine locations to the table you just created
    supabase.table("game_logs").insert({"mines": data['mines']}).execute()
    return jsonify({"status": "learned"})

@app.route('/api/ext/predictions', methods=['GET'])
def predict():
    mode = request.args.get('mode', 'AI_Mode')
    # Get the last 100 games to find patterns
    logs = supabase.table("game_logs").select("mines").order("created_at", desc=True).limit(100).execute()
    
    heat_map = [0] * 25
    for entry in logs.data:
        for mine in entry['mines']:
            if 0 <= mine < 25: heat_map[mine] += 1
                
    indexed = list(enumerate(heat_map))
    
    # 3 Mode Logic
    if mode == "Neural":
        indexed.sort(key=lambda x: (x[1] * 0.8) + (random.random() * 2))
    elif mode == "Quantum":
        indexed.sort(key=lambda x: x[1] + (random.uniform(-5, 5)))
    else: # AI Mode
        indexed.sort(key=lambda x: x[1])
    
    sorted_tiles = [x[0] for x in indexed]
    return jsonify([{
        "tile_array": sorted_tiles,
        "games_analyzed": len(logs.data)
    }])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
