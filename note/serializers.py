from rest_framework import serializers
from .models import Note
from accounts.models import User


class DoctorBasicSerializer(serializers.ModelSerializer):
    """Minimal doctor info for nested serialization"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'telephone']
        read_only_fields = ['id', 'username', 'email', 'telephone']


class PatientBasicSerializer(serializers.ModelSerializer):
    """Minimal patient info for nested serialization"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'telephone']
        read_only_fields = ['id', 'username', 'email', 'telephone']


class NoteSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating notes.
    Doctor is automatically set to the current user.
    """
    doctor = serializers.StringRelatedField(read_only=True)
    tags_list = serializers.SerializerMethodField(write_only=False)

    class Meta:
        model = Note
        fields = [
            'id',
            'title',
            'content',
            'patient',
            'doctor',
            'tags',
            'tags_list',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'doctor', 'created_at', 'updated_at']

    def get_tags_list(self, obj):
        """Convert tags string to list"""
        return obj.get_tags_list()

    def validate_patient(self, value):
        """Ensure patient has role='patient'"""
        if value.role != 'patient':
            raise serializers.ValidationError("Selected user is not a patient.")
        return value

    def create(self, validated_data):
        """Set doctor to current user"""
        validated_data['doctor'] = self.context['request'].user
        return super().create(validated_data)


class NoteDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer with nested doctor and patient information.
    Used for retrieving single notes.
    """
    doctor = DoctorBasicSerializer(read_only=True)
    patient = PatientBasicSerializer(read_only=True)
    tags_list = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = [
            'id',
            'title',
            'content',
            'patient',
            'doctor',
            'tags',
            'tags_list',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'doctor', 'patient']

    def get_tags_list(self, obj):
        """Convert tags string to list"""
        return obj.get_tags_list()


class NoteSearchSerializer(serializers.ModelSerializer):
    """Serializer for search results with limited fields"""
    doctor_username = serializers.CharField(source='doctor.username', read_only=True)
    patient_username = serializers.CharField(source='patient.username', read_only=True)
    tags_list = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = [
            'id',
            'title',
            'content',
            'patient_username',
            'doctor_username',
            'tags',
            'tags_list',
            'created_at',
        ]
        read_only_fields = fields

    def get_tags_list(self, obj):
        """Convert tags string to list"""
        return obj.get_tags_list()
