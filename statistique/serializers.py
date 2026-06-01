from rest_framework import serializers
from .models import Device, SensorReading


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Device
        fields = ['id', 'device_id', 'patient_name', 'registered_at', 'is_active']


class SensorReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SensorReading
        fields = ['id', 'device', 'timestamp', 'ppg_value', 'spo2', 'heart_rate']
        read_only_fields = ['id', 'timestamp']


class SensorReadingIngestSerializer(serializers.Serializer):
    """
    Used by the bracelet to POST data.
    Bracelet only sends device_id as string — no FK needed.
    """
    device_id  = serializers.CharField(max_length=64)
    ppg_value  = serializers.FloatField()
    spo2       = serializers.FloatField(required=False, allow_null=True)
    heart_rate = serializers.FloatField(required=False, allow_null=True)

    def validate_spo2(self, value):
        if value is not None and not (0 <= value <= 100):
            raise serializers.ValidationError("SpO2 must be between 0 and 100.")
        return value

    def validate_heart_rate(self, value):
        if value is not None and not (20 <= value <= 300):
            raise serializers.ValidationError("Heart rate out of physiological range.")
        return value