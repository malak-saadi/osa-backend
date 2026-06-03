
import requests
import json
import numpy as np

# Generate 88-point normal SpO2 signal
temps = np.linspace(0, 1, 88)
normal_signal = [0.97 + (np.random.random() - 0.5) * 0.02 for _ in range(88)]

# Test 1: Normal case
print("=== Test 1: Normal respiration ===")
normal_data = {
    "hrv_metrics": {
        "HRV_SampEn": 1.45,
        "HRV_RMSSD": 42.5,
        "HRV_SDNN": 35.2,
        "PPG_Rate_Mean": 65.0,
        "HR_mean": 65.5,
        "HR_std": 2.1,
        "HR_max": 72.0,
        "HR_min": 60.0
    },
    "signal_spo2": normal_signal
}

response = requests.post("http://127.0.0.1:8001/api/v1/predict/apnea/", json=normal_data)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
print()

# Generate 88-point apnea SpO2 signal
apnea_signal = [0.98 - 0.16 * np.exp(-((t - 0.5)/0.15)**2) + (np.random.random() - 0.5) * 0.006 for t in temps]

# Test 2: Apnea case
print("=== Test 2: Apnea detected ===")
apnea_data = {
    "hrv_metrics": {
        "HRV_SampEn": 0.85,
        "HRV_RMSSD": 18.2,
        "HRV_SDNN": 65.4,
        "PPG_Rate_Mean": 78.0,
        "HR_mean": 76.5,
        "HR_std": 12.4,
        "HR_max": 105.0,
        "HR_min": 48.0
    },
    "signal_spo2": apnea_signal
}

response = requests.post("http://127.0.0.1:8001/api/v1/predict/apnea/", json=apnea_data)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2, ensure_ascii=False))
