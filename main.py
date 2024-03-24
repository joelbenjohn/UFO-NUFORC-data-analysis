import streamlit as st
import pandas as pd
from preprocess import *
import pydeck as pdk


@st.cache_data
def get_NUFORC_data():
    return get_NUFORC_archive()

# Streamlit app
st.title('UFO Sightings Map')
data = get_NUFORC_data()
# Convert latitude and longitude to float
data['latitude'] = pd.to_numeric(data['latitude'], errors='coerce')
data['longitude'] = pd.to_numeric(data['longitude'], errors='coerce')

# Filter data for the map
map_data = data[['latitude', 'longitude']].dropna()

st.dataframe(data.head(5))
# Display map

# Streamlit UI for selecting "zoom level"
zoom_level = st.slider('Degree range', min_value=1.0, max_value=20.0, value=5.0, step = 0.5 )

# Mapping zoom levels to grid sizes (this mapping is hypothetical and should be adjusted based on your data and needs)
# grid_size_mapping = {1: 1.0, 2: 0.5, 3: 0.1, 4: 0.05, 5: 0.01, 6: 0.005, 7: 0.001, 8: 0.0005, 9: 0.0001, 10: 0.00005}
# grid_size = grid_size_mapping[zoom_level]
grid_size = zoom_level
# st.map(map_data)
# Recalculate occurrences based on the selected grid size
data = add_occurrences_based_on_range(data, grid_size=grid_size)
# Sort the groups by occurrences
sorted_grouped = data.sort_values(by=['occurrences', 'state'], ascending=[False, True])
st.dataframe(sorted_grouped)
# Define the map layer with updated occurrences
layer = pdk.Layer(
    'ScatterplotLayer',
    data,
    get_position='[longitude, latitude]',
    get_color='[200, 30, 0, 160]',
    auto_highlight=True,
    pickable=True,
)

# Define the view state with a rough correlation to the "zoom level", zoom=zoom_level * 2
view_state = pdk.ViewState(latitude=data['latitude'].mean(), longitude=data['longitude'].mean())

# Render the map with Pydeck
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{description}"}))

