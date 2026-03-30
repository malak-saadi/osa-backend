from rest_framework import serializers
from .models import SleepSession


class SleepSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model  = SleepSession
        fields = [
            'id', 'patient', 'date', 'start_time', 'end_time',
            'apnea_count', 'hypopnea_count', 'actual_sleep_hours',
            'duration_hours', 'ahi', 'efficiency', 'status', 'notes', 'created_at',
        ]
        # Ces champs sont calculés automatiquement par le backend, on ne les demande pas dans le POST
        read_only_fields = [
            'id', 'patient', 'duration_hours', 'ahi',
            'efficiency', 'status', 'created_at'
        ]
