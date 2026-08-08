import math
import streamlit as st
from streamlit_echarts import JsCode, st_echarts
from metrics import (
    load_data,
    wins_by_gp,
    average_position,
    poles_by_gp,
    points_per_season,
    abandon_reasons,
    position_distribution,
    teammate_duels,
)

df_drivers, df_races, df_driver_standings, df_results, df_status = load_data()

st.sidebar.title(":material/filter_alt: Filters", anchor=False)
driver_name = st.sidebar.selectbox("Driver", df_drivers["fullName"].to_numpy())
st.title(f"F1 Driver Analysis - {driver_name}", anchor=False)
st.markdown(
    ":gray[Career record for one driver: where the wins and poles came from, how scoring changed season by season, why races ended early, and how the head-to-head against each teammate turned out.]",
)

st.space()

driver_id = df_drivers[df_drivers["fullName"] == driver_name]["driverId"].item()

won_gp_counts, total_races = wins_by_gp(df_results, df_races, driver_id)
amount_won = won_gp_counts.sum()
pole_counts, total_poles = poles_by_gp(df_results, df_races, driver_id)
avg_position = average_position(driver_id, df_results)

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="Races Won", value=amount_won, border=True)
col2.metric(
    label="Win Rate", value=f"{((amount_won/total_races) * 100):.2f}%", border=True
)
col3.metric(label="Races Started", value=total_races, border=True)
col4.metric(
    label="Average Position",
    value=f"{avg_position:.2f}" if not math.isnan(avg_position) else "-",
    border=True,
)

st.divider()

st.html("""
    <style>
    .st-key-card_left, .st-key-card_right, .st-key-season_form, .st-key-abandon_reasons, .st-key-finishing_positions, .st-key-teammate_duels {
        background-color: #15151E;
        padding: 20px 12px 0px 12px;
        border-radius: 12px;
        border: 1px solid #2A2A37;
    }
    </style>
""")

if amount_won >= 1:
    st.markdown(
        """
        ## Where the results came from
        :gray[Wins and pole positions broken down by Grand Prix, most successful at the top.]
    """,
        anchors=False,
    )

    col1, col2 = st.columns(2, vertical_alignment="top", gap="large")
    with col1:
        won_sorted = won_gp_counts.sort_values()
        with st.container(key="card_left"):
            st_echarts(
                {
                    "backgroundColor": "#15151E",
                    "title": {
                        "text": f"Wins per Grand Prix ({total_races} races entered)",
                        "subtext": "Top 25 Grands Prix by career wins. Events entered but never won are not shown.",
                        "subtextStyle": {"fontSize": "12px"},
                        "top": 0,
                    },
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "grid": {"left": 8, "right": 24, "containLabel": True},
                    "xAxis": {
                        "type": "value",
                        "name": "Wins",
                        "nameLocation": "middle",
                        "minInterval": 1,
                        "axisLabel": "Wins",
                    },
                    "yAxis": {
                        "type": "category",
                        "data": won_sorted.index.tolist(),
                        "axisLabel": {"interval": 0},
                    },
                    "series": [
                        {
                            "type": "bar",
                            "data": won_sorted.tolist(),
                            "animationDuration": 800,
                            "label": {"show": True, "position": "right"},
                        }
                    ],
                },
                height="600px",
            )
    with col2:
        poles_sorted = pole_counts.sort_values()
        with st.container(key="card_right"):
            st_echarts(
                {
                    "backgroundColor": "#15151E",
                    "title": {
                        "text": f"Pole Positions per Grand Prix ({total_poles} total)",
                        "subtext": "Same 25-event view for qualifying. Blue marks the secondary series throughout the page.",
                        "top": 0,
                        "subtextStyle": {"fontSize": "12px"},
                    },
                    "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
                    "xAxis": {
                        "type": "value",
                        "name": "Pole Positions",
                        "nameLocation": "middle",
                        "minInterval": 1,
                        "axisLabel": "Pole Positions",
                    },
                    "yAxis": {
                        "type": "category",
                        "data": poles_sorted.index.tolist(),
                        "axisLabel": {"interval": 0},
                    },
                    "series": [
                        {
                            "type": "bar",
                            "data": poles_sorted.tolist(),
                            "animationDuration": 800,
                            "label": {"show": True, "position": "right"},
                            "itemStyle": {"color": "#3B87D6"},
                        }
                    ],
                },
                height="600px",
            )

st.divider()
st.markdown("""
    ## Season form
    :gray[Championship points per season. Point-scoring systems changed in 2010, so pre-2010 totals are not comparable with later ones.]
""")

points = points_per_season(df_results, df_races, driver_id)
with st.container(key="season_form"):
    st_echarts(
        {
            "backgroundColor": "#15151E",
            "title": {
                "text": f"{driver_name}'s points per season",
                "subtext": "Each point is a full season total, including sprint points from 2021 onwards.",
                "top": 0,
                "subtextStyle": {"fontSize": "12px"},
            },
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "name": "Year",
                "data": [str(year) for year in points.index],
            },
            "yAxis": {"type": "value", "name": "Points"},
            "series": [
                {
                    "type": "line",
                    "data": points.tolist(),
                    "smooth": True,
                    "areaStyle": {"opacity": 0.15},
                    "animationDuration": 800,
                }
            ],
        },
        height="400px",
    )

