import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import random

# List of all possible treatments
def get_treatment_list():
    treatments = [
        'Additional Root', 'Advanced Filling', 'Advanced Gum Treatment', 'Basic Filling', 
        'Basic Gum Treatment', 'Basic Scaling', 'Basic Tooth Extraction', 'Basic X-ray', 
        'Consultation', 'Dental Post & Core', 'Dental Spa', 'Membership Consultation Perk', 
        'Mouth Guard', 'Premium Bridge', 'Premium Crown', 'Prevention Seal', 
        'Root Canal Treatment', 'Wear Protect', 'Advanced Filling', 'Advanced Gum Treatment', 
        'Premium Bridge', 'Premium Crown', 'Basic Filling', 'Basic Scaling', 
        'Basic Tooth Extraction', 'Dental Spa', 'Mouth Guard', 'Prevention Seal'
    ]
    return treatments

# Dictionary representing specialties of each dentist
def get_specialties_matrix():
    specialties = {
        'Arnold': {
            'Additional Root', 'Advanced Filling', 'Advanced Gum Treatment', 'Basic Filling',
            'Basic Gum Treatment', 'Basic Scaling', 'Basic Tooth Extraction', 'Basic X-ray',
            'Consultation', 'Dental Post & Core', 'Dental Spa', 'Membership Consultation Perk',
            'Mouth Guard', 'Premium Bridge', 'Premium Crown', 'Prevention Seal',
            'Root Canal Treatment', 'Wear Protect'
        },
        'Ronald': {
            'Additional Root', 'Advanced Filling', 'Advanced Gum Treatment', 'Basic Filling',
            'Basic Gum Treatment', 'Basic Scaling', 'Basic Tooth Extraction', 'Basic X-ray',
            'Consultation', 'Dental Post & Core', 'Dental Spa', 'Membership Consultation Perk',
            'Mouth Guard', 'Premium Bridge', 'Premium Crown', 'Prevention Seal',
            'Root Canal Treatment', 'Wear Protect'
        },
        'Reynolds': {
            'Advanced Filling', 'Advanced Gum Treatment', 'Premium Bridge', 'Premium Crown'
        },
        'Miranda': {
            'Basic Filling', 'Basic Scaling', 'Basic Tooth Extraction', 'Dental Spa', 'Mouth Guard'
        },
        'Ashley': {'Prevention Seal'},
        'Meyden': set()  # No specialties
    }
    
    return specialties

# Function to get a random specialty from the combined specialties list
def get_random_specialty():
    all_specialties = get_treatment_list()  # Using the treatment list defined above
    return random.choice(all_specialties) if all_specialties else None

# Example usage
if __name__ == "__main__":
    specialties_matrix = get_specialties_matrix()
    print("Specialties Matrix:")
    print(specialties_matrix)

    random_specialty = get_random_specialty()
    print("\nRandomly Selected Specialty:")
    print(random_specialty)
