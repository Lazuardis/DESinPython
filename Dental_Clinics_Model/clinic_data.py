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


# test generate_dummy_dentist 
