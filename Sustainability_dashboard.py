import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# 1. CORE CONSTANTS (Fixed historical data)
# ==============================================================================
# These values define the fixed starting point and the grid intensity.
E_IT_BASELINE_KWH = 4_380_000  # Fixed Baseline Annual IT Energy Consumption
PUE_BASELINE = 1.8             # Fixed Fixed Baseline PUE
GRID_INTENSITY_GCO2_PER_KWH = 572 # Philippines Grid Emission Factor (in grams)

# Conversion Factor: gCO2e/kWh to tCO2e/kWh
EF_GRID_TCO2E_PER_KWH = GRID_INTENSITY_GCO2_PER_KWH / 1_000_000

# ==============================================================================
# 2. CALCULATION FUNCTIONS (Model Layer)
# ==============================================================================

def calculate_baseline_scenario():
    """Calculates all output metrics for the fixed PUE 1.8 baseline state."""
    
    # E_Total = PUE_Baseline * E_IT_Baseline
    E_TOTAL_BASE_KWH = PUE_BASELINE * E_IT_BASELINE_KWH
    GHG_BASE_TCO2E = E_TOTAL_BASE_KWH * EF_GRID_TCO2E_PER_KWH
    E_OVERHEAD_BASE_KWH = E_TOTAL_BASE_KWH - E_IT_BASELINE_KWH

    return {
        "E_IT_KWH": E_IT_BASELINE_KWH,
        "E_Total_KWH": E_TOTAL_BASE_KWH,
        "GHG_TCO2E": GHG_BASE_TCO2E,
        "E_Overhead_KWH": E_OVERHEAD_BASE_KWH
    }

def calculate_optimized_scenario(target_pue, it_reduction_factor):
    """
    Calculates optimized metrics based on user-defined targets (dynamic inputs).
    """
    
    # Calculate the reduced IT Energy (VM Consolidation)
    E_IT_OPTIMIZED_KWH = E_IT_BASELINE_KWH * (1 - it_reduction_factor)

    # Calculate Total Facility Energy using the optimized PUE
    E_TOTAL_OPTIMIZED_KWH = target_pue * E_IT_OPTIMIZED_KWH

    GHG_OPTIMIZED_TCO2E = E_TOTAL_OPTIMIZED_KWH * EF_GRID_TCO2E_PER_KWH
    E_OVERHEAD_OPTIMIZED_KWH = E_TOTAL_OPTIMIZED_KWH - E_IT_OPTIMIZED_KWH

    return {
        "E_IT_KWH": E_IT_OPTIMIZED_KWH,
        "E_Total_KWH": E_TOTAL_OPTIMIZED_KWH,
        "GHG_TCO2E": GHG_OPTIMIZED_TCO2E,
        "E_Overhead_KWH": E_OVERHEAD_OPTIMIZED_KWH
    }

def quantify_savings(baseline_data, optimized_data):
    """Calculates the absolute and percentage savings."""
    
    ENERGY_SAVINGS_KWH = baseline_data["E_Total_KWH"] - optimized_data["E_Total_KWH"]
    GHG_SAVINGS_TCO2E = baseline_data["GHG_TCO2E"] - optimized_data["GHG_TCO2E"]
    
    GHG_PERCENT_REDUCTION = (GHG_SAVINGS_TCO2E / baseline_data["GHG_TCO2E"]) * 100 if baseline_data["GHG_TCO2E"] != 0 else 0

    return {
        "Energy_Savings_KWH": ENERGY_SAVINGS_KWH,
        "GHG_Mitigation_TCO2E": GHG_SAVINGS_TCO2E,
        "GHG_Percent_Reduction": GHG_PERCENT_REDUCTION,
    }

# ==============================================================================
# 3. PAGE VIEW FUNCTIONS (View Layer)
# ==============================================================================

