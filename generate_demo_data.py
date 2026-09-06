import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


def normalize_scenario_name(scenario_name):
    """Accept both short names and UI labels used by the dashboard."""
    if scenario_name is None:
        raise ValueError("Scenario name cannot be null.")

    normalized = str(scenario_name).strip().lower()
    aliases = {
        "idle": "idle",
        "idle (low load)": "idle",
        "idle low load": "idle",
        "normal": "normal",
        "normal (medium load)": "normal",
        "normal medium load": "normal",
        "heavy": "heavy",
        "heavy load": "heavy",
        "heavy load (ai training)": "heavy",
        "heavy load ai training": "heavy",
        "emergency": "emergency",
        "emergency spike": "emergency",
    }

    if normalized not in aliases:
        raise ValueError(f"Unsupported scenario: {scenario_name}")
    return aliases[normalized]


def generate_scenario_data(scenario_name, hours=24, sample_rate_minutes=5):
    """Generate realistic demo data for a cooling scenario."""
    scenario_key = normalize_scenario_name(scenario_name)
    num_points = int((hours * 60) / sample_rate_minutes)
    start_time = datetime(2024, 8, 24, 0, 0, 0)
    timestamps = [start_time + timedelta(minutes=sample_rate_minutes * i) for i in range(num_points)]
    time_array = np.arange(num_points) / max(num_points, 1) * 2 * np.pi

    rng = np.random.default_rng(sum(ord(ch) for ch in scenario_key))

    if scenario_key == "idle":
        base_temp = 35
        base_pump = 22
        base_fan = 18
        base_efficiency = 87
        base_power = 45
        workload = 10
        temperature = base_temp + 0.3 * np.sin(time_array) + rng.normal(0, 0.2, num_points)
        pump_speed = base_pump + 1 * np.sin(time_array) + rng.normal(0, 1, num_points)
        fan_speed = base_fan + 1 * np.sin(time_array) + rng.normal(0, 1, num_points)
        efficiency = base_efficiency - 1 * np.sin(time_array) + rng.normal(0, 1, num_points)
        power_consumption = base_power + 2 * np.sin(time_array) + rng.normal(0, 2, num_points)

    elif scenario_key == "normal":
        base_temp = 40
        base_pump = 65
        base_fan = 60
        base_efficiency = 68
        base_power = 95
        workload = 60
        temperature = base_temp + 2 * np.sin(time_array) + rng.normal(0, 0.5, num_points)
        pump_speed = base_pump + 5 * np.sin(time_array) + rng.normal(0, 2, num_points)
        fan_speed = base_fan + 5 * np.sin(time_array) + rng.normal(0, 2, num_points)
        efficiency = base_efficiency - 3 * np.sin(time_array) + rng.normal(0, 2, num_points)
        power_consumption = base_power + 15 * np.sin(time_array) + rng.normal(0, 5, num_points)

    elif scenario_key == "heavy":
        base_temp = 45
        base_pump = 85
        base_fan = 80
        base_efficiency = 48
        base_power = 160
        workload = 95
        temperature = base_temp + 2 * np.sin(time_array) + rng.normal(0, 0.8, num_points)
        pump_speed = base_pump + 5 * np.sin(time_array) + rng.normal(0, 3, num_points)
        fan_speed = base_fan + 5 * np.sin(time_array) + rng.normal(0, 3, num_points)
        efficiency = base_efficiency - 3 * np.sin(time_array) + rng.normal(0, 2, num_points)
        power_consumption = base_power + 20 * np.sin(time_array) + rng.normal(0, 8, num_points)

    elif scenario_key == "emergency":
        base_temp = 45
        base_pump = 85
        base_fan = 80
        base_efficiency = 48
        base_power = 160
        workload = 100
        spike_start = num_points // 2
        spike_width = 30
        spike_magnitude = 20
        spike = spike_magnitude * np.exp(-((np.arange(num_points) - spike_start) ** 2) / (2 * spike_width**2))
        temperature = base_temp + 2 * np.sin(time_array) + spike + rng.normal(0, 0.5, num_points)
        pump_speed = base_pump + 5 * np.sin(time_array) + spike * 0.5 + rng.normal(0, 2, num_points)
        fan_speed = base_fan + 5 * np.sin(time_array) + spike * 0.5 + rng.normal(0, 2, num_points)
        efficiency = base_efficiency - 3 * np.sin(time_array) - spike * 0.3 + rng.normal(0, 2, num_points)
        power_consumption = base_power + 20 * np.sin(time_array) + spike * 2 + rng.normal(0, 5, num_points)

    else:
        raise ValueError(f"Unsupported scenario: {scenario_name}")

    temperature = np.clip(temperature, 30, 55)
    pump_speed = np.clip(pump_speed, 15, 100)
    fan_speed = np.clip(fan_speed, 10, 100)
    efficiency = np.clip(efficiency, 20, 95)
    power_consumption = np.clip(power_consumption, 20, 200)

    coolant_flow = 4 + (pump_speed / 100) * 6
    outlet_temp = temperature + (power_consumption / 100)
    delta_t = outlet_temp - temperature

    status = []
    for temp in temperature:
        if temp > 50:
            status.append("Critical")
        elif temp > 45:
            status.append("Warning")
        else:
            status.append("Normal")

    workload_array = workload * np.ones(num_points)
    df = pd.DataFrame(
        {
            "timestamp": timestamps,
            "temperature": temperature,
            "outlet_temp": outlet_temp,
            "delta_t": delta_t,
            "pump_speed": pump_speed,
            "fan_speed": fan_speed,
            "efficiency": efficiency,
            "power_consumption": power_consumption,
            "coolant_flow": coolant_flow,
            "workload": workload_array,
            "status": status,
            "scenario": scenario_key,
        }
    )
    return df


if __name__ == "__main__":
    print("Generating demo data for all scenarios...")
    os.makedirs("data", exist_ok=True)
    scenarios = ["idle", "normal", "heavy", "emergency"]
    for scenario in scenarios:
        print(f"\n✓ Generating {scenario} scenario...")
        df = generate_scenario_data(scenario)
        filename = f"data/{scenario}_scenario.csv"
        df.to_csv(filename, index=False)
        print(f"  → Saved to {filename}")
        print(f"  → {len(df)} data points generated")
        print(f"  → Avg temp: {df['temperature'].mean():.1f}°C")
        print(f"  → Avg efficiency: {df['efficiency'].mean():.1f}%")
    print("All demo data generated successfully!")

