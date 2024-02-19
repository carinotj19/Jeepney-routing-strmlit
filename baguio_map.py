import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import ast
import random

# App Title
st.title("Baguio City Route Explorer")

# Right Sidebar for Route Selection
st.sidebar.header("Route Selection")
route_options = ["Route 1: Trancoville Route", "Route 2: La Trinidad Route"] 
selected_route = st.sidebar.selectbox("Choose a route:", route_options) 

def calculate_reward(traffic, passenger_freq, landmark_proximity):
    base_reward = 0  # Initialize

    if traffic == 'high':
        if passenger_freq == 'low':
            base_reward = -5
        elif passenger_freq == 'medium':
            base_reward = -3
    elif traffic == 'low':
        if passenger_freq == 'low':
            base_reward = -1
        elif passenger_freq == 'medium':
            base_reward = 2

    if passenger_freq == 'high':
        if traffic == 'low':
            base_reward = 4 
        else:  # high traffic case 
            base_reward = 0

    if landmark_proximity:
        base_reward += 2

    return base_reward
    
q_table = pd.DataFrame(columns = ['Coordinates', 'Suitability'])

# Function to generate and combine route data
def generate_route_data(route_coordinates):
    route_data = pd.DataFrame(route_coordinates, columns=['Coordinates'])
    route_data['Traffic'] = route_data.apply(lambda row:  random.choice(["low", "medium", "high"]), axis=1)
    route_data['Passenger Frequency'] =  route_data.apply(lambda row:  random.choice(["low", "medium", "high"]), axis=1)
    route_data['Landmark Proximity'] = route_data.apply(lambda row:  random.choice([True, False]), axis=1)
    return route_data

# Update get_coordinates to trigger logic on change
def get_coordinates(selected_route):
    if selected_route == "Route 2: La Trinidad Route":
        data = pd.read_csv('LatriCoords.csv') 
    elif selected_route == "Route 1: Trancoville Route":
        data = pd.read_csv('TrancoCoords.csv') 
    else:
        return None 

    coordinates = data['Coordinates'].apply(ast.literal_eval)
    return generate_route_data(coordinates) 

# Function to draw and update the map 
def draw_map(route_coordinates):
    # Draw new line 
    if route_coordinates is not None:
        folium.PolyLine(route_coordinates, color="cadetblue", weight=5).add_to(map_baguio)

    # Render map using st_folium (updates Folium object within Streamlit)
    st_folium(map_baguio, width=700, height=450)

# Initial coordinates load
route_data = get_coordinates(selected_route)

st.write(route_data.head())
coordinates = route_data["Coordinates"]
st.write(coordinates.head())

for index, row in route_data.iterrows():  
    q_table.loc[len(q_table)] = [row['Coordinates'], 1]
    
# Simplified Q-Learning Training Loop
def train_model(route_data):
    alpha = 0.2  # Learning rate
    gamma = 0.8  # Discount factor
    
    for index, row in route_data.iterrows():
        coord = row['Coordinates']
        current_suitability = q_table.loc[q_table['Coordinates'] == coord, 'Suitability'].values[0]
        
        # Simulated 'Action' - Explore potential suitability
        if random.random() < 0.5:  # 50% chance to mark as non-suitable
            action = 0  # Designate as not suitable
        else:
            action = 1  # Keep as suitable 
        
        reward = calculate_reward(row['Traffic'], row['Passenger Frequency'], row['Landmark Proximity'])

        # Simplified Q-learning update (no 'next state' in our case)
        new_suitability = current_suitability + alpha * (reward - current_suitability) 
        q_table.loc[q_table['Coordinates'] == coord, 'Suitability'] = new_suitability
    
# Center map around Baguio City
baguio_lat = 16.4143
baguio_lon = 120.5988
map_zoom = 14.56

# Create initial map object
map_baguio = folium.Map(location=[baguio_lat, baguio_lon], zoom_start=map_zoom)

draw_map(coordinates) 