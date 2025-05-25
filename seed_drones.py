import psycopg2
from datetime import datetime, timedelta
import random

# Database connection parameters
DB_NAME = "drone_db"
DB_USER = "drone_user"
DB_PASSWORD = "drone_password"
DB_HOST = "localhost"
DB_PORT = "5432"

def get_pilot_ids():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        cur = conn.cursor()
        cur.execute("SELECT id FROM pilots;")
        pilot_ids = [row[0] for row in cur.fetchall()]
        
        return pilot_ids
    except Exception as e:
        print(f"Error getting pilot IDs: {e}")
        return []
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def generate_drone_data(num_drones=200):
    # Base coordinates (Astana, Kazakhstan)
    base_lat = 51.1694
    base_lon = 71.4491
    
    # Get available pilot IDs
    pilot_ids = get_pilot_ids()
    if not pilot_ids:
        print("No pilots found in the database. Please run seed_pilots.py first.")
        return []
    
    drones = []
    current_time = datetime.now()
    
    for i in range(num_drones):
        # Generate random position within ~10km radius
        lat = base_lat + random.uniform(-0.1, 0.1)
        lon = base_lon + random.uniform(-0.1, 0.1)
        
        # Generate random timestamp within last 5 minutes
        time_offset = random.uniform(0, 300)  # 300 seconds = 5 minutes
        created_at = current_time - timedelta(seconds=time_offset)
        
        # Randomly assign a pilot
        pilot_id = random.choice(pilot_ids)
        
        drones.append({
            'drone_id': f'DRONE-{i+1:03d}',
            'latitude': lat,
            'longitude': lon,
            'created_at': created_at,
            'pilot_id': pilot_id
        })
    
    return drones

def seed_database():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        # Create a cursor
        cur = conn.cursor()
        
        # Generate drone data
        drones = generate_drone_data()
        if not drones:
            return
        
        # Prepare the insert query
        insert_query = """
        INSERT INTO drones (drone_id, latitude, longitude, created_at, pilot_id)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (drone_id, created_at) DO NOTHING;
        """
        
        # Insert the data
        for drone in drones:
            cur.execute(insert_query, (
                drone['drone_id'],
                drone['latitude'],
                drone['longitude'],
                drone['created_at'],
                drone['pilot_id']
            ))
        
        # Commit the changes
        conn.commit()
        
        print(f"Successfully seeded {len(drones)} drone records!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    seed_database() 