def dashboard_page(IT_REDUCTION_FACTOR, PUE_OPTIMIZED):
    """Displays the main interactive dashboard with KPIs and charts."""
    
    # --- EXECUTE CALCULATIONS WITH DYNAMIC INPUTS ---
    baseline_results = calculate_baseline_scenario()
    optimized_results = calculate_optimized_scenario(PUE_OPTIMIZED, IT_REDUCTION_FACTOR)
    savings_metrics = quantify_savings(baseline_results, optimized_results)
    
    st.title("☁️ Cloud Sustainability Dashboard Prototype")
    st.subheader("Dual-Layered Strategy: IT Consolidation & Infrastructure Efficiency")
    st.markdown("---")

    # --- KPI METRICS (4 Columns) ---
    st.markdown("### 🏆 Core Mitigation Metrics")
    col1, col2, col3, col4 = st.columns(4)

    # 1. Absolute GHG Savings
    col1.metric("Absolute GHG Mitigation", 
                f"{savings_metrics['GHG_Mitigation_TCO2E']:,.1f} tCO2e", 
                delta="Annual Savings")

    # 2. Percentage GHG Reduction
    col2.metric("GHG Reduction Percentage", 
                f"{savings_metrics['GHG_Percent_Reduction']:.1f}%", 
                delta=f"Current Target")

    # 3. Total Energy Savings
    col3.metric("Total Energy Savings", 
                f"{savings_metrics['Energy_Savings_KWH'] / 1_000_000:.2f} Million kWh", 
                delta="Annual Savings")
    
    # 4. Optimized PUE
    col4.metric("Target Facility PUE", 
                f"{PUE_OPTIMIZED:.2f}", 
                delta=f"Baseline PUE: {PUE_BASELINE:.1f}")

    st.markdown("---")
    
    # --- NARRATIVE AND FORMULAS SECTION ---
    st.header("🔬 Methodology: How the Figures are Derived")
    
    st.markdown("""
        This dashboard visually represents the projected **sustainability performance** derived from key inputs related to data center efficiency and IT consolidation.

        The primary goal of this analysis is to **quantify the total Scope 2 GHG mitigation and energy savings** achievable by implementing a dual-layered efficiency strategy:
        1.  **IT Load Reduction:** Consolidating workloads (e.g., Virtual Machine consolidation) to reduce the actual energy required by IT equipment (E_IT).
        2.  **PUE Improvement:** Migrating to a modern, efficient facility (e.g., Cloud) to reduce the non-IT overhead (cooling, power conversion, etc.), represented by a lower **Power Usage Effectiveness (PUE)**.

        The figures displayed compare a legacy **Baseline Scenario** (high PUE, high IT load) against the **Optimized Scenario** (low PUE, consolidated IT load).

        ## Key Formulas for Metric Derivation

        ### Total Annual Energy Consumption ($E_{\t{Total}}$)

        This is the most fundamental metric, calculated by applying the **PUE** to the **IT equipment load** ($E_{\t{IT}}$).

        $$
        E_{\t{Total}} = \t{PUE } \t   x   E_{\t{IT}}
        $$

        ### Annual GHG Emissions ($\t{GHG}_{\t{Annual}}$)

        This metric converts the consumed energy ($E_{\t{Total}}$) into carbon emissions (**Scope 2**) using the grid's carbon intensity factor ($\t{EF}_{\t{Grid}}$).

        $$
        \t{GHG}_{\t{Annual}} = E_{\t{Total}} \t x \t{EF}_{\t{Grid}}
        $$

        ### Total GHG Mitigation (Savings) ($\Delta \t{GHG}$)

        This is the key outcome, representing the total emissions avoided by moving from the Baseline to the Optimized scenario.

        $$
        \Delta \t{GHG} = \t{GHG}_{\t{Baseline}} - \t{GHG}_{\t{Optimized}}
        $$
    """)
    st.markdown("---")


    # --- VISUALIZATION DATA PREPARATION ---
    st.header("📊 Scenario Comparison Charts")
    scenarios = ['Baseline', 'Optimized']
    
    # Data for Chart 1: GHG Mitigation
    ghg_data = pd.DataFrame({
        'GHG Emissions (tCO2e)': [baseline_results['GHG_TCO2E'], optimized_results['GHG_TCO2E']]
    }, index=scenarios)

    # Data for Chart 2: PUE Deconstruction (Stacked Energy)
    energy_data = pd.DataFrame({
        'IT Load (Servers/Storage)': [baseline_results['E_IT_KWH'], optimized_results['E_IT_KWH']],
        'Non-IT Overhead (Cooling/Losses)': [baseline_results['E_Overhead_KWH'], optimized_results['E_Overhead_KWH']]
    }, index=scenarios)
    
    # Convert energy to Million kWh for better chart readability
    energy_data = energy_data / 1_000_000


    # --- CHARTS (2 Columns for Visualization) ---
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("### 1. Annual Scope 2 GHG Emissions (tCO2e)")
        st.bar_chart(ghg_data, color=["#1E88E5"])
        st.caption(f"This chart compares the fixed legacy footprint to the simulated outcome. Absolute Reduction: **{savings_metrics['GHG_Mitigation_TCO2E']:,.1f} tCO2e**")

    with chart_col2:
        st.markdown("### 2. Total Energy Consumption Breakdown (Million kWh)")
        st.bar_chart(
            energy_data,
            color=["#FF9900", "#00BCD4"]
        )
        st.caption("The optimized scenario shows savings from both a reduced IT Load and lower Non-IT Overhead (PUE improvement).")

