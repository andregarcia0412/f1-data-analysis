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


def wins_by_gp(df_results: pd.DataFrame, df_races: pd.DataFrame, driver_id: int):
    df_driver_results = df_results[df_results["driverId"] == driver_id]
    won_race_ids = df_driver_results[df_driver_results["positionOrder"] == 1]["raceId"].to_numpy()
    won_gp_counts = df_races[df_races["raceId"].isin(won_race_ids)]["name"].value_counts()
    
    return (won_gp_counts, len(df_driver_results))

def average_position(driver_id: int, df_results: pd.DataFrame):
    return pd.to_numeric(df_results[df_results["driverId"] == driver_id]["position"], errors="coerce").mean()

def poles_by_gp(df_results: pd.DataFrame, df_races: pd.DataFrame, driver_id: int):
    df_driver_grid = df_results[df_results["driverId"] == driver_id]
    df_pole_ids = df_driver_grid[df_driver_grid["grid"] == 1]["raceId"].to_numpy()
    pole_counts = df_races[df_races["raceId"].isin(df_pole_ids)]["name"].value_counts()
    return pole_counts, len(df_pole_ids)