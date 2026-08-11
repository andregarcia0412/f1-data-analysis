import streamlit as st
from streamlit_echarts import st_echarts
from metrics import (
    load_data,
    top_gp_winner,
    fastest_time,
    fastest_speed_recorded,
    yearly_fastest_lap,
    wins_per_grid,
    top_gp_constructor,
    load_constructors,
    dnf_percentage,
)

df_drivers, df_races, df_driver_standings, df_results, df_status = load_data()
df_constructors = load_constructors()

st.sidebar.title(":material/filter_alt: Filters", anchor=False)
gp_name = st.sidebar.selectbox(
    "Grand Prix", df_races["name"].drop_duplicates().to_numpy()
)
st.title(f"F1 Grand Prix Analysis - {gp_name}", anchor=False)
st.markdown(
    ":gray[Event-level record for one Grand Prix: who has won it most, how lap times have fallen across its history, and how much the starting grid decides the result.]"
)

st.space()

top_wins, top_winner = top_gp_winner(df_results, df_races, df_drivers, gp_name)
fastest_lap_time, fastest_lap_driver = fastest_time(
    df_results, df_races, df_drivers, gp_name
)
fastest_lap_speed, fastest_driver = fastest_speed_recorded(
    df_results, df_races, df_drivers, gp_name
)

winner_team, total_team_wins = top_gp_constructor(
    df_results, df_races, df_constructors, gp_name
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
)
col3.metric(
    label="Fastest Lap Speed",
    value=fastest_lap_speed if fastest_lap_speed is not None else "-",
    delta_description=fastest_driver if fastest_driver is not None else "-",
    border=True,
)

col4.metric(
    label="Team with most wins",
    value=total_team_wins,
    delta_description=winner_team,
    border=True,
)

st.divider()
st.markdown(
    """
    ## How the event has changed
    :gray[Fastest lap set in each running of the race, from the first championship season to the most recent.]
""",
    anchors=False,
)

st.html("""
    <style>
    .st-key-lap_evolution, .st-key-wins_starting, .st-key-dnf_rate {
        background-color: #15151E;
        padding: 20px 12px 0px 12px;
        border-radius: 12px;
        border: 1px solid #2A2A37;
    }
    </style>
""")

years, laps = yearly_fastest_lap(df_results, df_races, gp_name)
if len(years) > 0 and len(laps) > 0:
    with st.container(key="lap_evolution"):
        st_echarts(
            {
                "backgroundColor": "#15151E",
                "title": {
                    "text": f"{gp_name} fastest lap time evolution",
                    "subtext": "One point per edition, so lower is faster. Years the race was not held are absent from the axis rather than plotted as zero. The step-ups follow rule changes that cut downforce or engine power; the long slide between them is normal development.",
                    "top": 0,
                    "subtextStyle": {
                        "fontSize": 12,
                        "lineHeight": 18,
                        "width": 800,
                        "overflow": "break",
                        "align": "left",
                    },
                },
                "grid": {
                    "top": 100,
                    "left": 50,
                    "right": 50,
                    "bottom": 24,
                    "containLabel": True,
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

st.divider()
wins_per_grid_counts = wins_per_grid(df_results, df_races, gp_name)

if not wins_per_grid_counts.empty:
    total_wins = int(wins_per_grid_counts.sum())
    from_pole = int(wins_per_grid_counts.get(1, 0))

    st.markdown(
        """
            ## How much the grid decides
            :gray[Winning starting positions across every edition of the race.]
        """,
        anchors=False,
    )

    with st.container(key="wins_starting"):
        st_echarts(
            {
                "backgroundColor": "#15151E",
                "title": {
                    "text": f"Wins by starting position at the {gp_name} ({from_pole} of {total_wins} from pole)",
                    "subtext": "Each bar counts the races won from that grid slot. Positions with no bar have never produced a winner here, which is the point of showing the full grid rather than only the slots that scored.",
                    "top": 0,
                    "subtextStyle": {"fontSize": "12px"},
                },
                "grid": {
                    "top": 100,
                    "left": 124,
                    "right": 124,
                    "bottom": 24,
                    "containLabel": True,
                },
                "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                "xAxis": {
                    "type": "category",
                    "name": "Starting position",
                    "data": [str(grid) for grid in wins_per_grid_counts.index],
                    "axisTick": {"alignWithLabel": True},
                    "axisLabel": {"interval": 0},
                },
                "yAxis": {"type": "value", "name": "Wins", "minInterval": 1},
                "series": [
                    {
                        "type": "bar",
                        "data": wins_per_grid_counts.tolist(),
                        "animationDuration": 800,
                    }
                ],
            },
            height="400px",
        )

st.divider()

st.markdown(
    """
    ## Reliability
    :gray[Share of the field that failed to finish, in each running of the race.]
""",
    anchors=False,
)

dnf_years, dnf_percentages = dnf_percentage(df_results, df_races, df_status, gp_name)

with st.container(key="dnf_rate"):
    st_echarts(
        {
            "backgroundColor": "#15151E",
            "title": {
                "text": f"{gp_name} DNF rate per year",
                "subtext": "Retirements as a percentage of cars that started. A DNF is any car classified with a status other than a finish or a lapped finish, so accidents and mechanical failures are counted together.",
                "top": 0,
                "subtextStyle": {
                    "fontSize": 12,
                    "lineHeight": 18,
                    "width": 800,
                    "overflow": "break",
                    "align": "left",
                },
            },
            "grid": {
                "top": 100,
                "left": 50,
                "right": 50,
                "bottom": 24,
                "containLabel": True,
            },
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "name": "Year",
                "data": dnf_years,
            },
            "yAxis": {"type": "value", "name": "DNF rate (%)"},
            "series": [
                {
                    "type": "line",
                    "data": dnf_percentages,
                    "smooth": True,
                    "areaStyle": {"opacity": 0.15},
                    "animationDuration": 800,
                }
            ],
        },
        height="400px",
    )
