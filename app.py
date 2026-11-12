import json

import pycountry
import streamlit as st
import streamlit.components.v1 as components


REGION_COUNTRIES = {
    "South America": ["BRA", "ARG", "COL", "PER", "VEN", "CHL", "ECU", "BOL", "PRY", "URY", "GUY", "SUR"],
    "Europe": ["FRA", "DEU", "ESP", "ITA", "GBR", "POL", "UKR", "ROU", "NLD", "BEL", "SWE", "NOR", "FIN", "GRC", "PRT", "CHE", "AUT", "CZE", "HUN", "IRL", "DNK", "BGR", "SRB", "HRV", "ISL"],
    "Asia": ["CHN", "IND", "IDN", "PAK", "BGD", "JPN", "PHL", "VNM", "TUR", "IRN", "THA", "KOR", "PRK", "SAU", "IRQ", "AFG", "MYS", "NPL", "LKA", "KHM", "LAO", "MMR", "MNG"],
    "Africa": ["NGA", "ETH", "EGY", "COD", "ZAF", "TZA", "KEN", "MAR", "DZA", "AGO", "GHA", "MOZ", "UGA", "SDN", "SEN", "CMR", "CIV", "TUN", "LBY", "ZWE", "BWA", "NAM", "MDG", "MLI", "NER"],
    "North America": ["USA", "CAN", "MEX", "GTM", "CUB", "HTI", "DOM", "HND", "NIC", "CRI", "PAN", "SLV", "JAM"],
}
REGION_DELAYS = {
    "South America": 15,
    "Europe": 8,
    "Asia": 12,
    "Africa": 18,
    "North America": 20,
}
REGIONS = list(REGION_COUNTRIES)
COUNTRIES = [country.alpha_3 for country in pycountry.countries]
COUNTRY_REGIONS = {
    country: region
    for region, countries in REGION_COUNTRIES.items()
    for country in countries
}

