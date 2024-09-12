import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random

def get_treatment_list():
    
    
    
    
    treatments = [
        'Additional Root', 'Advanced Filling', 'Advanced Gum Treatment', 'Basic Filling', 
        'Basic Gum Treatment', 'Basic Scaling', 'Basic Tooth Extraction', 'Basic X-ray', 
        'Consultation', 'Dental Post & Core', 'Dental Spa', 'Membership Consultation Perk', 
        'Mouth Guard', 'Premium Bridge', 'Premium Crown', 'Prevention Seal', 
        'Root Canal Treatment', 'Wear Protect'
    ]
    
    
    treatments = ['11', '12', '13', '14', '22', '24', '37', '61', '71', '72', '73', '74', '82', 
                  '88011', '88012', '88013', '88022', 'CC', '111', '113', '114', '115', '116', '117', 
                  '118', '119', '121', '123', '141', '151', '161', '171', '88111', '88114', '88115', '88121', 
                  '88161', '88162', '213', '221', '222', '231', '250', '251', '311', '314', '322', '323', '324', 
                  '391', '88311', '88314', '88316', '88324', '411', '414', '415', '416', '417', '418', '419', '431', 
                  '455', '88414', '521', '522', '523', '524', '525', '526', '531', '532', '533', '534', '535', '572', 
                  '574', '576', '577', '578', '88521', '88523', '88524', '88525', '88531', '88532', '88533', '88534', 
                  '88586', '613', '627', '642', '643', '651', '652', '655', '711', '712', '721', '722', '727', '728', 
                  '731', '732', '733', '736', '741', '743', '744', '811', '825', '833', '845', '846', '872', '874', 
                  '88943', '915', '916', '926', '927', '943', '945', '949', '965', '0', '981', '990', '9999', 'Cem', 
                  'D9986', 'Insert', 'Zclin', '15', '19', '316', '165', '88322', '556', '631', '656', '753', '768', 
                  '776', '823', '841', '873', '966', 'Script', 'CrownCem', 'Rev', 'Spl Ins', '18', 'Add LA', 'InvisR', 
                  '245', '451', '88535', '632', '658', '88522', 'Dr Invis Cons', 'FIC', '281', '618']

    
    # Remove duplicates by converting to a set and back to a list
    treatments = list(set(treatments))
    # Sort treatments to ensure consistent order
    treatments.sort()
    
    
    
    return treatments

def get_specialties_matrix():
    specialties = {
        'Arnold': [
            'Additional Root', 'Advanced Filling', 'Advanced Gum Treatment', 'Basic Filling',
            'Basic Gum Treatment', 'Basic Scaling', 'Basic Tooth Extraction', 'Basic X-ray',
            'Consultation', 'Dental Post & Core', 'Dental Spa', 'Membership Consultation Perk',
            'Mouth Guard', 'Premium Bridge', 'Premium Crown', 'Prevention Seal',
            'Root Canal Treatment', 'Wear Protect'
        ],
        'Ronald': [
            'Additional Root', 'Advanced Filling', 'Advanced Gum Treatment', 'Basic Filling',
            'Basic Gum Treatment', 'Basic Scaling', 'Basic Tooth Extraction', 'Basic X-ray',
            'Consultation', 'Dental Post & Core', 'Dental Spa', 'Membership Consultation Perk',
            'Mouth Guard', 'Premium Bridge', 'Premium Crown', 'Prevention Seal',
            'Root Canal Treatment', 'Wear Protect'
        ],
        'Reynolds': [
            'Advanced Filling', 'Advanced Gum Treatment', 'Premium Bridge', 'Premium Crown'
        ],
        'Miranda': [
            'Basic Filling', 'Basic Scaling', 'Basic Tooth Extraction', 'Dental Spa', 'Mouth Guard'
        ],
        'Ashley': ['Prevention Seal'],
        'Meyden': []  # No specialties
    }

    # Sort specialties for each dentist to ensure consistent order
    for dentist in specialties:
        specialties[dentist] = sorted(specialties[dentist])

    return specialties

