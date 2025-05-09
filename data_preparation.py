import pandas as pd
import geopandas as gpd
import requests
import os
import logging
from datetime import datetime
import numpy as np
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NYCTaxiDataProcessor:
    def __init__(self):
        self.data_dir = 'data'
        self.taxi_zones_url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip"
        self.trip_data_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{}.parquet"
        os.makedirs(self.data_dir, exist_ok=True)

    def download_taxi_zones(self):
        """Download NYC taxi zone shapefile"""
        try:
            logger.info("Downloading NYC taxi zones...")
            response = requests.get(self.taxi_zones_url)
            zones_file = os.path.join(self.data_dir, 'taxi_zones.zip')
            
            with open(zones_file, 'wb') as f:
                f.write(response.content)
            
            # Read and process zones
            zones = gpd.read_file(f"zip://{zones_file}")
            zones_info = zones[['LocationID', 'zone', 'borough']]
            zones_info.to_csv(os.path.join(self.data_dir, 'taxi_zones.csv'), index=False)
            logger.info(f"Saved {len(zones_info)} taxi zones")
            return zones_info
        except Exception as e:
            logger.error(f"Error downloading taxi zones: {str(e)}")
            raise

    def download_trip_data(self, year=2023, months=range(1, 13)):
        """Download NYC yellow taxi trip data for specified months"""
        try:
            all_trips = []
            
            for month in tqdm(months, desc="Downloading trip data"):
                date_str = f"{year}-{month:02d}"
                url = self.trip_data_url.format(date_str)
                
                try:
                    df = pd.read_parquet(url)
                    
                    # Select relevant columns and rename
                    df = df[[
                        'tpep_pickup_datetime',
                        'tpep_dropoff_datetime',
                        'PULocationID',
                        'DOLocationID',
                        'passenger_count'
                    ]].rename(columns={
                        'tpep_pickup_datetime': 'pickup_time',
                        'tpep_dropoff_datetime': 'dropoff_time',
                        'PULocationID': 'pickup_zone_id',
                        'DOLocationID': 'drop_zone_id',
                        'passenger_count': 'no_of_passengers'
                    })
                    
                    all_trips.append(df)
                    logger.info(f"Downloaded data for {date_str}")
                    
                except Exception as e:
                    logger.error(f"Error downloading data for {date_str}: {str(e)}")
                    continue
            
            if all_trips:
                combined_trips = pd.concat(all_trips, ignore_index=True)
                return combined_trips
            else:
                raise Exception("No trip data could be downloaded")
                
        except Exception as e:
            logger.error(f"Error in download_trip_data: {str(e)}")
            raise

    def process_trip_data(self, trips_df, zones_df):
        """Process and clean the trip data"""
        try:
            logger.info("Processing trip data...")
            
            # Merge with zone information
            trips_df = trips_df.merge(
                zones_df[['LocationID', 'zone']].rename(columns={'LocationID': 'pickup_zone_id', 'zone': 'pickup_zone'}),
                on='pickup_zone_id'
            ).merge(
                zones_df[['LocationID', 'zone']].rename(columns={'LocationID': 'drop_zone_id', 'zone': 'drop_zone'}),
                on='drop_zone_id'
            )
            
            # Add temporal features
            trips_df['hour'] = trips_df['pickup_time'].dt.hour
            trips_df['day_of_week'] = trips_df['pickup_time'].dt.dayofweek
            
            # Group by pickup zone, drop zone, hour, and day of week to get demand patterns
            demand_patterns = trips_df.groupby(
                ['pickup_zone', 'drop_zone', 'hour', 'day_of_week']
            ).agg({
                'pickup_time': 'count',  # Count trips as demand
                'no_of_passengers': 'mean'
            }).reset_index()
            
            demand_patterns.rename(columns={'pickup_time': 'no_of_bookings'}, inplace=True)
            
            # Save processed data
            demand_patterns.to_csv(os.path.join(self.data_dir, 'historical_rides.csv'), index=False)
            trips_df.to_csv(os.path.join(self.data_dir, 'current_rides.csv'), index=False)
            
            logger.info(f"Processed {len(trips_df)} trips into {len(demand_patterns)} demand patterns")
            return demand_patterns
            
        except Exception as e:
            logger.error(f"Error processing trip data: {str(e)}")
            raise

    def create_sample_current_rides(self, zones_df, n_samples=1000):
        """Create sample current rides based on zone patterns"""
        try:
            logger.info("Generating sample current rides...")
            
            zones = zones_df['zone'].unique()
            now = pd.Timestamp.now()
            
            current_rides = []
            for _ in range(n_samples):
                pickup_zone = np.random.choice(zones)
                drop_zone = np.random.choice([z for z in zones if z != pickup_zone])
                
                # Random time in next 24 hours
                pickup_time = now + pd.Timedelta(minutes=np.random.randint(0, 24*60))
                
                current_rides.append({
                    'pickup_zone': pickup_zone,
                    'drop_zone': drop_zone,
                    'pickup_time': pickup_time,
                    'no_of_passengers': np.random.randint(1, 5)
                })
            
            current_rides_df = pd.DataFrame(current_rides)
            current_rides_df.to_csv(os.path.join(self.data_dir, 'rides.csv'), index=False)
            logger.info(f"Generated {len(current_rides_df)} sample current rides")
            
        except Exception as e:
            logger.error(f"Error creating sample rides: {str(e)}")
            raise

def main():
    try:
        processor = NYCTaxiDataProcessor()
        
        # Download and process taxi zones
        zones_df = processor.download_taxi_zones()
        
        # Download recent trip data (last 3 months of 2023 for example)
        trips_df = processor.download_trip_data(
            year=2023,
            months=range(10, 13)  # October to December
        )
        
        # Process historical data
        demand_patterns = processor.process_trip_data(trips_df, zones_df)
        
        # Create sample current rides
        processor.create_sample_current_rides(zones_df)
        
        logger.info("Data preparation completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == '__main__':
    main() 