st.divider()
st.markdown("""
    ## Why races ended early
    :gray[Recorded retirement reasons across the career, and how finishing positions are distributed overall.]
""")

data = abandon_reasons(df_results, df_status, driver_id, 15)
reasons = [d["name"] for d in data]
values = [d["value"] for d in data]

with st.container(key="abandon_reasons"):
    st_echarts(
        {
            "backgroundColor": "#15151E",
            "title": {
                "text": f"{driver_name}'s top 15 abandon reasons",
                "subtext": "Count of races that ended in retirement, by the reason recorded in the results table. Other is the aggregated tail: every reason outside the top 15, combined.",
                "top": 0,
                "subtextStyle": {"fontSize": "12px"},
            },
            "xAxis": {
                "type": "category",
                "data": reasons,
                "axisTick": {"show": False},
                "axisLabel": {"interval": 0, "rotate": 30},
            },
            "yAxis": {"type": "value", "splitLine": {"show": True}},
            "tooltip": {"trigger": "item"},
            "series": [
                {
                    "type": "bar",
                    "data": values,
                    "barWidth": 2,
                    "itemStyle": {"color": "#B4B2A9"},
                    "z": 1,
                },
                {
                    "type": "scatter",
                    "data": [[r, v] for r, v in zip(reasons, values)],
                    "symbolSize": 14,
                    "itemStyle": {"color": "#E8352F"},
                    "label": {"show": True, "position": "right", "formatter": "{@[1]}"},
                    "z": 2,
                },
            ],
        },
        height="400px",
    )

position_counts = position_distribution(df_results, driver_id)

with st.container(key="finishing_positions"):
    st_echarts(
        {
            "backgroundColor": "#15151E",
            "title": {
                "text": f"Distribution of {driver_name}'s Finishing Positions",
                "subtext": "Classified finishes only. The first column is highlighted because it is the same 105 wins reported in the metric above.",
                "top": 0,
                "subtextStyle": {"fontSize": "14px"},
            },
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "xAxis": [
                {
                    "type": "category",
                    "data": [str(p) for p in position_counts.index],
                    "axisTick": {"alignWithLabel": True},
                    "name": "Positions",
                }
            ],
            "yAxis": [{"type": "value", "name": "Count"}],
            "series": [
                {
                    "name": "Count",
                    "type": "bar",
                    "data": position_counts.tolist(),
                    "barCategoryGap": 1,
                }
            ],
        },
        height="400px",
    )

st.divider()
st.markdown(
    """
    ## Teammate duels
    :gray[One row per season, against the teammate in the other car that year.]
""",
    anchors=False,
)
duels = teammate_duels(df_results, df_races, df_drivers, df_status, driver_id)

if not duels.empty:
    labels = duels["label"].tolist()
    ahead = duels["ahead"].tolist()
    behind = duels["behind"].tolist()
    inconclusive = duels["inconclusive"].tolist()
    half = [value / 2 for value in inconclusive]

    tooltip_formatter = JsCode("""
        function (params) {
            var row = params[0].axisValue + '<br/>';
            params.forEach(function (p) {
                if (p.seriesName.charAt(0) === '_') return;
                row += p.marker + ' ' + p.seriesName + ': '
                    + Math.round(Math.abs(p.value) * (p.seriesName === 'Neither classified' ? 2 : 1))
                    + '<br/>';
            });
            return row;
        }
        """)

    with st.container(key="teammate_duels"):
        st_echarts(
            {
                "backgroundColor": "#15151E",
                "title": {
                    "text": f"{driver_name} vs. teammates, season by season",
                    "top": 0,
                },
                "tooltip": {
                    "trigger": "axis",
                    "axisPointer": {"type": "shadow"},
                    "formatter": tooltip_formatter,
                },
                "legend": {
                    "data": ["Ahead", "Behind", "Neither classified"],
                    "top": 56,
                },
                "grid": {"top": 96, "left": 8, "right": 24, "containLabel": True},
                "xAxis": {
                    "type": "value",
                    "name": "Races",
                    "nameLocation": "middle",
                    "nameGap": 28,
                    "axisLabel": {
                        "formatter": JsCode("function (v) { return Math.abs(v); }")
                    },
                },
                "yAxis": {
                    "type": "category",
                    "data": labels,
                    "axisLabel": {"interval": 0},
                },
                "series": [
                    {
                        "name": "Behind",
                        "type": "bar",
                        "stack": "duel",
                        "data": [-value for value in behind],
                        "itemStyle": {"color": "#7A7F94"},
                    },
                    {
                        "name": "Neither classified",
                        "type": "bar",
                        "stack": "duel",
                        "data": half,
                        "itemStyle": {"color": "#3E4257"},
                    },
                    {
                        "name": "Ahead",
                        "type": "bar",
                        "stack": "duel",
                        "data": ahead,
                        "itemStyle": {"color": "#E8352F"},
                    },
                ],
            },
            height=f"{170 + len(labels) * 34}px",
        )
