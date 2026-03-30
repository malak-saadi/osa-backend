from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.auth import get_user_model

from .models import SleepSession
from .serializers import SleepSessionSerializer

User = get_user_model()


class SleepSessionListCreateView(generics.ListCreateAPIView):
    """
    GET /api/patient/sessions/ — Liste les sessions du patient connecté
    POST /api/patient/sessions/ — Ajoute une nouvelle session pour le patient connecté
    """
    serializer_class = SleepSessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'medecin' or user.role == 'admin':
            # Optionnel: si c'est un médecin, on pourrait lire "patient_id" dans l'URL (?patient_id=X)
            patient_id = self.request.query_params.get('patient_id')
            if patient_id:
                return SleepSession.objects.filter(patient_id=patient_id)
            return SleepSession.objects.all()

        # Par défaut (si c'est un patient), il ne voit que ses propres sessions
        return SleepSession.objects.filter(patient=user)

    def perform_create(self, serializer):
        user = self.request.user

        # Si c'est un médecin/admin, il doit préciser l'ID du patient dans le Body JSON
        if user.role in ['medecin', 'admin']:
            patient_id = self.request.data.get('patient')
            if not patient_id:
                raise serializers.ValidationError({"patient": "Veuillez spécifier l'ID du patient."})
            patient = get_object_or_404(User, pk=patient_id, role='patient')
            serializer.save(patient=patient)
        else:
            # Si c'est un patient, on force la session sur son compte
            serializer.save(patient=user)
