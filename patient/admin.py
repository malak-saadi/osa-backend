from django.contrib import admin
from .models import SleepSession

@admin.register(SleepSession)
class SleepSessionAdmin(admin.ModelAdmin):
    list_display  = ['patient', 'date', 'start_time', 'end_time', 'duration_hours', 'efficiency', 'ahi', 'status']
    list_filter   = ['status', 'date']
    search_fields = ['patient__username']
