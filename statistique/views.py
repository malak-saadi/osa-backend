from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.permissions import AllowAny
from .models import Device, SensorReading
from .serializers import (
    SensorReadingIngestSerializer,
    SensorReadingSerializer,
    DeviceSerializer,
)
from django.utils import timezone
from .models import SleepSession

class RegisterDeviceView(APIView):
    """
    POST /api/devices/register/
    Body: { "device_id": "BRACELET-001", "patient_name": "John Doe" }
    """
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = DeviceSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        device, created = Device.objects.get_or_create(
            device_id=serializer.validated_data['device_id'],
            defaults={'patient_name': serializer.validated_data.get('patient_name', '')}
        )
        return Response(
            DeviceSerializer(device).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class IngestReadingView(APIView):
    """
    POST /api/ingest/
    Called by the bracelet to push sensor data.

    Body:
    {
        "device_id":  "BRACELET-001",
        "ppg_value":  512.3,
        "spo2":       97.5,
        "heart_rate": 68.0
    }
    """
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = SensorReadingIngestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data

        # Auto-create device if it doesn't exist yet
        device, _ = Device.objects.get_or_create(device_id=data['device_id'])
        current_session = SleepSession.objects.filter(
          device=device, ended_at=None
        ).first()
        reading = SensorReading.objects.create(
            device     = device,
            session    = current_session,
            ppg_value  = data['ppg_value'],
            spo2       = data.get('spo2'),
            heart_rate = data.get('heart_rate'),
        )

        # Push to WebSocket → dashboard updates instantly
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"sensor_{device.device_id}",
            {
                'type'      : 'sensor_update',
                'ppg_value' : reading.ppg_value,
                'spo2'      : reading.spo2,
                'heart_rate': reading.heart_rate,
                'timestamp' : reading.timestamp.isoformat(),
            }
        )

        return Response({'status': 'ok', 'id': reading.id}, status=status.HTTP_201_CREATED)


class LatestReadingsView(APIView):
    """
    GET /api/readings/<device_id>/latest/?limit=100
    Returns last N readings — used on page load to prefill the charts.
    """
    permission_classes = [AllowAny]
    def get(self, request, device_id):
        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        limit    = int(request.query_params.get('limit', 100))
        readings = SensorReading.objects.filter(device=device).order_by('timestamp')[:limit]
        serializer = SensorReadingSerializer(readings, many=True)
        return Response(serializer.data)
    


class StartSessionView(APIView):
    """
    POST /api/statistique/sessions/start/
    Called when bracelet connects — creates a new session.
    Body: { "device_id": "BRACELET-001" }
    """
    permission_classes = [AllowAny]

    def post(self, request):
        device_id = request.data.get('device_id')
        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        # Close any open session for this device first
        SleepSession.objects.filter(device=device, ended_at=None).update(
            ended_at=timezone.now()
        )

        session = SleepSession.objects.create(device=device)
        return Response({'session_id': session.id}, status=status.HTTP_201_CREATED)


class EndSessionView(APIView):
    """
    POST /api/statistique/sessions/<session_id>/end/
    Called when bracelet disconnects — closes session + computes stats.
    """
    permission_classes = [AllowAny]

    def post(self, request, session_id):
        try:
            session = SleepSession.objects.get(id=session_id)
        except SleepSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        readings = SensorReading.objects.filter(session=session)
        count    = readings.count()

        if count > 0:
            spo2_vals = list(readings.filter(spo2__isnull=False).values_list('spo2', flat=True))
            ppg_vals  = list(readings.values_list('ppg_value', flat=True))
            hr_vals   = list(readings.filter(heart_rate__isnull=False).values_list('heart_rate', flat=True))

            # Compute AHI: count SpO2 drops below 90% per hour
            duration_hours = max((timezone.now() - session.started_at).seconds / 3600, 0.01)
            apnea_events   = sum(1 for v in spo2_vals if v < 90)
            ahi            = round(apnea_events / duration_hours, 2)

            session.avg_spo2       = round(sum(spo2_vals) / len(spo2_vals), 2) if spo2_vals else None
            session.avg_ppg        = round(sum(ppg_vals)  / len(ppg_vals),  2) if ppg_vals  else None
            session.avg_hr         = round(sum(hr_vals)   / len(hr_vals),   2) if hr_vals   else None
            session.min_spo2       = round(min(spo2_vals), 2)                  if spo2_vals else None
            session.total_readings = count
            session.ahi_score      = ahi
            session.apnea_detected = ahi >= 5  # Medical threshold
        
        session.ended_at = timezone.now()
        session.save()

        return Response({
            'session_id'    : session.id,
            'duration_min'  : session.duration_minutes,
            'avg_spo2'      : session.avg_spo2,
            'avg_ppg'       : session.avg_ppg,
            'ahi_score'     : session.ahi_score,
            'apnea_detected': session.apnea_detected,
        })


class SessionListView(APIView):
    """
    GET /api/statistique/sessions/<device_id>/
    Returns all sessions for a device — used in Sleep History page.
    """
    permission_classes = [AllowAny]

    def get(self, request, device_id):
        try:
            device = Device.objects.get(device_id=device_id)
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)

        sessions = SleepSession.objects.filter(device=device)
        data = []
        for s in sessions:
            data.append({
                'id'            : s.id,
                'started_at'    : s.started_at,
                'ended_at'      : s.ended_at,
                'duration_min'  : s.duration_minutes,
                'avg_spo2'      : s.avg_spo2,
                'avg_ppg'       : s.avg_ppg,
                'avg_hr'        : s.avg_hr,
                'min_spo2'      : s.min_spo2,
                'total_readings': s.total_readings,
                'ahi_score'     : s.ahi_score,
                'apnea_detected': s.apnea_detected,
            })
        return Response(data)


class SessionDetailView(APIView):
    """
    GET /api/statistique/sessions/detail/<session_id>/
    Returns all readings for one session — used to draw the curve.
    """
    permission_classes = [AllowAny]

    def get(self, request, session_id):
        try:
            session = SleepSession.objects.get(id=session_id)
        except SleepSession.DoesNotExist:
            return Response({'error': 'Session not found'}, status=status.HTTP_404_NOT_FOUND)

        readings = SensorReading.objects.filter(session=session).order_by('timestamp')
        data = [{
            'timestamp' : r.timestamp,
            'ppg_value' : r.ppg_value,
            'spo2'      : r.spo2,
            'heart_rate': r.heart_rate,
        } for r in readings]

        return Response({
            'session': {
                'id'        : session.id,
                'started_at': session.started_at,
                'ended_at'  : session.ended_at,
                'avg_spo2'  : session.avg_spo2,
                'avg_ppg'   : session.avg_ppg,
                'ahi_score' : session.ahi_score,
                'apnea_detected': session.apnea_detected,
            },
            'readings': data
        })