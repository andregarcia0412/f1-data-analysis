import streamlit as st
from metrics import load_data, wins_by_gp, average_position, poles_by_gp

df_drivers, df_races, df_driver_standings, df_results = load_data()

st.sidebar.title(":material/filter_alt: Filters", anchor=False)
driver_name = st.sidebar.selectbox(
    "Driver", 
    df_drivers["fullName"].to_numpy()
)
st.title(f"F1 Data Analysis - {driver_name}", anchor=False)

driver_id = df_drivers[df_drivers["fullName"] == driver_name]["driverId"].item()

won_gp_counts, total_races = wins_by_gp(df_results, df_races, driver_id)
amount_won = won_gp_counts.sum()
pole_counts, total_poles = poles_by_gp(df_results, df_races, driver_id)

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Races Won", value=amount_won, border=True)
col2.metric(label="Win Rate", value=f"{((amount_won/total_races) * 100):.2f}%", border=True)
col3.metric(label="Races Started", value=total_races, border=True)
col4.metric(label="Average Position", value=f"{average_position(driver_id, df_results):.2f}", border=True)

st.space()

if amount_won >= 1:
    col1, col2 = st.columns(2, vertical_alignment="top", gap="large")
    with col1:
        st.bar_chart(won_gp_counts, horizontal=True, sort=False, x_label="Grand Prix", y_label="Wins", height=500)
        st.caption(
            f"Wins per Grand Prix ({total_races} races entered)",
            width="stretch",
            text_alignment="left",
        )
    with col2:
        st.bar_chart(pole_counts, horizontal=True, sort=False, x_label="Grand Prix", y_label="Pole Positions", height=500)
        st.caption(
            f"Pole Positions per Grand Prix ({total_poles} total)",
            width="stretch",
            text_alignment="left"
        )