import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import ast
import numpy as np
from stable_baselines3 import DQN

# Load the trained DQN model
model = DQN.load("my_dqn_agent")

# App Title
st.title("Baguio City Route Explorer")

# Right Sidebar for Route Selection
st.sidebar.header("Route Selection")
route_options = ["Route 1: Trancoville Route", "Route 2: La Trinidad Route"]
selected_route = st.sidebar.selectbox("Choose a route:", route_options)

# Function to get coordinates and other data based on route selection
def get_data(selected_route):
    if selected_route == "Route 2: La Trinidad Route":
        data = pd.read_csv('LatriComplete.csv')
    elif selected_route == "Route 1: Trancoville Route":
        data = pd.read_csv('TrancoComplete.csv')
    else:
        return None  # Handle invalid route case

    return data

# Function to preprocess the data and predict top 5 coordinates
def get_top_coordinates(data):
    # Preprocess the data (assuming columns are named correctly)
    features = data[['traffic_volume', 'passenger_frequency', 'landmark_proximity']].values
    # Predict rewards using the DQN model
    rewards = model.predict(features)
    # Sort coordinates based on predicted rewards and select top 5
    top_indices = np.argsort(rewards)[-5:][::-1]  # Top 5 indices with highest rewards
    top_coordinates = data.iloc[top_indices]['Coordinates'].apply(ast.literal_eval).tolist()
    return top_coordinates

# Function to draw and update the map
def draw_map(route_coordinates):
    # Draw new line
    if route_coordinates is not None:
        folium.PolyLine(route_coordinates, color="cadetblue", weight=5).add_to(map_baguio)

    # Render map using st_folium (updates Folium object within Streamlit)
    st_folium(map_baguio, width=700, height=450)

# Initial data load
data = get_data(selected_route)
coordinates = data['Coordinates'].apply(ast.literal_eval)

# Center map around Baguio City
baguio_lat = 16.4143
baguio_lon = 120.5988
map_zoom = 14.56

# Create initial map object
map_baguio = folium.Map(location=[baguio_lat, baguio_lon], zoom_start=map_zoom)

# Initial draw
draw_map(coordinates)

# Streamlit re-run magic - Code below this runs whenever 'selected_route' changes
if selected_route:  # Ensure initial value isn't None
    new_data = get_data(selected_route)
    top_coordinates = get_top_coordinates(new_data)
    draw_map(top_coordinates)