HTML_TEMPLATE = r"""
<!DOCTYPE html>
<html>
<head>
    <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
    <style>
        body { margin: 0; background: #080808; color: white; font-family: Arial, sans-serif; }
        .stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin-bottom: 20px; }
        .card, .panel { background: #171717; border-radius: 10px; padding: 16px; }
        .label { color: #aaaaaa; font-size: 13px; }
        .value { font-size: 25px; font-weight: bold; margin-top: 8px; }
        .content { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
        .panel { background: #111111; padding: 10px; min-width: 0; }
        h3 { font-size: 17px; margin: 8px; }
        #map, #chart { width: 100%; height: 460px; }
        button { background: #dc2626; border: none; border-radius: 6px; padding: 10px 20px; color: white; font-weight: bold; cursor: pointer; margin-bottom: 15px; }
        @media(max-width: 700px) {
            .content { grid-template-columns: 1fr; }
            .stats { grid-template-columns: repeat(2, 1fr); }
        }
    </style>
</head>
<body>
    <button id="stop">Stop simulation</button>
    <div class="stats">
        <div class="card"><div class="label">Healthy Population</div><div class="value" id="healthy">7999.9 M</div></div>
        <div class="card"><div class="label">Infected</div><div class="value" id="infected">0.1 M</div></div>
        <div class="card"><div class="label">Immune</div><div class="value" id="recovered">0.0 M</div></div>
        <div class="card"><div class="label">Dead</div><div class="value" id="dead">0.0 M</div></div>
    </div>
    <div class="content">
        <div class="panel"><h3 id="chart-title">Statistics - Day 0</h3><div id="chart"></div></div>
        <div class="panel"><h3 id="map-title">World Infection Map - Day 0</h3><div id="map"></div></div>
    </div>
    <div id="status"></div>
    <script>
        const config = CONFIG_DATA;
        const state = { susceptible: 7999.9, infected: 0.1, recovered: 0, dead: 0, day: 0, running: true };
        const elements = {
            map: document.getElementById("map"),
            chart: document.getElementById("chart"),
            status: document.getElementById("status"),
            values: ["healthy", "infected", "recovered", "dead"].map(id => document.getElementById(id)),
            titles: [document.getElementById("chart-title"), document.getElementById("map-title")]
        };
        const totalPopulation = 8000;

        function getSeverity(country) {
            const region = config.country_regions[country];
            if (!region) return 0;

            const progress = region === config.start_region
                ? 1
                : Math.max(0, Math.min(1, (state.day - config.region_delays[region]) / 25));
            return Math.min(100, state.infected * 0.7 * progress / 10);
        }

        const mapData = {
            type: "choropleth",
            locationmode: "ISO-3",
            locations: config.countries,
            z: config.countries.map(() => 0),
            zmin: 0,
            zmax: 100,
            colorscale: [[0, "#ffffff"], [0.2, "#ffcccc"], [0.5, "#ff7777"], [0.8, "#ff3333"], [1, "#990000"]],
            marker: { line: { color: "#555555", width: 0.4 } },
            colorbar: { title: "Infection %", thickness: 15, tickfont: {color: "white"}, titlefont: {color: "white"} },
            customdata: config.countries.map(country => config.country_regions[country] || "Unassigned"),
            hovertemplate: "%{location}<br>%{customdata}<br>Infection: %{z:.1f}%<extra></extra>"
        };
        const darkLayout = {
            paper_bgcolor: "#111111", plot_bgcolor: "#111111", font: {color: "white"},
            margin: {l: 5, r: 5, t: 5, b: 5},
            geo: {
                showframe: false, showcoastlines: true, coastlinecolor: "#555555",
                showocean: true, oceancolor: "#000000", showland: true, landcolor: "#ffffff",
                showcountries: true, countrycolor: "#555555", showlakes: false,
                bgcolor: "#000000", projection: {type: "natural earth"}
            }
        };
        const chartSeries = [
            ["Healthy", "#ffffff", "susceptible"],
            ["Infected", "#ff3333", "infected"],
            ["Recovered", "#33cc77", "recovered"],
            ["Dead", "#888888", "dead"]
        ];
        const chartData = chartSeries.map(([name, color]) => ({
            name, x: [], y: [], mode: "lines", line: {color}
        }));
        const chartLayout = {
            paper_bgcolor: "#111111", plot_bgcolor: "#111111", font: {color: "white"},
            margin: {l: 45, r: 15, t: 15, b: 40},
            xaxis: {title: "Day", gridcolor: "#333333"},
            yaxis: {title: "Population (M)", gridcolor: "#333333"},
            legend: {orientation: "h", y: -0.2}
        };

        function updateDisplay() {
            elements.values.forEach((element, index) => {
                element.textContent = state[chartSeries[index][2]].toFixed(1) + " M";
            });
            elements.titles.forEach(title => title.textContent = `${title.id === "chart-title" ? "Statistics" : "World Infection Map"} - Day ${state.day}`);
            Plotly.restyle(elements.map, {z: [config.countries.map(getSeverity)]});
            Plotly.extendTraces(
                elements.chart,
                {x: chartSeries.map(() => [state.day]), y: chartSeries.map(([, , key]) => [state[key]])},
                chartSeries.map((_, index) => index),
                90
            );
        }

        function advanceSimulation() {
            const newInfections = state.susceptible * state.infected / totalPopulation * config.infectivity;
            const newDeaths = state.infected * config.lethal_rate;
            const newRecoveries = state.infected * config.recovery_rate;
            state.susceptible = Math.max(0, state.susceptible - newInfections);
            state.infected = Math.max(0, state.infected + newInfections - newDeaths - newRecoveries);
            state.dead += newDeaths;
            state.recovered += newRecoveries;
            updateDisplay();
        }

        async function initialize() {
            await Plotly.newPlot(elements.map, [mapData], darkLayout, {responsive: true, displayModeBar: false});
            await Plotly.newPlot(elements.chart, chartData, chartLayout, {responsive: true, displayModeBar: false});
            const interval = setInterval(() => {
                if (!state.running) return clearInterval(interval);
                state.day++;
                advanceSimulation();
                if (state.infected < 0.01) {
                    state.running = false;
                    elements.status.textContent = `Simulation ended on Day ${state.day}. The virus went extinct.`;
                } else if (state.day >= 90) {
                    state.running = false;
                    elements.status.textContent = "Simulation completed after 90 days.";
                }
            }, 80);
        }

        document.getElementById("stop").onclick = () => {
            state.running = false;
            elements.status.textContent = "Simulation stopped.";
        };
        initialize();
    </script>
</body>
</html>
"""


def build_config(infectivity, lethal_rate, recovery_rate, start_region):
    return {
        "infectivity": infectivity,
        "lethal_rate": lethal_rate,
        "recovery_rate": recovery_rate,
        "start_region": start_region,
        "countries": COUNTRIES,
        "country_regions": COUNTRY_REGIONS,
        "region_delays": REGION_DELAYS,
    }


st.set_page_config(page_title="Virus Sim", page_icon="😷", layout="wide")
st.title("Virus Sim")
st.markdown("Welcome to the Virus SIM, adjust your virus and observe how it behaves")
st.sidebar.header("Evolution panel")

infectivity = st.sidebar.slider("Infectivity (Transmission Rate)", 0.1, 1.0, 0.3, step=0.05)
lethal_rate = st.sidebar.slider("Lethality (Mortality Rate)", 0.0, 0.5, 0.02, step=0.01)
recovery_rate = st.sidebar.slider("Resistance (Recovery Rate)", 0.05, 0.5, 0.1, step=0.01)
start_region = st.sidebar.selectbox("Select Starting Region", REGIONS)

if st.sidebar.button("Release Virus"):
    config = build_config(infectivity, lethal_rate, recovery_rate, start_region)
    components.html(
        HTML_TEMPLATE.replace("CONFIG_DATA", json.dumps(config)),
        height=850,
        scrolling=True,
    )
else:
    st.info("Configure your virus on the left panel and release it to start the simulation.")
