import pytest
from flask import Flask
from flask_app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_run_simulation(client):
    # Define the input data for the simulation
    data = {
        'num_dentists': 1,
        'num_desk_staff': 1,
        'num_seats': 3,
        'sim_time': 100,
        'num_replications': 10
    }
    
    # Send a POST request to the /run_simulation endpoint
    response = client.post('/run_simulation', json=data)
    
    # Assert that the request was successful
    assert response.status_code == 200
    
    # Parse the JSON response
    results = response.get_json()
    
    # Assert that the keys we expect are in the response
    assert 'avg_dentist_utilization' in results
    assert 'avg_desk_staff_utilization' in results
    assert 'avg_seater_utilization' in results
    
    # Optionally, assert that the values are within expected ranges
    assert 0 <= results['avg_dentist_utilization'] <= 1
    assert 0 <= results['avg_desk_staff_utilization'] <= 1
    assert 0 <= results['avg_seater_utilization'] <= 1

def test_set_distribution(client):
    # Define the distribution data to set
    new_distribution = "random.gauss(10, 2)"
    
    # Send a POST request to the /set_distribution endpoint
    response = client.post('/set_distribution', json={'interarrival_distribution': new_distribution})
    
    # Assert that the request was successful
    assert response.status_code == 200
    
    # Parse the JSON response
    result = response.get_json()
    
    # Assert that the response indicates success
    assert result['status'] == 'success'

def test_get_distribution(client):
    # Send a GET request to the /get_distribution endpoint
    response = client.get('/get_distribution')
    
    # Assert that the request was successful
    assert response.status_code == 200
    
    # Parse the JSON response
    data = response.get_json()
    
    # Assert that the returned distribution is correct
    assert 'interarrival_distribution' in data
    assert isinstance(data['interarrival_distribution'], str)

def test_set_and_get_distribution(client):
    # First, set a new distribution
    new_distribution = "random.gauss(10, 2)"
    response = client.post('/set_distribution', json={'interarrival_distribution': new_distribution})
    
    # Assert that the set request was successful
    assert response.status_code == 200
    
    # Now, get the distribution to check if it was set correctly
    response = client.get('/get_distribution')
    
    # Assert that the get request was successful
    assert response.status_code == 200
    
    # Parse the JSON response
    data = response.get_json()
    
    # Assert that the returned distribution matches what was set
    assert data['interarrival_distribution'] == new_distribution