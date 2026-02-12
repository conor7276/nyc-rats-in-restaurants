import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import folium
from pathlib import Path



def app() -> None:

    st.header("We got rats at the function")
    
    # with st.sidebar:
        
    # Temporary fixed data will have to figure out databricks one day
    data_path = Path(__file__).resolve().parent.parent.parent / "data" / "intermediate_data" / "data_2025-12-15_2025-12-21.csv"

    df = pd.read_csv(data_path)

    cols = ['latitude', 'longitude', 'address', 'displayName']

    df = df[cols]

    rat_map = folium.Map(
        location = [40.7, -74.05],
        tiles = "cartodb positron"
    )


    # add icons
    for row in df.iterrows():

        rat_icon = folium.CustomIcon(
        icon_image = "icons/rat-emoji_transparent.png",
        icon_size = (25,25),
        icon_anchor = (12,12)
        )

        # html = f"""
        # <div style="font-family: Arial; font-size: 13px; width: 220px;">
        #     <b>{row[1]['restaurant_name']}</b><br>
        #     {row[1]['address']}<br>
        #     <hr style="margin: 5px 0;">
        #     <b>Inspection Result:</b> {row[1]['result']}<br>
        #     <b>Date:</b> {row[1]['inspection_date']}
        # </div>
        # """

        # popup = folium.Popup(html, max_width=300)

        folium.Marker(
            [row[1]['latitude'], row[1]['longitude']],
            icon = rat_icon,
            # popup = popup
        ).add_to(rat_map)


    st.write("Below is a map of the restaurants that failed rat inspections within the past week.")
    st_folium(rat_map, height = 500, width = 700)

    

    st.dataframe(df)
    st.write("Datasets included below. \n NYC Open Data Rodent Inspeciton Dataset.")

# idk why it doesn't work without this my other streamlit apps never needed this
app()