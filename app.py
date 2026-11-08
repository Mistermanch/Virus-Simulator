
import streamlit as st
import pandas as pd
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

def create_map():
    df = pd.DataFrame({"Country_Code": all_countries})

    df["Region"] = (
        df["Country_Code"]
        .map(country_to_region)
        .fillna("Unassigned")
    )

    df["Severity"] = 0.0

    fig = px.choropleth(
        df,
        locations="Country_Code",
        locationmode="ISO-3",
        color="Severity",
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
        font=dict(color="white"),
        uirevision="world_map"
    )

    return fig


if start_sim:
    st.session_state.running = True
    st.session_state.day = 0
    st.session_state.total_population = 8000.0
    st.session_state.susceptible = 7999.9
    st.session_state.infected = 0.1
    st.session_state.dead = 0.0
    st.session_state.recovered = 0.0
    st.session_state.history = []
    st.session_state.map_fig = create_map()


@st.fragment(run_every=0.25)
def simulation():

    if not st.session_state.get("running", False):
        return

    if st.button("Stop simulation", key="stop_sim"):
        st.session_state.running = False
        return

    st.session_state.day += 1
    day = st.session_state.day

    total_population = st.session_state.total_population
    susceptible = st.session_state.susceptible
    infected = st.session_state.infected
    dead = st.session_state.dead
    recovered = st.session_state.recovered

    new_infections = (
        susceptible * infected / total_population
    ) * infectivity

    new_deaths = infected * lethal_rate
    new_recoveries = infected * recovery_rate

    susceptible = max(0.0, susceptible - new_infections)
    infected = max(0.0, infected + new_infections - new_deaths - new_recoveries)

    dead += new_deaths
    recovered += new_recoveries

    st.session_state.susceptible = susceptible
    st.session_state.infected = infected
    st.session_state.dead = dead
    st.session_state.recovered = recovered

    st.session_state.history.append({
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
            progress = max(0, min(1, (day - delay) / 25))
            local_infected = infected * 0.7 * progress

        region_severity[region] = min(
            100,
            (local_infected / 1000) * 100
        )

    df_map = pd.DataFrame({"Country_Code": all_countries})

    df_map["Region"] = (
        df_map["Country_Code"]
        .map(country_to_region)
        .fillna("Unassigned")
    )

    severity_values = (
        df_map["Region"]
        .map(region_severity)
        .fillna(0)
        .tolist()
    )

    fig = st.session_state.map_fig
    fig.data[0].z = severity_values

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Healthy Population", f"{susceptible:.1f} M")
    col2.metric("Infected", f"{infected:.1f} M", delta=f"+{new_infections:.2f} M")
    col3.metric("Immune", f"{recovered:.1f} M")
    col4.metric("Dead", f"{dead:.1f} M")

    col_chart, col_map = st.columns([1, 1])

    with col_chart:
        st.subheader(f"Statistics - Day {day}")
        df_history = pd.DataFrame(st.session_state.history).set_index("Day")
        st.line_chart(df_history, height=450)

    with col_map:
        st.subheader(f"World Infection Map - Day {day}")
        st.plotly_chart(
            fig,
            use_container_width=True,
            key="world_map",
            config={
                "displayModeBar": False,
                "scrollZoom": False
            }
        )

    if infected < 0.01:
        st.session_state.running = False
        st.success(f"Simulation ended on Day {day}. The virus went extinct.")

    elif day >= 90:
        st.session_state.running = False
        st.success("Simulation completed after 90 days.")


if st.session_state.get("running", False):
    simulation()

elif not start_sim:
    st.info("Configure your virus on the left panel and start to watch a live simulation using mathematics to predict virus propagation.")
