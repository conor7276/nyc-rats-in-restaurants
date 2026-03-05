import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster, FastMarkerCluster
from pathlib import Path



def app() -> None:

    # @st.cache_resource
    def build_map(df):

        rat_map = folium.Map(
            location=[40.7, -74.05],
            tiles="cartodb positron"
        )

        data = df[
            ["latitude", "longitude", "restaurant_name", "address", "result", "inspection_date"]
        ].values.tolist()

        
        rat_file = "https://img.icons8.com/?size=256w&id=vzz0xyvO-UyC&format=png"

        # JS callbacks are very fast
        callback = f"""
                function (row) {{
                    var icon = L.icon({{
                        iconUrl: '{rat_file}',
                        iconSize: [25,25],
                        iconAnchor: [12,12]
                    }});

                    var popup =
                        "<b>" + row[2] + "</b><br>" +
                        row[3] + "<br><hr>" +
                        "<b>Result:</b> " + row[4] + "<br>" +
                        "<b>Date:</b> " + row[5];

                    return L.marker([row[0], row[1]], {{icon: icon}})
                        .bindPopup(popup);
                }}
        """
        FastMarkerCluster(data, callback=callback).add_to(rat_map)

        return rat_map

    st.header("NYC Rodent Inspection Map")
    
    # with st.sidebar:
        
    # Temporary fixed data will have to figure out databricks one day
    data_path = Path(__file__).resolve().parent.parent.parent / "data" / "final_data" / "aggregated_rat_data.csv"

    df = pd.read_csv(data_path)

    df = df.drop_duplicates()

    # Build Map
    rat_map = build_map(df)

    st.write("Below is a map of 500 restaurants that failed rat inspections within the latest dates of day that we have available.")


    st_folium(
        rat_map,
        use_container_width= True,
        returned_objects = []
    )

    
    st.write(
        f"""
        Datasets included below. NYC Open Data Rodent Inspeciton Dataset.

        Source Data: [NYC Open Data Rodent Inspection Data](https://data.cityofnewyork.us/Health/Rodent-Inspection/p937-wjvj/about_data)

        Locations sourced through [Google Maps API](https://developers.google.com/maps/documentation/places/web-service/overview)

        Mapping software [Leaflet](https://leafletjs.com/)

        """)

# idk why it doesn't work without this my other streamlit apps never needed this
app()