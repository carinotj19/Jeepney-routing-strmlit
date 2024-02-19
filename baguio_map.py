import streamlit as st
from streamlit_folium import st_folium
import folium
import pandas as pd
import ast

# App Title
st.title("Baguio City Route Explorer")

# Right Sidebar for Route Selection
st.sidebar.header("Route Selection")
route_options = ["Route 1: Trancoville Route", "Route 2: La Trinidad Route"] 
selected_route = st.sidebar.selectbox("Choose a route:", route_options) 

# Function to get coordinates based on route selection
def get_coordinates(selected_route):
    if selected_route == "Route 2: La Trinidad Route":
        data = pd.read_csv('LatriCoords.csv')
    elif selected_route == "Route 1: Trancoville Route":
        data = pd.read_csv('TrancoCoords.csv') 
    else:
        return None  # Handle invalid route case

    return data['Coordinates'].apply(ast.literal_eval)

# Function to draw and update the map 
def draw_map(route_coordinates):
    # Draw new line 
    if route_coordinates is not None:
        folium.PolyLine(route_coordinates, color="cadetblue", weight=5).add_to(map_baguio)

    # Render map using st_folium (updates Folium object within Streamlit)
    st_folium(map_baguio, width=700, height=450) 

# Initial coordinates load
coordinates = get_coordinates(selected_route)

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
    new_coordinates = get_coordinates(selected_route)
    draw_map(new_coordinates)
