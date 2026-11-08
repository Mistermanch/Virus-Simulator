import streamlit as st
import numpy as np
import pandas as pd
import time
import plotly.express as px

st.set_page_config(page_title="Virus Sim", page_icon="😷", layout="wide")

st.title("Virus Sim")
st.markdown("Welcome to the Virus SIM, adjust your virus and observe how it behaves")

st.sidebar.header("Evolution panel")

infectivity = st.sidebar.slider("Infectivity (Transmission Rate)", 0.1, 1.0, 0.3, step=0.05)
lethal_rate = st.sidebar.slider("Lethality (Mortality Rate)", 0.0, 0.5, 0.02, step=0.01)
recovery_rate = st.sidebar.slider("Resistance (Recovery Rate)", 0.05, 0.5, 0.1, step=0.01)

start_region = st.sidebar.selectbox("Select Starting Region", ["South America", "Europe", "Asia", "Africa", "North America"])

start_sim = st.sidebar.button("Release Virus")

region_countries = {
    "South America": ["BRA", "ARG", "COL", "PER", "VEN", "CHL", "ECU", "BOL", "PRY", "URY"],
    "Europe": ["FRA", "DEU", "ESP", "ITA", "GBR", "POL", "UKR", "ROU", "NLD", "BEL", "SWE", "NOR"],
    "Asia": ["CHN", "IND", "IDN", "PAK", "BGD", "JPN", "PHL", "VNM", "TUR", "IRN", "THA", "KOR"],
    "Africa": ["NGA", "ETH", "EGY", "COD", "ZAF", "TZA", "KEN", "MAR", "DZA", "AGO", "GHA", "MOZ"],
    "North America": ["USA", "CAN", "MEX"],
}

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

    col_chart, col_map = st.columns(2)
    box_chart = col_chart.empty()
    box_map = col_map.empty()

    history = []

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
            "Healthy (Susceptible)": susceptible,
            "Active Infections": infected,
            "Immune (Recovered)": recovered,
            "Casualties (Dead)": dead
        })

        map_rows = []
        for name, countries in region_countries.items():
            if name == start_region:
                local_infected = infected * 0.6
            else:
                local_infected = infected * 0.1 * (day / 30.0)

            severity = min(100.0, (float(local_infected) / 1000.0) * 100.0)

            for country in countries:
                map_rows.append({
                    "Country_Code": country,
                    "Region": name,
                    "Infection Severity (%)": severity
                })

        df_map = pd.DataFrame(map_rows)

        box_healthy.metric("Healthy Population", f"{susceptible:.1f} M")
        box_infected.metric("Infected", f"{infected:.1f} M", delta=f"+{new_infections:.2f} M" if infected > 0.01 else None)
        box_recovered.metric("Immune", f"{recovered:.1f} M")
        box_dead.metric("Dead", f"{dead:.1f} M")

        df_data = pd.DataFrame(history).set_index("Day")
        box_chart.line_chart(df_data)

        fig = px.choropleth(
            df_map, 
            locations="Country_Code", 
            color="Infection Severity (%)",
            hover_name="Region",
            color_continuous_scale=["#ffffff", "#ff0000"],
            range_color=[0, 100],
            template="plotly_dark"
        )
        
        fig.update_geos(
            showframe=False,
            showcoastlines=False,
            showocean=True,
            oceancolor="#000000",
            showlakes=False,
            showrivers=False,
            showcountries=False,
            bgcolor="#000000"
        )
        
        fig.update_traces(marker_line_width=0)
        
        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
            coloraxis_colorbar=dict(title="Severity %", thickness=15, len=0.7)
        )
        
        box_map.plotly_chart(fig, use_container_width=True)

        if infected < 0.01:
            st.success(f"Simulation ended on Day {day}. The virus went extinct.")
            break

        time.sleep(0.05)

else:
    st.info("Configure your virus on the left panel and start to watch a live simulation using mathematics to predict virus propagation")
