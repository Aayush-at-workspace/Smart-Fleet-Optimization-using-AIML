import os
import logging
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import sqlite3
import geopandas as gpd
from pyproj import Transformer

from feature_engineering import load_trips, build_features

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def build_aggregated_demand(db_path='data/data.db') -> pd.DataFrame:
    trips = load_trips(db_path)
    fe = build_features(trips)
    agg = (
        fe.groupby(['pickup_zone_id', 'hour', 'day_of_week', 'month', 'is_weekend', 'is_peak_hour'])
          .agg(no_of_bookings=('pickup_time', 'count'))
          .reset_index()
    )
    # Create a stable zone encoding for modeling
    unique_zones = pd.Index(sorted(agg['pickup_zone_id'].dropna().unique()))
    zone_to_code = {z: i for i, z in enumerate(unique_zones)}
    code_to_zone = {i: z for z, i in zone_to_code.items()}
    agg['pickup_zone_encoded'] = agg['pickup_zone_id'].map(zone_to_code).astype(int)
    # Ensure correct dtypes
    for c in ['hour', 'day_of_week', 'month', 'is_weekend', 'is_peak_hour']:
        agg[c] = agg[c].astype(int)
    return agg, zone_to_code, code_to_zone


def train_nn(db_path='data/data.db'):
    os.makedirs('models', exist_ok=True)
    logger.info("Building aggregated demand dataset...")
    df, zone_to_code, code_to_zone = build_aggregated_demand(db_path)

    features = ['pickup_zone_encoded', 'hour', 'day_of_week', 'month', 'is_weekend', 'is_peak_hour']
    X = df[features].values
    y = df['no_of_bookings'].values.astype(float)

    logger.info(f"Training set size (aggregated rows): {len(df):,}")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

    # Neural network regressor
    model = MLPRegressor(
        hidden_layer_sizes=(128, 64),
        activation='relu',
        solver='adam',
        learning_rate_init=1e-3,
        max_iter=50,
        early_stopping=True,
        n_iter_no_change=5,
        random_state=42,
        verbose=False
    )

    logger.info("Training neural network...")
    model.fit(X_train, y_train)

    # Evaluate
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
    test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
    test_r2 = r2_score(y_test, test_pred)
    logger.info(f"Train RMSE: {train_rmse:.3f} | Test RMSE: {test_rmse:.3f} | Test R2: {test_r2:.3f}")

    # Save artifacts
    joblib.dump(model, 'models/demand_mlp.joblib')
    joblib.dump(zone_to_code, 'models/zone_to_code.joblib')
    joblib.dump(code_to_zone, 'models/code_to_zone.joblib')
    with open('models/feature_list.txt', 'w') as f:
        f.write('\n'.join(features))
    logger.info("Saved model and mappings to models/")

    return True


def _build_time_feature_rows(dt: datetime, code_to_zone: dict) -> pd.DataFrame:
    hour = dt.hour
    day_of_week = dt.weekday()
    month = dt.month
    is_weekend = 1 if day_of_week >= 5 else 0
    is_peak_hour = 1 if (7 <= hour <= 10) or (16 <= hour <= 20) else 0

    rows = []
    for code in sorted(code_to_zone.keys()):
        rows.append({
            'pickup_zone_encoded': code,
            'hour': hour,
            'day_of_week': day_of_week,
            'month': month,
            'is_weekend': is_weekend,
            'is_peak_hour': is_peak_hour
        })
    return pd.DataFrame(rows)


def predict_top_zones_for_datetime(dt: datetime, top_k: int = 3):
    model = joblib.load('models/demand_mlp.joblib')
    code_to_zone = joblib.load('models/code_to_zone.joblib')
    df = _build_time_feature_rows(dt, code_to_zone)
    features = ['pickup_zone_encoded', 'hour', 'day_of_week', 'month', 'is_weekend', 'is_peak_hour']
    preds = model.predict(df[features].values)
    df['predicted_demand'] = preds
    df['pickup_zone_id'] = df['pickup_zone_encoded'].map(code_to_zone)
    top = df.sort_values('predicted_demand', ascending=False).head(top_k)
    return top[['pickup_zone_id', 'predicted_demand']].reset_index(drop=True)


