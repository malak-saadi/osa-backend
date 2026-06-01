import requests
import numpy as np

BASE_URL = "http://localhost:8000/api/v1/predict/apnea/"


def generate_test_data(mode="normal"):
    if mode == "apnea":
        hrv_metrics = {
            'HRV_SampEn': 0.85,
            'HRV_RMSSD': 18.2,
            'HRV_SDNN': 65.4,
            'PPG_Rate_Mean': 78.0,
            'HR_mean': 76.5,
            'HR_std': 12.4,
            'HR_max': 105.0,
            'HR_min': 48.0
        }
        spo2_min = 0.82
    else:
        hrv_metrics = {
            'HRV_SampEn': 1.45,
            'HRV_RMSSD': 42.5,
            'HRV_SDNN': 35.2,
            'PPG_Rate_Mean': 65.0,
            'HR_mean': 65.5,
            'HR_std': 2.1,
            'HR_max': 72.0,
            'HR_min': 60.0
        }
        spo2_min = 0.97

    temps = np.linspace(0, 1, 88)
    amplitude = 0.98 - spo2_min
    signal = 0.98 - amplitude * np.exp(-((temps - 0.5) / 0.15) ** 2)
    noise = np.random.normal(0, 0.003, 88)
    signal_spo2 = (signal + noise).tolist()

    return hrv_metrics, signal_spo2


def test_apnea():
    print("\n🧪 Testing API with APNEA data...")
    hrv, spo2 = generate_test_data("apnea")
    response = requests.post(BASE_URL, json={"hrv_metrics": hrv, "signal_spo2": spo2})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")


def test_normal():
    print("\n🧪 Testing API with NORMAL data...")
    hrv, spo2 = generate_test_data("normal")
    response = requests.post(BASE_URL, json={"hrv_metrics": hrv, "signal_spo2": spo2})
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")


def test_bad_data():
    print("\n🧪 Testing API with BAD (invalid) data...")

    # Test missing feature
    print("\n  1. Missing feature:")
    bad_hrv = {
        'HRV_SampEn': 1.45,
        'HRV_RMSSD': 42.5,
        'HRV_SDNN': 35.2,
        'PPG_Rate_Mean': 65.0,
        'HR_mean': 65.5,
        'HR_std': 2.1,
        'HR_max': 72.0
    }
    bad_spo2 = [0.98]*88
    resp = requests.post(BASE_URL, json={"hrv_metrics": bad_hrv, "signal_spo2": bad_spo2})
    print(f"     Status: {resp.status_code}")
    print(f"     Error: {resp.json()}")

    # Test wrong length spo2
    print("\n  2. Wrong length SpO2:")
    bad_spo2_short = [0.98]*80
    resp = requests.post(BASE_URL, json={"hrv_metrics": bad_hrv | {'HR_min': 60.0}, "signal_spo2": bad_spo2_short})
    print(f"     Status: {resp.status_code}")
    print(f"     Error: {resp.json()}")


if __name__ == "__main__":
    test_normal()
    test_apnea()
    test_bad_data()
