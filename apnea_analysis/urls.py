from django.urls import path
from .views import PredictApneaView

urlpatterns = [
    path('predict/apnea/', PredictApneaView.as_view(), name='predict-apnea'),
]
