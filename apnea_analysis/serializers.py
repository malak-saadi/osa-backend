from rest_framework import serializers


class ApneaPredictSerializer(serializers.Serializer):
    HRV_FEATURES = [
        'HRV_SampEn', 'HRV_RMSSD', 'HRV_SDNN',
        'PPG_Rate_Mean', 'HR_mean', 'HR_std',
        'HR_max', 'HR_min'
    ]

    hrv_metrics = serializers.DictField(
        child=serializers.FloatField(),
        required=True,
        help_text="Dictionary containing exactly 8 HRV metrics"
    )
    signal_spo2 = serializers.ListField(
        child=serializers.FloatField(),
        required=True,
        help_text="List of exactly 88 SpO2 values"
    )

    def validate_hrv_metrics(self, value):
        missing_features = [f for f in self.HRV_FEATURES if f not in value]
        extra_features = [f for f in value if f not in self.HRV_FEATURES]

        if missing_features:
            raise serializers.ValidationError(
                f"Missing required HRV features: {', '.join(missing_features)}"
            )
        if extra_features:
            raise serializers.ValidationError(
                f"Unexpected extra HRV features: {', '.join(extra_features)}"
            )
        return value

    def validate_signal_spo2(self, value):
        if len(value) != 88:
            raise serializers.ValidationError(
                f"signal_spo2 must contain exactly 88 elements, got {len(value)}"
            )
        return value
