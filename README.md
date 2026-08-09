# F1 Data Analysis

An interactive Formula 1 dashboard built with Streamlit, exploring 75 seasons of championship data (1950–2024) from three angles: drivers, Grands Prix, and circuits.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://formula-1-data-analysis.streamlit.app/)
![Python](https://img.shields.io/badge/python-3.13-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/streamlit-1.61-FF4B4B?logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

**Live app: [formula-1-data-analysis.streamlit.app](https://formula-1-data-analysis.streamlit.app/)**

> This is a study project, built to learn Streamlit, pandas and data visualization with Apache ECharts.

## About

The dashboard turns the raw Ergast-derived race results into questions a fan would actually ask: where did a driver's wins come from, how did they fare against each teammate, how much faster has a circuit become over 70 years, and how often does pole position convert into a win?

Every page is driven by a sidebar filter, and all the aggregation logic lives in a single module (`metrics.py`), separated from the presentation code in `pages/`.

## Features

### 🏎️ Drivers

Career record for a single driver, selected from the full roster.

- Headline metrics: races won, win rate, races started, average finishing position
- Wins and pole positions broken down by Grand Prix
- Championship points per season
- Retirement reasons, with the long tail aggregated into "Other"
- Distribution of finishing positions across the career
- Season-by-season teammate duels (ahead / behind / neither classified), as a diverging stacked bar chart
- Driver portrait fetched on demand from the Wikipedia REST API, with an initials fallback

### 🏁 Races

Event-level history for a single Grand Prix.

- Headline metrics: driver with most wins, fastest lap, fastest lap speed, most successful constructor
- Fastest lap time evolution across every edition of the race
- Wins by starting grid position, showing how much the grid decides the result

### 🌍 Circuits

Every circuit that has hosted a championship race, filterable by country.

- Headline metrics: circuits, countries, races held
- World map with one bubble per circuit, sized by races hosted
- Sortable circuit table with altitude and a race-count progress column

## Tech stack

| Tool                                                               | Role                                                  |
| ------------------------------------------------------------------ | ----------------------------------------------------- |
| [Streamlit](https://streamlit.io/)                                  | Multipage app, layout, widgets, caching               |
| [pandas](https://pandas.pydata.org/)                                | Loading, joining and aggregating the CSV dataset      |
| [NumPy](https://numpy.org/)                                         | Numeric helpers (bubble sizing on the map)            |
| [streamlit-echarts](https://github.com/andfanilo/streamlit-echarts) | Apache ECharts charts, including custom JS formatters |
| [uv](https://docs.astral.sh/uv/)                                    | Dependency and virtual environment management         |

Theming (colors, fonts, chart palettes) is centralized in `.streamlit/config.toml`, so the visual identity is declared once instead of per chart.

## Data

The `data/` folder contains the [Formula 1 World Championship (1950–2024)](https://www.kaggle.com/datasets/rohanrao/formula-1-world-championship-1950-2020) dataset by Rohan Rao, published on Kaggle under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) license. It is a snapshot of the now-retired [Ergast Developer API](https://ergast.com/mrd/).

The app currently reads `drivers.csv`, `races.csv`, `results.csv`, `status.csv`, `driver_standings.csv`, `circuits.csv` and `constructors.csv`. The remaining files (lap times, pit stops, qualifying, sprint results) ship with the dataset and are available for future analyses.

Missing values are encoded as `\N` in the source files and parsed as `NaN` on load.

## Getting started

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended)

### Run it

```bash
git clone https://github.com/andregarcia0412/f1-data-analysis.git
cd f1-data-analysis
uv run streamlit run main.py
```

`uv run` creates the virtual environment and installs the locked dependencies on first execution. The app opens at `http://localhost:8501`.

<details>
<summary>Without uv (pip + venv)</summary>

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install streamlit streamlit-echarts pandas numpy requests
streamlit run main.py
```

</details>

## Notes and caveats

- Points per season are not comparable across eras — the scoring system changed several times, most significantly in 2010.
- Teammate duels only count races where **both** cars were classified; anything else is reported as inconclusive rather than as a win for either driver.
- Finishing-position charts consider classified finishes only.
- Driver images are requested from Wikipedia by name and cached for 24 hours. Drivers whose page title does not match their name simply render the initials fallback.

## License

Released under the MIT License.

The Formula 1 dataset is licensed separately by its author under CC BY 4.0 — see [Data](#data).
