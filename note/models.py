from django.db import models
from django.conf import settings


class Note(models.Model):
    """
    Clinical note model for doctors to document patient information.
    Only the doctor who created the note can edit/delete it.
    Other doctors can view notes on the same patient (read-only).
    """
    
    title = models.CharField(
        max_length=200,
        help_text="Title of the clinical note"
    )
    content = models.TextField(
        help_text="Detailed content of the clinical note"
    )
    patient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_notes',
        limit_choices_to={'role': 'patient'},
        help_text="Patient this note is about"
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_notes',
        limit_choices_to={'role': 'medecin'},
        help_text="Doctor who wrote this note"
    )
    tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated tags for organizing notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', '-created_at']),
            models.Index(fields=['doctor', '-created_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title} - {self.patient.username} by Dr. {self.doctor.username}"

    def get_tags_list(self):
        """Return tags as a list"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]

    def set_tags_list(self, tags_list):
        """Set tags from a list"""
        self.tags = ', '.join(tags_list) if tags_list else ''
