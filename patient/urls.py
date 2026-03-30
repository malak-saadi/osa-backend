from django.urls import path
from .views import SleepSessionListCreateView

urlpatterns = [
    path('sessions/', SleepSessionListCreateView.as_view(), nam='sleep-session-list'),
]
