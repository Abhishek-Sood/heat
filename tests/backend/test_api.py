import requests

BASE_URL = "http://localhost:8000"

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_patient_summary_not_found():
    r = requests.get(f"{BASE_URL}/patient-summary/9999")
    assert r.status_code == 404
