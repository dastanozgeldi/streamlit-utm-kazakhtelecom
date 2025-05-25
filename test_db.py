import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

import streamlit as st

DATABASE_URL = st.secrets["db_url"]

def test_connection():
    try:
        # Test connection
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Test if tables exist
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            AND table_name IN ('drones', 'pilots');
        """)
        
        tables = cur.fetchall()
        print("Found tables:", [table[0] for table in tables])
        
        # Test if we can query the tables
        for table in ['drones', 'pilots']:
            cur.execute(f"SELECT COUNT(*) FROM {table};")
            count = cur.fetchone()[0]
            print(f"Number of records in {table}: {count}")
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_connection() 