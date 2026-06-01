
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from pathlib import Path

base_dir = Path(__file__).parent
models_dir = base_dir / "apnea_analysis" / "models"

print("⏳ Loading models...")
hrv_model = joblib.load(models_dir / "model_hrv.pkl")
print("✅ HRV model loaded!")
spo2_model = tf.keras.models.load_model(
    models_dir / "best_model2_prune50.keras",
    compile=False,
    safe_mode=False
)
print("✅ SpO2 model loaded!")


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
    signal_spo2 = (signal + noise)
    return hrv_metrics, signal_spo2


def predict_apnea(hrv_metrics, signal_spo2):
    ordre_strict = [
        'HRV_SampEn', 'HRV_RMSSD', 'HRV_SDNN',
        'PPG_Rate_Mean', 'HR_mean', 'HR_std',
        'HR_max', 'HR_min'
    ]
    df_hrv = pd.DataFrame([hrv_metrics])[ordre_strict]
    prob_hrv = float(hrv_model.predict_proba(df_hrv)[0][1])

    tensor_spo2 = tf.convert_to_tensor(
        signal_spo2.reshape(1, 88, 1),
        dtype=tf.float32
    )
    prob_spo2 = float(spo2_model(tensor_spo2, training=False).numpy()[0][1])

    prob_fusion = (prob_hrv * 0.8) + (prob_spo2 * 0.2)
    decision = "⚠️ APNÉE DÉTECTÉE" if prob_fusion >= 0.5 else "✅ RESPIRATION NORMALE"

    return {
        "prob_hrv": round(prob_hrv, 4),
        "prob_spo2": round(prob_spo2, 4),
        "prob_fusion": round(prob_fusion, 4),
        "decision": decision
    }


print("\n🧪 Testing normal case...")
hrv_norm, spo2_norm = generate_test_data("normal")
result_norm = predict_apnea(hrv_norm, spo2_norm)
print(result_norm)

print("\n🧪 Testing apnea case...")
hrv_apnea, spo2_apnea = generate_test_data("apnea")
result_apnea = predict_apnea(hrv_apnea, spo2_apnea)
print(result_apnea)

print("\n✅ All tests passed!")

