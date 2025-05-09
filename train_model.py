import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def preprocess_data(df):
    """Preprocess the data with validation and feature engineering"""
    try:
        # Validate required columns
        required_columns = ['pickup_zone', 'pickup_time', 'no_of_bookings']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"Missing required columns. Expected: {required_columns}")
        
        # Convert pickup_time to datetime
        df['pickup_time'] = pd.to_datetime(df['pickup_time'])
        
        # Extract time features
        df['hour'] = df['pickup_time'].dt.hour
        df['day_of_week'] = df['pickup_time'].dt.dayofweek
        df['month'] = df['pickup_time'].dt.month
        
        # Create time-based features
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_peak_hour'] = df['hour'].isin([8, 9, 17, 18, 19]).astype(int)
        
        # Encode zones
        label_encoder = LabelEncoder()
        df['pickup_zone_encoded'] = label_encoder.fit_transform(df['pickup_zone'])
        
        return df, label_encoder
    except Exception as e:
        logger.error(f"Error in preprocessing: {str(e)}")
        raise

def train_demand_predictor():
    try:
        # Create models directory
        os.makedirs('models', exist_ok=True)
        
        # Load and validate data
        logger.info("Loading historical ride data...")
        df = pd.read_csv('historical_rides.csv')
        
        # Preprocess data
        logger.info("Preprocessing data...")
        df, label_encoder = preprocess_data(df)
        
        # Prepare features
        features = [
            'pickup_zone_encoded',
            'hour',
            'day_of_week',
            'month',
            'is_weekend',
            'is_peak_hour'
        ]
        
        X = df[features]
        y = df['no_of_bookings']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        logger.info("Training Random Forest model...")
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate model
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        test_r2 = r2_score(y_test, test_pred)
        
        logger.info(f"Model Performance:")
        logger.info(f"Train RMSE: {train_rmse:.2f}")
        logger.info(f"Test RMSE: {test_rmse:.2f}")
        logger.info(f"Test R2 Score: {test_r2:.2f}")
        
        # Save model and encoder
        logger.info("Saving model and encoder...")
        joblib.dump(model, 'models/demand_predictor.joblib')
        joblib.dump(label_encoder, 'models/zone_encoder.joblib')
        
        # Save feature list for reference
        with open('models/feature_list.txt', 'w') as f:
            f.write('\n'.join(features))
        
        logger.info("Model training completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error during model training: {str(e)}")
        return False

if __name__ == "__main__":
    success = train_demand_predictor()
    if success:
        print("Model training completed successfully!")
    else:
        print("Error occurred during model training. Check logs for details.") 