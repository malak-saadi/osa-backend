
import requests
import json

try:
    print("Calling IoT API...")
    response = requests.get("https://utah-spectacular-incentives-openings.trycloudflare.com/sensor-data", timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Text (first 2000 chars): {response.text[:2000]}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nData keys:", list(data.keys()))
        
        if "hrv_metrics" in data:
            print("\nHRV metrics keys:", list(data["hrv_metrics"].keys()))
            print("HRV metrics values:", data["hrv_metrics"])
            
        if "signal_spo2" in data:
            print(f"\nSpO2 signal length: {len(data['signal_spo2'])}")
            if len(data["signal_spo2"]) > 0:
                print(f"First 5 SpO2 values: {data['signal_spo2'][:5]}")
                
except Exception as e:
    print(f"Error calling IoT API: {type(e).__name__}: {e}")
