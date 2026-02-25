import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster
from pathlib import Path



def app() -> None:

    # @st.cache_resource
    def build_map(df):

        # df = df.head(50)


        rat_map = folium.Map(
            location = [40.7, -74.05],
            tiles = "cartodb positron"
        )

        marker_cluster = MarkerCluster().add_to(rat_map)
        rat_icon = folium.CustomIcon(
            icon_image = "icons/rat-emoji_transparent.png",
            icon_size = (25,25),
            icon_anchor = (12,12)
        )

        
        # add icons
        for row in df.itertuples(index=False):
            html = f"""
            <div style="font-family: Arial; font-size: 13px; width: 220px;">
                <b>{row.restaurant_name}</b><br>
                {row.address}<br>
                <hr style="margin: 5px 0;">
                <b>Inspection Result:</b> {row.result}<br>
                <b>Date:</b> {row.inspection_date}
            </div>
            """

            # popup = folium.Popup(html, max_width=300)

            folium.Marker(
                [row.latitude, row.longitude],
                icon = rat_icon,
                popup = html
            ).add_to(marker_cluster)

        return rat_map

    st.header("We got rats at the function")
    
    # with st.sidebar:
        
    # Temporary fixed data will have to figure out databricks one day
    data_path = Path(__file__).resolve().parent.parent.parent / "data" / "final_data" / "aggregated_rat_data.csv"

    df = pd.read_csv(data_path)

    df = df.drop_duplicates()

    # st.dataframe(df)

    # cols = ['latitude', 'longitude', 'address', 'address']

    # df = df[cols]

    rat_map = build_map(df)

    st.write("Below is a map of the restaurants that failed rat inspections within the past week.")


    st_folium(
        rat_map,
        use_container_width= True,
        returned_objects = []
        # height = 500,
        # width = 700
    )

    
    st.write("Datasets included below. \n NYC Open Data Rodent Inspeciton Dataset.")

# idk why it doesn't work without this my other streamlit apps never needed this
app()