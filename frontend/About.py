import streamlit as st

st.set_page_config(
    page_title="Rats in Restaurants",
    page_icon = "🐀"
)
st.header("NYC Rats in Restuarants.")

st.write("NYC is known for its food worldwide, it is also known for its abundance of rats" \
"This dashboard shows what restaurants have recently failed rodent inspections using NYC" \
"Open Data's Rodent Inspection dataset that can be viewed below combined with Google Maps API's " \
"to tell which address' are restaurants or not.")
st.write("Rats in the room.")

st.sidebar.success("Select a Page")