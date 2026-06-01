import requests
import math
import random
import time

API_URL   = 'http://127.0.0.1:8000/api/statistique/ingest/'
DEVICE_ID = 'BRACELET-001'

print(f"[Simulator] Sending data to {API_URL}")
print("[Simulator] Press Ctrl+C to stop\n")

t = 0
while True:
    # ── PPG: realistic sine wave + noise ──────────────────
    ppg = 512 + 200 * math.sin(2 * math.pi * t / 20) + random.gauss(0, 10)

    # ── SpO2: normally 97-99%, occasional dip ─────────────
    spo2 = 97.5 + random.gauss(0, 0.5)
    if random.random() < 0.03:       # 3% chance — simulates apnea event
        spo2 -= random.uniform(4, 8)
    spo2 = max(85.0, min(100.0, spo2))

    # ── Heart Rate: ~68-72 BPM ────────────────────────────
    heart_rate = 70 + random.gauss(0, 2)

    payload = {
        'device_id' : DEVICE_ID,
        'ppg_value' : round(ppg, 2),
        'spo2'      : round(spo2, 2),
        'heart_rate': round(heart_rate, 1),
    }

    try:
        r = requests.post(API_URL, json=payload, timeout=2)
        print(f"  PPG={payload['ppg_value']:7.2f}  |  SpO2={payload['spo2']:.1f}%  |  HR={payload['heart_rate']} bpm  -> {r.status_code}")
    except requests.ConnectionError:
        print("  [!] Cannot connect — is Daphne running?")

    t += 1
    time.sleep(0.5)    # 2 readings per second