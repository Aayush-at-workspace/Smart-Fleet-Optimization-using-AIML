import pandas as pd
import geopandas as gpd
import requests
import os
import logging
from datetime import datetime
import numpy as np
from tqdm import tqdm
from sqlalchemy import create_engine
from sqlalchemy import text
from dateutil.parser import isoparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NYCTaxiDataProcessor:
    def __init__(self):
        self.data_dir = 'data'
        self.taxi_zones_url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zones.zip"
        self.trip_data_url = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{}.parquet"
        os.makedirs(self.data_dir, exist_ok=True)
        # Initialize SQLite database engine under data/data.db
        self.engine = create_engine(f"sqlite:///{os.path.join(self.data_dir, 'data.db')}")

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
            # Calculate centroids
            zones['centroid_lat'] = zones.geometry.centroid.y
            zones['centroid_lon'] = zones.geometry.centroid.x
            # Persist zones to SQL (replace existing table) with centroids included
            zones_info = zones[['LocationID', 'zone', 'borough', 'centroid_lat', 'centroid_lon']]
            zones_info.to_sql('taxi_zones', self.engine, if_exists='replace', index=False)
            # zones_info.to_csv(os.path.join(self.data_dir, 'taxi_zones.csv'), index=False)
            logger.info(f"Saved {len(zones_info)} taxi zones with centroids")
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
                # Persist combined trips to SQL (replace existing table). CSV writes are intentionally omitted.
                combined_trips.to_sql('trips', self.engine, if_exists='replace', index=False)
                return combined_trips
            else:
                raise Exception("No trip data could be downloaded")
                
        except Exception as e:
            logger.error(f"Error in download_trip_data: {str(e)}")
            raise

    def preview_table(self, table_name='trips'):
        """Print first 10 rows and total count for a table stored in the SQL database"""
        try:
            logger.info(f"Previewing table: {table_name}")
            # Show first 10 rows
            head_df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 10", self.engine)
            pd.set_option('display.max_columns', None)
            print(head_df)
            print("Columns:", head_df.columns)
            # Show total count
            count_df = pd.read_sql(f"SELECT COUNT(*) as count FROM {table_name}", self.engine)
            total = int(count_df['count'].iloc[0])
            print(f"Total rows in {table_name}: {total}")
            return head_df, total
        except Exception as e:
            logger.error(f"Error previewing table '{table_name}': {str(e)}")
            raise

def main():
    try:
        processor = NYCTaxiDataProcessor()
        # Download and process taxi zones
        zones_df = processor.download_taxi_zones()
        # Download recent trip data (last 3 months of 2023 for example)
         trips_df = processor.download_trip_data(year=2023, months=range(10, 13))
        # Preview stored SQL tables
        processor.preview_table('taxi_zones')
        processor.preview_table('trips')
        processor.preview_table('new_rides')
        logger.info("Data preparation completed successfully!")
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise

if __name__ == '__main__':
    main()