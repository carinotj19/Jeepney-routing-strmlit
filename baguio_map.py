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
    # Recompile the model to ensure it is set up correctly
    model.compile(optimizer='adam', loss='mse', metrics=['mse'])
    return model

# Function to create a map with Folium
def create_map(data, model):
    m = folium.Map(location=[16.4023, 120.596], zoom_start=13)  # Baguio city coordinates
    route_coordinates = []

    # Prepare the batch for predictions
    states = data[['Traffic', 'Passenger Frequency', 'Landmark Proximity']].values.astype(np.float32)
    scores = model.predict(states)

    for index, row in data.iterrows():
        score = scores[index][0]
        color = 'green' if score > 0.8 else 'yellow' if score > 0.6 else 'orange' if score > 0.4 else 'red'
        route_coordinates.append([row['Latitude'], row['Longitude']])
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=5,
            color=color,
            popup=f"Traffic: {row['Traffic']}, Passenger Frequency: {row['Passenger Frequency']}, Landmark Proximity: {row['Landmark Proximity']}",
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

# Display map
if selected_file:
    data = load_data(selected_file)
    map_ = create_map(data, model)
    folium_static(map_, width=700, height=450)
else:
    # Display default Baguio city map
    map_ = folium.Map(location=[16.4023, 120.596], zoom_start=13)
    folium_static(map_, width=700, height=450)
