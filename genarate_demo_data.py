import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os


def generate_scenario_data(scenario_name, hours=24, sample_rate_minutes=5):
    """
    Generate realistic demo data for a cooling scenario

    Parameters:
    - scenario_name: "idle", "normal", "heavy", or "emergency"
    - hours: number of hours to simulate (default 24)
    - sample_rate_minutes: minutes between samples (default 5)
    """

    np.random.seed(42)

    num_points = int((hours * 60) / sample_rate_minutes)

    start_time = datetime(2024, 8, 24, 0, 0, 0)
    timestamps = [start_time + timedelta(minutes=sample_rate_minutes * i) for i in range(num_points)]

    time_array = np.arange(num_points) / num_points * 2 * np.pi

    if scenario_name == "idle":
        base_temp = 35
        base_pump = 22
        base_fan = 18
        base_efficiency = 87
        base_power = 45
        workload = 10
        status = "Idle"

        temperature = base_temp + 0.3 * np.sin(time_array) + np.random.normal(0, 0.2, num_points)
        pump_speed = base_pump + 1 * np.sin(time_array) + np.random.normal(0, 1, num_points)
        fan_speed = base_fan + 1 * np.sin(time_array) + np.random.normal(0, 1, num_points)
        efficiency = base_efficiency - 1 * np.sin(time_array) + np.random.normal(0, 1, num_points)
        power_consumption = base_power + 2 * np.sin(time_array) + np.random.normal(0, 2, num_points)

    elif scenario_name == "normal":
        base_temp = 40
        base_pump = 65
        base_fan = 60
        base_efficiency = 68
        base_power = 95
        workload = 60
        status = "Normal"

        temperature = base_temp + 2 * np.sin(time_array) + np.random.normal(0, 0.5, num_points)
        pump_speed = base_pump + 5 * np.sin(time_array) + np.random.normal(0, 2, num_points)
        fan_speed = base_fan + 5 * np.sin(time_array) + np.random.normal(0, 2, num_points)
        efficiency = base_efficiency - 3 * np.sin(time_array) + np.random.normal(0, 2, num_points)
        power_consumption = base_power + 15 * np.sin(time_array) + np.random.normal(0, 5, num_points)

    elif scenario_name == "heavy":
        base_temp = 47
        base_pump = 85
        base_fan = 82
        base_efficiency = 58
        base_power = 150
        workload = 90
        status = "Heavy"

        temperature = base_temp + 3 * np.sin(time_array) + np.random.normal(0, 0.8, num_points)
        pump_speed = base_pump + 6 * np.sin(time_array) + np.random.normal(0, 3, num_points)
        fan_speed = base_fan + 6 * np.sin(time_array) + np.random.normal(0, 3, num_points)
        efficiency = base_efficiency - 4 * np.sin(time_array) + np.random.normal(0, 3, num_points)
        power_consumption = base_power + 25 * np.sin(time_array) + np.random.normal(0, 8, num_points)

    elif scenario_name == "emergency":
        base_temp = 58
        base_pump = 95
        base_fan = 98
        base_efficiency = 42
        base_power = 210
        workload = 100
        status = "Emergency"

        temperature = base_temp + 5 * np.sin(time_array) + np.random.normal(0, 1.5, num_points)
        pump_speed = base_pump + 3 * np.sin(time_array) + np.random.normal(0, 2, num_points)
        fan_speed = base_fan + 2 * np.sin(time_array) + np.random.normal(0, 2, num_points)
        efficiency = base_efficiency - 6 * np.sin(time_array) + np.random.normal(0, 4, num_points)
        power_consumption = base_power + 30 * np.sin(time_array) + np.random.normal(0, 12, num_points)

    else:
        raise ValueError(f"Unknown scenario: {scenario_name}")

    df = pd.DataFrame({
        "timestamp": timestamps,
        "temperature": temperature,
        "pump_speed": pump_speed,
        "fan_speed": fan_speed,
        "efficiency": efficiency,
        "power_consumption": power_consumption,
        "workload": workload,
        "status": status,
        "scenario": scenario_name,
    })

    return df


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)

    scenarios = {
        "idle": "idle_scenario.csv",
        "normal": "normal_scenario.csv",
        "heavy": "heavy_scenario.csv",
        "emergency": "emergency_scenario.csv",
    }

    for scenario, filename in scenarios.items():
        df = generate_scenario_data(scenario)
        filepath = os.path.join(data_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Generated {filepath} ({len(df)} rows)")


if __name__ == "__main__":
    main()
