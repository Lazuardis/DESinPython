import simpy
import numpy as np
import random

class EaterySimulation:
    def __init__(self, env, front_staff_cap, back_staff_cap, two_seater_cap, four_seater_cap):
        self.env = env
        self.front_staff = simpy.Resource(env, capacity=front_staff_cap)
        self.back_staff = simpy.Resource(env, capacity=back_staff_cap)
        self.two_seater = simpy.Resource(env, capacity=two_seater_cap)
        self.four_seater = simpy.Resource(env, capacity=four_seater_cap)
        
        self.customer_count = 0
        self.customer_served = 0
        self.waiting_customer = 0
        self.dissatisfied_customer = 0
        self.twoseater_util = 0
        self.fourseater_util = 0
        self.front_staff_utility = 0
        self.back_staff_utility = 0
        self.customer_waiting_time = []
        self.arriving_time = []

        
        self.processing_time = {
            "till_process": random.uniform(1, 3),
            "coffee_process": random.gauss(1, 0.5),
            "pizza_process": random.gauss(5, 1),
            "dining_in": random.gauss(10, 5)
        }

    def customer_arrival(self, inter_arrival_time):
        while True:
            yield self.env.timeout(random.expovariate(1/inter_arrival_time))
            self.arriving_time.append(self.env.now)
            self.customer_count += 1
            customer_type = random.choices([1, 2, 3, 4], [0.4, 0.3, 0.2, 0.1])[0]
            self.env.process(self.till_activity(self.customer_count, customer_type))

    def till_activity(self, customer, customer_type):
        waiting_time = 0
        with self.front_staff.request() as till_request:
            till_wait_start = self.env.now
            self.waiting_customer += customer_type
            yield till_request
            self.front_staff_utility += 1
            waiting_time += self.env.now - till_wait_start
            self.waiting_customer -= customer_type
            yield self.env.timeout(self.processing_time["till_process"])
            self.front_staff_utility -= 1

        order_type = random.randint(1, 3)
        dining_in = random.choices([0, 1], [0.2, 0.8])[0]

        if order_type == 1:
            self.env.process(self.coffee_activity(customer, customer_type, dining_in, waiting_time))
        elif order_type == 2:
            self.env.process(self.pizza_activity(customer, customer_type, dining_in, waiting_time))
        else:
            self.env.process(self.coffee_pizza_activity(customer, customer_type, dining_in, waiting_time))

    def coffee_activity(self, customer, customer_type, dining_in, waiting_time):
        with self.front_staff.request() as coffee_request:
            self.waiting_customer += customer_type
            order_waiting = self.env.now
            yield coffee_request
            self.front_staff_utility += 1
            yield self.env.timeout(self.processing_time["coffee_process"] * customer_type)
            self.waiting_customer -= customer_type
            waiting_time += self.env.now - order_waiting
            self.front_staff_utility -= 1

        if dining_in == 1:
            self.env.process(self.dining_activity(customer, customer_type, waiting_time))
        else:
            self.customer_served += customer_type
            self.customer_waiting_time.append(waiting_time)

    def pizza_activity(self, customer, customer_type, dining_in, waiting_time):
        with self.back_staff.request() as pizza_request:
            self.waiting_customer += customer_type
            order_waiting = self.env.now
            yield pizza_request
            self.back_staff_utility += 1
            yield self.env.timeout(self.processing_time["pizza_process"] * customer_type)
            self.waiting_customer -= customer_type
            waiting_time += self.env.now - order_waiting
            self.back_staff_utility -= 1

        if dining_in == 1:
            self.env.process(self.dining_activity(customer, customer_type, waiting_time))
        else:
            self.customer_served += customer_type
            self.customer_waiting_time.append(waiting_time)

    def coffee_pizza_activity(self, customer, customer_type, dining_in, waiting_time):
        order_waiting = self.env.now
        self.waiting_customer += customer_type

        req_back_staff = self.back_staff.request()
        req_front_staff = self.front_staff.request()
        yield simpy.events.AllOf(self.env, [req_back_staff, req_front_staff])

        coffee_process_time = self.processing_time["coffee_process"]
        pizza_process_time = self.processing_time["pizza_process"]
        yield self.env.timeout(
            coffee_process_time * customer_type if coffee_process_time > pizza_process_time else pizza_process_time * customer_type
        )

        waiting_time += self.env.now - order_waiting
        self.waiting_customer -= customer_type

        self.back_staff.release(req_back_staff)
        self.front_staff.release(req_front_staff)

        if dining_in == 1:
            self.env.process(self.dining_activity(customer, customer_type, waiting_time))
        else:
            self.customer_served += customer_type
            self.customer_waiting_time.append(waiting_time)

    def dining_activity(self, customer, customer_type, waiting_time):
        table_waiting = self.env.now
        if customer_type <= 2:
            with self.two_seater.request() as twoseater_request:
                willingness_to_wait = random.uniform(10, 25)
                self.waiting_customer += customer_type
                decision = yield twoseater_request | self.env.timeout(willingness_to_wait)
                waiting_time += self.env.now - table_waiting
                if twoseater_request in decision:
                    self.twoseater_util += 1
                    self.waiting_customer -= customer_type
                    yield self.env.timeout(self.processing_time["dining_in"])
                    self.customer_served += customer_type
                    self.twoseater_util -= 1
                else:
                    self.customer_served += customer_type
                    self.waiting_customer -= customer_type
                    self.dissatisfied_customer += customer_type
        else:
            with self.four_seater.request() as fourseater_request:
                willingness_to_wait = random.uniform(10, 25)
                self.waiting_customer += customer_type
                decision = yield fourseater_request | self.env.timeout(willingness_to_wait)
                waiting_time += self.env.now - table_waiting
                if fourseater_request in decision:
                    self.fourseater_util += 1
                    self.waiting_customer -= customer_type
                    yield self.env.timeout(self.processing_time["dining_in"])
                    self.customer_served += customer_type
                    self.fourseater_util -= 1
                else:
                    self.customer_served += customer_type
                    self.waiting_customer -= customer_type
                    self.dissatisfied_customer += customer_type

        self.customer_waiting_time.append(waiting_time)

    def monitor_customer(self):
        while True:
            yield self.env.timeout(5)
            self.timestamp.append(self.env.now)
            self.waiting_customer_array.append(self.waiting_customer)

    def monitor_utilization(self):
        while True:
            yield self.env.timeout(2)
            self.timestamp.append(self.env.now)
            self.twoseater_util_array.append(self.twoseater_util)
            self.fourseater_util_array.append(self.fourseater_util)
            self.front_staff_util_array.append(self.front_staff_utility)
            self.back_staff_util_array.append(self.back_staff_utility)

    def run_simulation(self, inter_arrival_time, run_time):
        self.timestamp = []
        self.waiting_customer_array = []
        self.twoseater_util_array = []
        self.fourseater_util_array = []
        self.front_staff_util_array = []
        self.back_staff_util_array = []

        self.env.process(self.customer_arrival(inter_arrival_time))
        self.env.process(self.monitor_customer())
        self.env.process(self.monitor_utilization())
        self.env.run(until=run_time)
        
        results = {
            "average_waiting_time": np.mean([max(0, x) for x in self.customer_waiting_time]),
            "average_waiting_customer": np.mean([max(0, x) for x in self.waiting_customer_array]),
            "front_staff_util": np.mean(self.front_staff_util_array) / self.front_staff.capacity,
            "back_staff_util": np.mean(self.back_staff_util_array) / self.back_staff.capacity,
            "twoseater_util": np.mean(self.twoseater_util_array) / self.two_seater.capacity,
            "fourseater_util": np.mean(self.fourseater_util_array) / self.four_seater.capacity,
            "customer_served": self.customer_served,
            "front_staff_util_array": self.front_staff_util_array,
            "back_staff_util_array": self.back_staff_util_array,
            "twoseater_util_array": self.twoseater_util_array,
            "fourseater_util_array": self.fourseater_util_array,
            "customer_count": self.customer_count,
            "arrival_times": [self.arriving_time[0]] + [j - i for i, j in zip(self.arriving_time[:-1], self.arriving_time[1:])]
        }
        
        return results

    
    

        # print(f"Average number of customer waiting: {np.mean(self.waiting_customer_array):.2f}")
        # print(f"Average customer waiting time: {np.mean(self.customer_waiting_time):.2f}")
        # print(f"Front Staff Util: {np.mean(self.front_staff_util_array)/self.front_staff.capacity:.2f}")
        # print(f"Back Staff Util: {np.mean(self.back_staff_util_array)/self.back_staff.capacity:.2f}")
        # print(f"Two Seater Util: {np.mean(self.twoseater_util_array)/self.two_seater.capacity:.2f}")
        # print(f"Four Seater Util: {np.mean(self.fourseater_util_array)/self.four_seater.capacity:.2f}")
        # print(f"Number of customer served: {self.customer_served}")


