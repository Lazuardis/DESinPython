import streamlit as st
import simpy
import random
from Eatery_Model import EaterySimulation
import seaborn as sns
import matplotlib.pyplot as plt

# Cache the simulation results to avoid rerunning the simulation on every interaction
# @st.cache_data
def run_eatery_simulation(inter_arrival_time, front_staff_cap, back_staff_cap, two_seater_cap, four_seater_cap, run_time):
    # random.seed(100)
    env = simpy.Environment()
    eatery_simulation = EaterySimulation(
        env, 
        front_staff_cap=front_staff_cap, 
        back_staff_cap=back_staff_cap, 
        two_seater_cap=two_seater_cap, 
        four_seater_cap=four_seater_cap
    )
    
    results = eatery_simulation.run_simulation(
        inter_arrival_time=inter_arrival_time, 
        run_time=run_time
    )
    
    return results

# Streamlit App
st.title("Eatery Simulation")

# Input Fields
inter_arrival_time = st.number_input(
    "Inter-arrival time (minutes)", 
    value=10, 
    help="The average time (in minutes) between customer arrivals. For example, if set to 10, on average, a customer will arrive every 10 minutes assuming the arrival pattern follows an exponential distribution."
)
front_staff_cap = st.number_input("Front Staff Capacity", value=2)
back_staff_cap = st.number_input("Back Staff Capacity", value=2)
two_seater_cap = st.number_input("Two-Seater Capacity", value=2)
four_seater_cap = st.number_input("Four-Seater Capacity", value=2)

# Run Simulation Button
if st.button("Run Simulation"):
    # Run the simulation and cache the results
    results = run_eatery_simulation(
        inter_arrival_time=inter_arrival_time, 
        front_staff_cap=front_staff_cap, 
        back_staff_cap=back_staff_cap, 
        two_seater_cap=two_seater_cap, 
        four_seater_cap=four_seater_cap, 
        run_time=60*8
    )
    
    # Store results in the session state for further use
    st.session_state['simulation_results'] = results

# If the simulation has been run, display the metrics
if 'simulation_results' in st.session_state:
    results = st.session_state['simulation_results']
    
    # Display Results as Metrics in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Average Customer Waiting Time (minutes)", f"{results['average_waiting_time']:.1f}")
        st.metric("Average Number of Waiting Customers", f"{results['average_waiting_customer']:.1f}")
        st.metric("Front Staff Utilization", f"{results['front_staff_util']:.1f}")
        st.metric("Customer Count (Group)", f"{results['customer_count']}")
    
    with col2:
        st.metric("Back Staff Utilization", f"{results['back_staff_util']:.1f}")
        st.metric("Two-Seater Utilization", f"{results['twoseater_util']:.1f}")
        st.metric("Four-Seater Utilization", f"{results['fourseater_util']:.1f}")
        st.metric("Number of Customers Served", f"{results['customer_served']}")
    
    # show the back staff, two seater, and four seater utilization array in a line chart with dropdown
    st.title("Utilization Array")

    # Multiselect for choosing which metrics to display
    selected_metrics = st.multiselect(
        "Select Utilization Metrics to Display",
        options=["Front Staff Utilization", "Back Staff Utilization", "Two-Seater Utilization", "Four-Seater Utilization"],
        default=["Front Staff Utilization", "Back Staff Utilization", "Two-Seater Utilization", "Four-Seater Utilization"]
    )

    # Prepare the chart data based on the selected metrics
    chart_data = {}
    if "Front Staff Utilization" in selected_metrics:
        chart_data["Front Staff Utilization"] = results["front_staff_util_array"]
    if "Back Staff Utilization" in selected_metrics:
        chart_data["Back Staff Utilization"] = results["back_staff_util_array"]
    if "Two-Seater Utilization" in selected_metrics:
        chart_data["Two-Seater Utilization"] = results["twoseater_util_array"]
    if "Four-Seater Utilization" in selected_metrics:
        chart_data["Four-Seater Utilization"] = results["fourseater_util_array"]

    # Display the line chart if any metrics are selected
    if chart_data:
        st.line_chart(chart_data)
    else:
        st.write("Please select at least one metric to display.")
        
    
    # Display using histogram the customer arrival time distribution
    st.title("Customer Arrival Time Distribution")
    st.write("Histogram of customer arrival time distribution")
    

    # Create the histogram using seaborn
    plt.figure(figsize=(10, 6))  # Optional: Adjust figure size
    sns.histplot(results["arrival_times"], bins=20, kde=True)

    # Display the plot in Streamlit
    st.pyplot(plt)