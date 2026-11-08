
import streamlit as st
import streamlit.components.v1 as components
import pycountry
import json

st.set_page_config(page_title="Virus Sim", page_icon="😷", layout="wide")

st.title("Virus Sim")
st.markdown("Welcome to the Virus SIM, adjust your virus and observe how it behaves")

st.sidebar.header("Evolution panel")

infectivity = st.sidebar.slider("Infectivity (Transmission Rate)", 0.1, 1.0, 0.3, step=0.05)
lethal_rate = st.sidebar.slider("Lethality (Mortality Rate)", 0.0, 0.5, 0.02, step=0.01)
recovery_rate = st.sidebar.slider("Resistance (Recovery Rate)", 0.05, 0.5, 0.1, step=0.01)

start_region = st.sidebar.selectbox(
    "Select Starting Region",
    ["South America", "Europe", "Asia", "Africa", "North America"]
)

start_sim = st.sidebar.button("Release Virus")

region_countries = {
    "South America": ["BRA", "ARG", "COL", "PER", "VEN", "CHL", "ECU", "BOL", "PRY", "URY", "GUY", "SUR"],
    "Europe": ["FRA", "DEU", "ESP", "ITA", "GBR", "POL", "UKR", "ROU", "NLD", "BEL", "SWE", "NOR", "FIN", "GRC", "PRT", "CHE", "AUT", "CZE", "HUN", "IRL", "DNK", "BGR", "SRB", "HRV", "ISL"],
    "Asia": ["CHN", "IND", "IDN", "PAK", "BGD", "JPN", "PHL", "VNM", "TUR", "IRN", "THA", "KOR", "PRK", "SAU", "IRQ", "AFG", "MYS", "NPL", "LKA", "KHM", "LAO", "MMR", "MNG"],
    "Africa": ["NGA", "ETH", "EGY", "COD", "ZAF", "TZA", "KEN", "MAR", "DZA", "AGO", "GHA", "MOZ", "UGA", "SDN", "SEN", "CMR", "CIV", "TUN", "LBY", "ZWE", "BWA", "NAM", "MDG", "MLI", "NER"],
    "North America": ["USA", "CAN", "MEX", "GTM", "CUB", "HTI", "DOM", "HND", "NIC", "CRI", "PAN", "SLV", "JAM"]
}

country_to_region = {
    country: region
    for region, countries in region_countries.items()
    for country in countries
}

all_countries = [country.alpha_3 for country in pycountry.countries]

region_delays = {
    "South America": 15,
    "Europe": 8,
    "Asia": 12,
    "Africa": 18,
    "North America": 20
}

