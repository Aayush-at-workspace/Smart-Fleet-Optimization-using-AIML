import os
import sqlite3
import logging
import pandas as pd


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def load_trips(db_path: str = 'data/data.db') -> pd.DataFrame:
    """Load minimal trip columns needed for feature engineering from SQLite."""
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database not found at {db_path}")
    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT pickup_time, pickup_zone_id, no_of_passengers
            FROM trips
            WHERE pickup_time IS NOT NULL
            """,
            conn
        )
    # Ensure types
    df['pickup_time'] = pd.to_datetime(df['pickup_time'])
    # Coerce passengers to numeric (some sources store as floats)
    df['no_of_passengers'] = pd.to_numeric(df['no_of_passengers'], errors='coerce').fillna(0).astype(int)
    return df


def build_features(trips_df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered features used by the model and analysis.

    Features created:
      - hour: 0-23 extracted from pickup_time
      - day_of_week: 0-6 (Mon=0)
      - month: 1-12
      - is_weekend: 1 if Sat/Sun else 0
      - is_peak_hour: 1 if in typical commute windows else 0
      - pickup_zone_encoded: stable integer encoding of pickup_zone_id
    """
    features_df = trips_df.copy()
    ts = pd.to_datetime(features_df['pickup_time'])
    features_df['hour'] = ts.dt.hour
    features_df['day_of_week'] = ts.dt.dayofweek  # 0=Mon
    features_df['month'] = ts.dt.month
    features_df['is_weekend'] = (features_df['day_of_week'] >= 5).astype(int)
    # Define peak hour windows: 7-10 and 16-20 inclusive of starts
    features_df['is_peak_hour'] = (
        ((features_df['hour'] >= 7) & (features_df['hour'] <= 10)) |
        ((features_df['hour'] >= 16) & (features_df['hour'] <= 20))
    ).astype(int)

    # Encode pickup_zone_id as categorical codes to create a dense integer space
    # Keep a stable mapping by sorting unique values
    unique_zones = pd.Index(sorted(features_df['pickup_zone_id'].dropna().unique()))
    zone_to_code = {zone: code for code, zone in enumerate(unique_zones)}
    features_df['pickup_zone_encoded'] = features_df['pickup_zone_id'].map(zone_to_code).astype('Int64')

    return features_df


def get_model_features(df: pd.DataFrame) -> pd.DataFrame:
    """Return a model-ready feature frame with engineered columns only.

    Columns:
      pickup_zone_encoded, hour, day_of_week, month, is_weekend, is_peak_hour
    """
    cols = ['pickup_zone_encoded', 'hour', 'day_of_week', 'month', 'is_weekend', 'is_peak_hour']
    out = df[cols].dropna().copy()
    # Ensure integer dtypes where applicable
    for c in ['pickup_zone_encoded', 'hour', 'day_of_week', 'month', 'is_weekend', 'is_peak_hour']:
        out[c] = out[c].astype(int)
    return out


def demand_by_zone_for_time(features_df: pd.DataFrame, hour: int, day_of_week: int) -> pd.DataFrame:
    """Aggregate demand for a specific hour and day by pickup zone.

    Returns columns: pickup_zone_id, trip_count, total_passengers
    """
    time_slice = features_df[(features_df['hour'] == hour) & (features_df['day_of_week'] == day_of_week)]
    agg = (
        time_slice
        .groupby('pickup_zone_id')
        .agg(trip_count=('pickup_time', 'count'), total_passengers=('no_of_passengers', 'sum'))
        .reset_index()
        .sort_values('trip_count', ascending=False)
    )
    return agg

def main():
    try:
        logger.info("Loading trips and building features...")
        trips = load_trips('data/data.db')
        features = build_features(trips)
        model_df = get_model_features(features)
        logger.info(f"Engineered features shape: {model_df.shape}")
    except Exception as e:
        logger.error(f"Error in feature engineering: {str(e)}")
        raise


if __name__ == '__main__':
    main()


