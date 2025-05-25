import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set page to wide mode
st.set_page_config(layout="wide")

st.title('Active Drones Map')

def generate_fake_drone_data(num_drones=20):
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
# Create a full-width container for the map
with st.container():
    st.map(data, use_container_width=True)

# Add a refresh button
if st.button('Refresh Data'):
    st.cache_data.clear()
    st.rerun()