if start_sim:

    config = {
        "infectivity": infectivity,
        "lethal_rate": lethal_rate,
        "recovery_rate": recovery_rate,
        "start_region": start_region,
        "countries": all_countries,
        "country_regions": country_to_region,
        "region_delays": region_delays
    }

    config_json = json.dumps(config)

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
        <style>
            body {
                margin: 0;
                background: #080808;
                color: white;
                font-family: Arial, sans-serif;
            }

            .stats {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 12px;
                margin-bottom: 20px;
            }

            .card {
                background: #171717;
                border-radius: 10px;
                padding: 16px;
            }

            .label {
                color: #aaaaaa;
                font-size: 13px;
            }

            .value {
                font-size: 25px;
                font-weight: bold;
                margin-top: 8px;
            }

            .content {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 15px;
            }

            .panel {
                background: #111111;
                border-radius: 10px;
                padding: 10px;
                min-width: 0;
            }

            h3 {
                font-size: 17px;
                margin: 8px;
            }

            #map, #chart {
                width: 100%;
                height: 460px;
            }

            button {
                background: #dc2626;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                color: white;
                font-weight: bold;
                cursor: pointer;
                margin-bottom: 15px;
            }

            @media(max-width: 700px) {
                .content {
                    grid-template-columns: 1fr;
                }

                .stats {
                    grid-template-columns: repeat(2, 1fr);
                }
            }
        </style>
    </head>

    <body>

        <button id="stop">Stop simulation</button>

        <div class="stats">
            <div class="card">
                <div class="label">Healthy Population</div>
                <div class="value" id="healthy">7999.9 M</div>
            </div>

            <div class="card">
                <div class="label">Infected</div>
                <div class="value" id="infected">0.1 M</div>
            </div>

            <div class="card">
                <div class="label">Immune</div>
                <div class="value" id="recovered">0.0 M</div>
            </div>

            <div class="card">
                <div class="label">Dead</div>
                <div class="value" id="dead">0.0 M</div>
            </div>
        </div>

        <div class="content">
            <div class="panel">
                <h3 id="chart-title">Statistics - Day 0</h3>
                <div id="chart"></div>
            </div>

            <div class="panel">
                <h3 id="map-title">World Infection Map - Day 0</h3>
                <div id="map"></div>
            </div>
        </div>

        <div id="status"></div>

        <script>
            const config = CONFIG_DATA;

            let susceptible = 7999.9;
            let infected = 0.1;
            let recovered = 0;
            let dead = 0;
            let day = 0;
            let running = true;

            const totalPopulation = 8000;
            const mapElement = document.getElementById("map");
            const chartElement = document.getElementById("chart");

            const regions = [
                "South America",
                "Europe",
                "Asia",
                "Africa",
                "North America"
            ];

            function getSeverity(country, currentDay, currentInfected) {
                const region = config.country_regions[country];

                if (!region) return 0;

                let localInfected;

                if (region === config.start_region) {
                    localInfected = currentInfected * 0.7;
                } else {
                    const delay = config.region_delays[region];
                    const progress = Math.max(
                        0,
                        Math.min(1, (currentDay - delay) / 25)
                    );

                    localInfected = currentInfected * 0.7 * progress;
                }

                return Math.min(100, localInfected / 10);
            }

            const initialData = {
                type: "choropleth",
                locationmode: "ISO-3",
                locations: config.countries,
                z: config.countries.map(() => 0),
                zmin: 0,
                zmax: 100,
                colorscale: [
                    [0, "#ffffff"],
                    [0.2, "#ffcccc"],
                    [0.5, "#ff7777"],
                    [0.8, "#ff3333"],
                    [1, "#990000"]
                ],
                marker: {
                    line: {
                        color: "#555555",
                        width: 0.4
                    }
                },
                colorbar: {
                    title: "Infection %",
                    thickness: 15,
                    tickfont: {color: "white"},
                    titlefont: {color: "white"}
                },
                customdata: config.countries.map(
                    c => config.country_regions[c] || "Unassigned"
                ),
                hovertemplate:
                    "%{location}<br>%{customdata}<br>" +
                    "Infection: %{z:.1f}%<extra></extra>"
            };

            const darkLayout = {
                paper_bgcolor: "#111111",
                plot_bgcolor: "#111111",
                font: {color: "white"},
                margin: {l: 5, r: 5, t: 5, b: 5},
                geo: {
                    showframe: false,
                    showcoastlines: true,
                    coastlinecolor: "#555555",
                    showocean: true,
                    oceancolor: "#000000",
                    showland: true,
                    landcolor: "#ffffff",
                    showcountries: true,
                    countrycolor: "#555555",
                    showlakes: false,
                    bgcolor: "#000000",
                    projection: {type: "natural earth"}
                }
            };

            const chartData = [
                {name: "Healthy", x: [], y: [], mode: "lines", line: {color: "#ffffff"}},
                {name: "Infected", x: [], y: [], mode: "lines", line: {color: "#ff3333"}},
                {name: "Recovered", x: [], y: [], mode: "lines", line: {color: "#33cc77"}},
                {name: "Dead", x: [], y: [], mode: "lines", line: {color: "#888888"}}
            ];

            const chartLayout = {
                paper_bgcolor: "#111111",
                plot_bgcolor: "#111111",
                font: {color: "white"},
                margin: {l: 45, r: 15, t: 15, b: 40},
                xaxis: {
                    title: "Day",
                    gridcolor: "#333333"
                },
                yaxis: {
                    title: "Population (M)",
                    gridcolor: "#333333"
                },
                legend: {orientation: "h", y: -0.2}
            };

            async function initialize() {
                await Plotly.newPlot(
                    mapElement,
                    [initialData],
                    darkLayout,
                    {responsive: true, displayModeBar: false}
                );

                await Plotly.newPlot(
                    chartElement,
                    chartData,
                    chartLayout,
                    {responsive: true, displayModeBar: false}
                );

                runSimulation();
            }

            function updateStatistics() {
                document.getElementById("healthy").textContent =
                    susceptible.toFixed(1) + " M";

                document.getElementById("infected").textContent =
                    infected.toFixed(1) + " M";

                document.getElementById("recovered").textContent =
                    recovered.toFixed(1) + " M";

                document.getElementById("dead").textContent =
                    dead.toFixed(1) + " M";

                document.getElementById("chart-title").textContent =
                    "Statistics - Day " + day;

                document.getElementById("map-title").textContent =
                    "World Infection Map - Day " + day;
            }

            function updateMap() {
                const severity = config.countries.map(
                    country => getSeverity(country, day, infected)
                );

                Plotly.restyle(
                    mapElement,
                    {z: [severity]}
                );
            }

            function updateChart() {
                Plotly.extendTraces(
                    chartElement,
                    {
                        x: [[day], [day], [day], [day]],
                        y: [[susceptible], [infected], [recovered], [dead]]
                    },
                    [0, 1, 2, 3],
                    90
                );
            }

            function runSimulation() {
                const interval = setInterval(() => {

                    if (!running) {
                        clearInterval(interval);
                        return;
                    }

                    day++;

                    const newInfections =
                        (susceptible * infected / totalPopulation)
                        * config.infectivity;

                    const newDeaths = infected * config.lethal_rate;
                    const newRecoveries = infected * config.recovery_rate;

                    susceptible = Math.max(
                        0,
                        susceptible - newInfections
                    );

                    infected = Math.max(
                        0,
                        infected + newInfections - newDeaths - newRecoveries
                    );

                    dead += newDeaths;
                    recovered += newRecoveries;

                    updateStatistics();
                    updateMap();
                    updateChart();

                    if (infected < 0.01) {
                        running = false;
                        document.getElementById("status").textContent =
                            "Simulation ended on Day " + day +
                            ". The virus went extinct.";
                    }

                    if (day >= 90) {
                        running = false;
                        document.getElementById("status").textContent =
                            "Simulation completed after 90 days.";
                    }

                }, 80);
            }

            document.getElementById("stop").onclick = () => {
                running = false;
                document.getElementById("status").textContent =
                    "Simulation stopped.";
            };

            initialize();
        </script>

    </body>
    </html>
    """

    html = html.replace("CONFIG_DATA", config_json)

    components.html(html, height=850, scrolling=True)

else:
    st.info("Configure your virus on the left panel and release it to start the simulation.")
