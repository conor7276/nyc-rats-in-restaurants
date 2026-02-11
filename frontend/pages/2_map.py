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

    rat_map = folium.Map(location = [40.7, -74.05])


    # add icons
    for row in df.iterrows():

        rat_icon = folium.CustomIcon(
        icon_image = "icons/rat-emoji.jpg",
        icon_size = (25,25),
        icon_anchor = ([row[1]['latitude'], row[1]['longitude']])
        )

        folium.Marker(
            [row[1]['latitude'], row[1]['longitude']],
            # icon = rat_icon,
            popup = row[1]['address']
        ).add_to(rat_map)

    st_folium(rat_map, height = 500, width = 700)
    

    st.dataframe(df)


# idk why it doesn't work without this my other streamlit apps never needed this
app()