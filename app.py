# pyrefly: ignore [missing-import]
from pandas._libs import indexing
# pyrefly: ignore [missing-import]
import streamlit as st 
import pandas as pd 
# pyrefly: ignore [missing-import]
import plotly.express as px
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
# pyrefly: ignore [missing-import]
from plotly.subplots import make_subplots
import numpy as np 
from datetime import datetime, timedelta

# page configuration
st.set_page_config(
    page_title = "TACS",
    page_icon = ":dash:",
    layout= "wide",
    initial_sidebar_state = "expanded"
)

# title and header

st.title("Thermal Adaptive Cooling System")
st.subheader("Real-Time Thermal Cooling Dashboard")

# col1 , col2 = st.columns([1 , 2])
# with col2:
#     st.write("###  Quick Summary") 
#     st.markdown(""" 
#     **System Overview:** 
#     - Average Temperature: 40.2°C 
#     - System Efficiency: 68% 
#     - Energy Savings: 25-35% vs baseline 
#     - Water Reduction: 50% 

#     **Key Benefits:** 
#     -  Adaptive cooling response 
#     -  Low-cost implementation 
#     -  Significant energy savings 
#     -  Environmental impact 
#     """) 
st.markdown("---")

# slidebar
st.sidebar.title("Scenario Selection")
st.sidebar.write("Choose a cooling scenario to simulate: ")

scenario = st.sidebar.radio(
    "Selection Scenario:",
    ("Idle (Low Load)", "Normal (Medium Load)",
    "Heavy Load (AI Training)", "Emergency Spike"),
    index=1
)
st.sidebar.markdown("---")
st.sidebar.subheader("Scenerio Details")
st.sidebar.info(f"**Current:** {scenario}\n\n**Status:** Simulating cooling response\n\n**Duration:** 24hours")
st.sidebar.markdown("---")
st.sidebar.subheader("Time Period")
time_range = st.sidebar.selectbox(
    "Select Time Range:",
    ("24 Hours", "7 Days(Stimulated)","30 Days(Simulated)")
)
st.sidebar.info(f"Showing data for: {time_range}")
#temporary data 
@st.cache_data
def load_scenario_data(scenario_name): 
    """Load demo data for selected scenario""" 
     
    # Map scenario name to file 
    scenario_file_map = { 
        "Idle (Low Load)": "data/idle_scenario.csv", 
        "Normal (Medium Load)": "data/normal_scenario.csv", 
        "Heavy Load (AI Training)": "data/heavy_scenario.csv", 
        "Emergency Spike": "data/emergency_scenario.csv" 
    }
     
    filename = scenario_file_map[scenario_name] 
     
    try: 
        df = pd.read_csv(filename) 
        df['timestamp'] = pd.to_datetime(df['timestamp']) 
        return df 
    except FileNotFoundError: 
        st.error(f" Data file not found: {filename}") 
        st.info("Make sure to run: python generate_demo_data.py") 
        return None 

# Load data for selected scenario 
data = load_scenario_data(scenario) 
if data is None: 
    st.stop() 

# Main Dashboard - Metrics
st.subheader(" Current system Metrics")
col1, col2, col3, col4 = st.columns(4)
latest_temp = data['temperature'].iloc[-1]
latest_pump = data['pump_speed'].iloc[-1]
latest_fan = data['fan_speed'].iloc[-1]
latest_efficiency = data['efficiency'].iloc[-1]

with col1:
    st.metric(
        label="Temperature",
        value=f"{latest_temp:.1f}C", # degree celsius
        delta=f"{latest_temp - 40:.1f}C from target"  # degree celsius
    )
with col2:
    st.metric(
        label="Pump Speed",
        value=f"{latest_pump:.0f}%",
        delta="Response: Adaptive"
    )
with col3:
    st.metric(
        label="Fan Speed",
        value=f"{latest_fan:.0f}%",
        delta="Synchronized"
    )
with col4:
    st.metric(
        label="Efficiency",
        value=f"{latest_efficiency:.0f}%",
        delta="+33% vs baseline"
    )
