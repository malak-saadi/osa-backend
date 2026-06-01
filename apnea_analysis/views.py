import numpy as np
import pandas as pd
import tensorflow as tf
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.apps import apps
from .serializers import ApneaPredictSerializer


class PredictApneaView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ApneaPredictSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            apnea_app = apps.get_app_config('apnea_analysis')

            if not apnea_app.models_loaded:
                return Response(
                    {"error": "Models not loaded yet. Please try again later."},
                    status=status.HTTP_503_SERVICE_UNAVAILABLE
                )

            data = serializer.validated_data

            # Process HRV data
            hrv_metrics = data['hrv_metrics']
            ordre_strict = ApneaPredictSerializer.HRV_FEATURES
            df_hrv = pd.DataFrame([hrv_metrics])[ordre_strict]

            # Predict HRV probability
            prob_hrv = float(apnea_app.modele_hrv.predict_proba(df_hrv)[0][1])

            # Process SpO2 data
            signal_spo2 = np.array(data['signal_spo2'])
            tensor_spo2 = tf.convert_to_tensor(
                signal_spo2.reshape(1, 88, 1),
                dtype=tf.float32
            )

            # Predict SpO2 probability (direct inference)
            prob_spo2 = float(
                apnea_app.modele_spo2(tensor_spo2, training=False).numpy()[0][1]
            )

            # Compute fused probability
            poids_hrv, poids_spo2 = 0.8, 0.2
            prob_fusion = (prob_hrv * poids_hrv) + (prob_spo2 * poids_spo2)

            # Make decision
            decision = (
                "⚠️ APNÉE DÉTECTÉE"
                if prob_fusion >= 0.5
                else "✅ RESPIRATION NORMALE"
            )

            return Response({
                "prob_hrv": round(prob_hrv, 4),
                "prob_spo2": round(prob_spo2, 4),
                "prob_fusion": round(prob_fusion, 4),
                "decision": decision
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Inference error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
