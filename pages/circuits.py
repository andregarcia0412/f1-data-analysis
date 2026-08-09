import streamlit as st
from metrics import load_data, load_circuits, races_per_circuit

_, df_races, _, _, _ = load_data()
df_circuits = load_circuits()

st.title("F1 Circuits Around the World", anchor=False)
st.markdown(
    ":gray[Every circuit that has hosted a championship race, where it is, and how much of the calendar it has carried. Use the country filter to narrow the map and the table together.]",
    anchors=False,
)

st.space()

st.sidebar.title(":material/filter_alt: Filters", anchor=False)
countries = sorted(df_circuits["country"].unique())
selected_countries = st.sidebar.multiselect("Country", countries, default=countries)

df_map = races_per_circuit(df_circuits, df_races)
df_map = df_map[df_map["country"].isin(selected_countries)]

if df_map.empty:
    st.info("Select at least one country to see the circuits.")
    st.stop()

col1, col2, col3 = st.columns(3)
col1.metric(label="Circuits", value=len(df_map), border=True)
col2.metric(label="Countries", value=df_map["country"].nunique(), border=True)
col3.metric(label="Races Held", value=int(df_map["races"].sum()), border=True)

st.divider()

st.markdown(
    """
    ## Where the sport races
    :gray[One bubble per circuit, placed at its real coordinates.]
""",
    anchors=False,
)

st.map(df_map, latitude="lat", longitude="lng", size="size", height=550)
st.caption(
    "Circle size is proportional to how many races the circuit has hosted",
    width="stretch",
    text_alignment="center",
)

st.divider()

st.markdown(
    """
    ## Circuit list
    :gray[Sorted by races held, highest first. Scroll inside the grid for the rest of the field.]
            """,
    anchors=False,
)

st.dataframe(
    df_map[["name", "location", "country", "alt", "races"]],
    column_config={
        "name": "Circuit",
        "location": "City",
        "country": "Country",
        "alt": st.column_config.NumberColumn("Altitude", format="%d m"),
        "races": st.column_config.ProgressColumn(
            "Races Held", min_value=0, max_value=int(df_map["races"].max()), format="%d"
        ),
    },
    hide_index=True,
    width="stretch",
)
