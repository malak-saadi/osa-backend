from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet

# Create a router and register the NoteViewSet
router = DefaultRouter()
router.register(r'', NoteViewSet, basename='note')

urlpatterns = [
    path('', include(router.urls)),
]
