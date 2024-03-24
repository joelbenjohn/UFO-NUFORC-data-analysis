import streamlit as st
import pandas as pd
from preprocess import *
import pydeck as pdk
import matplotlib.pyplot as plt
from wordcloud import WordCloud

@st.cache_data
def get_NUFORC_data():
    return get_NUFORC_archive()

@st.cache_data
def get_occurences(_data, grid_size):
    return add_occurrences_based_on_range(_data, grid_size=grid_size)

# Streamlit app
st.title('UFO Sighting Analysis Dashboard')
description = """
## UFO Sighting Analysis Dashboard

Welcome to the UFO Sighting Analysis Dashboard! This interactive web app leverages 
extensive data from the National UFO Reporting Center (NUFORC) archive to bring you 
in-depth insights into UFO sightings across the globe. 
"""
description2 ="""
### What You Can Do:
- **Explore Data**: Navigate through decades of UFO sighting reports, visualized through dynamic maps and charts.
- **Sighting Trends**: Discover trends over time, including peak sighting periods and the evolution of sighting locations.
- **Interactive Map**: Use the interactive map to explore sightings by location. Zoom in and out to see how sightings cluster in different areas.
- **Detailed Analysis**: Click on any point on the map to get detailed information about each sighting, including the observer's description.

This dashboard is designed for enthusiasts, researchers, and the curious alike to explore the intriguing world of UFO sightings. Dive in and uncover patterns, anomalies, and stories hidden within the data!

**Note**: The data presented in this dashboard is collected from public reports and not verified for accuracy. Interpret findings with an open mind.

"""

# Display the description
st.markdown(description)
data = get_NUFORC_data()
# Convert latitude and longitude to float
data['latitude'] = pd.to_numeric(data['latitude'], errors='coerce')
data['longitude'] = pd.to_numeric(data['longitude'], errors='coerce')

# Filter data for the map
map_data = data[['latitude', 'longitude']].dropna()
st.markdown("""
### NUFORC dataset
""")
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
data = get_occurences(data, grid_size)
# Sort the groups by occurrences
sorted_grouped = data.sort_values(by=['occurrences', 'state'], ascending=[False, True])

# Define the map layer with updated occurrences
layer = pdk.Layer(
    'ScatterplotLayer',
    data,
    get_position='[longitude, latitude]',
    get_color='[200, 30, 0, 160]',
    get_radius="radius",
    auto_highlight=True,
    pickable=True,
)

# Define the view state with a rough correlation to the "zoom level", zoom=zoom_level * 2
view_state = pdk.ViewState(latitude=data['latitude'].mean(), longitude=data['longitude'].mean(), zoom = 2)

# Render the map with Pydeck
# Configure tooltips to include datetime_str
tooltip = {
    "html": "<b>Date Time:</b> {datetime_str}<br><b>Duration:</b> {duration (hours/min)}<br><b>Description:</b> {comments}",  # Adjust based on your columns
    "style": {
        "backgroundColor": "steelblue",
        "color": "white"
    }
}
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip=tooltip))

st.markdown("""
### Data sorted by occurences and city
""")
st.dataframe(sorted_grouped)

st.markdown(description2)


st.markdown("""
## Shape Analysis
""")

# Assuming 'data' is your DataFrame
shape_counts = data['shape'].value_counts()
st.bar_chart(shape_counts)

st.markdown("""
## Description Analysis
""")
# keyword = st.text_input("Search descriptions")
# if keyword:
#     filtered_data = data[data['comments'].str.contains(keyword, case=False)]
#     st.write(filtered_data)
# Concatenate all descriptions into a single string
all_descriptions = ' '.join(data['comments'].dropna())

# Generate a word cloud image
wordcloud = WordCloud(background_color='white', 
                      width=1600,  # Increase width
                      height=800,  # Increase height
                      max_font_size=200,  # Adjust font size if needed
                      max_words=200, 
                      contour_width=3, 
                      contour_color='steelblue').generate(all_descriptions)
# Display the generated image:
plt.figure(figsize=(20, 10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')  # Don't show axes for a cleaner look
st.pyplot(plt)  # Use st.pyplot() to display the plot in Streamlit

st.markdown("""
## Duration Analysis
""")
data['duration (seconds)'] = pd.to_numeric(data['duration (seconds)'], errors='coerce')
# duration_log = np.log1p(data['duration (seconds)'])  # Log-transform for better visualization
# Create a histogram with a log-transformed x-axis
plt.figure(figsize=(10, 6))
plt.hist(data['duration (seconds)'], bins=50, color='skyblue', log=True)
plt.xscale('log')  # Log-transform the x-axis
plt.title('Histogram of Log-transformed Duration')
plt.xlabel('Duration (seconds, log scale)')
plt.ylabel('Frequency (log scale)')
st.pyplot(plt)

st.markdown("""
## Datetime Analysis
""")
# Plotting the resampled data
plt.figure(figsize=(10, 6))  # Optional: Adjusts the size of the plot
data.resample('Y', on='datetime').size().plot()
plt.title('UFO Sightings per Year')
plt.ylabel('Number of Sightings')
plt.xlabel('Year')
st.pyplot(plt)