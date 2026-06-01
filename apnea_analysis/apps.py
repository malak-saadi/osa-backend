import os
import joblib
import tensorflow as tf
import warnings
from django.apps import AppConfig
from pathlib import Path
import json
import zipfile


class ApneaAnalysisConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apnea_analysis'

    # Global variables to hold loaded models (loaded once at startup)
    modele_hrv = None
    modele_spo2 = None
    models_loaded = False

    def ready(self):
        if not self.models_loaded:
            self._load_models()

    def _strip_quantization_config(self, config):
        """Recursively remove quantization_config from config to avoid loading errors"""
        if isinstance(config, dict):
            # Make a copy to avoid modifying original
            new_config = {}
            for k, v in config.items():
                if k == 'quantization_config':
                    continue  # Skip this key entirely
                new_config[k] = self._strip_quantization_config(v)
            return new_config
        elif isinstance(config, list):
            return [self._strip_quantization_config(item) for item in config]
        return config

    def _custom_deserialize_layer(self, layer_config):
        """Custom layer deserializer that strips quantization_config"""
        layer_config = self._strip_quantization_config(layer_config)
        return tf.keras.layers.deserialize(layer_config)

    def _load_models(self):
        try:
            base_dir = Path(__file__).resolve().parent
            models_dir = base_dir / 'models'

            hrv_model_path = models_dir / 'model_hrv.pkl'
            spo2_model_path = models_dir / 'best_model2_prune50.keras'

            warnings.filterwarnings("ignore")
            tf.get_logger().setLevel('ERROR')

            print("⏳ Loading HRV model (Scikit-Learn)...")
            self.modele_hrv = joblib.load(hrv_model_path)

            print("⏳ Loading SpO2 model (Keras)...")

            # Extract .keras file to modify config
            temp_dir = base_dir / 'temp_model'
            temp_dir.mkdir(exist_ok=True)

            with zipfile.ZipFile(spo2_model_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Modify config.json to strip quantization_config
            config_path = temp_dir / 'config.json'
            with open(config_path, 'r', encoding='utf-8') as f:
                model_config = json.load(f)
            model_config = self._strip_quantization_config(model_config)

            # Write modified config back
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(model_config, f)

            # Re-zip the modified model
            modified_model_path = temp_dir / 'modified_model.keras'
            with zipfile.ZipFile(modified_model_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        if file != 'modified_model.keras':
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)

            # Load the modified model
            self.modele_spo2 = tf.keras.models.load_model(
                modified_model_path,
                compile=False,
                safe_mode=False
            )

            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)

            self.models_loaded = True
            print("✅ All models loaded successfully!")

        except Exception as e:
            print(f"❌ Error loading models: {e}")
            import traceback
            traceback.print_exc()
            raise
