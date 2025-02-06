
import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import folium
from streamlit_folium import folium_static

# Initialize session state for data and original snapshot
if 'data' not in st.session_state:
    st.session_state['data'] = None
if 'selected_row' not in st.session_state:
    st.session_state['selected_row'] = None

# File upload for existing CSV
st.header("Location Data Management")
st.sidebar.link_button("Thesis System Map", "https://jeepney-routing-strmlit.streamlit.app/?fbclid=IwY2xjawIRNkZleHRuA2FlbQIxMQABHboDvMHusZdk2aX-YbJULluBwnEKYJY7aAhmisHDN-HL9XKlYJKfqu3ogw_aem_cL0skWZ7SPI2Dmb4ol8kwA")
uploaded_file = st.file_uploader("Upload CSV File (Coordinates, Traffic, Passenger Frequency, Landmark Proximity)", type=['csv'])

# Ensure the uploaded file is processed and updates session state immediately
if uploaded_file is not None:
    if 'uploaded_file_name' not in st.session_state or st.session_state['uploaded_file_name'] != uploaded_file.name:
        try:
            st.session_state['data'] = pd.read_csv(uploaded_file)  # Load CSV into session state
            st.session_state['uploaded_file_name'] = uploaded_file.name  # Store the file name to avoid reprocessing
            st.success("CSV file loaded successfully!")
        except Exception as e:
            st.error(f"Error processing file: {e}")
else:
    st.session_state['data'] = None
    st.session_state['uploaded_file_name'] = None
    st.warning("No file uploaded. Please upload a file to view data.")

if st.session_state['data'] is not None and not st.session_state['data'].empty:
    # Display the current dataset with AgGrid
    st.subheader("Current Data")
    gb = GridOptionsBuilder.from_dataframe(st.session_state['data'])
    gb.configure_selection("single", use_checkbox=True)  # Enable single row selection with checkboxes
    grid_options = gb.build()
    
    grid_response = AgGrid(
        st.session_state['data'],
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,  # Trigger updates on selection change
        enable_enterprise_modules=False,
        height=300,  # Adjust height as needed
        theme="streamlit"  # Optional themes: "streamlit", "light", "dark"
    )
    # Capture the selected row
    selected = grid_response['selected_rows'] if 'selected_rows' in grid_response else None

    if isinstance(selected, pd.DataFrame) and not selected.empty:
        st.session_state['selected_row'] = selected.iloc[0].to_dict()
    else:
        st.session_state['selected_row'] = None  # Reset if no row is selected

# Scroll down and populate the fields when a row is selected
if st.session_state['selected_row']:
    selected_coords = eval(st.session_state['selected_row']['Coordinates'])  # Convert string to list
    st.subheader("Map View of Selected Location")
    
    # Create a Folium map
    m = folium.Map(location=selected_coords, zoom_start=24)
    folium.Marker(
        location=selected_coords,
        popup=f"Selected Coordinate: {selected_coords}",
        icon=folium.Icon(color="red")
    ).add_to(m)

    # Render the map in Streamlit
    folium_static(m, width=700, height=200)
    
    st.subheader("Update or Add Entries")

    # Populate the form fields with the selected row's values
    coordinates = st.text_input(
        "Enter Coordinates (e.g., [16.4023,120.596]):", 
        value=st.session_state['selected_row']['Coordinates'] if st.session_state['selected_row'] else ""
    )

    # Input for Traffic as percentage
    traffic_percentage = st.number_input(
        "Traffic (%): Enter a value between 0 and 100", 
        value=int(st.session_state['selected_row']['Traffic'] * 100) if st.session_state['selected_row'] else 0,
        step=1, 
        min_value=0, 
        max_value=100
    )

    # Convert percentage back to the range of 0–1
    traffic = traffic_percentage / 100

    col1, col2 = st.columns(2)
    with col1:
        passenger_frequency = st.number_input(
            "Passenger Frequency", 
            value=st.session_state['selected_row']['Passenger Frequency'] if st.session_state['selected_row'] else 0, 
            step=1
        )
    with col2:
        landmark_proximity = st.checkbox(
            "Landmark Proximity", 
            value=bool(st.session_state['selected_row']['Landmark Proximity']) if st.session_state['selected_row'] else False
        )

    # Add or update entry
    if st.button("Update/Add Entry"):
        if coordinates.strip():
            # Check if the coordinates already exist
            existing_row = st.session_state['data']['Coordinates'] == coordinates
            if existing_row.any():
                # Update the existing row
                st.session_state['data'].loc[existing_row, "Traffic"] = traffic
                st.session_state['data'].loc[existing_row, "Passenger Frequency"] = passenger_frequency
                st.session_state['data'].loc[existing_row, "Landmark Proximity"] = landmark_proximity
                st.success(f"Updated data for coordinates: {coordinates}")
            else:
                # Add a new row
                new_row = {
                    "Coordinates": coordinates,
                    "Traffic": traffic,
                    "Passenger Frequency": passenger_frequency,
                    "Landmark Proximity": landmark_proximity
                }
                st.session_state['data'] = pd.concat([st.session_state['data'], pd.DataFrame([new_row])], ignore_index=True)
                st.success(f"Added new entry for coordinates: {coordinates}")
        else:
            st.error("Please enter valid coordinates.")

# Export updated data
if st.session_state['data'] is not None and not st.session_state['data'].empty:
    st.subheader("Export Data")
    if st.button("Export to CSV"):
        st.session_state['data'].to_csv("updated_coordinates_data.csv", index=False)
        st.success("Data exported as updated_coordinates_data.csv")
