from django.contrib import admin
from .models import Note


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient_username', 'doctor_username', 'created_at', 'updated_at')
    list_filter = ('doctor', 'patient', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'patient__username', 'doctor__username', 'tags')
    readonly_fields = ('created_at', 'updated_at')
    fields = ('title', 'content', 'patient', 'doctor', 'tags', 'created_at', 'updated_at')
    ordering = ('-created_at',)

    def patient_username(self, obj):
        return obj.patient.username
    patient_username.short_description = 'Patient'

    def doctor_username(self, obj):
        return obj.doctor.username
    doctor_username.short_description = 'Doctor'

    def get_readonly_fields(self, request, obj=None):
        """Make patient and doctor read-only after creation"""
        if obj:  # Editing an existing note
            return self.readonly_fields + ['patient', 'doctor']
        return self.readonly_fields
