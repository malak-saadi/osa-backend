from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404

from .models import Note
from .serializers import NoteSerializer, NoteDetailSerializer, NoteSearchSerializer
from .permissions import IsNoteOwner, CanCreateNote
from accounts.permissions import IsMedecin


class NoteViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing clinical notes.
    
    Doctors can:
    - Create notes for patients
    - View all notes (their own and others' on shared patients)
    - Edit/Delete only their own notes
    - Search notes by keyword
    - Add/modify tags
    
    Patients can:
    - View notes about themselves
    """
    
    permission_classes = [IsAuthenticated, IsNoteOwner]
    queryset = Note.objects.all()

    def apply_query_filters(self, queryset):
        """Apply optional list/search filters from query parameters."""
        query = self.request.query_params.get('q', '').strip()
        tags = self.request.query_params.get('tags', '').strip()
        patient_id = self.request.query_params.get('patient_id')
        doctor_id = self.request.query_params.get('doctor_id')

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(content__icontains=query)
                | Q(tags__icontains=query)
            )

        if tags:
            tag_terms = [tag.strip() for tag in tags.split(',') if tag.strip()]
            if tag_terms:
                tag_query = Q()
                for tag in tag_terms:
                    tag_query |= Q(tags__icontains=tag)
                queryset = queryset.filter(tag_query)

        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)

        if doctor_id:
            queryset = queryset.filter(doctor_id=doctor_id)

        return queryset

    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'retrieve':
            return NoteDetailSerializer
        elif self.action == 'search':
            return NoteSearchSerializer
        return NoteSerializer

    def get_queryset(self):
        """
        Filter notes based on user role and query parameters.
        Doctors see their own notes and notes from other doctors on shared patients.
        Patients see notes about themselves only.
        """
        user = self.request.user
        
        if user.role == 'medecin':
            # Doctors see their own notes
            queryset = Note.objects.filter(doctor=user)
            
            # Also see other doctors' notes on their mutual patients
            # Get all patients this doctor has notes for
            patient_ids = Note.objects.filter(doctor=user).values_list('patient_id', flat=True)
            # Get notes from other doctors on these same patients
            other_doctors_notes = Note.objects.filter(patient_id__in=patient_ids)
            
            # Combine both querysets
            queryset = (queryset | other_doctors_notes).distinct()
        
        elif user.role == 'patient':
            # Patients only see notes about themselves
            queryset = Note.objects.filter(patient=user)
        
        else:  # admin
            # Admins see all notes
            queryset = Note.objects.all()

        return queryset.select_related('doctor', 'patient')

    def list(self, request, *args, **kwargs):
        """List notes with optional query-param filtering."""
        queryset = self.apply_query_filters(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        """
        Override permissions based on action.
        Only doctors can create notes.
        Only note owners can edit/delete.
        """
        if self.action == 'create':
            return [IsAuthenticated(), IsMedecin()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsNoteOwner()]
        return [IsAuthenticated()]

    @action(detail=False, methods=['get'])
    def search(self, request):
        """Backward-compatible search endpoint using the same optional filters as the main list."""
        queryset = self.apply_query_filters(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by_patient/(?P<patient_id>[^/.]+)')
    def by_patient(self, request, patient_id=None):
        """
        Get all notes for a specific patient.
        Only accessible if user is the patient, the patient's doctor, or admin.
        
        Path parameter:
        - patient_id: patient user id
        """
        from accounts.models import User
        
        patient = get_object_or_404(User, pk=patient_id, role='patient')
        
        # Check permissions: can only view if you're the patient or their doctor or admin
        if request.user.role == 'patient' and request.user != patient:
            return Response(
                {'error': 'You can only view notes about yourself'},
                status=status.HTTP_403_FORBIDDEN
            )

        notes = self.get_queryset().filter(patient=patient)
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='by_doctor/(?P<doctor_id>[^/.]+)')
    def by_doctor(self, request, doctor_id=None):
        """
        Get all notes written by a specific doctor.
        Only accessible if you're the doctor or admin.
        
        Path parameter:
        - doctor_id: doctor user id
        """
        from accounts.models import User
        
        doctor = get_object_or_404(User, pk=doctor_id, role='medecin')
        
        # Check permissions: can only view if you're the doctor or admin
        if request.user.role == 'medecin' and request.user != doctor:
            return Response(
                {'error': 'You can only view your own notes'},
                status=status.HTTP_403_FORBIDDEN
            )

        notes = self.get_queryset().filter(doctor=doctor)
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def add_tags(self, request, pk=None):
        """
        Add tags to a note (comma-separated).
        Only the note owner (doctor) can add tags.
        
        Request body:
        {
            "tags": "tag1, tag2, tag3"
        }
        """
        note = self.get_object()
        
        # Check if user is the note owner
        if note.doctor != request.user:
            return Response(
                {'error': 'Only the note owner can modify tags'},
                status=status.HTTP_403_FORBIDDEN
            )

        new_tags = request.data.get('tags', '').strip()
        
        if not new_tags:
            return Response(
                {'error': 'Tags field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Merge existing tags with new ones
        existing_tags = note.get_tags_list()
        new_tags_list = [tag.strip() for tag in new_tags.split(',')]
        
        # Combine and remove duplicates
        all_tags = list(set(existing_tags + new_tags_list))
        note.set_tags_list(all_tags)
        note.save()

        serializer = self.get_serializer(note)
        return Response({
            'message': 'Tags added successfully',
            'note': serializer.data
        })

    @action(detail=True, methods=['patch'])
    def remove_tags(self, request, pk=None):
        """
        Remove specific tags from a note.
        Only the note owner (doctor) can remove tags.
        
        Request body:
        {
            "tags": "tag1, tag2"
        }
        """
        note = self.get_object()
        
        # Check if user is the note owner
        if note.doctor != request.user:
            return Response(
                {'error': 'Only the note owner can modify tags'},
                status=status.HTTP_403_FORBIDDEN
            )

        tags_to_remove = request.data.get('tags', '').strip()
        
        if not tags_to_remove:
            return Response(
                {'error': 'Tags field is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Parse tags to remove
        tags_to_remove_list = [tag.strip() for tag in tags_to_remove.split(',')]
        
        # Remove specified tags
        existing_tags = note.get_tags_list()
        filtered_tags = [tag for tag in existing_tags if tag not in tags_to_remove_list]
        
        note.set_tags_list(filtered_tags)
        note.save()

        serializer = self.get_serializer(note)
        return Response({
            'message': 'Tags removed successfully',
            'note': serializer.data
        })

    @action(detail=False, methods=['get'])
    def my_notes(self, request):
        """
        Get all notes created by the current doctor.
        Only available for doctors.
        """
        if request.user.role != 'medecin':
            return Response(
                {'error': 'Only doctors can use this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        notes = Note.objects.filter(doctor=request.user).select_related('doctor', 'patient')
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def patient_notes(self, request):
        """
        Get all notes about the current logged-in patient.
        Only available for patients.
        """
        if request.user.role != 'patient':
            return Response(
                {'error': 'Only patients can use this endpoint'},
                status=status.HTTP_403_FORBIDDEN
            )

        notes = Note.objects.filter(patient=request.user).select_related('doctor', 'patient')
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)
