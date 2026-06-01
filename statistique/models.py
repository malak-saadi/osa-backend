from django.db import models


class Device(models.Model):
    """Represents a physical bracelet"""
    device_id    = models.CharField(max_length=64, unique=True)
    patient_name = models.CharField(max_length=128, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    is_active    = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.device_id} — {self.patient_name}"


class SensorReading(models.Model):
    """One reading sent by the bracelet"""
    device     = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    timestamp  = models.DateTimeField(auto_now_add=True)

    # Raw PPG signal value (from IR/Red LED sensor)
    ppg_value  = models.FloatField(help_text="Raw PPG amplitude")

    # SpO2 percentage derived from PPG red/IR ratio
    spo2       = models.FloatField(help_text="SpO2 in %", null=True, blank=True)

    # Heart rate derived from PPG peak detection
    heart_rate = models.FloatField(help_text="BPM", null=True, blank=True)
    session = models.ForeignKey(
    'SleepSession', 
    on_delete=models.SET_NULL, 
    null=True, blank=True, 
    related_name='readings'
      )
    class Meta:
        ordering = ['-timestamp']
        indexes  = [models.Index(fields=['device', 'timestamp'])]

    def __str__(self):
        return f"[{self.timestamp}] PPG={self.ppg_value} SpO2={self.spo2}% HR={self.heart_rate}bpm"
    


class SleepSession(models.Model):
    """
    Represents one sleep session (each time patient wears the bracelet).
    Created automatically when bracelet connects, closed when it disconnects.
    """
    device      = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='sessions')
    started_at  = models.DateTimeField(auto_now_add=True)
    ended_at    = models.DateTimeField(null=True, blank=True)
    
    # Computed stats (filled when session ends)
    avg_spo2    = models.FloatField(null=True, blank=True)
    avg_ppg     = models.FloatField(null=True, blank=True)
    avg_hr      = models.FloatField(null=True, blank=True)
    min_spo2    = models.FloatField(null=True, blank=True)
    total_readings = models.IntegerField(default=0)
    
    # Apnea detection result
    apnea_detected = models.BooleanField(null=True, blank=True)
    ahi_score      = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"Session {self.id} — {self.device.device_id} — {self.started_at.date()}"

    @property
    def duration_minutes(self):
        if self.ended_at:
            return round((self.ended_at - self.started_at).seconds / 60, 1)
        return None    

