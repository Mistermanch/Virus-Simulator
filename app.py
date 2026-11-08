import streamlit as st
import numpy as np
import pandas as pd
import time

st.set_page_config(page_title="Virus Sim", page_icon="😷", layout="wide")

st.title("Virus Sim")
st.markdown("Welcome to the Cirus SIM, adjust your virus and observe how it behaves")

st.sidebar.header("Evolution panel")

infectivity = st.sidebar.slider("Infectivity (Transmission Rate)", 0.1, 1.0, 0.3, step=0.05)
lethal_rate = st.sidebar.slider("Lethality (Mortality Rate)", 0.0, 0.5, 0.02, step=0.01)
recovery_rate = st.sidebar.slider("Resistance (Recovery Rate)", 0.05, 0.5, 0.1, step=0.01)

start_region = st.sidebar.selectbox("Select Starting Region", ["South America", "Europe", "Asia", "Africa", "North America"])

start_sim = st.sidebar.button("Release Virus")

if start_sim:
    total_population = 8000.0
    susceptible = total_population - 0.1
    infected = 0.1
    dead = 0.0
    recovered = 0.0

    metrics = st.columns(4)
    box_healthy = metrics[0].empty()
    box_infected = metrics[1].empty()
    box_recovered = metrics[2].empty()
    box_dead = metrics[3].empty()

    box_chart = st.empty()

    history = []

    #time
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

#UI Update
        box_healthy.metric("Healthy Population", f"{susceptible:.1f} M")
        box_infected.metric("Infected", f"{infected:.1f} M", delta=f"+{new_infections:.1f} M" if infected > 0.1 else None)
        box_recovered.metric("Immune", f"{recovered:.1f} M")
        box_dead.metric("Dead", f"{dead:.1f} M")

        df_data = pd.DataFrame(history).set_index("Day")
        box_chart.line_chart(df_data)

#End Sim

        if infected < 0.01:
            st.success(f"Simulation ended on Day {day} the virus went extinct")
            break

        time.sleep(0.1)

else:
    st.info("Configure your virus on the left panel and start to watch a live simulation using mathematics to predict virus propagation")
