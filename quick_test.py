
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")
import django
django.setup()
print("✅ Django setup complete!")

from apnea_analysis.apps import ApneaAnalysisConfig
app = ApneaAnalysisConfig("apnea_analysis", None)
print("✅ App config initialized!")

from apnea_analysis.serializers import ApneaPredictSerializer
print("✅ Serializer imported!")

from apnea_analysis.views import PredictApneaView
print("✅ View imported!")

print("\n✅ All imports successful!")

print("\nNow loading models manually (to test)...")

import joblib
import tensorflow as tf
from pathlib import Path

base_dir = Path(__file__).parent
models_dir = base_dir / "apnea_analysis" / "models"

hrv_model = joblib.load(models_dir / "model_hrv.pkl")
print("✅ Loaded HRV model!")
print(type(hrv_model))

spo2_model = tf.keras.models.load_model(
    models_dir / "best_model2_prune50.keras",
    compile=False,
    safe_mode=False
)
print("✅ Loaded SpO2 model!")
print(type(spo2_model))

print("\n✅ All components working!")
