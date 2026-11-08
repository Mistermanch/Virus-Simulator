# Virus Simulator

A simple interactive virus-spread simulator built with Streamlit. It shows how an outbreak changes over time and how it can spread between regions of the world.

## How it relates to the SIR model

The simulator is inspired by the **SIR model**, which divides a population into three groups:

- **Susceptible (S):** people who can still become infected.
- **Infected (I):** people who currently have the virus.
- **Recovered (R):** people who recovered and are considered immune.

This project also includes a fourth group, **Dead**, to represent the virus mortality rate. Each day, people move from Susceptible to Infected, and from Infected to Recovered or Dead.

The main controls represent simplified model parameters:

- **Infectivity:** controls how quickly the virus infects susceptible people.
- **Resistance (Recovery Rate):** controls how quickly infected people recover.
- **Lethality (Mortality Rate):** controls how many infected people die.
- **Starting Region:** selects where the outbreak begins. Other regions are affected after a delay.

The results are displayed as population statistics, a line chart, and a world infection map. The simulation runs for a maximum of 90 days and can be stopped at any time.

## Run the app locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

You can also try the live app: [Virus Simulator](https://virus-simulator-3rxatagbt5ztrkrqmaaf5v.streamlit.app)