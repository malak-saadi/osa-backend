
import requests
import json

API_BASE = "http://127.0.0.1:8000"

# Données pour créer un compte test
register_data = {
    "username": "testuser2",
    "email": "test2@example.com",
    "password": "password1234",
    "confirm_password": "password1234",
    "telephone": "0612345679",
    "role": "patient"
}

print("🔑 Création du compte test...")
response = requests.post(f"{API_BASE}/api/auth/register/", json=register_data)
print(f"Code HTTP: {response.status_code}")
print(json.dumps(response.json(), indent=2))

print("\n🔓 Tentative de connexion...")
login_data = {
    "username": "testuser2",
    "password": "password1234"
}
login_response = requests.post(f"{API_BASE}/api/auth/login/", json=login_data)
print(f"Code HTTP: {login_response.status_code}")
print(json.dumps(login_response.json(), indent=2))
