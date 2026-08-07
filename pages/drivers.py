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

if amount_won >= 1:
    col1, col2 = st.columns(2, vertical_alignment="top", gap="large")
    with col1:
        won_sorted = won_gp_counts.sort_values()
        st_echarts(
            {
                "title": {
                    "subtext": f"Wins per Grand Prix ({total_races} races entered)",
                    "bottom": 25,
                    "subtextStyle": {"fontSize": "14px"},
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
        st_echarts(
            {
                "title": {
                    "subtext": f"Pole Positions per Grand Prix ({total_poles} total)",
                    "bottom": 25,
                    "subtextStyle": {"fontSize": "14px"},
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
                    }
                ],
            },
            height="600px",
        )


points = points_per_season(df_results, df_races, driver_id)
st_echarts(
    {
        "title": {
            "subtext": f"{driver_name}'s points per season",
            "bottom": 25,
            "subtextStyle": {"fontSize": "14px"},
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

data = abandon_reasons(df_results, df_status, driver_id, 15)
reasons = [d["name"] for d in data]
values = [d["value"] for d in data]

st_echarts(
    {
        "title": {
            "subtext": f"{driver_name}'s top {15 if len(data) == 16 else len(data)} abandon reasons",
            "bottom": 0,
            "subtextStyle": {"fontSize": "14px"},
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
                "itemStyle": {"color": "#185FA5"},
                "label": {"show": True, "position": "right", "formatter": "{@[1]}"},
                "z": 2,
            },
        ],
    },
    height="400px",
)

position_counts = position_distribution(df_results, driver_id)

st_echarts(
    {
        "title": {
            "subtext": f"Distribution of {driver_name}'s Finishing Positions",
            "bottom": 25,
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

    st_echarts(
        {
            "title": {
                "subtext": f"{driver_name} vs. teammates, season by season",
                "bottom": 0,
                "subtextStyle": {"fontSize": "14px"},
            },
            "tooltip": {
                "trigger": "axis",
                "axisPointer": {"type": "shadow"},
                "formatter": tooltip_formatter,
            },
            "legend": {"data": ["Ahead", "Behind", "Neither classified"], "top": 0},
            "grid": {"left": 8, "right": 24, "top": 40, "containLabel": True},
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
                    "name": "_inconclusive_left",
                    "type": "bar",
                    "stack": "duel",
                    "data": [-value for value in half],
                    "itemStyle": {"color": "#D9D7D0"},
                    "silent": True,
                },
                {
                    "name": "Behind",
                    "type": "bar",
                    "stack": "duel",
                    "data": [-value for value in behind],
                    "itemStyle": {"color": "#B4B2A9"},
                },
                {
                    "name": "Neither classified",
                    "type": "bar",
                    "stack": "duel",
                    "data": half,
                    "itemStyle": {"color": "#D9D7D0"},
                },
                {
                    "name": "Ahead",
                    "type": "bar",
                    "stack": "duel",
                    "data": ahead,
                    "itemStyle": {"color": "#185FA5"},
                },
            ],
        },
        height=f"{120 + len(labels) * 34}px",
    )
