import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import tensorflow as tf

# Function to load the CSV file
@st.cache_data
def load_data(file_name):
    data = pd.read_csv(file_name)
    data[['Latitude', 'Longitude']] = data['Coordinates'].str.strip('[]').str.split(',', expand=True).astype(float)
    return data

# Function to load and recompile the DQN model
@st.cache_resource
def load_dqn_model():
    custom_objects = {'mse': tf.keras.losses.MeanSquaredError()}
    model = tf.keras.models.load_model('dqn_model.h5', custom_objects=custom_objects)
    model.compile(optimizer='adam', loss='mse', metrics=['mse'])  # Ensure proper compilation
    return model

# Function to create a map with simplified marker labels
def create_map(data, model):
    m = folium.Map(location=[16.4023, 120.596], zoom_start=13)  # Baguio city coordinates
    route_coordinates = []

    # Prepare predictions
    states = data[['Traffic', 'Passenger Frequency', 'Landmark Proximity']].values.astype(np.float32)
    scores = model.predict(states)

    for index, row in data.iterrows():
        score = scores[index][0]
        if score > 0.8:
            color = 'green'
            label = "Ideal Loading/Unloading Spot"
        elif score > 0.6:
            color = 'yellow'
            label = "Moderate Potential Spot"
        elif score > 0.4:
            color = 'orange'
            label = "Low Potential Spot"
        else:
            color = 'red'
            label = "Not Suitable"

        route_coordinates.append([row['Latitude'], row['Longitude']])
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            color=color,
            popup=f"{label}\nScore: {score:.2f}",
            fill=True,
            fill_opacity=0.8
        ).add_to(m)

    # Draw route line
    if route_coordinates:
        folium.PolyLine(route_coordinates, color="cadetblue", weight=5).add_to(m)

    return m

# Function to create a map with dynamic line coloring
def create_dynamic_map(data, model):
    m = folium.Map(location=[16.4023, 120.596], zoom_start=13)  # Baguio city coordinates

    # Prepare predictions
    states = data[['Traffic', 'Passenger Frequency', 'Landmark Proximity']].values.astype(np.float32)
    scores = model.predict(states)

    # Add markers and store coordinates with scores
    coordinates_with_scores = []
    for index, row in data.iterrows():
        score = scores[index][0]
        color = 'green' if score > 0.8 else 'yellow' if score > 0.6 else 'orange' if score > 0.4 else 'red'
        coordinates_with_scores.append((row['Latitude'], row['Longitude'], color))
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            color=color,
            popup=f"Score: {score:.2f}",
            fill=True,
            fill_opacity=0.8
        ).add_to(m)

    # Draw split-color lines between points
    for i in range(len(coordinates_with_scores) - 1):
        start = coordinates_with_scores[i]
        end = coordinates_with_scores[i + 1]
        midpoint = [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2]

        # First half line (start -> midpoint)
        folium.PolyLine(
            locations=[[start[0], start[1]], midpoint],
            color=start[2],  # Color of the start coordinate
            weight=5
        ).add_to(m)

        # Second half line (midpoint -> end)
        folium.PolyLine(
            locations=[midpoint, [end[0], end[1]]],
            color=end[2],  # Color of the end coordinate
            weight=5
        ).add_to(m)

    return m

# Streamlit app layout
st.set_page_config(page_title="Thesis System Map", layout="wide")
st.title('🚏 Thesis System Map')
st.markdown("Visualize and analyze route data with suitability predictions. Select a file or upload your own to begin!")

# Sidebar for file selection
st.sidebar.header("Route File Options")
file_options = ['Optimized_LatriComplete', 'Optimized_TrancoComplete', 'Unoptimized_LatriComplete', 'Unoptimized_TrancoComplete']
selected_file = st.sidebar.selectbox('Select a Route File', [None] + file_options)

uploaded_file = st.sidebar.file_uploader("Or Upload a CSV File", type=['csv'])

# Initialize the DQN model
with st.spinner("Loading the prediction model..."):
    model = load_dqn_model()

# Display map
if selected_file or uploaded_file:
    try:
        if uploaded_file:
            data = load_data(uploaded_file)
        else:
            data = load_data(selected_file)

        st.subheader("Loaded Data Preview")
        st.dataframe(data.head(), use_container_width=True)

        map_ = create_dynamic_map(data, model)
        st.subheader("Generated Map with Dynamic Lines")
        folium_static(map_, width=900, height=500)
    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Select or upload a route file to display the map.")
    map_ = folium.Map(location=[16.4023, 120.596], zoom_start=13)
    folium_static(map_, width=900, height=500)

# Updated Legend in Sidebar
st.sidebar.markdown("### Marker Legend")
st.sidebar.markdown("""
- 🟢 **Ideal Loading/Unloading Spot (Score > 0.8)**
- 🟡 **Moderate Potential Spot (Score > 0.6)**
- 🟠 **Low Potential Spot (Score > 0.4)**
- 🔴 **Not Suitable (Score ≤ 0.4)**
""")