#alert
if latest_temp > 50:
    st.error("Critical: Tempearture abouve 50°C!")
elif latest_temp > 45:
    st.warning("WARNING: Tempearture abouve 45°C")
else:
    st.success("System Status: All metrics normal")
st.markdown("--- ")

#sample chart
st.subheader("System Performance Trend")
tab1, tab2, tab3, tab4 = st.tabs(["Temperature", "Control Response", "Power Usage", "Efficiency"]) 
with tab1:
    fig = px.line(
        data,
        x ='timestamp',
        y = 'temperature',
        title = "Temperature Trend (24 Hours)",
        labels={'temperature': 'Temperature(°C)','timestamp': 'Time'},
        line_shape = 'linear'
    )

    fig.add_hline(
        y = 40,
        line_dash ="dash",
        line_color = "green",
        annotation_text = "target: 40°C"
    )
    fig.add_hrect(
        y0 = 45,
        y1 = 50,
        fillcolor = "orange",
        opacity = 0.1,
        annotation_text ="Warning Zone"
    )
    fig.add_hrect(
        y0 = 50,
        y1 = 55,
        fillcolor = "red",
        opacity = 0.1,
        annotation_text ="Critical Zone"
    )
    fig.update_layout(
        hovermode='x unified',
        height = 500,
        template='plotly_white'
    )
    st.plotly_chart (fig, use_container_width=True)

    st.write("Temperature Statistics")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Average", f"{data['temperature'].mean():.1f}°C")
    with col2:
        st.metric("Minimum", f"{data['temperature'].min():.1f}°C")
    with col3:
        st.metric("Maximum", f"{data['temperature'].max():.1f}°C")
    with col4:
        st.metric("Std Dev", f"{data['temperature'].mean():.1f}°C")


    with tab2:
        fig = make_subplots( 
            specs=[[{"secondary_y": True}]], 
            subplot_titles=("Pump & Fan Speed vs Temperature",) 
        )
    # Pump speed 
        fig.add_trace( 
            go.Bar( 
            x=data['timestamp'],  
            y=data['pump_speed'],  
            name="Pump Speed %", 
            marker_color='blue',  
            opacity=0.6 
            ),
            secondary_y=False 
        )

        fig.add_trace(
            go.bar(
                x = data['timestamp'],
                y = data['fan_speed'],
                name="Fan Speed",
                marker_color ='orange',
                opacity = 0.6
            ),
            secondary_y = False
        )
        fig.add_trace(
            go.Scatter(
                x = data['timestamp'],
                y = data['temperature'],
                name ="Temperature(°C)",
                line=dict(color='red', width=3),
                mode ='lines'
            ),
            secondary_y=True
        )
        fig.apdate_layout(
            title="Pump & Fan Response to temperature Changes",
            hovermode='x unified',
            height = 500,
            template ='Plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

        st.write("Control Response Statistics")
        col1, col2, col3, col4= st.columns(4)
        with col1:
            st.metric("Avg Pump Speed", f"{data['pump_speed'].mean():.0f}%")
        with col2:
            st.metric("Avg Fan Speed", f"{data['fan_speed'].mean():.0f}%")
        with col3:
            st.metric("Max Pump", f"{data['pump_speed'].max():.0f}%")
        with col4:
            st.metric("max Fan", f"{data['fan_speed'].max():.0f}%")

        with tab3:
            fig = px.area(
                data,
                x = 'timestamp',
                y = 'power_comsumption',
                title="Coolong Power Consumption(24 Hours)",
                labels ={'power_consumption': 'Power (w)', 'timestamp':'Time'}
            )
            fig.add_hline(
                y = 140,
                line_dash="dash",
                line_color ="red",
                annotation_text = "Baseline (100% continuous): 140W"
            )
            



#footer
st.markdown("---") 
st.markdown(""" 
###  Dashboard Information 
**Data Source:** Simulated realistic demo data   
**Scenario:** {scenario}   
**Time Period:** 24-hour simulation   
**Last Updated:** {timestamp} 
""".format(scenario=scenario, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