def get_top3_closest_highprob_zones(drop_zone_id, dt, db_path='data/data.db', top_k=5):
    # Load centroids
    conn = sqlite3.connect(db_path)
    zones_df = pd.read_sql('SELECT LocationID, centroid_lat, centroid_lon FROM taxi_zones', conn)
    conn.close()
    
    # Get model predictions for all zones for the given datetime
    model = joblib.load('models/demand_mlp.joblib')
    code_to_zone = joblib.load('models/code_to_zone.joblib')
    zone_to_code = {v: k for k, v in code_to_zone.items()}
    df = _build_time_feature_rows(dt, code_to_zone)
    features = ['pickup_zone_encoded', 'hour', 'day_of_week', 'month', 'is_weekend', 'is_peak_hour']
    preds = model.predict(df[features].values)
    df['predicted_demand'] = preds
    df['pickup_zone_id'] = df['pickup_zone_encoded'].map(code_to_zone)

    # Convert predictions to probabilities using softmax
    df['probability'] = np.exp(df['predicted_demand']) / np.sum(np.exp(df['predicted_demand']))

    # Ensure pickup_zone_id is integer type to match LocationID
    df['pickup_zone_id'] = df['pickup_zone_id'].astype(int)

    # Merge predictions into zones_df
    zones_df = zones_df.merge(df[['pickup_zone_id', 'predicted_demand',         'probability']],left_on='LocationID', right_on='pickup_zone_id', how='left')
    
    # Fill NaN values for zones not in predictions
    zones_df['predicted_demand'] = zones_df['predicted_demand'].fillna(0)
    zones_df['probability'] = zones_df['probability'].fillna(0)

    # Get the drop zone coordinates
    if drop_zone_id not in zones_df['LocationID'].values:
        raise ValueError(f"Drop zone id {drop_zone_id} not found in centroids.")
    
    drop_lat_raw = zones_df[zones_df['LocationID'] == drop_zone_id]['centroid_lat'].iloc[0]
    drop_lon_raw = zones_df[zones_df['LocationID'] == drop_zone_id]['centroid_lon'].iloc[0]

    # Prepare coordinates in degrees (WGS84). Convert if inputs are projected (e.g., EPSG:2263).
    lat_arr = zones_df['centroid_lat'].to_numpy()
    lon_arr = zones_df['centroid_lon'].to_numpy()

    # Detect non-degree units by range check
    if np.nanmax(np.abs(lat_arr)) > 90 or np.nanmax(np.abs(lon_arr)) > 180:
        transformer = Transformer.from_crs("EPSG:2263", "EPSG:4326", always_xy=True)
        lon_deg, lat_deg = transformer.transform(lon_arr, lat_arr)
        drop_lon_deg, drop_lat_deg = transformer.transform(drop_lon_raw, drop_lat_raw)
    else:
        lat_deg, lon_deg = lat_arr, lon_arr
        drop_lat_deg, drop_lon_deg = drop_lat_raw, drop_lon_raw

    # Calculate distances using haversine formula (in meters)
    def _haversine_m(lat1, lon1, lat2, lon2):
        R = 6371000.0  # Earth radius in meters
        phi1 = np.radians(lat1)
        phi2 = np.radians(lat2)
        dphi = np.radians(lat2 - lat1)
        dlambda = np.radians(lon2 - lon1)
        a = np.sin(dphi / 2.0) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2.0) ** 2
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return R * c

    zones_df['distance'] = _haversine_m(lat_deg,
                                        lon_deg,
                                        drop_lat_deg,
                                        drop_lon_deg)

    # Sort by highest probability, then by distance
    zones_df = zones_df.sort_values(['probability', 'distance'], ascending=[False, True])
    top = zones_df.head(top_k)
    
    return top[['pickup_zone_id', 'probability', 'distance']].reset_index(drop=True)


if __name__ == "__main__":
    ok = train_nn('data/data.db')
    if ok:
        print("Training complete.")
        # Example inference
        result = predict_top_zones_for_datetime(datetime.now(), top_k=3)
        print(result)
    else:
        print("Training failed.")
