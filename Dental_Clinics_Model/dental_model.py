import simpy
import random
import pandas as pd
import numpy as np
from clinic_data import *


class Dentist:
    def __init__(self, name, specialties):
        self.name = name
        self.specialties = specialties  # Set or list of procedures the dentist can perform
        self.total_busy_time = 0  # Total time the dentist has been busy
        self.procedures_performed = 0  # Number of procedures performed by the dentist
        self.last_busy_start_time = None  # Time when the dentist last started being busy
        
    def start_busy(self, current_time):
        """Record the start of a busy period for the dentist."""
        self.last_busy_start_time = current_time

    def end_busy(self, current_time):
        """Record the end of a busy period and update the total busy time."""
        if self.last_busy_start_time is not None:
            busy_duration = current_time - self.last_busy_start_time
            self.total_busy_time += busy_duration
            self.last_busy_start_time = None
            self.procedures_performed += 1  # Increment procedures count when busy period ends


class DentalClinic:
    def __init__(self, env, num_dentists, num_desk_staff, num_seats, set_dentist_schedule, treatment_demand_list=None):
        self.env = env

        self.desk_staff = simpy.Resource(env, num_desk_staff)
        self.seats = simpy.Resource(env, num_seats)
        
        self.dentists = simpy.FilterStore(self.env)
        
        if set_dentist_schedule == True:
            dentist_matrix = get_specialties_matrix()

        else:
            dentist_matrix = generate_dummy_dentist(num_dentists)

        
        for name, specialties in dentist_matrix.items():
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
        
        
        
    
    def customer_arrival(self, customer, treatment_demand_list=None):
        arrival_time = self.env.now
        self.total_customers_arrived += 1
        
        if treatment_demand_list is not None:
            
            treatment = treatment_demand_list[self.total_customers_arrived-1]
            
        else:
            treatment = random.choice(get_treatment_list())
        yield self.env.process(self.administration_process(customer, arrival_time, treatment))

    def administration_process(self, customer, arrival_time, treatment):
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

        yield self.env.process(self.dental_treatment(customer, arrival_time, treatment))

    def dental_treatment(self, customer, arrival_time, treatment):
        
        with self.dentists.get(lambda dentist: treatment in dentist.specialties) as dentist_request, self.seats.request() as seat_request:
            
        
            waiting_dentist_time = self.env.now
            
            # Wait until either a seat or a suitable dentist is available
            decision = yield dentist_request | seat_request

            if seat_request in decision:
                # If a seat becomes available first
                self.current_seater_utilization += 1
                
                # Wait for the seat to become available
                yield seat_request


                # Now wait for the dentist to become available
                dentist = yield dentist_request
                
                self.seats.release(seat_request)
                self.seater_busy_time += self.env.now - waiting_dentist_time
                self.current_seater_utilization -= 1

                dentist.start_busy(self.env.now)
                self.current_dentist_utilization += 1

                # Record the wait time before treatment
                wait_time = self.env.now - waiting_dentist_time
                self.total_waiting_time += wait_time
                self.customer_wait_times.append(wait_time)

                # Perform the dental treatment
                service_time = random.uniform(10, 30)  # Dummy value for service time
                service_time = get_treatment_duration(treatment)
                yield self.env.timeout(service_time)
                
                dentist.end_busy(self.env.now)
                # Record dentist busy time
                self.dentist_busy_time += self.env.now - self.env.now + wait_time
                self.total_customers_served += 1
                

                # Return the dentist to the FilterStore
                self.dentists.put(dentist)
                self.current_dentist_utilization -= 1   
                
            else:
                # If a suitable dentist is available before a seat
                dentist = yield dentist_request
                

                dentist.start_busy(self.env.now)  
                self.current_dentist_utilization += 1      

                # Record the wait time before treatment
                wait_time = self.env.now - arrival_time
                self.total_waiting_time += wait_time
                self.customer_wait_times.append(wait_time)

                # Perform the dental treatment
                service_time = random.uniform(5, 10)  # Dummy value for service time\
                service_time = get_treatment_duration(treatment)
                yield self.env.timeout(service_time)
                
                dentist.end_busy(self.env.now)
                
                # Record dentist busy time
                self.dentist_busy_time += self.env.now - self.env.now + wait_time
                self.total_customers_served += 1
            
                # Return the dentist to the FilterStore
                self.dentists.put(dentist)
                
                self.current_dentist_utilization -= 1
                
                
            # Update revenue
            self.revenue += 50  # Dummy revenue value
            
            


    def record_utilization(self, record_interval=1):
        while True:
            yield self.env.timeout(record_interval)
            self.dentist_utilization_over_time.append(self.current_dentist_utilization)
            self.desk_staff_utilization_over_time.append(self.current_desk_staff_utilization)
            self.seater_utilization_over_time.append(self.current_seater_utilization)
            
    

    
    
            
            
    # def generate_dentist_statistics_df(self):
    #     """Generate a DataFrame containing statistics for each dentist."""
    #     # Initialize an empty list to store dentist data
    #     dentist_data = []

    #     # Loop through each dentist in the FilterStore and collect their statistics
    #     for dentist in self.dentists.items:
    #         dentist_data.append({
    #             'Name': dentist.name,
    #             'Total Busy Time': dentist.total_busy_time,
    #             'Procedures Performed': dentist.procedures_performed,
    #             # 'Utilization': dentist.total_busy_time / self.sim_duration  # Calculate utilization
    #         })

    #     # Create a DataFrame from the collected data
    #     dentist_df = pd.DataFrame(dentist_data)

    #     return dentist_df

def customer_arrivals_on_distribution(env, clinic, interarrival_distribution, sim_time):
    customer_id = 0
    
    interarrival_function = lambda: eval(interarrival_distribution)
    
    while env.now < sim_time:
        yield env.timeout(interarrival_function())  # Dummy interarrival time
        customer_id += 1
        env.process(clinic.customer_arrival(f'Customer {customer_id}'))
            
        
def customer_arrivals_on_schedule(env, clinic, schedule_df):
    customer_id = 0
    
    for arrival_interval in schedule_df:
        yield env.timeout(arrival_interval)  # Dummy interarrival time
        customer_id += 1
        env.process(clinic.customer_arrival(f'Customer {customer_id}'))
        
def terminating_condition(env, clinic, sim_time, terminate):

    while True:
        yield env.timeout(1)
        if clinic.env.now >= sim_time:
            if clinic.total_customers_served == clinic.total_customers_arrived:
                print(env.now)   
                terminate.succeed()
                 
                
def terminating_condition_schedule(env, clinic, terminate, schedule_df):

    while True:
        yield env.timeout(1)
        if clinic.total_customers_served == len(schedule_df):
            terminate.succeed()    