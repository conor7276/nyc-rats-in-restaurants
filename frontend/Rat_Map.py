import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster, FastMarkerCluster
from pathlib import Path
import os
from dotenv import load_dotenv, dotenv_values
import argparse


# Load CARTO API KEY
secrets_path = os.path.join(Path.cwd().parent, "secrets.env")
local_check = load_dotenv(secrets_path)

# For local testing
if local_check == True:
    local_creds = dotenv_values(secrets_path)
    CARTO_API_KEY = local_creds['CARTO_API_KEY']
# For deployment
else:
    CARTO_API_KEY = os.getenv('CARTO_API_KEY')

    if not CARTO_API_KEY:
        raise "API KEY failed to load"


def app() -> None:

    st.set_page_config(
        page_title="Rats in Restaurants",
        page_icon = "🐀"
    )

    def build_map(df):

        rat_map = folium.Map(
            location=[40.7, -74.05]
        )

        folium.TileLayer(
            tiles = f"https://basemaps.cartocdn.com/rastertiles/light_all/{{z}}/{{x}}/{{y}}{{r}}.png?key={CARTO_API_KEY}",
            attr='© <a href="https://carto.com/attributions">CARTO</a>, © OpenStreetMap contributors',
            name = "CARTODB Positron"
        ).add_to(rat_map)

        data = df[
            ["lat", "lon", "name", "address", "neighborhood", "type", "result", "inspection_date"]
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
                        row[3] + "<br>" + row[4] + "<br>" +
                        "<b>Type:</b> " + row[5] + "<br>" +
                        "<b>Result:</b> " + row[6] + "<br>" +
                        "<b>Date:</b> " + row[7];

                    return L.marker([row[0], row[1]], {{icon: icon}})
                        .bindPopup(popup);
                }}
        """
        FastMarkerCluster(data, callback=callback).add_to(rat_map)

        return rat_map

    st.header("NYC Rodent Inspection Map")
        
    data_path = Path(__file__).resolve().parent.parent / "data" / "final_data" / "final_rat_data.csv"

    df = pd.read_csv(data_path)

    df = df.drop_duplicates()

    # Build Map
    rat_map = build_map(df)

    st.write("""   
        NYC is known for its food worldwide, it is also known for its abundance of rats. 
        This dashboard shows what restaurants have recently failed rodent inspections using NYC 
        Open Data's Rodent Inspection dataset that can be viewed below combined with Geoapify's Places API
        to tell which addreses are restaurants or not. Below is a map of the most recent restaurants
        that failed rat inspections within the latest days we have available.     
            """)


    st_folium(
        rat_map,
        use_container_width= True,
        returned_objects = []
    )

    
    st.write(
        f"""
        Datasets included below. NYC Open Data Rodent Inspeciton Dataset.

        Source Data: [NYC Open Data Rodent Inspection Data](https://data.cityofnewyork.us/Health/Rodent-Inspection/p937-wjvj/about_data)

        Locations sourced through [Geoapify](https://www.geoapify.com/maps-api/)

        Mapping software [Leaflet](https://leafletjs.com/)
                 
        **Don't forget to check out my other projects!**
            
        [Github](https://github.com/conor7276)
            
        [Linkedin](https://www.linkedin.com/in/conor7276)

        """)

# idk why it doesn't work without this my other streamlit apps never needed this
app()