def generate_dummy_dentist(number_of_dentist):
    # Comprehensive set of all possible specialties
    all_specialties = get_treatment_list()

    # Dictionary to store the dummy dentists
    dummy_dentists = {}

    # Loop to generate each dummy dentist
    for i in range(1, number_of_dentist + 1):
        dentist_name = f'Dentist_{i}'
        # Assign a sorted copy of all specialties to ensure consistency
        dummy_dentists[dentist_name] = all_specialties.copy()

    return dummy_dentists


def preprocess_historical_treatment_pattern():

    data = pd.read_csv('Model_Input_Preprocess_v2.csv')
    data
    # transpose data and set first row as header 
    data_transposed = data.T
    data_transposed.columns = data_transposed.iloc[0]
    data_transposed = data_transposed[1:]
    data_transposed.head()

    interarrival_mean = (480 * len(data_transposed)) / data_transposed['total_treatment'].sum()
    interarrival_mean
    data_transposed.reset_index(inplace=True)
    data_transposed.rename(columns={'index': 'date'}, inplace=True)
    data_transposed
    treatment_columns = data_transposed.columns[1:-2]
    treatment_columns


    treatment_columns = data_transposed.columns[1:-2]
    total_demand_column = 'total_treatment'

    # set filtered_data second column until last to be float 
    data_transposed.iloc[:, 1:] = data_transposed.iloc[:, 1:].astype(float)

    # Initialize an empty DataFrame to store results
    # create new_df empty but with same column name as data_transposed 
    new_df = pd.DataFrame(columns=data_transposed.columns)


    # Function to simulate treatment distribution for any number of treatments
    def simulate_treatment_distribution(row, treatment_columns, total_demand_column):
        # Extract treatment probabilities and column names
        probabilities = row[treatment_columns].astype(float).values
        treatments = treatment_columns
        total_demand = int(row[total_demand_column])
        
        # Initialize a counter for selected treatments
        selected_treatments = {treatment: 0 for treatment in treatments}
        
        # Randomly select treatments based on probabilities until total demand is zero
        while total_demand > 0:
            selected_treatment = np.random.choice(treatments, p=probabilities)
            selected_treatments[selected_treatment] += 1
            total_demand -= 1

        # Return a series with the results
        return pd.Series([row['date']] + list(selected_treatments.values()), index=['date'] + list(selected_treatments.keys()))

    # Apply the function to each row in the original DataFrame
    new_df = data_transposed.apply(simulate_treatment_distribution, axis=1, treatment_columns=treatment_columns, total_demand_column=total_demand_column)
    
    
    return new_df


def retrieve_treatment_name():

    new_df = preprocess_historical_treatment_pattern()


    # Initialize a dictionary to store the results in the desired format
    results_dict = {}

    # Outer loop to go through each date
    for idx, row in new_df.iterrows():
        date = row['date']
        
        # Create an empty list to store selected treatments for this date
        selected_treatments_for_date = []
        
        # Select all the numeric columns (from second to last column)
        treatment_columns = new_df.columns[1:]
        
        # Inner loop: total number of iterations equals the sum of all treatment values in this row
        total_treatments = row[treatment_columns].sum()
        
        for _ in range(int(total_treatments)):
            # Get columns with non-zero values for weighted random selection
            available_treatments = row[treatment_columns][row[treatment_columns] > 0]
            
            # Treatment names (column headers) and their corresponding weights (values)
            treatments = available_treatments.index.values  # convert to numpy array
            weights = available_treatments.values.astype(float)  # ensure numeric dtype
            
            # Randomly select a treatment based on current weights
            selected_treatment = np.random.choice(treatments, p=weights/weights.sum())
            
            # Append the selected treatment to the list for this date
            selected_treatments_for_date.append(selected_treatment)
            
            # Decrease the value in the selected treatment column by 1
            new_df.at[idx, selected_treatment] -= 1
        
        # Store the list of selected treatments in the dictionary
        results_dict[date] = selected_treatments_for_date

    # Display the final result
    return results_dict

def get_treatment_duration(treatment_name):
    treatment_duration = pd.read_csv('treatment_duration.csv')


    # change column to type float
    treatment_duration['Duration'] = treatment_duration['Duration'].astype('float') 

    treatment_duration_dict = treatment_duration.set_index('Item Code')['Duration'].to_dict()
    
    duration = treatment_duration_dict[treatment_name]
    
    return duration
        



# test generate_dummy_dentist 
