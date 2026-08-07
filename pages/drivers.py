import streamlit as st
from streamlit_echarts import st_echarts
from metrics import load_data, wins_by_gp, average_position, poles_by_gp, points_per_season

df_drivers, df_races, df_driver_standings, df_results = load_data()

st.sidebar.title(":material/filter_alt: Filters", anchor=False)
driver_name = st.sidebar.selectbox(
    "Driver", 
    df_drivers["fullName"].to_numpy()
)
st.title(f"F1 Driver Analysis - {driver_name}", anchor=False)

driver_id = df_drivers[df_drivers["fullName"] == driver_name]["driverId"].item()

won_gp_counts, total_races = wins_by_gp(df_results, df_races, driver_id)
amount_won = won_gp_counts.sum()
pole_counts, total_poles = poles_by_gp(df_results, df_races, driver_id)

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Races Won", value=amount_won, border=True)
col2.metric(label="Win Rate", value=f"{((amount_won/total_races) * 100):.2f}%", border=True)
col3.metric(label="Races Started", value=total_races, border=True)
col4.metric(label="Average Position", value=f"{average_position(driver_id, df_results):.2f}", border=True)

if amount_won >= 1:
    col1, col2 = st.columns(2, vertical_alignment="top", gap="large")
    with col1:
        won_sorted = won_gp_counts.sort_values()
        st_echarts({
            "title": {
              "subtext": f"Wins per Grand Prix ({total_races} races entered)",
              "bottom": 25,
              "subtextStyle": {"fontSize": "14px"}
            },
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"left": 8, "right": 24, "containLabel": True},
            "xAxis": {
                "type": "value",
                "name": "Wins",
                "nameLocation": "middle",
                "minInterval": 1,
                "axisLabel": "Wins"
            },
            "yAxis": {
                "type": "category",
                "data": won_sorted.index.tolist(),
                "axisLabel": {"interval": 0},
            },
            "series": [{
                "type": "bar",
                "data": won_sorted.tolist(),
                "animationDuration": 800,
                "label": {"show": True, "position": "right"},
            }],
        }, height="600px")
    with col2:
        poles_sorted = pole_counts.sort_values()
        st_echarts({
            "title": {
              "subtext": f"Pole Positions per Grand Prix ({total_poles} total)",
              "bottom": 25,
              "subtextStyle": {"fontSize": "14px"}
            },
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"left": 8, "right": 24, "containLabel": True},
            "xAxis": {
                "type": "value",
                "name": "Pole Positions",
                "nameLocation": "middle",
                "minInterval": 1,
                "axisLabel": "Pole Positions"
            },
            "yAxis": {
                "type": "category",
                "data": poles_sorted.index.tolist(),
                "axisLabel": {"interval": 0},
            },
            "series": [{
                "type": "bar",
                "data": poles_sorted.tolist(),
                "animationDuration": 800,
                "label": {"show": True, "position": "right"},
            }],
        }, height="600px")


points = points_per_season(df_results, df_races, driver_id)
st_echarts({
    "title": {
        "subtext": f"{driver_name}'s points per season",
        "bottom": 25,
        "subtextStyle": {"fontSize": "14px"}
    },
    "tooltip": {"trigger": "axis"},
    "xAxis": {
        "type": "category",
        "name": "Year",
        "data": [str(year) for year in points.index],
    },
    "yAxis": {"type": "value", "name": "Points"},
    "series": [{
        "type": "line",
        "data": points.tolist(),
        "smooth": True,
        "areaStyle": {"opacity": 0.15},
        "animationDuration": 800,
    }],
}, height="400px")