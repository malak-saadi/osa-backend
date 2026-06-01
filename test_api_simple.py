import requests
import json
import numpy as np

url = "http://127.0.0.1:8000/api/v1/predict/apnea/"

# Function to generate realistic test signals
def generate_signal(min_val=0.97, duration=88):
    t = np.linspace(0, 1, duration)
    signal = 0.98 - (0.98 - min_val) * np.exp(-((t - 0.5)/0.15)**2)
    return signal.tolist()

# Test normal case
print("🔍 Testing normal case...")
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
    "signal_spo2": generate_signal(min_val=0.97)
}

response = requests.post(url, json=normal_data)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# Test apnea case
print("\n🔍 Testing apnea case...")
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
    "signal_spo2": generate_signal(min_val=0.82)
}

response = requests.post(url, json=apnea_data)
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))
