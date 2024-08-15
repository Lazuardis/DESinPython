from flask import Flask, request, jsonify
import random
import simpy
from dental_model import DentalClinic, customer_arrivals

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



@app.route('/run_simulation', methods=['POST'])
def run_simulation():
    data = request.json
    num_dentists = data['num_dentists']
    num_desk_staff = data['num_desk_staff']
    num_seats = data['num_seats']
    sim_time = data['sim_time']
    num_replications = data.get('num_replications', 1)

    results = run_multiple_simulations(num_dentists, num_desk_staff, num_seats, sim_time, num_replications)
    return jsonify(results)

def run_simulation_once(num_dentists, num_desk_staff, num_seats, sim_time, interarrival_distribution='random.expovariate(1.0 / 5)'):
    env = simpy.Environment()

    clinic = DentalClinic(env, num_dentists, num_desk_staff, num_seats)
    env.process(customer_arrivals(env, clinic, interarrival_distribution))
    env.process(clinic.record_utilization())

    env.run(until=sim_time)

    # Calculate utilization based on the provided formula
    dentist_utilization = sum(clinic.dentist_utilization_over_time) / (num_dentists * len(clinic.dentist_utilization_over_time))
    desk_staff_utilization = sum(clinic.desk_staff_utilization_over_time) / (num_desk_staff * len(clinic.desk_staff_utilization_over_time))
    seater_utilization = sum(clinic.seater_utilization_over_time) / (num_seats * len(clinic.seater_utilization_over_time))

    # Return the metrics
    return {
        "dentist_utilization": dentist_utilization,
        "desk_staff_utilization": desk_staff_utilization,
        "seater_utilization": seater_utilization,
    }

def run_multiple_simulations(num_dentists, num_desk_staff, num_seats, sim_time, num_replications):
    dentist_utilizations = []
    desk_staff_utilizations = []
    seater_utilizations = []

    for _ in range(num_replications):
        results = run_simulation_once(num_dentists, num_desk_staff, num_seats, sim_time)
        dentist_utilizations.append(results['dentist_utilization'])
        desk_staff_utilizations.append(results['desk_staff_utilization'])
        seater_utilizations.append(results['seater_utilization'])

    # Calculate the mean utilization across all replications
    avg_dentist_utilization = sum(dentist_utilizations) / num_replications
    avg_desk_staff_utilization = sum(desk_staff_utilizations) / num_replications
    avg_seater_utilization = sum(seater_utilizations) / num_replications

    # Return the arrays and the mean utilizations
    return {
        "dentist_utilizations": dentist_utilizations,
        "desk_staff_utilizations": desk_staff_utilizations,
        "seater_utilizations": seater_utilizations,
        "avg_dentist_utilization": avg_dentist_utilization,
        "avg_desk_staff_utilization": avg_desk_staff_utilization,
        "avg_seater_utilization": avg_seater_utilization,
    }


if __name__ == '__main__':
    app.run(debug=True, port=5000)

