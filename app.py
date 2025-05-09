from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import joblib
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load the trained model and encoder
try:
    model = joblib.load('models/demand_predictor.joblib')
    zone_encoder = joblib.load('models/zone_encoder.joblib')
    
    # Load feature list
    with open('models/feature_list.txt', 'r') as f:
        feature_list = f.read().splitlines()
    
    logger.info("Successfully loaded ML model and encoder")
except Exception as e:
    logger.error(f"Error loading ML model or encoder: {str(e)}")
    model = None
    zone_encoder = None
    feature_list = None

def load_rides():
    """Load and preprocess active rides data"""
    try:
        rides_df = pd.read_csv('rides.csv')
        rides_df['pickup_time'] = pd.to_datetime(rides_df['pickup_time'])
        return rides_df
    except Exception as e:
        logger.error(f"Error loading rides data: {str(e)}")
        return pd.DataFrame()

def find_return_matches(drop_location, pickup_location, drop_time, time_window=1.5):
    """Find potential return trip matches"""
    try:
        rides_df = load_rides()
        if rides_df.empty:
            return []

        window_end = pd.to_datetime(drop_time) + timedelta(hours=time_window)
        
        matches = rides_df[
            (rides_df['pickup_zone'] == drop_location) &
            (rides_df['drop_zone'] == pickup_location) &
            (rides_df['pickup_time'] >= pd.to_datetime(drop_time)) &
            (rides_df['pickup_time'] <= window_end)
        ].sort_values('pickup_time')

        return matches.to_dict('records')
    except Exception as e:
        logger.error(f"Error finding return matches: {str(e)}")
        return []

def predict_zone_demand(zone, hour, day_of_week):
    """Predict demand for a given zone at specific time"""
    try:
        if model is None or zone_encoder is None:
            return 0.0
        
        # Create feature vector
        features = pd.DataFrame({
            'pickup_zone_encoded': [zone_encoder.transform([zone])[0]],
            'hour': [hour],
            'day_of_week': [day_of_week],
            'month': [datetime.now().month],
            'is_weekend': [1 if day_of_week in [5, 6] else 0],
            'is_peak_hour': [1 if hour in [8, 9, 17, 18, 19] else 0]
        })
        
        # Ensure features are in the correct order
        features = features[feature_list]
        
        prediction = model.predict(features)[0]
        return float(prediction)
    except Exception as e:
        logger.error(f"Error predicting demand: {str(e)}")
        return 0.0

@app.route('/')
def home():
    """Render the main dashboard"""
    return render_template('index.html')

@app.route('/complete_ride', methods=['POST'])
def complete_ride():
    """Handle ride completion and return suggestions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "error": "No data provided in request"
            }), 400
        
        # Validate required fields
        required_fields = ['cab_id', 'pickup', 'drop', 'drop_time']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}"
            }), 400

        # Validate locations
        valid_locations = ['Delhi', 'Noida', 'Gurgaon', 'Saket', 'Faridabad']
        if data['pickup'] not in valid_locations:
            return jsonify({
                "error": f"Invalid pickup location. Must be one of: {', '.join(valid_locations)}"
            }), 400
        
        if data['drop'] not in valid_locations:
            return jsonify({
                "error": f"Invalid drop location. Must be one of: {', '.join(valid_locations)}"
            }), 400

        if data['pickup'] == data['drop']:
            return jsonify({
                "error": "Pickup and drop locations cannot be the same"
            }), 400

        # Parse drop time
        try:
            drop_time = datetime.fromisoformat(data['drop_time'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({
                "error": "Invalid drop_time format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
            }), 400

        # Look for return trip matches
        matches = find_return_matches(
            data['drop'],
            data['pickup'],
            drop_time
        )

        if matches:
            # Return the best match
            best_match = matches[0]
            return jsonify({
                "status": "match found",
                "ride_details": {
                    "pickup": best_match['pickup_zone'],
                    "drop": best_match['drop_zone'],
                    "pickup_time": best_match['pickup_time'].isoformat(),
                    "passengers": best_match['no_of_passengers']
                }
            })

        # If no match, predict demand for nearby zones
        zones = ['Delhi', 'Noida', 'Gurgaon', 'Saket', 'Faridabad']
        current_hour = drop_time.hour
        current_day = drop_time.weekday()

        predictions = []
        for zone in zones:
            score = predict_zone_demand(zone, current_hour, current_day)
            predictions.append({
                "zone": zone,
                "score": score
            })

        # Sort predictions by score and get top 3
        predictions.sort(key=lambda x: x['score'], reverse=True)
        top_predictions = predictions[:3]

        return jsonify({
            "status": "no match found",
            "suggested_zones": top_predictions
        })

    except Exception as e:
        logger.error(f"Error processing ride completion: {str(e)}")
        return jsonify({
            "error": "Internal server error",
            "details": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "components": {
            "model": "loaded" if model is not None else "not loaded",
            "database": "connected" if not load_rides().empty else "error"
        },
        "timestamp": datetime.now().isoformat()
    }
    return jsonify(status)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 