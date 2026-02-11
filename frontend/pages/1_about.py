import streamlit as st

def app() -> None:
    st.set_page_config(
        page_title = "About",
        page_icon = "👋"
    )
    st.write("About page.")
    st.sidebar.demo("Hello")