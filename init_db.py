import psycopg2
from psycopg2 import sql

# Database connection parameters
DB_NAME = "drone_db"
DB_USER = "drone_user"
DB_PASSWORD = "drone_password"
DB_HOST = "localhost"
DB_PORT = "5432"

def create_database():
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
        
        # Create drones table
        create_table_query = """
        CREATE TABLE IF NOT EXISTS drones (
            id SERIAL PRIMARY KEY,
            drone_id VARCHAR(50) NOT NULL,
            latitude DOUBLE PRECISION NOT NULL,
            longitude DOUBLE PRECISION NOT NULL,
            created_at TIMESTAMP NOT NULL,
            UNIQUE(drone_id, created_at)
        );
        """
        
        cur.execute(create_table_query)
        
        # Commit the changes
        conn.commit()
        
        print("Database and table created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_database() 