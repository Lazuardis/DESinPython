import streamlit as st
import simpy
import random
from dental_model import DentalClinic, customer_arrivals_on_distribution, customer_arrivals_on_schedule
import matplotlib.pyplot as plt
import seaborn as sns
import requests

def app():
    def run_simulation(num_dentists, num_desk_staff, num_seats, sim_time, interarrival_type):
        
        # random.seed(random_seed)
        env = simpy.Environment()

        clinic = DentalClinic(env, num_dentists, num_desk_staff, num_seats) 

        if interarrival_type == 'By Fitted Distribution':
            response = requests.get('http://127.0.0.1:5000/get_distribution')
            # response = requests.get('https://db1a-35-202-194-168.ngrok-free.app/get_distribution')
            
            if response.status_code == 200:
                interarrival_distribution = response.json()['interarrival_distribution']
            else:
                # Default value if the server request fails
                interarrival_distribution = 'random.expovariate(1.0 / 5)'

            env.process(customer_arrivals_on_distribution(env, clinic, interarrival_distribution))
        
        elif interarrival_type == 'By Schedule':
            response = requests.get('http://127.0.0.1:5000/get_arrival_schedule')

            if response.status_code == 200:
                schedule = response.json()['arrival_schedule']
            else:
                # Default value if the server request fails
                st.warning("No Schedule found. Upload schedule first")
                
            env.process(customer_arrivals_on_schedule(env, clinic, schedule))
            
        
        env.process(clinic.record_utilization())

        env.run(until=sim_time)

        # Calculate utilization based on the provided formula
        dentist_utilization = sum(clinic.dentist_utilization_over_time) / (num_dentists * len(clinic.dentist_utilization_over_time))
        desk_staff_utilization = sum(clinic.desk_staff_utilization_over_time) / (num_desk_staff * len(clinic.desk_staff_utilization_over_time))
        seater_utilization = sum(clinic.seater_utilization_over_time) / (num_seats * len(clinic.seater_utilization_over_time))

        # Calculate average waiting time
        average_waiting_time = sum(clinic.customer_wait_times) / len(clinic.customer_wait_times) if clinic.customer_wait_times else 0

        # Return the metrics
        return {
            "total_customers_arrived": clinic.total_customers_arrived,
            "total_customers_served": clinic.total_customers_served,
            "dentist_utilization": dentist_utilization,
            "desk_staff_utilization": desk_staff_utilization,
            "seater_utilization": seater_utilization,
            "average_waiting_time": average_waiting_time,
            "dentist_utilization_over_time": clinic.dentist_utilization_over_time,
            "desk_staff_utilization_over_time": clinic.desk_staff_utilization_over_time,
            "seater_utilization_over_time": clinic.seater_utilization_over_time,
            "revenue": clinic.revenue
        }

    # Streamlit UI
    st.title('Dental Clinic Simulation')

    # Input fields for the constants in two columns
    col1, col2 = st.columns(2)

    with col1:
        # random_seed = st.number_input('Random Seed', value=42, step=1)
        num_dentists = st.number_input('Number of Dentists', value=1, step=1, min_value=1)
        num_desk_staff = st.number_input('Number of Desk Staff', value=1, step=1, min_value=1)
         

    with col2:        
        num_seats = st.number_input('Number of Seats', value=3, step=1, min_value=1)
        sim_time = st.number_input('Simulation Time     (minutes)', value=480, step=1, min_value=1)
        # record_interval = st.number_input('Record Interval (minutes)', value=1, step=1, min_value=1)
    
    interarrival_type = st.selectbox("Interarrival Type", ("By Fitted Distribution", "By Schedule"))   

    if st.button('Run Simulation'):
        results = run_simulation(num_dentists, num_desk_staff, num_seats, sim_time, interarrival_type)

        # Display output metrics in two columns 
        col3, col4 = st.columns(2)

        with col3:
            st.metric(label="Total customers served", value=results['total_customers_served'])
            st.metric(label="Dentist utilization", value=f"{results['dentist_utilization']:.2%}")
            st.metric(label="Seater utilization", value=f"{results['seater_utilization']:.2%}")

        with col4:
            st.metric(label="Total Revenue", value=f"$ {results['revenue']}")
            st.metric(label="Desk staff utilization", value=f"{results['desk_staff_utilization']:.2%}")
            st.metric(label="Average waiting time (minutes)", value=f"{results['average_waiting_time']:.2f}")
            
        st.markdown('## Dentist Utilization Over Time')
        
        # Create the histogram using seaborn
        plt.figure(figsize=(10, 6))  # Optional: Adjust figure size
        sns.lineplot(results["dentist_utilization_over_time"])
        plt.xlabel("Time")
        plt.ylabel("Utilization")
        plt.title("Dentist Utilization Over Time")

        # Display the plot in Streamlit
        st.pyplot(plt)
        
        st.markdown('## Seater Utilization Over Time')

        # Create the histogram using seaborn
        plt.figure(figsize=(10, 6))  # Optional: Adjust figure size
        sns.lineplot(results["seater_utilization_over_time"])
        plt.xlabel("Time")
        plt.ylabel("Utilization")
        plt.title("Seater Utilization Over Time")

        # Display the plot in Streamlit
        st.pyplot(plt)
