import pandas as pd
import streamlit as st

@st.cache_data
def load_data():
    df_drivers = pd.read_csv("./data/drivers.csv")
    df_drivers["fullName"] = df_drivers["forename"] + " " + df_drivers["surname"] 
    return (
        df_drivers,
        pd.read_csv("./data/races.csv"),
        pd.read_csv("./data/driver_standings.csv"),
        pd.read_csv("./data/results.csv"),
    )
df_drivers, df_races, df_driver_standings, df_results = load_data()   
st.title("F1 Data Analysis")
st.sidebar.title(":material/filter_alt: Filters", anchor=False)
driver_name = st.sidebar.selectbox("Driver", df_drivers["fullName"].to_numpy())
driver_id = df_drivers[df_drivers["fullName"] == driver_name]["driverId"].item()

df_driver_results = df_results[df_results["driverId"] == driver_id]
won_race_ids = df_driver_results[df_driver_results["positionOrder"] == 1]["raceId"].to_numpy()
won_gp_counts = df_races[df_races["raceId"].isin(won_race_ids)]["name"].value_counts()
amount_won = (df_driver_results["positionOrder"] == 1).sum()
total_races = len(df_driver_results)

if total_races == 0:
    st.subheader(f"{driver_name} has no race results", anchor=False)
else:
    st.subheader(f"{driver_name} has won {amount_won} of {total_races} races ({((amount_won/total_races) * 100):.2f}%)", anchor=False)
    if amount_won >= 1:
        st.bar_chart(won_gp_counts, horizontal=True, sort=False, x_label="Grand Prix", y_label="Wins")