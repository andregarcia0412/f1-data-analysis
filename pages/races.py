import streamlit as st
from metrics import load_data, top_gp_winner, fastest_time

df_drivers, df_races, df_driver_standings, df_results = load_data()

st.sidebar.title(":material/filter_alt: Filters", anchor=False)
gp_name = st.sidebar.selectbox(
    "Grand Prix", 
    df_races["name"].drop_duplicates().to_numpy()
)
st.title(f"F1 Grand Prix Analysis - {gp_name}", anchor=False)

top_wins, top_winner = top_gp_winner(df_results, df_races, df_drivers, gp_name)
fastest_lap_time, fastest_lap_driver = fastest_time(df_results, df_races, df_drivers, gp_name)

col1, col2, col3, col4 = st.columns(4, vertical_alignment="center")

col1.metric(label="Driver with most wins", value=top_wins, delta_description=top_winner, border=True)
col2.metric(label="Fastest Lap", value=fastest_lap_time, delta_description=fastest_lap_driver, border=True, help="Based on race sessions only; practice and qualifying are excluded.")