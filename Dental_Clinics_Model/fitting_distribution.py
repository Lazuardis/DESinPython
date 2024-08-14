import pandas as pd
import numpy as np
import scipy.stats as stats

def process_interarrival_times(arrival_times):
    # Convert the 'Arrival_Time' column to datetime
    arrival_times['Arrival_Time'] = pd.to_datetime(arrival_times['Arrival_Time'], format='%H:%M')

    # Define the start of working hours
    start_time = pd.to_datetime('07:00', format='%H:%M')

    # Calculate the inter-arrival time
    arrival_times['Inter-Arrival Time'] = arrival_times['Arrival_Time'].diff().fillna(arrival_times['Arrival_Time'] - start_time)

    # Convert the inter-arrival time to minutes
    arrival_times['Inter-Arrival Time (Minutes)'] = arrival_times['Inter-Arrival Time'].dt.total_seconds() / 60

    return arrival_times[['Inter-Arrival Time (Minutes)']]

def fit_distribution_interarrival(inter_arrival_times):
    # Extract the data as a numpy array
    data = inter_arrival_times['Inter-Arrival Time (Minutes)'].values

    # Fit the data to different distributions and calculate the goodness of fit
    distributions = ['norm', 'expon', 'gamma', 'weibull_min']
    fitting_results = []

    for dist_name in distributions:
        dist = getattr(stats, dist_name)
        params = dist.fit(data)
        # Perform the Kolmogorov-Smirnov test
        ks_stat, ks_p_value = stats.kstest(data, dist_name, args=params)
        fitting_results.append((dist_name, params, ks_stat, ks_p_value))

    # Convert the results into a DataFrame for easier interpretation
    fitting_df = pd.DataFrame(fitting_results, columns=['Distribution', 'Parameters', 'KS Statistic', 'P-Value'])
    fitting_df = fitting_df.sort_values(by='KS Statistic')
    
    best_fit = fitting_df.iloc[0]  # The first row after sorting by KS Statistic

    # Extracting the distribution name and parameters
    distribution_name = best_fit['Distribution']
    params = best_fit['Parameters']

    # Initialize the interarrival_distribution variable
    interarrival_distribution = None

    # Determine the appropriate distribution and assign to the variable
    if distribution_name == 'expon':
        rate = 1.0 / params[1]  # For exponential, params[1] is the scale (mean)
        interarrival_distribution = f"random.expovariate({rate})"
    elif distribution_name == 'norm':
        mean, std_dev = params
        interarrival_distribution = f"random.gauss({mean}, {std_dev})"
    # elif distribution_name == 'lognorm':
    #     sigma, loc, scale = params
    #     interarrival_distribution = f"random.lognormvariate({loc}, {sigma})"
    elif distribution_name == 'gamma':
        shape, loc, scale = params
        interarrival_distribution = f"random.gammavariate({shape}, {scale})"
    elif distribution_name == 'weibull_min':
        shape, loc, scale = params
        interarrival_distribution = f"random.weibullvariate({scale}, {shape})"
    else:
        interarrival_distribution = "Unsupported distribution"

    # Return the distribution as a string
    return interarrival_distribution
