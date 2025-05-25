import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# Set page to wide mode
st.set_page_config(layout="wide")

st.title('Active Drones Map')

def generate_fake_drone_data(num_drones=200):
    # Base coordinates (Astana, Kazakhstan)
    base_lat = 51.1694
    base_lon = 71.4491
    
    drones = []
    current_time = datetime.now()
    
    for i in range(num_drones):
        # Generate random position within ~10km radius
        lat = base_lat + random.uniform(-0.1, 0.1)
        lon = base_lon + random.uniform(-0.1, 0.1)
        
        # Generate random timestamp within last 5 minutes
        time_offset = random.uniform(0, 300)  # 300 seconds = 5 minutes
        created_at = current_time - timedelta(seconds=time_offset)
        
        drones.append({
            'id': f'DRONE-{i+1:03d}',
            'latitude': lat,
            'longitude': lon,
            'created_at': created_at
        })
    
    return pd.DataFrame(drones)

@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_data():
    try:
        data = generate_fake_drone_data()
        return data
    except Exception as e:
        st.error(f"Error generating drone data: {str(e)}")
        return pd.DataFrame(columns=['id', 'latitude', 'longitude', 'created_at'])

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
        <h4>{drone['id']}</h4>
        <p>Latitude: {drone['latitude']:.6f}</p>
        <p>Longitude: {drone['longitude']:.6f}</p>
        <p>Last Update: {drone['created_at'].strftime('%H:%M:%S')}</p>
        <button onclick='streamVideo("{drone['id']}")' style='background-color: #4CAF50; color: white; padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer;'>Stream Video</button>
    </div>
    """
    
    folium.Marker(
        location=[drone['latitude'], drone['longitude']],
        popup=folium.Popup(popup_content, max_width=300),
        tooltip=drone['id']
    ).add_to(marker_cluster)

# Add JavaScript for the stream button
m.get_root().html.add_child(folium.Element("""
<script>
function streamVideo(droneId) {
    window.open('https://www.youtube.com/watch?v=hXD8itTKdY0', '_blank');
}
</script>
"""))

# Display the map
with st.container():
    st_folium(m, width="100%", height=600)

# Add a refresh button
if st.button('Refresh Data'):
    st.cache_data.clear()
    st.rerun()