import numpy as np
import pandas as pd

np.random.seed(42)
HOURS = np.linspace(0, 24, 288)  # 5-min intervals

def generate_solar(hours):
    solar = np.zeros_like(hours)
    for i, h in enumerate(hours):
        if 6 <= h <= 18:
            base = np.sin(np.pi * (h - 6) / 12) * 100
            cloud_noise = np.random.normal(0, 5)
            solar[i] = max(0, base + cloud_noise)
    return solar

def generate_wind(hours):
    wind_base = 40 + 20 * np.sin(2 * np.pi * hours / 24)
    wind_noise = np.random.normal(0, 15, size=len(hours))
    wind = wind_base + wind_noise
    return np.clip(wind, 0, 100)

def generate_hybrid(solar, wind):
    return (solar + wind) / 2

def get_demand(hours):
    demand = 60 + 20 * np.sin(np.pi * (hours - 6) / 12)
    return np.clip(demand, 40, 100)

def generate_all():
    solar = generate_solar(HOURS)
    wind = generate_wind(HOURS)
    hybrid = generate_hybrid(solar, wind)
    demand = get_demand(HOURS)

    df = pd.DataFrame({
        'hour': HOURS,
        'solar': solar,
        'wind': wind,
        'hybrid': hybrid,
        'demand': demand
    })
    return df

if __name__ == "__main__":
    df = generate_all()
    print(df.head())
    print("✅ Simulation data generated!")