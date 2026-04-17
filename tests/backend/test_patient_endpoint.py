import requests
import json

# Test the patient addition endpoint
test_patient = {
    "name": "Dr. John Smith",
    "dob": "2004-01-15",  # Must be full date in YYYY-MM-DD format
    "gender": "Male",
    "contact": "+1-555-0123",
    "address": "123 Medical Center Drive, City, State 12345"
}

try:
    # Test POST endpoint to add patient
    print("Testing patient addition endpoint...")
    response = requests.post(
        "http://localhost:8000/api/patients/add",
        json=test_patient,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 201:
        print("✅ Patient added successfully!")
        patient_data = response.json()
        patient_id = patient_data.get("data", {}).get("id")
        
        if patient_id:
            print(f"\nTesting patient retrieval for ID: {patient_id}")
            # Test GET endpoint to retrieve the patient
            get_response = requests.get(f"http://localhost:8000/api/patients/{patient_id}")
            print(f"GET Status Code: {get_response.status_code}")
            print(f"GET Response: {get_response.json()}")
            
            # Test GET all patients endpoint
            print("\nTesting get all patients endpoint...")
            list_response = requests.get("http://localhost:8000/api/patients/")
            print(f"List Status Code: {list_response.status_code}")
            print(f"List Response: {list_response.json()}")
    else:
        print("❌ Failed to add patient")
        
except Exception as e:
    print(f"Error testing endpoints: {str(e)}")