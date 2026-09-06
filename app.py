import os
from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

# Page configuration
st.set_page_config(
    page_title="Thermal Adaptive Cooling System - TACS",
    page_icon="favicon.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.title("Thermal Adaptive Cooling System")
st.subheader("Real Time Thermal Cooling Dashboard")
st.markdown("---")

# Sidebar
st.sidebar.title("Scenario Selection")
st.sidebar.write("Choose a cooling scenario to simulate:")

scenario = st.sidebar.radio(
    "Selection Scenario:",
    ("Idle (Low Load)", "Normal (Medium Load)", "Heavy Load (AI Training)", "Emergency Spike"),
    index=1,
)
st.sidebar.markdown("---")
st.sidebar.subheader("Scenario Details")
st.sidebar.info(
    f"**Current:** {scenario}\n\n**Status:** Simulating cooling response\n\n**Duration:** 24 hours"
)


@st.cache_data
def load_scenario_data(scenario_name):
    """Load demo data for the selected scenario."""
    scenario_file_map = {
        "Idle (Low Load)": "data/idle_scenario.csv",
        "Normal (Medium Load)": "data/normal_scenario.csv",
        "Heavy Load (AI Training)": "data/heavy_scenario.csv",
        "Emergency Spike": "data/emergency_scenario.csv",
    }

    filename = scenario_file_map.get(scenario_name)
    if filename is None:
        st.error(f"Unsupported scenario: {scenario_name}")
        return None

    if not os.path.exists(filename):
        st.error(f"Data file not found: {filename}")
        st.info("Run: python generate_demo_data.py")
        return None

    df = pd.read_csv(filename)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


data = load_scenario_data(scenario)
if data is None:
    st.stop()

# Main dashboard metrics
st.subheader("Current System Metrics")
col1, col2, col3, col4 = st.columns(4)
latest_temp = data["temperature"].iloc[-1]
latest_pump = data["pump_speed"].iloc[-1]
latest_fan = data["fan_speed"].iloc[-1]
latest_efficiency = data["efficiency"].iloc[-1]

with col1:
    st.metric(
        label="Temperature",
        value=f"{latest_temp:.1f}°C",
        delta=f"{latest_temp - 40:.1f}°C from target",
    )
with col2:
    st.metric(label="Pump Speed", value=f"{latest_pump:.0f}%", delta="Response: Adaptive")
with col3:
    st.metric(label="Fan Speed", value=f"{latest_fan:.0f}%", delta="Synchronized")
with col4:
    st.metric(label="Efficiency", value=f"{latest_efficiency:.0f}%", delta="+33% vs baseline")

if latest_temp > 50:
    st.error("Critical: Temperature above 50°C!")
elif latest_temp > 45:
    st.warning("Warning: Temperature above 45°C!")
else:
    st.success("System status: All metrics normal")

st.markdown("---")

# Charts
st.subheader("System Performance Trend")
tab1, tab2, tab3, tab4 = st.tabs(["Temperature", "Control Response", "Power Usage", "Efficiency"])

with tab1:
    fig = px.line(
        data,
        x="timestamp",
        y="temperature",
        title="Temperature Trend (24 Hours)",
        labels={"temperature": "Temperature (°C)", "timestamp": "Time"},
    )
    fig.add_hline(y=40, line_dash="dash", line_color="green", annotation_text="Target: 40°C")
    fig.add_hrect(y0=45, y1=50, fillcolor="orange", opacity=0.1, annotation_text="Warning Zone")
    fig.add_hrect(y0=50, y1=55, fillcolor="red", opacity=0.1, annotation_text="Critical Zone")
    fig.update_layout(hovermode="x unified", height=500, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.write("Temperature Statistics")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Average", f"{data['temperature'].mean():.1f}°C")
    with c2:
        st.metric("Minimum", f"{data['temperature'].min():.1f}°C")
    with c3:
        st.metric("Maximum", f"{data['temperature'].max():.1f}°C")
    with c4:
        st.metric("Std Dev", f"{data['temperature'].std():.1f}°C")

with tab2:
    fig = make_subplots(specs=[[{"secondary_y": True}]], subplot_titles=("Pump & Fan Speed vs Temperature",))
    fig.add_trace(
        go.Bar(
            x=data["timestamp"],
            y=data["pump_speed"],
            name="Pump Speed (%)",
            marker_color="blue",
            opacity=0.6,
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Bar(
            x=data["timestamp"],
            y=data["fan_speed"],
            name="Fan Speed (%)",
            marker_color="orange",
            opacity=0.6,
        ),
        secondary_y=False,
    )
    fig.add_trace(
        go.Scatter(
            x=data["timestamp"],
            y=data["temperature"],
            name="Temperature (°C)",
            line=dict(color="red", width=3),
            mode="lines",
        ),
        secondary_y=True,
    )
    fig.update_layout(
        title="Pump & Fan Response to Temperature Changes",
        hovermode="x unified",
        height=500,
        template="plotly_white",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.write("Control Response Statistics")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Avg Pump Speed", f"{data['pump_speed'].mean():.0f}%")
    with c2:
        st.metric("Avg Fan Speed", f"{data['fan_speed'].mean():.0f}%")
    with c3:
        st.metric("Max Pump", f"{data['pump_speed'].max():.0f}%")
    with c4:
        st.metric("Max Fan", f"{data['fan_speed'].max():.0f}%")

with tab3:
    fig = px.area(
        data,
        x="timestamp",
        y="power_consumption",
        title="Cooling Power Consumption (24 Hours)",
        labels={"power_consumption": "Power (W)", "timestamp": "Time"},
    )
    fig.add_hline(
        y=140,
        line_dash="dash",
        line_color="red",
        annotation_text="Baseline (100% continuous): 140W",
    )
    fig.update_layout(hovermode="x unified", height=500, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.write("Power Consumption Statistics")
    baseline_power = 140
    c1, c2, c3, c4 = st.columns(4)
    avg_power = data["power_consumption"].mean()
    with c1:
        st.metric("Avg Power", f"{avg_power:.1f}W")
    with c2:
        st.metric("Baseline (100%)", f"{baseline_power:.0f}W")
    with c3:
        savings_percent = max((1 - avg_power / baseline_power) * 100, 0)
        st.metric("Savings", f"{savings_percent:.0f}%")
    with c4:
        daily_kwh = (avg_power * 24) / 1000
        st.metric("Daily Usage", f"{daily_kwh:.2f} kWh")

with tab4:
    fig = px.line(
        data,
        x="timestamp",
        y="efficiency",
        title="System Efficiency (24 Hours)",
        labels={"efficiency": "Efficiency (%)", "timestamp": "Time"},
    )
    fig.add_hline(y=35, line_dash="dash", line_color="blue", annotation_text="Baseline: 35%")
    fig.add_hrect(y0=60, y1=100, fillcolor="green", opacity=0.1, annotation_text="Excellent")
    fig.update_layout(hovermode="x unified", height=500, template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.write("Efficiency Statistics")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Avg Efficiency", f"{data['efficiency'].mean():.0f}%")
    with c2:
        st.metric("Min Efficiency", f"{data['efficiency'].min():.0f}%")
    with c3:
        st.metric("Max Efficiency", f"{data['efficiency'].max():.0f}%")
    with c4:
        improvement = data["efficiency"].mean() - 35
        st.metric("vs Baseline", f"{improvement:.0f}%")

# Analysis section
st.subheader("Analysis & Benefits")

baseline_daily_kwh = 3.36
avg_power_watts = data["power_consumption"].mean()
actual_daily_kwh = (avg_power_watts * 24) / 1000
daily_savings_kwh = max(baseline_daily_kwh - actual_daily_kwh, 0.0)
daily_savings_percent = (daily_savings_kwh / baseline_daily_kwh) * 100 if baseline_daily_kwh else 0.0
electricity_rate = 8
co2_per_kwh = 0.6

monthly_savings_kwh = daily_savings_kwh * 30
monthly_savings_rupees = monthly_savings_kwh * electricity_rate
annual_savings_kwh = daily_savings_kwh * 365
annual_savings_rupees = annual_savings_kwh * electricity_rate
annual_co2_reduction_kg = daily_savings_kwh * co2_per_kwh * 365
annual_co2_reduction_tons = annual_co2_reduction_kg / 1000

daily_water_reduction_liters = 7200
annual_water_reduction_liters = daily_water_reduction_liters * 365
annual_water_reduction_million = annual_water_reduction_liters / 1_000_000

investment = 25000
payback_months = investment / monthly_savings_rupees if monthly_savings_rupees > 0 else float("inf")

col1, col2 = st.columns(2)
with col1:
    st.markdown("Energy Savings")
    st.metric("Daily Savings", f"{daily_savings_kwh:.2f} kWh", f"{daily_savings_percent:.0f}% reduction")
    st.metric("Monthly Savings (Rupees)", f"₹{monthly_savings_rupees:.0f}", "at ₹8/kWh")
    st.metric("Annual Savings", f"₹{annual_savings_rupees:.0f}", "full year")
    st.metric("Payback Period", f"{payback_months:.1f} months", "investment recovery")
    st.info(
        f"""
        **Energy Breakdown:**
        - Baseline (100%): 3.36 kWh/day
        - Adaptive: {actual_daily_kwh:.2f} kWh/day
        - Daily Savings: {daily_savings_kwh:.2f} kWh
        - Monthly Savings: {monthly_savings_kwh:.0f} kWh
        """
    )
with col2:
    st.markdown("### Environmental Impact")
    st.metric("Daily Water Saved", f"{daily_water_reduction_liters:,.0f} L", "50% reduction")
    st.metric("Annual Water", f"{annual_water_reduction_million:.2f}M liters", "600+ people")
    st.metric("Annual CO2 Reduction", f"{annual_co2_reduction_tons:.2f} tons", "CO2 equivalent")
    st.metric("Carbon Footprint", "-35%", "vs baseline")
    st.info(
        f"""
        **Environmental Benefits:**
        - Daily CO2 Reduction: {daily_savings_kwh * co2_per_kwh:.2f} kg
        - Annual CO2: {annual_co2_reduction_tons:.2f} tons
        - Equivalent to: {annual_co2_reduction_tons / 0.055:.0f} trees planted
        - Water saved for: 600+ people annually
        """
    )

st.markdown("---")

st.markdown("### Performance Comparison: Baseline vs Adaptive")
comparison_data = {
    "Metric": [
        "Average Temperature",
        "Temperature Stability",
        "Response Time",
        "Daily Energy Usage",
        "System Efficiency",
        "Water Usage",
        "CO2 Emissions",
        "Monthly Cost",
    ],
    "Baseline (100% Continuous)": [
        "42°C",
        "±4°C",
        "8-10 sec",
        "3.36 kWh",
        "35%",
        "100%",
        f"{2.0:.2f} kg/day",
        f"₹{3.36 * 30 * electricity_rate:.0f}",
    ],
    "TACS": [
        f"{data['temperature'].mean():.1f}°C",
        "±2°C",
        "4-6 sec",
        f"{actual_daily_kwh:.2f} kWh",
        f"{data['efficiency'].mean():.0f}%",
        "50%",
        f"{daily_savings_kwh * co2_per_kwh:.2f} kg/day",
        f"₹{actual_daily_kwh * 30 * electricity_rate:.0f}",
    ],
    "Improvement": [
        f"{40 - data['temperature'].mean():.1f}°C cooler" if data["temperature"].mean() < 40 else "Same",
        "2× more stable",
        "2× faster",
        f"{daily_savings_percent:.0f}% less",
        f"+{data['efficiency'].mean() - 35:.0f}%",
        "-50%",
        f"{daily_savings_percent:.0f}% less",
        f"-₹{monthly_savings_rupees:.0f}",
    ],
}
comparison_df = pd.DataFrame(comparison_data)

st.dataframe(comparison_df, use_container_width=True, height=400)

csv = comparison_df.to_csv(index=False)
st.download_button(
    label="Download Comparison Table (CSV)",
    data=csv,
    file_name="cooling_comparison.csv",
    mime="text/csv",
)
st.markdown("---")

st.markdown("### Business Metrics & ROI")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Investment", "₹25,000", "per rack")
with col2:
    st.metric("Monthly Savings", f"₹{monthly_savings_rupees:.0f}", "at scale")
with col3:
    st.metric("Payback Period", f"{payback_months:.1f} months", "breakeven")
with col4:
    annual_roi = (annual_savings_rupees / investment) * 100
    st.metric("Annual ROI", f"{annual_roi:.0f}%", "return")

months_array = np.arange(0, 24)
cumulative_savings = monthly_savings_rupees * months_array
investment_line = np.full_like(months_array, investment, dtype=float)
roi_data = pd.DataFrame({
    "Month": months_array,
    "Cumulative Savings": cumulative_savings,
    "Investment": investment_line,
})
fig_roi = px.line(
    roi_data,
    x="Month",
    y=["Cumulative Savings", "Investment"],
    title="ROI Timeline - When Does Investment Pay Back?",
    labels={"value": "Amount (₹)", "Month": "Months"},
)

breakeven_month = investment / monthly_savings_rupees if monthly_savings_rupees > 0 else float("inf")
fig_roi.add_vline(
    x=breakeven_month,
    line_dash="dash",
    line_color="green",
    annotation_text=f"Breakeven: Month {breakeven_month:.1f}" if np.isfinite(breakeven_month) else "No breakeven",
)
st.plotly_chart(fig_roi, use_container_width=True)
st.info(
    f"""
    **Investment Analysis:**
    - Initial Investment: ₹25,000 per rack
    - Monthly Savings: ₹{monthly_savings_rupees:.0f}
    - Payback Period: {payback_months:.1f} months ({payback_months/12:.1f} years)
    - 2-Year Total Savings: ₹{annual_savings_rupees * 2:.0f}
    - 5-Year Total Savings: ₹{annual_savings_rupees * 5:.0f}
    """
)
st.markdown("---")

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    **Version:** 1.0

    **Developted By:** Team Orbiora

    **Project:** Thermal Adaptive Cooling System

    **Tech Stack**
    - Frontend: Streamlit
    - Backend: FastAPI & WebSocket
    - Database: Supabase/PostgreSQL
    - Data: Pandas
    - Visualization: Plotly
    """
)

st.markdown("---")
st.markdown(
    """
    ### Dashboard Information
    **Data Source:** Simulated realistic demo data
    **Scenario:** {scenario}
    **Time Period:** 24-hour simulation
    **Last Updated:** {timestamp}
    """.format(
        scenario=scenario,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
)

