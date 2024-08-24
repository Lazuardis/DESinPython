import simpy
import random
import pandas as pd
import numpy as np
from clinic_data import get_specialties_matrix, get_treatment_list


class Dentist:
    def __init__(self, name, specialties):
        self.name = name
        self.specialties = specialties  # Set or list of procedures the dentist can perform

class DentalClinic:
    def __init__(self, env, num_dentists, num_desk_staff, num_seats):
        self.env = env

        self.desk_staff = simpy.Resource(env, num_desk_staff)
        self.seats = simpy.Resource(env, num_seats)
        
        self.dentists = simpy.FilterStore(self.env)
        
        specialties_matrix = get_specialties_matrix()
        
        for name, specialties in specialties_matrix.items():
            self.dentists.put(Dentist(name, specialties))
        
        self.total_customers_arrived = 0
        self.total_customers_served = 0
        self.revenue = 0

        # Track busy time for utilization
        self.dentist_busy_time = 0
        self.desk_staff_busy_time = 0
        self.seater_busy_time = 0

        # Track current utilization
        self.current_dentist_utilization = 0
        self.current_desk_staff_utilization = 0
        self.current_seater_utilization = 0

        # Track utilization over time
        self.dentist_utilization_over_time = []
        self.desk_staff_utilization_over_time = []
        self.seater_utilization_over_time = []

        # Track waiting times
        self.total_waiting_time = 0
        self.customer_wait_times = []
        
        
    def customer_arrival(self, customer):
        arrival_time = self.env.now
        self.total_customers_arrived += 1
        yield self.env.process(self.administration_process(customer, arrival_time))

    def administration_process(self, customer, arrival_time):
        with self.desk_staff.request() as admin_request, self.seats.request() as seat_request:
            
            waiting_admin_time = self.env.now
            
            decision = yield admin_request | seat_request

            if seat_request in decision:
                self.current_seater_utilization += 1
                with admin_request:
                    yield admin_request
                    self.seats.release(seat_request)
                    self.seater_busy_time += self.env.now - waiting_admin_time
                    self.current_seater_utilization -= 1
                    
                    # Record total waiting time before administration
                    wait_time = self.env.now - waiting_admin_time
                    self.total_waiting_time += wait_time
                    self.customer_wait_times.append(wait_time)

                    self.current_desk_staff_utilization += 1

                    start_time = self.env.now
                    administration_time = random.uniform(1, 3)  # Dummy value
                    yield self.env.timeout(administration_time)
                    self.desk_staff_busy_time += self.env.now - start_time
                    self.current_desk_staff_utilization -= 1
            else:
                self.current_desk_staff_utilization += 1
                
                start_time = self.env.now
                administration_time = random.uniform(1, 3)  # Dummy value
                yield self.env.timeout(administration_time)
                self.desk_staff_busy_time += self.env.now - start_time
                self.current_desk_staff_utilization -= 1

        yield self.env.process(self.dental_treatment(customer, arrival_time))

    def dental_treatment(self, customer, arrival_time):
        # Choose a random specialty that the customer requires (for simulation purposes)
        required_specialty = random.choice(get_treatment_list())

        
        # Request a dentist who can perform the required specialty
        dentist_request = self.dentists.get(lambda dentist: required_specialty in dentist.specialties)
        
        # Request a seat for the customer
        seat_request = self.seats.request()
        
        waiting_dentist_time = self.env.now
        
        # Wait until either a seat or a suitable dentist is available
        decision = yield dentist_request | seat_request

        if seat_request in decision:
            # If a seat becomes available first
            self.current_seater_utilization += 1
            
            # Wait for the seat to become available
            yield seat_request
            self.seats.release(seat_request)
            self.seater_busy_time += self.env.now - waiting_dentist_time
            self.current_seater_utilization -= 1

            # Now wait for the dentist to become available
            dentist = yield dentist_request
            self.current_dentist_utilization += 1

            # Record the wait time before treatment
            wait_time = self.env.now - waiting_dentist_time
            self.total_waiting_time += wait_time
            self.customer_wait_times.append(wait_time)

            # Perform the dental treatment
            service_time = random.uniform(10, 30)  # Dummy value for service time
            yield self.env.timeout(service_time)
            
            # Record dentist busy time
            self.dentist_busy_time += self.env.now - self.env.now + wait_time
            self.total_customers_served += 1
            self.current_dentist_utilization -= 1

            # Return the dentist to the FilterStore
            self.dentists.put(dentist)
            
        else:
            # If a suitable dentist is available before a seat
            dentist = yield dentist_request
            self.current_dentist_utilization += 1

            # Record the wait time before treatment
            wait_time = self.env.now - arrival_time
            self.total_waiting_time += wait_time
            self.customer_wait_times.append(wait_time)

            # Perform the dental treatment
            service_time = random.uniform(5, 10)  # Dummy value for service time
            yield self.env.timeout(service_time)
            
            # Record dentist busy time
            self.dentist_busy_time += self.env.now - self.env.now + wait_time
            self.total_customers_served += 1
            self.current_dentist_utilization -= 1

            # Return the dentist to the FilterStore
            self.dentists.put(dentist)
            
        # Update revenue
        self.revenue += 50  # Dummy revenue value


    def record_utilization(self, record_interval=1):
        while True:
            yield self.env.timeout(record_interval)
            self.dentist_utilization_over_time.append(self.current_dentist_utilization)
            self.desk_staff_utilization_over_time.append(self.current_desk_staff_utilization)
            self.seater_utilization_over_time.append(self.current_seater_utilization)

def customer_arrivals_on_distribution(env, clinic, interarrival_distribution):
    customer_id = 0
    
    interarrival_function = lambda: eval(interarrival_distribution)
    
    while True:
        yield env.timeout(interarrival_function())  # Dummy interarrival time
        customer_id += 1
        env.process(clinic.customer_arrival(f'Customer {customer_id}'))
        
        
def customer_arrivals_on_schedule(env, clinic, schedule_df):
    customer_id = 0
    
    for arrival_interval in schedule_df:
        yield env.timeout(arrival_interval)  # Dummy interarrival time
        customer_id += 1
        env.process(clinic.customer_arrival(f'Customer {customer_id}'))