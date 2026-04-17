import requests
import json

# Test with corrected data format
correct_patient = {
    "name": "JP Bhatia",
    "dob": "2004-06-15",  # Changed from "2004" to full date format
    "gender": "male",
    "contact": "9876543210",  # Changed from "null" to actual contact
    "address": "sector 19"
}

try:
    print("Testing patient addition with correct date format...")
    response = requests.post(
        "http://localhost:8000/api/patients/add",
        json=correct_patient,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    if response.status_code == 201:
        print("✅ Patient added successfully!")
        print(f"Response: {response.json()}")
    else:
        print("❌ Failed to add patient")
        print(f"Error: {response.json()}")
        
except requests.exceptions.ConnectionError:
    print("❌ Server is not running. Please start the server first:")
    print('cd "C:\\Users\\abhisheksood\\OneDrive - Nagarro\\Desktop\\heat\\backend"')
    print("uvicorn app.main:app --reload --port 8000")
except Exception as e:
    print(f"Error: {str(e)}")

print("\n" + "="*50)
print("IMPORTANT: Date of Birth Format")
print("="*50)
print("✅ Correct format: '2004-01-15' (YYYY-MM-DD)")
print("❌ Incorrect format: '2004' (just year)")
print("❌ Incorrect format: '15/01/2004' (DD/MM/YYYY)")
print("❌ Incorrect format: '01-15-2004' (MM-DD-YYYY)")
print("="*50)