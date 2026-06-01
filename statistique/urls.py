from django.urls import path
from .views import (
    IngestReadingView, LatestReadingsView, RegisterDeviceView,
    StartSessionView, EndSessionView, SessionListView, SessionDetailView
)

urlpatterns = [
    path('ingest/',                          IngestReadingView.as_view(),   name='ingest'),
    path('readings/<str:device_id>/latest/', LatestReadingsView.as_view(),  name='latest-readings'),
    path('devices/register/',                RegisterDeviceView.as_view(),  name='register-device'),
    # Sessions
    path('sessions/start/',                       StartSessionView.as_view(),  name='session-start'),
    path('sessions/<int:session_id>/end/',         EndSessionView.as_view(),    name='session-end'),
    path('sessions/<str:device_id>/',             SessionListView.as_view(),   name='session-list'),
    path('sessions/detail/<int:session_id>/',     SessionDetailView.as_view(), name='session-detail'),
]