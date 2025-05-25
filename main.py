import os
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import psycopg2
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

# Set page to wide mode
st.set_page_config(layout="wide")

st.header('Карта активных дронов')

# Database connection string
DATABASE_URL = st.secrets["db_url"]

# Define restricted areas
RESTRICTED_AREAS = {
    'akorda': {
        'name': 'Акорда',
        'description': 'Президентский дворец Казахстана',
        'coordinates': [
            [51.1255, 71.4305],  # Northwest
            [51.1255, 71.4355],  # Northeast
            [51.1225, 71.4355],  # Southeast
            [51.1225, 71.4305],  # Southwest
            [51.1255, 71.4305]   # Close the polygon
        ],
        'color': 'red'
    },
    'parliament': {
        'name': 'Парламент',
        'description': 'Здание Парламента Республики Казахстан',
        'coordinates': [
            [51.1275, 71.4455],
            [51.1275, 71.4505],
            [51.1245, 71.4505],
            [51.1245, 71.4455],
            [51.1275, 71.4455]
        ],
        'color': 'red'
    },
    'khan_shater': {
        'name': 'Хан Шатыр',
        'description': 'Торгово-развлекательный центр',
        'coordinates': [
            [51.1305, 71.4055],
            [51.1305, 71.4105],
            [51.1275, 71.4105],
            [51.1275, 71.4055],
            [51.1305, 71.4055]
        ],
        'color': 'orange'
    },
    'bayterek': {
        'name': 'Байтерек',
        'description': 'Национальный символ Казахстана',
        'coordinates': [
            [51.1285, 71.4305],
            [51.1285, 71.4355],
            [51.1255, 71.4355],
            [51.1255, 71.4305],
            [51.1285, 71.4305]
        ],
        'color': 'orange'
    },
    'nazarbayev_center': {
        'name': 'Центр Назарбаева',
        'description': 'Музей и культурный центр',
        'coordinates': [
            [51.1325, 71.4255],
            [51.1325, 71.4305],
            [51.1295, 71.4305],
            [51.1295, 71.4255],
            [51.1325, 71.4255]
        ],
        'color': 'orange'
    },
    'military_base': {
        'name': 'Военная база',
        'description': 'Военное подразделение',
        'coordinates': [
            [51.1355, 71.4155],
            [51.1355, 71.4205],
            [51.1325, 71.4205],
            [51.1325, 71.4155],
            [51.1355, 71.4155]
        ],
        'color': 'red'
    },
    'airport': {
        'name': 'Международный аэропорт',
        'description': 'Аэропорт Нурсултан Назарбаев',
        'coordinates': [
            [51.0225, 71.4655],
            [51.0225, 71.4755],
            [51.0175, 71.4755],
            [51.0175, 71.4655],
            [51.0225, 71.4655]
        ],
        'color': 'red'
    },
    'train_station': {
        'name': 'Железнодорожный вокзал',
        'description': 'Главный железнодорожный вокзал',
        'coordinates': [
            [51.1825, 71.4155],
            [51.1825, 71.4205],
            [51.1795, 71.4205],
            [51.1795, 71.4155],
            [51.1825, 71.4155]
        ],
        'color': 'orange'
    },
    'power_plant': {
        'name': 'ТЭЦ-2',
        'description': 'Теплоэлектроцентраль',
        'coordinates': [
            [51.1925, 71.4255],
            [51.1925, 71.4305],
            [51.1895, 71.4305],
            [51.1895, 71.4255],
            [51.1925, 71.4255]
        ],
        'color': 'red'
    },
    'water_reservoir': {
        'name': 'Водохранилище',
        'description': 'Главное водохранилище города',
        'coordinates': [
            [51.1425, 71.3955],
            [51.1425, 71.4005],
            [51.1395, 71.4005],
            [51.1395, 71.3955],
            [51.1425, 71.3955]
        ],
        'color': 'orange'
    }
}

def remove_drone(drone_id):
    try:
        conn = psycopg2.connect(DATABASE_URL)
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

