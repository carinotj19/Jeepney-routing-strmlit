Industry-Style System Documentation
1. Overview

    **Project Name:**  
    REFINING JEEPNEY LOADING AND UNLOADING ZONES IN BAGUIO CITY AND LA TRINIDAD:
    A REINFORCEMENT LEARNING APPROACH FOR ALLEVIATING TRAFFIC CONGESTION

    **Purpose & Goals:**  
    - Provide designated loading and unloading zones for jeepneys without impeding traffic flow.
    - Use a reinforcement learning approach to calculate a suitability score based on traffic, passenger frequency, and landmark proximity.
    - Enable users to manage data (CSV format) and visualize ideal routes on a map.

    **Applications:**  
    - **Counter Application:**  
      - Allows users to edit, add, alter, and delete rows in a CSV dataset.
      - Exports the edited data as CSV files.
      - Currently supports CSV input and output only.
    - **Jeepney Routing Application:**  
      - Processes the CSV data provided from the counter app.
      - Calculates a custom suitability score for each coordinate using three parameters:
        - Traffic
        - Passenger frequency
        - Landmark proximity
      - Displays a map (using Folium) showing road segments classified from “ideal” to “not suitable”.
    
2. System Architecture & Integration

    **Overall Architecture:**  
    - The two applications are built using Streamlit but function independently.
    - The counter app generates and modifies CSV files that the routing application reads.

    **Technology Stack:**
    - **Programming Language:** Python
    - **Framework:** Streamlit
    - **Libraries & Dependencies:** streamlit, pandas, numpy, folium, streamlit-folium, tensorflow
    
3. Installation & Setup

    **Prerequisites:**  
    - Python (version 3.8 or higher recommended)
    - Pip for installing dependencies

    **Installation Steps:**  
    1. Clone the repository:
       ```bash
       git clone <repository_url>
       cd <repository_folder>
       ```
    2. Set up a virtual environment:
       ```bash
       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate
       ```
    3. Install dependencies:
       ```bash
       pip install -r requirements.txt
       ```
    
4. Usage Guide

    **Counter Application:**  
    - Launch with:
      ```bash
      streamlit run counter_app.py
      ```
    - Upload/edit/export CSV data.

    **Jeepney Routing Application:**  
    - Launch with:
      ```bash
      streamlit run jeepney_routing_app.py
      ```
    - Load CSV, compute suitability scores, and display results on an interactive map.
    
5. Troubleshooting & FAQ

    **Common Issues:**  
    - CSV file format errors: Ensure correct headers and data format.
    - Application launch failures: Verify dependencies are installed and virtual environment is activated.
    - Map display issues: Check Folium and streamlit-folium installations.
    
6. Change Log & Version History

    **Version 1.0 (YYYY-MM-DD):**  
    - Initial release of both applications.
    - Basic CSV management and suitability scoring implemented.
    
7. Appendices

    **Sample CSV Format:**
    ```csv
    latitude,longitude,traffic,passenger_frequency,landmark_proximity
    16.4023,120.5960,High,Medium,Close
    16.4030,120.5970,Medium,High,Far
    ```

    **External Resources:**  
    - [Streamlit Documentation](https://docs.streamlit.io/)
    - [Folium Documentation](https://python-visualization.github.io/folium/)
    - [TensorFlow Documentation](https://www.tensorflow.org/)
    
