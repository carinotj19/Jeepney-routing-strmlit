import streamlit as st
import pandas as pd

# Initialize session state for data and original snapshot
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=["Coordinates", "Traffic", "Passenger Frequency", "Landmark Proximity"])
if 'original_data' not in st.session_state:
    st.session_state['original_data'] = None

# File upload for existing CSV
st.header("Location Data Management")
uploaded_file = st.file_uploader("Upload CSV File (Coordinates, Traffic, Passenger Frequency, Landmark Proximity)", type=['csv'])

# Load the data if a file is uploaded
if uploaded_file:
    st.session_state['data'] = pd.read_csv(uploaded_file)
    st.session_state['original_data'] = st.session_state['data'].copy()  # Keep a copy of the original data
    st.success("CSV file loaded successfully!")

# Display the current dataset
st.subheader("Current Data")
st.dataframe(st.session_state['data'])

# Input fields for a new or updated entry
st.subheader("Update or Add Entries")
coordinates = st.text_input("Enter Coordinates (e.g., [16.4023,120.596]):", "")

# Input for Traffic as percentage
traffic_percentage = st.number_input(
    "Traffic (%): Enter a value between 0 and 100", 
    value=0, 
    step=1, 
    min_value=0, 
    max_value=100, 
    key="traffic_percentage"
)

# Convert percentage to value between 0 and 1
traffic = traffic_percentage / 100

col1, col2 = st.columns(2)
with col1:
    passenger_frequency = st.number_input("Passenger Frequency", value=0, step=1, key="passenger_frequency")
with col2:
    landmark_proximity = st.number_input("Landmark Proximity (0 or 1)", value=0, step=1, min_value=0, max_value=1, key="landmark_proximity")

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

# Check for changes
def has_changes():
    if st.session_state['original_data'] is None:
        return True  # No original data means everything is a change
    return not st.session_state['data'].equals(st.session_state['original_data'])

# Export updated data
if not st.session_state['data'].empty:
    st.subheader("Export Data")
    if st.button("Export to CSV"):
        if has_changes():
            st.session_state['original_data'] = st.session_state['data'].copy()  # Update original snapshot
            st.session_state['data'].to_csv("updated_coordinates_data.csv", index=False)
            st.success("Data exported as updated_coordinates_data.csv")
        else:
            st.error("No changes detected. Please make changes before exporting.")

    # Provide a download button for the updated data
    if has_changes():
        csv_data = st.session_state['data'].to_csv(index=False)
        st.download_button(
            label="Download Updated CSV",
            data=csv_data,
            file_name="updated_coordinates_data.csv",
            mime="text/csv",
        )
    else:
        st.error("No changes detected. Please make changes before downloading.")
