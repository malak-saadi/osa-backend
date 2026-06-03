
import requests
import json

# Call the IoT API
print("=== Checking real IoT sensor data ===")
try:
    response = requests.get("https://utah-spectacular-incentives-openings.trycloudflare.com/sensor-data")
    print(f"Response status: {response.status_code}")
    print(f"Response text:\n{response.text[:2000]}")
except Exception as e:
    print(f"Error: {e}")
