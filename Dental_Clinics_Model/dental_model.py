import simpy
import random

class DentalClinic:
    def __init__(self, env, num_dentists, num_desk_staff, num_seats):
        self.env = env
        self.dentists = simpy.Resource(env, num_dentists)
        self.desk_staff = simpy.Resource(env, num_desk_staff)
        self.seats = simpy.Resource(env, num_seats)
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
        
    # def dentist_schedule(self, dentist_schedule, dentist performance):
        
        
        

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
        with self.dentists.request() as dentist_request, self.seats.request() as seat_request:
            
            waiting_dentist_time = self.env.now
            
            decision = yield dentist_request | seat_request

            if seat_request in decision:
                self.current_seater_utilization += 1
                with dentist_request:
                    yield dentist_request
                    self.seats.release(seat_request)
                    self.seater_busy_time += self.env.now - waiting_dentist_time
                    self.current_seater_utilization -= 1
                    
                    # Record total waiting time before dental treatment
                    wait_time = self.env.now - waiting_dentist_time
                    self.total_waiting_time += wait_time
                    self.customer_wait_times.append(wait_time)
                    
                    self.current_dentist_utilization += 1
                    start_time = self.env.now

                    service_time = random.uniform(10, 30)  # Dummy value
                    yield self.env.timeout(service_time)
                    self.dentist_busy_time += self.env.now - start_time
                    self.total_customers_served += 1
                    self.current_dentist_utilization -= 1
            else:
                self.current_dentist_utilization += 1

                start_time = self.env.now

                # Record total waiting time before dental treatment
                wait_time = self.env.now - arrival_time
                self.total_waiting_time += wait_time
                self.customer_wait_times.append(wait_time)

                service_time = random.uniform(5, 10)  # Dummy value
                yield self.env.timeout(service_time)
                self.dentist_busy_time += self.env.now - start_time
                self.total_customers_served += 1
                self.current_dentist_utilization -= 1
                
        self.revenue += 50  # Dummy revenue

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