def add_new_drone(drone_id, latitude, longitude, pilot_id=None):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        insert_query = """
        INSERT INTO drones (drone_id, latitude, longitude, created_at, pilot_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        
        cur.execute(insert_query, (
            drone_id,
            latitude,
            longitude,
            datetime.now(),
            pilot_id
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
        conn = psycopg2.connect(DATABASE_URL)
        
        # Query to get the most recent position for each drone with pilot details
        query = """
        WITH latest_positions AS (
            SELECT DISTINCT ON (drone_id)
                d.drone_id,
                d.latitude,
                d.longitude,
                d.created_at,
                d.pilot_id,
                p.first_name,
                p.last_name,
                p.phone_number
            FROM drones d
            LEFT JOIN pilots p ON d.pilot_id = p.id
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
        return pd.DataFrame(columns=['drone_id', 'latitude', 'longitude', 'created_at', 'pilot_id', 'first_name', 'last_name', 'phone_number'])
    
@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_pilots():
    try:
        conn = psycopg2.connect(DATABASE_URL)
        
        query = """
        SELECT id, first_name, last_name, phone_number
        FROM pilots
        ORDER BY first_name, last_name;
        """
        
        pilots = pd.read_sql_query(query, conn)
        conn.close()
        return pilots
    except Exception as e:
        st.error(f"Error loading pilots: {str(e)}")
        return pd.DataFrame(columns=['id', 'first_name', 'last_name', 'phone_number'])

data = load_data()

# Sidebar form for adding new drones
with st.sidebar:
    st.header("Add New Drone")
    
    # Load pilots for the dropdown
    pilots_df = load_pilots()
    pilot_options = {f"{row['first_name']} {row['last_name']}": row['id'] 
                    for _, row in pilots_df.iterrows()}
    
    # Form for new drone entry
    with st.form("new_drone_form"):
        drone_id = st.text_input("Drone ID", placeholder="DRONE-XXX")
        latitude = st.number_input("Latitude", value=51.1694, format="%.6f")
        longitude = st.number_input("Longitude", value=71.4491, format="%.6f")
        
        # Add pilot selection dropdown
        selected_pilot = st.selectbox(
            "Select Pilot",
            options=["No Pilot"] + list(pilot_options.keys()),
            index=0
        )
        
        submitted = st.form_submit_button("Add Drone")
        
        if submitted:
            if not drone_id:
                st.error("Please enter a Drone ID")
            else:
                # Get pilot_id if a pilot was selected
                pilot_id = None if selected_pilot == "No Pilot" else pilot_options[selected_pilot]
                
                if add_new_drone(drone_id, latitude, longitude, pilot_id):
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
m = folium.Map(location=[51.1694, 71.4491], zoom_start=12)  # Adjusted zoom level to show more areas
marker_cluster = MarkerCluster().add_to(m)

# Add restricted areas
for area_id, area in RESTRICTED_AREAS.items():
    # Create polygon for restricted area
    folium.Polygon(
        locations=area['coordinates'],
        color=area['color'],
        fill=True,
        fill_color=area['color'],
        fill_opacity=0.2,
        popup=folium.Popup(
            f"""
            <div style='width: 200px'>
                <h4>{area['name']}</h4>
                <p>{area['description']}</p>
                <p style='color: {area['color']}; font-weight: bold;'>Ограниченная зона</p>
            </div>
            """,
            max_width=300
        ),
        tooltip=f"Ограниченная зона: {area['name']}"
    ).add_to(m)

# Add markers for each drone
for _, drone in data.iterrows():
    # Create popup content with drone and pilot details
    pilot_info = ""
    if pd.notna(drone['pilot_id']):
        pilot_info = f"""
        <div style='margin-top: 10px; padding-top: 10px; border-top: 1px solid #ccc;'>
            <h4 style='margin: 0 0 5px 0;'>Пилот</h4>
            <p style='margin: 2px 0;'><strong>Имя:</strong> {drone['first_name']} {drone['last_name']}</p>
            <p style='margin: 2px 0;'><strong>Телефон:</strong> {drone['phone_number']}</p>
        </div>
        """
    
    popup_content = f"""
    <div style='width: 200px'>
        <h4>{drone['drone_id']}</h4>
        <p>Latitude: {drone['latitude']:.6f}</p>
        <p>Longitude: {drone['longitude']:.6f}</p>
        <p>Last Update: {drone['created_at'].strftime('%H:%M:%S')}</p>
        {pilot_info}
        <a href="https://www.youtube.com/watch?v=82x5c6JyD4U" target="_blank" 
           style='display: inline-block; background-color: #4CAF50; color: white; padding: 8px 16px; 
           border: none; border-radius: 4px; cursor: pointer; text-decoration: none; text-align: center; width: 100%; margin-top: 10px;'>
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

# Add a legend
legend_html = """
<div style="position: fixed; bottom: 50px; left: 50px; z-index: 1000; background-color: white; padding: 10px; border: 2px solid grey; border-radius: 5px;">
    <p><strong>Ограниченные зоны:</strong></p>
    <p><span style="color: red;">■</span> Высокая опасность</p>
    <p><span style="color: orange;">■</span> Средняя опасность</p>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))