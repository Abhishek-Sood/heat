import requests
import json
import time

# Wait a bit to ensure server is ready
time.sleep(2)

# Test data
test_patient = {
    "name": "Dr. Emily Watson",
    "dob": "1988-07-12",
    "gender": "Female", 
    "contact": "+1-555-0234",
    "address": "789 Healthcare Blvd"
}

try:
    print("Testing patient addition endpoint...")
    response = requests.post(
        "http://localhost:8000/api/patients/add",
        json=test_patient,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print("✅ Patient added successfully!")
        print(f"Response: {response.json()}")
    else:
        print("❌ Failed to add patient")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError as e:
    print(f"Connection error: {str(e)}")
except Exception as e:
    print(f"Error: {str(e)}")