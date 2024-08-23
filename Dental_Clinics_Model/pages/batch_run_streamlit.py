import streamlit as st
import simpy
import random
from dental_model import DentalClinic, customer_arrivals_on_distribution, customer_arrivals_on_schedule
import matplotlib.pyplot as plt
import seaborn as sns
import requests

def app():
    st.title("Batch Simulation Analysis")

    # Input fields for the constants in two columns
    col1, col2 = st.columns(2)

    with col1:
        num_dentists = st.number_input('Number of Dentists', value=1, step=1, min_value=1)
        num_desk_staff = st.number_input('Number of Desk Staff', value=1, step=1, min_value=1)
        num_seats = st.number_input('Number of Seats', value=3, step=1, min_value=1)
        
    with col2:
        sim_time = st.number_input('Simulation Time (minutes)', value=480, step=1, min_value=1)
        num_replications = st.number_input('Number of Replications', value=100, step=1, min_value=1)
        interarrival_type = st.selectbox("Select Interarrival Type", ["By Fitted Distribution", "By Schedule"])
        
    

    if st.button('Run Multiple Simulations'):
        # Send request to Flask server
        response = requests.post(
            'http://127.0.0.1:5000/run_simulation', 
            # 'https://db1a-35-202-194-168.ngrok-free.app/run_simulation',
            json={
            'num_dentists': num_dentists,
            'num_desk_staff': num_desk_staff,
            'num_seats': num_seats,
            'sim_time': sim_time,
            'num_replications': num_replications,
            'interarrival_type': interarrival_type
        })

        if response.status_code == 200:
            results = response.json()

            st.markdown("### Mean Utilization Across All Replications")
            st.metric(label="Average Dentist Utilization", value=f"{results['avg_dentist_utilization']:.2%}")
            # st.metric(label="Average Desk Staff Utilization", value=f"{results['avg_desk_staff_utilization']:.2%}")
            st.metric(label="Average Seater Utilization", value=f"{results['avg_seater_utilization']:.2%}")
            st.metric(label="Average Waiting Time", value=f"{results['avg_waiting_time_all']:.2f} minutes")

            # Plot the utilization arrays   
            st.markdown("### Dentist Utilization Across Replications")
            plt.figure(figsize=(10, 6))
            sns.histplot(data=results["dentist_utilizations"], kde=True)
            plt.ylabel("Frequency")
            plt.xlabel("Dentist Utilization")
            plt.title("Dentist Utilization Across Replications")
            st.pyplot(plt)

            st.markdown("### Seater Utilization Across Replications")
            plt.figure(figsize=(10, 6))
            sns.histplot(data=results["seater_utilizations"], kde=True)
            plt.ylabel("Frequency")
            plt.xlabel("Seater Utilization")
            plt.title("Seater Utilization Across Replications")
            st.pyplot(plt)
            
            #plot the average waiting time
            st.markdown("### Average Waiting Time Across Replications")
            plt.figure(figsize=(10, 6))
            sns.histplot(data=results["avg_waiting_time_list"], kde=True)
            plt.ylabel("Frequency")
            plt.xlabel("Average Waiting Time")
            plt.title("Average Waiting Time Across Replications")
            st.pyplot(plt)
            
            
        else:
            st.error("Failed to run the batch simulation.")

