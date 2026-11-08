
import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.express as px
import pycountry

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

country_to_region = {}

for region, countries in region_countries.items():
    for country in countries:
        country_to_region[country] = region

all_countries = [country.alpha_3 for country in pycountry.countries]

if start_sim:
    total_population = 8000.0
    susceptible = total_population - 0.1
    infected = 0.1
    dead = 0.0
    recovered = 0.0

    col1, col2, col3, col4 = st.columns(4)

    box_healthy = col1.empty()
    box_infected = col2.empty()
    box_recovered = col3.empty()
    box_dead = col4.empty()

    col_chart, col_map = st.columns([1, 1])

    box_chart = col_chart.empty()
    box_map = col_map.empty()

    history = []

    region_delays = {
        "South America": 15,
        "Europe": 8,
        "Asia": 12,
        "Africa": 18,
        "North America": 20
    }

    for day in range(1, 90):
        new_infections = (susceptible * infected / total_population) * infectivity
        new_deaths = infected * lethal_rate
        new_recoveries = infected * recovery_rate

        susceptible = max(0.0, susceptible - new_infections)
        infected = max(0.0, infected + new_infections - new_deaths - new_recoveries)

        dead += new_deaths
        recovered += new_recoveries

        history.append({
            "Day": day,
            "Healthy": susceptible,
            "Infected": infected,
            "Recovered": recovered,
            "Dead": dead
        })

        region_severity = {}

        for region in region_countries:
            if region == start_region:
                local_infected = infected * 0.7
            else:
                delay = region_delays[region]
                spread_progress = max(0, min(1, (day - delay) / 25))
                local_infected = infected * 0.7 * spread_progress

            severity = min(100, (local_infected / 1000) * 100)
            region_severity[region] = severity

        df_map = pd.DataFrame({
            "Country_Code": all_countries
        })

        df_map["Region"] = (
            df_map["Country_Code"]
            .map(country_to_region)
            .fillna("Unassigned")
        )

        df_map["Infection Severity (%)"] = (
            df_map["Region"]
            .map(region_severity)
            .fillna(0)
        )

        box_healthy.metric("Healthy Population", f"{susceptible:.1f} M")
        box_infected.metric("Infected", f"{infected:.1f} M", delta=f"+{new_infections:.2f} M" if infected > 0.01 else None)
        box_recovered.metric("Immune", f"{recovered:.1f} M")
        box_dead.metric("Dead", f"{dead:.1f} M")

        df_history = pd.DataFrame(history).set_index("Day")
        box_chart.line_chart(df_history)

        fig = px.choropleth(
            df_map,
            locations="Country_Code",
            locationmode="ISO-3",
            color="Infection Severity (%)",
            hover_name="Region",
            color_continuous_scale=[
                [0.0, "#ffffff"],
                [0.2, "#ffcccc"],
                [0.5, "#ff7777"],
                [0.8, "#ff3333"],
                [1.0, "#990000"]
            ],
            range_color=[0, 100],
            template="plotly_dark"
        )

        fig.update_geos(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#555555",
            showocean=True,
            oceancolor="#000000",
            showland=True,
            landcolor="#ffffff",
            showlakes=False,
            showrivers=False,
            showcountries=True,
            countrycolor="#555555",
            bgcolor="#000000",
            projection_type="natural earth"
        )

        fig.update_traces(
            marker_line_width=0.4,
            marker_line_color="#555555",
            colorbar_title="Infection %"
        )

        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
            coloraxis_colorbar=dict(
                title="Severity %",
                thickness=15,
                len=0.7,
                tickfont=dict(color="white"),
                title_font=dict(color="white")
            ),
            font=dict(color="white")
        )

        box_map.plotly_chart(
            fig,
            use_container_width=True,
            key=f"world_map_{day}"
        )

        if infected < 0.01:
            st.success(f"Simulation ended on Day {day}. The virus went extinct.")
            break

        time.sleep(0.05)

else:
    st.info("Configure your virus on the left panel and start to watch a live simulation using mathematics to predict virus propagation")
