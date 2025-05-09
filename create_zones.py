import pandas as pd
import os

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Define zones with their boroughs
zones_data = [
    # Manhattan
    ('Manhattan - Downtown', 'Manhattan'),
    ('Manhattan - Midtown', 'Manhattan'),
    ('Manhattan - Upper East Side', 'Manhattan'),
    ('Manhattan - Upper West Side', 'Manhattan'),
    ('Manhattan - Harlem', 'Manhattan'),
    ('Manhattan - Financial District', 'Manhattan'),
    ('Manhattan - Chelsea', 'Manhattan'),
    ('Manhattan - Greenwich Village', 'Manhattan'),
    
    # Brooklyn
    ('Brooklyn - Downtown', 'Brooklyn'),
    ('Brooklyn - Williamsburg', 'Brooklyn'),
    ('Brooklyn - Park Slope', 'Brooklyn'),
    ('Brooklyn - Bay Ridge', 'Brooklyn'),
    ('Brooklyn - Crown Heights', 'Brooklyn'),
    ('Brooklyn - Bushwick', 'Brooklyn'),
    ('Brooklyn - Bedford-Stuyvesant', 'Brooklyn'),
    
    # Queens
    ('Queens - Astoria', 'Queens'),
    ('Queens - Long Island City', 'Queens'),
    ('Queens - Flushing', 'Queens'),
    ('Queens - Jamaica', 'Queens'),
    ('Queens - Forest Hills', 'Queens'),
    ('Queens - Jackson Heights', 'Queens'),
    
    # Bronx
    ('Bronx - South Bronx', 'Bronx'),
    ('Bronx - North Bronx', 'Bronx'),
    ('Bronx - Fordham', 'Bronx'),
    ('Bronx - Pelham Bay', 'Bronx'),
    ('Bronx - Riverdale', 'Bronx'),
    
    # Staten Island
    ('Staten Island - North', 'Staten Island'),
    ('Staten Island - South', 'Staten Island'),
    ('Staten Island - Mid-Island', 'Staten Island'),
]

# Create DataFrame
zones_df = pd.DataFrame(
    [(i + 1, zone, borough) for i, (zone, borough) in enumerate(zones_data)],
    columns=['LocationID', 'zone', 'borough']
)

# Save to CSV
zones_file = os.path.join('data', 'taxi_zones.csv')
zones_df.to_csv(zones_file, index=False)

print(f"Created taxi_zones.csv with {len(zones_df)} zones") 