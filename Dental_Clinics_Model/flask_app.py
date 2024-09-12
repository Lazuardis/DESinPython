from flask import Flask, request, jsonify
import random
import simpy
from dental_model import *
from clinic_data import *
import requests

app = Flask(__name__)

# In-memory storage for the interarrival distribution
data_store = {
    "interarrival_distribution": "random.expovariate(1.0 / 5)"
}

@app.route('/')
def home():
    return "It is running"

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

@app.route('/run_simulation_once', methods=['POST'])
def run_simulation_individual():
    data = request.json
    num_dentists = data['num_dentists']
    num_desk_staff = data['num_desk_staff']
    num_seats = data['num_seats']
    sim_time = data['sim_time']
    interarrival_type = data['interarrival_type']
    set_dentist_schedule = data.get('set_dentist_schedule', False)
    num_days = data['num_days']
    customer_treatment_pattern = data['customer_treatment_pattern']
    
    if customer_treatment_pattern == 'Random':
    # Use run_single_simulation as the reference
    # results = run_single_simulation(num_dentists, num_desk_staff, num_seats, sim_time, interarrival_type, set_dentist_schedule)
        results = run_single_sim_multiple_days(num_days, num_dentists, num_desk_staff, num_seats, sim_time, interarrival_type, set_dentist_schedule)
        
    else:
        
        treatment_demand = retrieve_treatment_name()
        
        results = run_single_sim_multiple_days(num_days, num_dentists, num_desk_staff, num_seats, sim_time, interarrival_type, set_dentist_schedule, customer_treatment_pattern=treatment_demand)
        
        
    
    return jsonify(results)

def run_single_sim_multiple_days(num_days, num_dentists, num_desk_staff, num_seats, sim_time, interarrival_type, set_dentist_schedule, customer_treatment_pattern=None):
    # Initialize lists to store cumulative results
    total_customers_arrived = 0
    total_customers_served = 0
    total_dentist_utilization = []
    total_desk_staff_utilization = []
    total_seater_utilization = []
    total_waiting_time = 0
    total_revenue = 0
    
    if customer_treatment_pattern is not None:
        
        customer_treatment_pattern = dict(list(customer_treatment_pattern.items())[:num_days])
        
        for day in range(num_days):
            
            day_index = list(customer_treatment_pattern.keys())[day]
            treatment_demand_list  = customer_treatment_pattern[day_index]
            
            result = run_single_simulation(num_dentists, num_desk_staff, num_seats, sim_time, interarrival_type, set_dentist_schedule)

            # Aggregate results
            total_customers_arrived += result["total_customers_arrived"]
            total_customers_served += result["total_customers_served"]
            total_dentist_utilization.extend(result["dentist_utilization_over_time"])
            total_desk_staff_utilization.extend(result["desk_staff_utilization_over_time"])
            total_seater_utilization.extend(result["seater_utilization_over_time"])
            total_waiting_time += result["average_waiting_time"] * result["total_customers_served"]  # Weighted by served customers
            total_revenue += result["revenue"]
            
    
    else:

    # Loop through the number of days
        for day in range(num_days):
            # Run a single simulation for the day
            result = run_single_simulation(num_dentists, num_desk_staff, num_seats, sim_time, interarrival_type, set_dentist_schedule)

            # Aggregate results
            total_customers_arrived += result["total_customers_arrived"]
            total_customers_served += result["total_customers_served"]
            total_dentist_utilization.extend(result["dentist_utilization_over_time"])
            total_desk_staff_utilization.extend(result["desk_staff_utilization_over_time"])
            total_seater_utilization.extend(result["seater_utilization_over_time"])
            total_waiting_time += result["average_waiting_time"] * result["total_customers_served"]  # Weighted by served customers
            total_revenue += result["revenue"]

    # Calculate averages where necessary
    avg_dentist_utilization = sum(total_dentist_utilization) / (len(total_dentist_utilization) * num_dentists) if total_dentist_utilization else 0
    avg_desk_staff_utilization = sum(total_desk_staff_utilization) / (len(total_desk_staff_utilization) * num_desk_staff) if total_desk_staff_utilization else 0
    avg_seater_utilization = sum(total_seater_utilization) / (len(total_seater_utilization) * num_seats) if total_seater_utilization else 0
    avg_waiting_time = total_waiting_time / total_customers_served if total_customers_served else 0

    # Return aggregated results
    return {
        "total_customers_arrived": total_customers_arrived,
        "total_customers_served": total_customers_served,
        "dentist_utilization": avg_dentist_utilization,
        "desk_staff_utilization": avg_desk_staff_utilization,
        "seater_utilization": avg_seater_utilization,
        "average_waiting_time": avg_waiting_time,
        "revenue": total_revenue,
        "dentist_utilization_over_time": total_dentist_utilization,
        "desk_staff_utilization_over_time": total_desk_staff_utilization,
        "seater_utilization_over_time": total_seater_utilization
    }


