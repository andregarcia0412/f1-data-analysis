import streamlit as st
from streamlit_echarts import st_echarts
from metrics import (
    load_data,
    top_gp_winner,
    fastest_time,
    fastest_speed_recorded,
    yearly_fastest_lap,
)

df_drivers, df_races, df_driver_standings, df_results, _ = load_data()

st.sidebar.title(":material/filter_alt: Filters", anchor=False)
gp_name = st.sidebar.selectbox(
    "Grand Prix", df_races["name"].drop_duplicates().to_numpy()
)
st.title(f"F1 Grand Prix Analysis - {gp_name}", anchor=False)

top_wins, top_winner = top_gp_winner(df_results, df_races, df_drivers, gp_name)
fastest_lap_time, fastest_lap_driver = fastest_time(
    df_results, df_races, df_drivers, gp_name
)
fastest_lap_speed, fastest_driver = fastest_speed_recorded(
    df_results, df_races, df_drivers, gp_name
)

col1, col2, col3, col4 = st.columns(4, vertical_alignment="center")

col1.metric(
    label="Driver with most wins",
    value=top_wins,
    delta_description=top_winner,
    border=True,
)
col2.metric(
    label="Fastest Lap",
    value=fastest_lap_time if fastest_lap_time is not None else "-",
    delta_description=(fastest_lap_driver if fastest_lap_driver is not None else "-"),
    border=True,
    help="Based on race sessions only; practice and qualifying are excluded.",
)
col3.metric(
    label="Fastest Lap Speed",
    value=fastest_lap_speed if fastest_lap_speed is not None else "-",
    delta_description=fastest_driver if fastest_driver is not None else "-",
    border=True,
    help="Based on race sessions only; practice and qualifying are excluded.",
)

years, laps = yearly_fastest_lap(df_results, df_races, gp_name)
if len(years) > 0 and len(laps) > 0:
    st_echarts(
        {
            "title": {
                "subtext": f"{gp_name} fastest lap time evolution",
                "bottom": 25,
                "subtextStyle": {"fontSize": "14px"},
            },
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "name": "Year",
                "data": years,
            },
            "yAxis": {"type": "value", "name": "Lap time (s)"},
            "series": [
                {
                    "type": "line",
                    "data": laps,
                    "smooth": True,
                    "areaStyle": {"opacity": 0.15},
                    "animationDuration": 800,
                }
            ],
        },
        height="400px",
    )
