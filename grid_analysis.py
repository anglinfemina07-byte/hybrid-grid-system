import numpy as np
from simulation import generate_all, HOURS

df = generate_all()

def frequency_stability(power, demand):
    deviation = power - demand
    frequency = 50 + (deviation / demand) * 0.5
    return np.clip(frequency, 48, 52)

def voltage_stability(power, demand):
    ratio = power / (demand + 1e-6)
    voltage = 0.95 + (ratio - 1) * 0.1
    return np.clip(voltage, 0.90, 1.10)

def variability_index(power):
    diff = np.diff(power)
    return np.std(diff)

def fault_ride_through(power, fault_start=140, fault_duration=6):
    power_fault = power.copy()
    power_fault[fault_start:fault_start + fault_duration] *= 0.3
    recovery = np.linspace(0.3, 1.0, 20)
    end = fault_start + fault_duration
    power_fault[end:end + 20] = power[end:end + 20] * recovery
    return power_fault

def analyze():
    results = {}
    for source in ['solar', 'wind', 'hybrid']:
        power = df[source].values
        demand = df['demand'].values
        freq = frequency_stability(power, demand)
        volt = voltage_stability(power, demand)
        var = variability_index(power)
        fault = fault_ride_through(power)
        freq_score = 100 - np.mean(np.abs(freq - 50)) * 20
        volt_score = 100 - np.mean(np.abs(volt - 1.0)) * 100
        var_score = max(0, 100 - var * 2)
        recovery_time = np.argmax(fault[146:] > power[146:] * 0.9)
        fault_score = max(0, 100 - recovery_time * 5)
        results[source] = {
            'frequency': freq,
            'voltage': volt,
            'fault': fault,
            'variability': var,
            'freq_score': round(freq_score, 2),
            'volt_score': round(volt_score, 2),
            'var_score': round(var_score, 2),
            'fault_score': round(fault_score, 2),
            'overall': round((freq_score + volt_score + var_score + fault_score) / 4, 2)
        }
    return results

if __name__ == "__main__":
    r = analyze()
    for k, v in r.items():
        print(f"{k.upper()} — Overall Score: {v['overall']}")