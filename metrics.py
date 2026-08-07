import pandas as pd
import numpy as np
import streamlit as st


@st.cache_data
def load_data():
    df_drivers = pd.read_csv("./data/drivers.csv", na_values=[r"\N"])
    df_drivers["fullName"] = df_drivers["forename"] + " " + df_drivers["surname"]
    return (
        df_drivers,
        pd.read_csv("./data/races.csv", na_values=[r"\N"]),
        pd.read_csv("./data/driver_standings.csv", na_values=[r"\N"]),
        pd.read_csv("./data/results.csv", na_values=[r"\N"]),
        pd.read_csv("./data/status.csv", na_values=[r"\N"]),
    )


@st.cache_data
def load_circuits():
    return pd.read_csv("./data/circuits.csv", na_values=[r"\N"])


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

    subset = subset.dropna(subset=["fastestLapTime"])

    if subset.empty:
        return None, None

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

    speeds = pd.to_numeric(subset["fastestLapSpeed"], errors="coerce").dropna()

    if speeds.empty:
        return None, None

    fastest_speed_recorded_row = subset.loc[speeds.idxmax()].to_dict()
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


def yearly_fastest_lap(df_results: pd.DataFrame, df_races: pd.DataFrame, gp_name: str):
    races_subset = df_races[df_races["name"] == gp_name][
        ["raceId", "year"]
    ].sort_values(by="year")
    merged = pd.merge(races_subset, df_results, on="raceId").dropna()[
        ["year", "fastestLapTime"]
    ]

    if merged.empty:
        return [], []

    parts = merged["fastestLapTime"].str.split(":", expand=True)
    merged["seconds"] = parts[0].astype(float) * 60 + parts[1].astype(float)
    best = merged.groupby("year")["seconds"].min().sort_index()

    return best.index.astype(int).tolist(), best.round(3).tolist()


@st.cache_data
def races_per_circuit(df_circuits: pd.DataFrame, df_races: pd.DataFrame):
    race_counts = df_races.groupby("circuitId").size().rename("races")
    df_map = df_circuits.merge(race_counts, on="circuitId")
    df_map["size"] = 30000 + np.sqrt(df_map["races"]) * 4000
    return df_map.sort_values(by="races", ascending=False)


def position_distribution(df_results: pd.DataFrame, driver_id: int):
    counts = (
        df_results[df_results["driverId"] == driver_id]["positionOrder"]
        .value_counts()
        .sort_index()
    )

    return counts.reindex(range(1, int(counts.index.max()) + 1), fill_value=0)


def wins_per_grid(df_results: pd.DataFrame, df_races: pd.DataFrame, gp_name: str):
    race_ids = df_races[df_races["name"] == gp_name]["raceId"]
    winners = df_results[
        df_results["raceId"].isin(race_ids) & (df_results["positionOrder"] == 1)
    ]
    counts = winners["grid"].value_counts().sort_index()

    if counts.empty:
        return counts

    return counts.reindex(range(1, int(counts.index.max()) + 1), fill_value=0)


def teammate_duels(
    df_results: pd.DataFrame,
    df_races: pd.DataFrame,
    df_drivers: pd.DataFrame,
    df_status: pd.DataFrame,
    driver_id: int,
):
    classified = df_status[
        df_status["status"].eq("Finished") | df_status["status"].str.startswith("+")
    ]["statusId"]

    base = df_results[["raceId", "driverId", "constructorId", "positionOrder"]].copy()
    base["classified"] = df_results["statusId"].isin(classified)

    pairs = base.merge(base, on=["raceId", "constructorId"], suffixes=("", "_mate"))
    pairs = pairs[
        (pairs["driverId"] == driver_id) & (pairs["driverId_mate"] != driver_id)
    ]

    if pairs.empty:
        return pd.DataFrame(columns=["label", "ahead", "behind", "inconclusive"])

    pairs = pairs.merge(df_races[["raceId", "year"]], on="raceId")

    both_classified = pairs["classified"] & pairs["classified_mate"]
    pairs["ahead"] = both_classified & (
        pairs["positionOrder"] < pairs["positionOrder_mate"]
    )
    pairs["behind"] = both_classified & (
        pairs["positionOrder"] > pairs["positionOrder_mate"]
    )
    pairs["inconclusive"] = ~pairs["ahead"] & ~pairs["behind"]

    duels = (
        pairs.groupby(["year", "driverId_mate"])[["ahead", "behind", "inconclusive"]]
        .sum()
        .reset_index()
    )
    duels = duels.merge(
        df_drivers[["driverId", "fullName"]],
        left_on="driverId_mate",
        right_on="driverId",
    )
    duels["races"] = duels["ahead"] + duels["behind"] + duels["inconclusive"]
    duels["label"] = duels["year"].astype(str) + "  ·  " + duels["fullName"]

    duels = duels.sort_values(by=["year", "races"], ascending=[True, True])
    return duels[["label", "ahead", "behind", "inconclusive"]]
