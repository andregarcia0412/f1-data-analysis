import pandas as pd
import streamlit as st

df_drivers = pd.read_csv("./data/drivers.csv")
df_races = pd.read_csv("./data/races.csv")
df_driver_standings = pd.read_csv("./data/driver_standings.csv")
df_results = pd.read_csv("./data/results.csv")

df_drivers["fullName"] = df_drivers["forename"] + " " + df_drivers["surname"]
driver_name = st.selectbox("Driver", df_drivers["fullName"].to_numpy())
driver_id = df_drivers[df_drivers["fullName"] == driver_name]["driverId"].item()

df_driver_results = df_results[df_results["driverId"] == driver_id]
won_race_ids = df_driver_results[df_driver_results["positionOrder"] == 1]["raceId"].to_numpy()
won_gp_names = df_races[df_races["raceId"].isin(won_race_ids)]["name"].drop_duplicates()
print(won_gp_names)
amount_won = (df_driver_results["positionOrder"] == 1).sum()
st.subheader(f"{driver_name} has won {amount_won} races", anchor=False)