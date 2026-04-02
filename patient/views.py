from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.permissions import IsAdmin, IsAdminOrMedecin
from accounts.models import User
from .serializers import PatientSerializer


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsAdminOrMedecin]

    def get_queryset(self):
        queryset = User.objects.filter(role=User.Role.PATIENT).select_related("profile")

        search = self.request.query_params.get("search")
        ordering = self.request.query_params.get("ordering")

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(telephone__icontains=search)
                | Q(profile__address__icontains=search)
            )

        allowed_ordering = [
            "created_at",
            "-created_at",
            "username",
            "-username",
            "email",
            "-email",
        ]
        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)

        return queryset


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    queryset = User.objects.filter(role=User.Role.PATIENT).select_related("profile")

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated(), IsAdminOrMedecin()]