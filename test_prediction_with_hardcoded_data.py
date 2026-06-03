
import requests
import json

# Hardcoded data from last successful IoT call
iot_data = {
    "sensor_data": [{"spo2": 100.0, "heart_rate": 78, "gsr": 697, "ppg": 885}],
    "hrv_metrics": {
        "HRV_SampEn": 1.424,
        "HRV_RMSSD": 130.15,
        "HRV_SDNN": 176.89,
        "PPG_Rate_Mean": 9147.89,
        "HR_mean": 72.66,
        "HR_std": 19.17,
        "HR_max": 166,
        "HR_min": 44
    },
    "signal_spo2": [100.0, 98.0, 98.0, 100.0, 99.0, 99.0, 97.0, 99.0, 99.0, 99.0,
                    99.0, 98.0, 100.0, 97.0, 99.0, 100.0, 100.0, 100.0, 99.0, 99.0,
                    100.0, 100.0, 100.0, 97.0, 97.0, 99.0, 99.0, 98.0, 99.0, 99.0,
                    100.0, 99.0, 99.0, 100.0, 100.0, 97.0, 98.0, 98.0, 99.0, 98.0,
                    99.0, 100.0, 97.0, 97.0, 100.0, 98.0, 97.0, 98.0, 97.0, 99.0,
                    98.0, 99.0, 98.0, 100.0, 100.0, 99.0, 99.0, 99.0, 100.0, 98.0,
                    98.0, 100.0, 99.0, 98.0, 98.0, 99.0, 97.0, 98.0, 99.0, 97.0,
                    99.0, 100.0, 100.0, 98.0, 100.0, 97.0, 100.0, 97.0, 97.0, 99.0,
                    97.0, 98.0, 99.0, 99.0, 100.0, 100.0, 98.0, 98.0, 97.0, 99.0,
                    100.0, 99.0]  # 88 elements exactly for this test
}

# Process data
hrv = iot_data["hrv_metrics"]
signal_spo2 = iot_data["signal_spo2"]
# Take LAST 88 elements and convert from % to 0-1
processed_spo2 = [x / 100.0 for x in signal_spo2[-88:]]
print(f"HRV metrics keys: {list(hrv.keys())}")
print(f"Processed SpO2 length: {len(processed_spo2)}")
print(f"Processed SpO2 first 3: {processed_spo2[:3]}, last 3: {processed_spo2[-3:]}")

# Call prediction API
payload = {
    "hrv_metrics": hrv,
    "signal_spo2": processed_spo2
}

print("\nCalling prediction API...")
response = requests.post("http://127.0.0.1:8001/api/v1/predict/apnea/", json=payload)
print(f"Response status code: {response.status_code}")
if response.status_code == 200:
    print(f"Prediction result: {json.dumps(response.json(), indent=2)}")
else:
    print(f"Error: {response.text}")
