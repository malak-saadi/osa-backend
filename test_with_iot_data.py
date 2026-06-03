
import requests
import json

# 1. Get real IoT data
print("Fetching real IoT data...")
iot_response = requests.get("https://utah-spectacular-incentives-openings.trycloudflare.com/sensor-data", timeout=10)
iot_data = iot_response.json()
print("✓ Got IoT data!")

# 2. Process data like our dashboard does
hrv = iot_data["hrv_metrics"]
signal_spo2 = iot_data["signal_spo2"]
# Take LAST 88 elements and convert from % to 0-1
processed_spo2 = [x / 100.0 for x in signal_spo2[-88:]]

print("\nHRV metrics:", hrv)
print(f"\nProcessed SpO2 signal (length {len(processed_spo2)}):", processed_spo2[:5], "...", processed_spo2[-5:])

# 3. Call our prediction API
payload = {
    "hrv_metrics": hrv,
    "signal_spo2": processed_spo2
}

print("\nCalling our prediction API...")
prediction_response = requests.post("http://127.0.0.1:8001/api/v1/predict/apnea/", json=payload)
print(f"Status: {prediction_response.status_code}")
print(f"Response: {json.dumps(prediction_response.json(), indent=2, ensure_ascii=False)}")