def run_single_simulation(num_dentists, num_desk_staff, num_seats, sim_time, interarrival_type, set_dentist_schedule):

    env = simpy.Environment()
    clinic = DentalClinic(env, num_dentists, num_desk_staff, num_seats, set_dentist_schedule)
    terminate = env.event()

    if interarrival_type == 'By Fitted Distribution':
        response = requests.get('http://127.0.0.1:5000/get_distribution')
        if response.status_code == 200:
            interarrival_distribution = response.json()['interarrival_distribution']
        else:
            interarrival_distribution = 'random.expovariate(1.0 / 5)'
        env.process(customer_arrivals_on_distribution(env, clinic, interarrival_distribution, sim_time))
        env.process(terminating_condition(env, clinic, sim_time, terminate))

    elif interarrival_type == 'By Schedule':
        response = requests.get('http://127.0.0.1:5000/get_arrival_schedule')
        if response.status_code == 200:
            schedule = response.json()['arrival_schedule']
        else:
            schedule = []
            print("No Schedule found. Upload schedule first")
        env.process(customer_arrivals_on_schedule(env, clinic, schedule))
        env.process(terminating_condition_schedule(env, clinic, terminate, schedule))

    
    
    env.process(clinic.record_utilization())
    
    env.run(until=terminate)


    num_dentists = num_dentists if not set_dentist_schedule else len(get_specialties_matrix())

    dentist_utilization = sum(clinic.dentist_utilization_over_time) / (num_dentists * len(clinic.dentist_utilization_over_time))
    desk_staff_utilization = sum(clinic.desk_staff_utilization_over_time) / (num_desk_staff * len(clinic.desk_staff_utilization_over_time))
    seater_utilization = sum(clinic.seater_utilization_over_time) / (num_seats * len(clinic.seater_utilization_over_time))
    average_waiting_time = sum(clinic.customer_wait_times) / len(clinic.customer_wait_times) if clinic.customer_wait_times else 0

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

@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    data = request.json
    num_dentists = data['num_dentists']
    num_desk_staff = data['num_desk_staff']
    num_seats = data['num_seats']
    sim_time = data['sim_time']
    num_replications = data.get('num_replications', 1)
    interarrival_type = data['interarrival_type']
    set_dentist_schedule = data.get('set_dentist_schedule', False)

    # Use run_multiple_simulations to run the batch
    results = run_multiple_simulations(num_dentists, num_desk_staff, num_seats, sim_time, num_replications, interarrival_type, set_dentist_schedule)
    return jsonify(results)

def run_multiple_simulations(num_dentists, num_desk_staff, num_seats, sim_time, num_replications, interarrival_type, set_dentist_schedule):
    dentist_utilizations = []
    desk_staff_utilizations = []
    seater_utilizations = []
    avg_waiting_time_list = []
    revenue_array = []

    for _ in range(num_replications):
        results = run_single_simulation(num_dentists, num_desk_staff, num_seats, sim_time, interarrival_type, set_dentist_schedule)
        dentist_utilizations.append(results['dentist_utilization'])
        desk_staff_utilizations.append(results['desk_staff_utilization'])
        seater_utilizations.append(results['seater_utilization'])
        avg_waiting_time_list.append(results['average_waiting_time'])
        revenue_array.append(results['revenue'])

    avg_dentist_utilization = sum(dentist_utilizations) / num_replications
    avg_desk_staff_utilization = sum(desk_staff_utilizations) / num_replications
    avg_seater_utilization = sum(seater_utilizations) / num_replications
    avg_waiting_time_all = sum(avg_waiting_time_list) / num_replications
    avg_revenue = sum(revenue_array) / num_replications
    std_revenue = np.std(revenue_array)

    return {
        "dentist_utilizations": dentist_utilizations,
        "desk_staff_utilizations": desk_staff_utilizations,
        "seater_utilizations": seater_utilizations,
        "avg_waiting_time_list": avg_waiting_time_list,
        "avg_dentist_utilization": avg_dentist_utilization,
        "avg_desk_staff_utilization": avg_desk_staff_utilization,
        "avg_seater_utilization": avg_seater_utilization,
        "avg_waiting_time_all": avg_waiting_time_all,
        "revenue_array": revenue_array,
        "avg_revenue": avg_revenue,
        "std_revenue": std_revenue
    }

if __name__ == '__main__':
    app.run(debug=True, port=5000)
