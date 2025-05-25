import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import psycopg2
from datetime import datetime

# Set page to wide mode
st.set_page_config(layout="wide")

st.header('Карта активных дронов')

# Database connection parameters
DB_NAME = "drone_db"
DB_USER = "drone_user"
DB_PASSWORD = "drone_password"
DB_HOST = "localhost"
DB_PORT = "5432"

def remove_drone(drone_id):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        cur = conn.cursor()
        
        delete_query = """
        DELETE FROM drones
        WHERE drone_id = %s;
        """
        
        cur.execute(delete_query, (drone_id,))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error removing drone: {str(e)}")
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def add_new_drone(drone_id, latitude, longitude):
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        cur = conn.cursor()
        
        insert_query = """
        INSERT INTO drones (drone_id, latitude, longitude, created_at)
        VALUES (%s, %s, %s, %s)
        """
        
        cur.execute(insert_query, (
            drone_id,
            latitude,
            longitude,
            datetime.now()
        ))
        
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding drone: {str(e)}")
        return False
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_data():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        
        # Query to get the most recent position for each drone
        query = """
        WITH latest_positions AS (
            SELECT DISTINCT ON (drone_id)
                drone_id,
                latitude,
                longitude,
                created_at
            FROM drones
            ORDER BY drone_id, created_at DESC
        )
        SELECT * FROM latest_positions
        ORDER BY created_at DESC;
        """
        
        # Read the query results into a pandas DataFrame
        data = pd.read_sql_query(query, conn)
        
        # Close the connection
        conn.close()
        
        return data
    except Exception as e:
        st.error(f"Error loading drone data from database: {str(e)}")
        return pd.DataFrame(columns=['drone_id', 'latitude', 'longitude', 'created_at'])
    
data = load_data()

# Sidebar form for adding new drones
with st.sidebar:
    st.header("Add New Drone")
    
    # Form for new drone entry
    with st.form("new_drone_form"):
        drone_id = st.text_input("Drone ID", placeholder="DRONE-XXX")
        latitude = st.number_input("Latitude", value=51.1694, format="%.6f")
        longitude = st.number_input("Longitude", value=71.4491, format="%.6f")
        
        submitted = st.form_submit_button("Add Drone")
        
        if submitted:
            if not drone_id:
                st.error("Please enter a Drone ID")
            else:
                if add_new_drone(drone_id, latitude, longitude):
                    st.success(f"Successfully added {drone_id}")
                    st.cache_data.clear()  # Clear cache to refresh the map
                    st.rerun()
    
    st.divider()
    
    # Add drone removal section
    st.header("Remove Drone")
    with st.form("remove_drone_form"):
        drone_to_remove = st.selectbox(
            "Select drone to remove",
            options=data['drone_id'].tolist(),
            key="drone_selector"
        )
        remove_submitted = st.form_submit_button("Remove Selected Drone")
        
        if remove_submitted:
            if remove_drone(drone_to_remove):
                st.success(f"Successfully removed {drone_to_remove}")
                st.cache_data.clear()
                st.rerun()


# Create a map centered on Astana
m = folium.Map(location=[51.1694, 71.4491], zoom_start=12)
marker_cluster = MarkerCluster().add_to(m)

# Add markers for each drone
for _, drone in data.iterrows():
    # Create popup content with drone details and stream button
    popup_content = f"""
    <div style='width: 200px'>
        <h4>{drone['drone_id']}</h4>
        <p>Latitude: {drone['latitude']:.6f}</p>
        <p>Longitude: {drone['longitude']:.6f}</p>
        <p>Last Update: {drone['created_at'].strftime('%H:%M:%S')}</p>
        <a href="https://www.youtube.com/watch?v=hXD8itTKdY0" target="_blank" 
           style='display: inline-block; background-color: #4CAF50; color: white; padding: 8px 16px; 
           border: none; border-radius: 4px; cursor: pointer; text-decoration: none; text-align: center; width: 100%; margin-bottom: 8px;'>
           Stream Video
        </a>
    </div>
    """
    
    folium.Marker(
        location=[drone['latitude'], drone['longitude']],
        popup=folium.Popup(popup_content, max_width=300),
        tooltip=drone['drone_id']
    ).add_to(marker_cluster)

# Display the map
with st.container():
    st_folium(m, width="100%")

# Add a refresh button
if st.button('Refresh Data'):
    st.cache_data.clear()
    st.rerun()