import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
def generate_scenario_data(scenario_name, hours=24, sample_rate_minutes = 5):
    """ 
    Generate realistic demo data for a cooling scenario 
    Parameters: 
    - scenario_name: "idle", "normal", "heavy", or "emergency" 
    - hours: number of hours to simulate (default 24) 
    - sample_rate_minutes: samples per minute (default 5) 
    """ 

    num_points = int((hours * 60) / sample_rate_minutes) 

    start_time = datetime(2024, 8, 24, 0, 0, 0) 
    timestamps = [start_time + timedelta(minutes=sample_rate_minutes*i) for i in range(num_points)] 

    time_array = np.arange(num_points) / num_points * 2 * np.pi 

    if scenario_name == "idle": 
        base_temp = 35 
        base_pump = 22 
        base_fan = 18 
        base_efficiency = 87 
        base_power = 45 
        workload = 10 
 
        temperature = base_temp + 0.3*np.sin(time_array) + np.random.normal(0, 0.2, num_points) 
        pump_speed = base_pump + 1*np.sin(time_array) + np.random.normal(0, 1, num_points) 
        fan_speed = base_fan + 1*np.sin(time_array) + np.random.normal(0, 1, num_points) 
        efficiency = base_efficiency - 1*np.sin(time_array) + np.random.normal(0, 1, num_points) 
        power_consumption = base_power + 2*np.sin(time_array) + np.random.normal(0, 2, num_points) 

    elif scenario_name == "normal": 
        base_temp = 40 
        base_pump = 65 
        base_fan = 60 
        base_efficiency = 68 
        base_power = 95 
        workload = 60 

        # Medium variation (realistic pattern) 
        temperature = base_temp + 2*np.sin(time_array) + np.random.normal(0, 0.5, num_points) 
        pump_speed = base_pump + 5*np.sin(time_array) + np.random.normal(0, 2, num_points) 
        fan_speed = base_fan + 5*np.sin(time_array) + np.random.normal(0, 2, num_points) 
        efficiency = base_efficiency - 3*np.sin(time_array) + np.random.normal(0, 2, num_points) 
        power_consumption = base_power + 15*np.sin(time_array) + np.random.normal(0, 5, num_points)
    
    elif scenario_name == "heavy":
        base_temp = 45 
        base_pump = 85
        base_fan = 80
        base_efficiency = 48
        base_power = 160
        workload = 95

        # High variation (challenging conditions) 
        temperature = base_temp + 2*np.sin(time_array) + np.random.normal(0, 0.8, num_points) 
        pump_speed = base_pump + 5*np.sin(time_array) + np.random.normal(0, 3, num_points) 
        fan_speed = base_fan + 5*np.sin(time_array) + np.random.normal(0, 3, num_points) 
        efficiency = base_efficiency - 3*np.sin(time_array) + np.random.normal(0, 2, num_points) 
        power_consumption = base_power + 20*np.sin(time_array) + np.random.normal(0, 8, num_points) 
    
    elif scenario_name =="emergency":
        base_temp = 45
        base_pump = 85
        base_fan = 80
        base_efficiency =48
        base_power = 160
        workload = 100

         # Create spike at middle of day 
        spike_start = num_points // 2 
        spike_width = 30 
        spike_magnitude = 20 
        # Gaussian spike 
        spike = spike_magnitude * np.exp(-((np.arange(num_points) - spike_start)**2) / (2*spike_width**2)) 
        # Base pattern plus spike 
        temperature = base_temp + 2*np.sin(time_array) + spike + np.random.normal(0, 0.5, num_points) 
        pump_speed = base_pump + 5*np.sin(time_array) + spike*0.5 + np.random.normal(0, 2, num_points) 
        fan_speed = base_fan + 5*np.sin(time_array) + spike*0.5 + np.random.normal(0, 2, num_points) 
        efficiency = base_efficiency - 3*np.sin(time_array) - spike*0.3 + np.random.normal(0, 2, num_points) 
        power_consumption = base_power + 20*np.sin(time_array) + spike*2 + np.random.normal(0, 5, num_points) 

    # Clip values to realistic ranges 
    temperature = np.clip(temperature, 30, 55) 
    pump_speed = np.clip(pump_speed, 15, 100) 
    fan_speed = np.clip(fan_speed, 10, 100) 
    efficiency = np.clip(efficiency, 20, 95) 
    power_consumption = np.clip(power_consumption, 20, 200) 

    # Add derived columns 
    coolant_flow = 4 + (pump_speed / 100) * 6  # 4-10 L/min based on pump speed 
    outlet_temp = temperature + (power_consumption / 100)  # Outlet higher than inlet 
    delta_t = outlet_temp - temperature  # Temperature delta

    #Determine status
    status =[]
    for temp in temperature:
        if temp >50:
            status.append("Critical")
        elif temp > 45:
            status.append("Warning")
        else:
            status.append("Normal")
     # Create DataFrame 
    df = pd.DataFrame({ 
        'timestamp': timestamps, 
        'temperature': temperature, 
        'outlet_temp': outlet_temp, 
        'delta_t': delta_t, 
        'pump_speed': pump_speed, 
        'fan_speed': fan_speed, 
        'efficiency': efficiency, 
        'power_consumption': power_consumption, 
        'coolant_flow': coolant_flow, 
        'workload': workload * np.ones(num_points), 
        'status': status, 
        'scenario': scenario_name 
    }) 
    return df 

if __name__ == "__main__": 
    print("Generating demo data for all scenarios...") 
    scenarios = ["idle", "normal", "heavy", "emergency"] 
    for scenario in scenarios: 
        print(f"\n✓ Generating {scenario} scenario...") 
        # Generate data 
        df = generate_scenario_data(scenario) 
        # Save to CSV 
        filename = f"data/{scenario}_scenario.csv" 
        df.to_csv(filename, index=False) 
        print(f"  → Saved to {filename}") 
        print(f"  → {len(df)} data points generated") 
        print(f"  → Avg temp: {df['temperature'].mean():.1f}°C") 
        print(f"  → Avg efficiency: {df['efficiency'].mean():.1f}%") 
    print("All demo data generated successfully!")
    