def about_page():
    """Displays the 'About' information for the application."""
    st.title("ℹ️ About the Cloud Sustainability Modeler")
    st.markdown("---")

    st.markdown("""
        ### Application Purpose
        This tool is designed to provide a rapid, high-level simulation of the **carbon and energy savings** achievable by migrating from an on-premise, legacy data center environment to a more efficient, modern data center or cloud platform.

        It focuses on quantifying the impact of a **dual-layered efficiency strategy**:
        1.  **IT Consolidation:** Reducing the sheer amount of energy-consuming equipment (servers, storage) through virtualization, right-sizing, or platform optimization. This is represented by the **IT Energy Reduction %** slider.
        2.  **Infrastructure Efficiency:** Moving to a facility with a significantly better **Power Usage Effectiveness (PUE)**, which reduces the energy needed for cooling, lighting, and power delivery overhead.

        ### Key Assumptions & Fixed Inputs
        The model uses a few key fixed data points to establish a consistent baseline:
        * **Baseline Annual IT Energy E_IT:** **4,380,000 kWh**
        * **Baseline PUE:** **1.8** (Typical of older, less-optimized data centers)
        * **Grid Intensity Factor:** **572 gCO2e/kWh** (Based on the average grid mix for the Philippines, used to calculate Scope 2 emissions)

        ### How to Use the Dashboard
        Use the controls in the sidebar to define your **Optimization Targets**:
        * **IT Energy Reduction:** Simulate the impact of your VM consolidation or optimization strategy.
        * **Facility PUE Target:** Set the target PUE for the new cloud or co-location environment (typically between 1.1 and 1.3). The resulting charts show the calculated **GHG Mitigation** and the **Energy Breakdown** across the two scenarios.

        ---
        _This tool is a prototype for quick scenario modeling and should be validated with detailed environmental data for final decision-making._
    """)
    st.markdown("---")


def main_app_flow():
    """Manages the overall app flow and navigation."""

    st.set_page_config(layout="wide", 
                        page_title="Cloud Sustainability Modeler", 
                        initial_sidebar_state="expanded")

    # Initialize session state for navigation if not present
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard'
    
    # --- SIDEBAR: NAVIGATION & INPUT CONTROLS ---
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        # Use radio buttons for clean navigation between pages
        page_selection = st.radio("Select View:", 
                                  ['Dashboard', 'About this App'], 
                                  key='nav_radio')
        
        # Update session state based on radio selection
        st.session_state.current_page = page_selection

        st.markdown("---")
        
        # Only show inputs on the Dashboard page
        if st.session_state.current_page == 'Dashboard':
            st.markdown("## ⚙️ Optimization Targets (Interactive Simulation)")
            
            # Input 1: IT Consolidation (Layer 1)
            it_reduction_percent = st.slider(
                "1. IT Energy Reduction (VM Consolidation %)",
                min_value=0.0, max_value=30.0, value=20.0, step=1.0, format="%.0f%%"
            )
            IT_REDUCTION_FACTOR = it_reduction_percent / 100.0 # Convert to decimal

            # Input 2: PUE Upgrade (Layer 2)
            PUE_OPTIMIZED = st.slider(
                "2. Facility PUE Target (Infrastructure Upgrade)",
                min_value=1.1, max_value=PUE_BASELINE, value=1.2, step=0.01
            )
            
            st.markdown("---")
            st.info(f"Fixed Baseline PUE: **{PUE_BASELINE:.1f}**")
            st.info(f"Fixed Baseline IT Load: **{E_IT_BASELINE_KWH:,.0f} kWh**")
        else:
            # Set placeholder values if on the About page (not strictly needed 
            # as they aren't used, but good practice)
            IT_REDUCTION_FACTOR = 0.0
            PUE_OPTIMIZED = PUE_BASELINE

    # --- MAIN CONTENT SWITCHER ---
    if st.session_state.current_page == 'Dashboard':
        # Pass the dynamic inputs to the dashboard page function
        dashboard_page(IT_REDUCTION_FACTOR, PUE_OPTIMIZED)
    elif st.session_state.current_page == 'About this App':
        about_page()

if __name__ == "__main__":
    main_app_flow()