import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import tensorflow as tf
from folium.plugins import MarkerCluster

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
    # Recompile the model to ensure it is set up correctly
    model.compile(optimizer='adam', loss='mse', metrics=['mse'])
    return model

# Function to get color based on DQN value
def get_color(value):
    if value > 0.8:
        return 'green'
    elif value > 0.6:
        return 'yellow'
    elif value > 0.4:
        return 'orange'
    else:
        return 'red'

# Function to create a map with Folium
def create_map(data, model, filter_colors):
    m = folium.Map(location=[16.4023, 120.596], zoom_start=13)  # Baguio city coordinates
    route_coordinates = []

    # Prepare the batch for predictions
    states = data[['Traffic', 'Passenger Frequency', 'Landmark Proximity']].values.astype(np.float32)
    scores = model.predict(states).flatten()

    green_cluster = []

    for index, row in data.iterrows():
        score = scores[index]
        color = get_color(score)
        route_coordinates.append([row['Latitude'], row['Longitude']])

        if color in filter_colors:
            if color == 'green':
                green_cluster.append([row['Latitude'], row['Longitude']])
                if len(green_cluster) >= 5:
                    folium.CircleMarker(
                        location=np.mean(green_cluster, axis=0).tolist(),
                        radius=10,
                        color='green',
                        popup=f"Green cluster of {len(green_cluster)} points",
                        fill=True
                    ).add_to(m)
                    green_cluster = []
            else:
                if green_cluster:
                    for point in green_cluster:
                        folium.CircleMarker(
                            location=point,
                            radius=5,
                            color='green',
                            fill=True
                        ).add_to(m)
                    green_cluster = []

                folium.CircleMarker(
                    location=[row['Latitude'], row['Longitude']],
                    radius=5,
                    color=color,
                    popup=f"Traffic: {row['Traffic']}, Passenger Frequency: {row['Passenger Frequency']}, Landmark Proximity: {row['Landmark Proximity']}",
                    fill=True
                ).add_to(m)

    # Draw remaining green cluster if any
    if green_cluster:
        for point in green_cluster:
            folium.CircleMarker(
                location=point,
                radius=5,
                color='green',
                fill=True
            ).add_to(m)

    # Draw route line
    if route_coordinates:
        folium.PolyLine(route_coordinates, color="cadetblue", weight=5).add_to(m)

    return m

# Streamlit app layout
st.title('Thesis System Map')

# Dropdown menu for selecting a file
file_options = ['LatriComplete.csv', 'TrancoComplete.csv']
selected_file = st.selectbox('Select a Route File', [None] + file_options)

# Initialize the DQN model
model = load_dqn_model()

# Color filter checkboxes
st.sidebar.title('Filter Circles by Color')
show_green = st.sidebar.checkbox('Show Green Circles', value=True)
show_yellow = st.sidebar.checkbox('Show Yellow Circles', value=True)
show_orange = st.sidebar.checkbox('Show Orange Circles', value=True)
show_red = st.sidebar.checkbox('Show Red Circles', value=True)

# Create a list of colors to filter
filter_colors = []
if show_green:
    filter_colors.append('green')
if show_yellow:
    filter_colors.append('yellow')
if show_orange:
    filter_colors.append('orange')
if show_red:
    filter_colors.append('red')

# Display map
if selected_file:
    data = load_data(selected_file)
    map_ = create_map(data, model, filter_colors)
    folium_static(map_, width=700, height=450)
else:
    # Display default Baguio city map
    map_ = folium.Map(location=[16.4023, 120.596], zoom_start=13)
    folium_static(map_, width=700, height=450)
