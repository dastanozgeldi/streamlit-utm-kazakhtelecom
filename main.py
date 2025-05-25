import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import psycopg2

# Set page to wide mode
st.set_page_config(layout="wide")

st.title('Active Drones Map')

# Database connection parameters
DB_NAME = "drone_db"
DB_USER = "drone_user"
DB_PASSWORD = "drone_password"
DB_HOST = "localhost"
DB_PORT = "5432"

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

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading drone data...')
# Load the drone data
data = load_data()
# Notify the reader that the data was successfully loaded.
data_load_state.text("Done! (using st.cache_data)")

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

# Display the map of all active drones
st.subheader('Map of all active drones')

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
           border: none; border-radius: 4px; cursor: pointer; text-decoration: none; text-align: center;'>
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
    st_folium(m, width="100%", height=600)

# Add a refresh button
if st.button('Refresh Data'):
    st.cache_data.clear()
    st.rerun()