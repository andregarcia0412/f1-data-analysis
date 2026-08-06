import streamlit as st

st.set_page_config(page_title="F1 Data Analysis", layout="wide", page_icon=":material/sports_motorsports:")

pages = [
    st.Page("pages/drivers.py", title="Drivers", icon=":material/sports_motorsports:"),
    st.Page("pages/races.py", title="Races", icon=":material/sports_score:"),
]
pg = st.navigation(pages)
pg.run()