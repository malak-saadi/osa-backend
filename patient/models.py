from django.db import models
from django.conf import settings

class SleepSession(models.Model):

    class Status(models.TextChoices):
        NORMAL   = 'normal',   'Normal'
        WARNING  = 'warning',  'Warning'
        CRITICAL = 'critical', 'Critical'

    patient       = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sleep_sessions',
        limit_choices_to={'role': 'patient'},
    )
    date          = models.DateField()
    start_time    = models.DateTimeField()
    end_time      = models.DateTimeField()

    # Données brutes (fournies par le capteur ou l'utilisateur)
    apnea_count        = models.IntegerField(default=0, help_text="Nombre d'apnées")
    hypopnea_count     = models.IntegerField(default=0, help_text="Nombre d'hypopnées")
    actual_sleep_hours = models.FloatField(blank=True, null=True, help_text="Heures de sommeil réel")
    notes              = models.TextField(blank=True)

    # Champs calculés automatiquement
    duration_hours = models.FloatField(blank=True, null=True, help_text="Temps total au lit (heures)")
    ahi            = models.FloatField(blank=True, null=True, help_text="Index Apnée-Hypopnée")
    efficiency     = models.FloatField(blank=True, null=True, help_text="Efficacité du sommeil (%)")
    status         = models.CharField(max_length=10, choices=Status.choices, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-start_time']

    def save(self, *args, **kwargs):
        # 1. Calcul de la durée totale au lit
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_hours = round(delta.total_seconds() / 3600, 2)

            # 2. Calcul de l'efficacité (si actual_sleep_hours est fourni)
            if self.actual_sleep_hours:
                # plafonné à 100% au cas où
                eff = (self.actual_sleep_hours / self.duration_hours) * 100
                self.efficiency = round(min(eff, 100.0), 2)
            else:
                self.efficiency = 100.0 # Par défaut 100% si on ne connaît pas le temps d'éveil

            # 3. Calcul de l'AHI = (Apnées + Hypopnées) / Heures de sommeil (ou durée totale)
            sleep_time_for_ahi = self.actual_sleep_hours if self.actual_sleep_hours else self.duration_hours
            if sleep_time_for_ahi > 0:
                self.ahi = round((self.apnea_count + self.hypopnea_count) / sleep_time_for_ahi, 2)
            else:
                self.ahi = 0.0

            # 4. Calcul du Statut basé sur l'AHI
            if self.ahi < 5:
                self.status = self.Status.NORMAL
            elif 5 <= self.ahi < 15:
                self.status = self.Status.WARNING
            else:
                self.status = self.Status.CRITICAL

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Session {self.patient.username} — {self.date} ({self.status})"
