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
        pd.read_csv("./data/status.csv"),
    )


def wins_by_gp(df_results: pd.DataFrame, df_races: pd.DataFrame, driver_id: int):
    df_driver_results = df_results[df_results["driverId"] == driver_id]
    won_race_ids = df_driver_results[df_driver_results["positionOrder"] == 1][
        "raceId"
    ].to_numpy()
    won_gp_counts = df_races[df_races["raceId"].isin(won_race_ids)][
        "name"
    ].value_counts()

    return (won_gp_counts, len(df_driver_results))


def average_position(driver_id: int, df_results: pd.DataFrame):
    return pd.to_numeric(
        df_results[df_results["driverId"] == driver_id]["position"], errors="coerce"
    ).mean()


def poles_by_gp(df_results: pd.DataFrame, df_races: pd.DataFrame, driver_id: int):
    df_driver_grid = df_results[df_results["driverId"] == driver_id]
    df_pole_ids = df_driver_grid[df_driver_grid["grid"] == 1]["raceId"].to_numpy()
    pole_counts = df_races[df_races["raceId"].isin(df_pole_ids)]["name"].value_counts()
    return pole_counts, len(df_pole_ids)


def top_gp_winner(
    df_results: pd.DataFrame,
    df_races: pd.DataFrame,
    df_drivers: pd.DataFrame,
    gp_name: str,
):
    race_ids = df_races[df_races["name"] == gp_name]["raceId"].to_numpy()
    subset = df_results[df_results["raceId"].isin(race_ids)]
    most_wins = subset[subset["positionOrder"] == 1]["driverId"].value_counts()
    driver_name = df_drivers[df_drivers["driverId"] == most_wins.idxmax()][
        "fullName"
    ].item()
    return most_wins.max(), driver_name


def fastest_time(
    df_results: pd.DataFrame,
    df_races: pd.DataFrame,
    df_drivers: pd.DataFrame,
    gp_name: str,
):
    race_ids = df_races[df_races["name"] == gp_name]["raceId"].to_numpy()
    subset = df_results[df_results["raceId"].isin(race_ids)]
    fastest_lap_time_row = subset.loc[subset["fastestLapTime"].idxmin()].to_dict()
    driver_name = df_drivers[
        df_drivers["driverId"] == fastest_lap_time_row["driverId"]
    ]["fullName"].item()
    return fastest_lap_time_row["fastestLapTime"], driver_name


def points_per_season(df_results: pd.DataFrame, df_races: pd.DataFrame, driver_id: int):
    driver_results_df = df_results[df_results["driverId"] == driver_id][
        ["raceId", "points"]
    ]
    driver_races_df = df_races[df_races["raceId"].isin(driver_results_df["raceId"])][
        ["raceId", "year"]
    ]
    df_points_per_season = pd.merge(driver_races_df, driver_results_df, on="raceId")
    return df_points_per_season.groupby("year")["points"].sum()


def fastest_speed_recorded(
    df_results: pd.DataFrame,
    df_races: pd.DataFrame,
    df_drivers: pd.DataFrame,
    gp_name: str,
):
    race_ids = df_races[df_races["name"] == gp_name]["raceId"].to_numpy()
    subset = df_results[df_results["raceId"].isin(race_ids)]
    fastest_speed_recorded_row = subset.loc[
        pd.to_numeric(subset["fastestLapSpeed"], errors="coerce").dropna().idxmax()
    ].to_dict()
    driver_name = df_drivers[
        df_drivers["driverId"] == fastest_speed_recorded_row["driverId"]
    ]["fullName"].item()
    return fastest_speed_recorded_row["fastestLapSpeed"], driver_name


def abandon_reasons(
    df_results: pd.DataFrame,
    df_status: pd.DataFrame,
    driver_id: int,
    values_threshold=5,
):
    driver_status_df = df_results[df_results["driverId"] == driver_id]
    status_counts = (
        pd.merge(driver_status_df, df_status, on="statusId")["status"]
        .value_counts()
        .drop("Finished", errors="ignore")
    )
    status_counts = status_counts[~status_counts.index.str.startswith("+")]

    top = status_counts.head(values_threshold).sort_values()
    others = status_counts.iloc[values_threshold:].sum()

    data = [{"name": name, "value": int(value)} for name, value in top.items()]
    if others > 0:
        data.insert(0, {"name": "Other", "value": int(others)})

    return data
