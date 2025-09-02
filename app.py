from flask import Flask, request, jsonify, send_from_directory
import logging
import os
import sqlite3
from dateutil.parser import isoparse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='frontend/build', static_url_path='')

@app.route('/zones', methods=['GET'])
def zones():
    """Return list of zones with ids and names from SQLite or CSV fallback."""
    zones_list = []
    try:
        db_path = os.path.join('data', 'data.db')
        if os.path.exists(db_path):
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('SELECT LocationID, zone, borough FROM taxi_zones')
                rows = cur.fetchall()
                zones_list = [{"id": r[0], "zone": r[1], "borough": r[2]} for r in rows]
        else:
            raise FileNotFoundError('data.db not found')
    except Exception as e:
        logger.warning("/zones DB lookup failed (%s). Falling back to CSV.", e)
        csv_path = os.path.join('data', 'taxi_zones.csv')
        if os.path.exists(csv_path):
            try:
                import pandas as pd
                df = pd.read_csv(csv_path)
                for _, r in df.iterrows():
                    zones_list.append({"id": int(r.get('LocationID')), "zone": r.get('zone'), "borough": r.get('borough')})
            except Exception as e2:
                logger.error("/zones CSV read failed: %s", e2)
    return jsonify({"zones": zones_list})

@app.route('/complete_ride', methods=['POST'])
def complete_ride():
    data = request.get_json(silent=True) or {}
    logger.info("Received /complete_ride payload: %s", data)

    # Validate required inputs
    required = ['pickup', 'drop', 'pickup_time', 'drop_time', 'passengers']
    missing = [k for k in required if k not in data]
    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    pickup_name = str(data.get('pickup')).strip()
    drop_name = str(data.get('drop')).strip()
    pickup_time = str(data.get('pickup_time')).strip()
    drop_time = str(data.get('drop_time')).strip()
    try:
        passengers = int(data.get('passengers'))
    except Exception:
        return jsonify({"error": "passengers must be an integer"}), 400

    # Build zone name -> id mapping
    name_to_id = {}
    db_path = os.path.join('data', 'data.db')
    if os.path.exists(db_path):
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('SELECT LocationID, zone FROM taxi_zones')
                for loc_id, zone in cur.fetchall():
                    name_to_id[str(zone).strip().lower()] = int(loc_id)
        except Exception as e:
            logger.warning("Failed reading taxi_zones from DB: %s", e)
    # CSV fallback
    if not name_to_id:
        csv_path = os.path.join('data', 'taxi_zones.csv')
        if os.path.exists(csv_path):
            try:
                import pandas as pd
                dfz = pd.read_csv(csv_path)
                for _, r in dfz.iterrows():
                    name_to_id[str(r.get('zone')).strip().lower()] = int(r.get('LocationID'))
            except Exception as e:
                logger.error("Failed reading taxi_zones.csv: %s", e)

    pickup_zone_id = name_to_id.get(pickup_name.lower())
    drop_zone_id = name_to_id.get(drop_name.lower())
    if pickup_zone_id is None or drop_zone_id is None:
        return jsonify({"error": "Unknown pickup or drop zone name"}), 400

    # Insert into new_rides table and fetch the inserted row
    os.makedirs('data', exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        cur = conn.cursor()
        cur.execute(
            'CREATE TABLE IF NOT EXISTS new_rides ('
            'id INTEGER PRIMARY KEY AUTOINCREMENT,'
            'pickup_time TEXT NOT NULL,'
            'dropoff_time TEXT NOT NULL,'
            'pickup_zone_id INTEGER NOT NULL,'
            'drop_zone_id INTEGER NOT NULL,'
            'no_of_passengers INTEGER NOT NULL)'
        )
        cur.execute(
            'INSERT INTO new_rides (pickup_time, dropoff_time, pickup_zone_id, drop_zone_id, no_of_passengers) '
            'VALUES (?, ?, ?, ?, ?)',
            (pickup_time, drop_time, pickup_zone_id, drop_zone_id, passengers)
        )
        inserted_id = cur.lastrowid
        conn.commit()
        cur.execute('SELECT id, pickup_time, dropoff_time, pickup_zone_id, drop_zone_id, no_of_passengers '
                    'FROM new_rides WHERE id = ?', (inserted_id,))
        row = cur.fetchone()

    # Print/log the inserted row
    logger.info("Inserted new_ride row: %s", row)

    # --- Call the top-k prediction function and return with response ---
    recommendations = []
    try:
        from train_model import get_top3_closest_highprob_zones
        top_df = get_top3_closest_highprob_zones(drop_zone_id, isoparse(drop_time))

        # Build id -> zone name mapping
        id_to_zone = {}
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('SELECT LocationID, zone FROM taxi_zones')
                for loc_id, zone in cur.fetchall():
                    id_to_zone[int(loc_id)] = str(zone)
        except Exception as e:
            logger.warning("Failed reading taxi_zones for name mapping: %s", e)

        for rec in top_df.to_dict(orient='records'):
            zid = int(rec.get('pickup_zone_id')) if rec.get('pickup_zone_id') is not None else None
            recommendations.append({
                "id": zid,
                "name": id_to_zone.get(zid, f"Zone {zid}" if zid is not None else "Unknown"),
                "probability": float(rec.get('probability', 0.0)),
                "distance": float(rec.get('distance', 0.0))
            })

        logger.info("Top recommended zones: %s", recommendations)
        print("Top recommended zones:", recommendations)
    except Exception as e:
        logger.error("Error getting top recommended zones: %s", e)

    # Return the inserted row and recommendations as JSON
    keys = ['id', 'pickup_time', 'dropoff_time', 'pickup_zone_id', 'drop_zone_id', 'no_of_passengers']
    return jsonify({"new_ride": dict(zip(keys, row)), "recommendations": recommendations})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

# Serve React app for all non-API routes
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react(path):
    # Skip static files and API routes
    if path.startswith('static/') or path.startswith('api/') or path.startswith('zones') or path.startswith('complete_ride') or path.startswith('health'):
        # Let Flask handle these routes normally
        return app.send_static_file(path)
    
    # For any other route, serve the React app
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 