import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. Page Configuration ---
st.set_page_config(page_title="Dairy Partner Workplan", page_icon="🥛", layout="wide")

# --- 2. Embedded Dataset ---
# This dictionary simulates the flat structure needed for AppSheet later.
@st.cache_data
def load_data():
    raw_data = [
        {"Partner": "Paras", "Month": "January", "Activity": "Procurement", "Sub-Activity": "Farmer Onboarding", "Planned": 50, "Achieved": 45},
        {"Partner": "Paras", "Month": "January", "Activity": "Quality", "Sub-Activity": "Adulteration Tests", "Planned": 200, "Achieved": 200},
        {"Partner": "Lactalis", "Month": "January", "Activity": "Procurement", "Sub-Activity": "Route Expansion", "Planned": 10, "Achieved": 8},
        {"Partner": "Lactalis", "Month": "January", "Activity": "Sales", "Sub-Activity": "Retailer Visits", "Planned": 150, "Achieved": 120},
        {"Partner": "Schreiber", "Month": "February", "Activity": "Quality", "Sub-Activity": "BMC Sanitation", "Planned": 30, "Achieved": 30},
        {"Partner": "Schreiber", "Month": "February", "Activity": "Logistics", "Sub-Activity": "Chiller Maintenance", "Planned": 15, "Achieved": 10},
        {"Partner": "Govind", "Month": "February", "Activity": "Sales", "Sub-Activity": "Branding Campaigns", "Planned": 5, "Achieved": 2},
        {"Partner": "Govind", "Month": "February", "Activity": "Procurement", "Sub-Activity": "Farmer Onboarding", "Planned": 80, "Achieved": 60},
        {"Partner": "Parag", "Month": "March", "Activity": "Quality", "Sub-Activity": "Adulteration Tests", "Planned": 300, "Achieved": 290},
        {"Partner": "Parag", "Month": "March", "Activity": "Logistics", "Sub-Activity": "Route Expansion", "Planned": 20, "Achieved": 22}, # Exceeded target
    ]
    return pd.DataFrame(raw_data)

df = load_data()

# --- 3. Sidebar Filters ---
st.sidebar.header("Filter Options")

# Partner Filter
selected_partners = st.sidebar.multiselect(
    "Select Dairy Partner(s):",
    options=df["Partner"].unique(),
    default=df["Partner"].unique()
)

# Month Filter
selected_months = st.sidebar.multiselect(
    "Select Month(s):",
    options=df["Month"].unique(),
    default=df["Month"].unique()
)

# Apply filters to the dataframe
filtered_df = df[(df["Partner"].isin(selected_partners)) & (df["Month"].isin(selected_months))]

# --- 4. Main Dashboard ---
st.title("🥛 Dairy Partner Workplan Tracker")
st.markdown("Track monthly planned vs. achieved targets across all dairy partners.")

# Handle empty data selection gracefully
if filtered_df.empty:
    st.warning("No data available for the selected filters. Please adjust your selections.")
    st.stop()

# --- 5. Key Metrics ---
total_planned = filtered_df['Planned'].sum()
total_achieved = filtered_df['Achieved'].sum()
# Prevent division by zero
progress_pct = (total_achieved / total_planned * 100) if total_planned > 0 else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Planned Tasks", f"{total_planned:,}")
col2.metric("Total Achieved Tasks", f"{total_achieved:,}")
col3.metric("Overall Completion", f"{progress_pct:.1f}%")

st.divider()

# --- 6. Visualizations ---
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Partner Performance")
    # Group data by partner for the chart
    partner_group = filtered_df.groupby('Partner')[['Planned', 'Achieved']].sum().reset_index()
    fig_bar = px.bar(
        partner_group, 
        x="Partner", 
        y=["Planned", "Achieved"], 
        barmode="group",
        color_discrete_map={"Planned": "#3182bd", "Achieved": "#31a354"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col_chart2:
    st.subheader("Activity Breakdown")
    # Group data by Activity to see where focus is going
    activity_group = filtered_df.groupby('Activity')['Planned'].sum().reset_index()
    fig_pie = px.pie(
        activity_group, 
        names='Activity', 
        values='Planned',
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 7. Detailed Data View ---
st.subheader("Workplan Details")
# Calculate individual row progress
filtered_df['Completion (%)'] = ((filtered_df['Achieved'] / filtered_df['Planned']) * 100).round(1)

# Display as an interactive table
st.dataframe(
    filtered_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Completion (%)": st.column_config.ProgressColumn(
            "Completion (%)",
            format="%.1f%%",
            min_value=0,
            max_value=100,
        )
    }
)
