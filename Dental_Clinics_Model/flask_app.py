from flask import Flask, request, jsonify
import random
import simpy
from dental_model import DentalClinic, customer_arrivals_on_distribution, customer_arrivals_on_schedule
import requests

app = Flask(__name__)

# In-memory storage for the interarrival distribution
data_store = {
    "interarrival_distribution": "random.expovariate(1.0 / 5)"
}

@app.route('/')
def home():
    return f"It is running"

@app.route('/set_distribution', methods=['POST'])
def set_distribution():
    data = request.json
    data_store['interarrival_distribution'] = data['interarrival_distribution']
    return jsonify({"status": "success"}), 200

@app.route('/get_distribution', methods=['GET'])
def get_distribution():
    return jsonify(data_store)

@app.route('/set_arrival_schedule', methods=['POST'])
def set_arrival_schedule():
    data = request.json
    data_store['arrival_schedule'] = data['arrival_schedule']
    return jsonify({"status": "success"}), 200

@app.route('/get_arrival_schedule', methods=['GET'])
def get_arrival_schedule():
    return jsonify(data_store)

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    data = request.json
    num_dentists = data['num_dentists']
    num_desk_staff = data['num_desk_staff']
    num_seats = data['num_seats']
    sim_time = data['sim_time']
    num_replications = data.get('num_replications', 1)
    interarrival_type = data['interarrival_type']
    

    results = run_multiple_simulations(num_dentists, num_desk_staff, num_seats, sim_time, num_replications, interarrival_type)
    return jsonify(results)

def run_simulation_once(num_dentists, num_desk_staff, num_seats, sim_time, interarrival_type):
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
        "dentist_utilization": dentist_utilization,
        "desk_staff_utilization": desk_staff_utilization,
        "seater_utilization": seater_utilization,
        "average_waiting_time": average_waiting_time,
    }

def run_multiple_simulations(num_dentists, num_desk_staff, num_seats, sim_time, num_replications, interarrival_type):
    dentist_utilizations = []
    desk_staff_utilizations = []
    seater_utilizations = []
    avg_waiting_time_list = []

    for _ in range(num_replications):
        results = run_simulation_once(num_dentists, num_desk_staff, num_seats, sim_time, interarrival_type)
        dentist_utilizations.append(results['dentist_utilization'])
        desk_staff_utilizations.append(results['desk_staff_utilization'])
        seater_utilizations.append(results['seater_utilization'])
        avg_waiting_time_list.append(results['average_waiting_time'])
        
    # Calculate the mean utilization across all replications
    avg_dentist_utilization = sum(dentist_utilizations) / num_replications
    avg_desk_staff_utilization = sum(desk_staff_utilizations) / num_replications
    avg_seater_utilization = sum(seater_utilizations) / num_replications
    avg_waiting_time_all = sum(avg_waiting_time_list) / num_replications

    # Return the arrays and the mean utilizations
    return {
        "dentist_utilizations": dentist_utilizations,
        "desk_staff_utilizations": desk_staff_utilizations,
        "seater_utilizations": seater_utilizations,
        "avg_waiting_time_list": avg_waiting_time_list,
        "avg_dentist_utilization": avg_dentist_utilization,
        "avg_desk_staff_utilization": avg_desk_staff_utilization,
        "avg_seater_utilization": avg_seater_utilization,
        "avg_waiting_time_all": avg_waiting_time_all
    }


if __name__ == '__main__':
    app.run(debug=True, port=5000)

