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

## Installation and local setup

### 1. Clone the repository

Open your terminal and run:

```bash
git clone https://github.com/Mistermanch/Virus-Simulator
```

Replace the URL with your repository URL.

### 2. Open the project folder

```bash
cd Virus-Simulator
```

### 3. Install the dependencies

Make sure Python is installed, then run:

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
streamlit run app.py
```

The application will open automatically in your browser. If it doesn't, visit:

http://localhost:8501

You can also try the live app: [Virus Simulator](https://virus-simulator-3rxatagbt5ztrkrqmaaf5v.streamlit.app)