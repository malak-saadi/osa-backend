from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Note

User = get_user_model()


class NoteModelTestCase(TestCase):
    """Test cases for the Note model"""

    def setUp(self):
        """Set up test data"""
        self.doctor = User.objects.create_user(
            username='doctor1',
            email='doctor@example.com',
            password='testpass123',
            role='medecin'
        )
        self.patient = User.objects.create_user(
            username='patient1',
            email='patient@example.com',
            password='testpass123',
            role='patient'
        )
        self.note = Note.objects.create(
            title='Test Note',
            content='This is a test note',
            patient=self.patient,
            doctor=self.doctor,
            tags='test, clinical'
        )

    def test_note_creation(self):
        """Test that a note can be created"""
        self.assertEqual(self.note.title, 'Test Note')
        self.assertEqual(self.note.patient, self.patient)
        self.assertEqual(self.note.doctor, self.doctor)

    def test_note_tags_list(self):
        """Test getting tags as a list"""
        tags = self.note.get_tags_list()
        self.assertEqual(len(tags), 2)
        self.assertIn('test', tags)
        self.assertIn('clinical', tags)

    def test_note_string_representation(self):
        """Test the string representation of a note"""
        expected = f"Test Note - patient1 by Dr. doctor1"
        self.assertEqual(str(self.note), expected)


class NoteAPITestCase(TestCase):
    """Test cases for Note API endpoints"""

    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create doctors
        self.doctor1 = User.objects.create_user(
            username='doctor1',
            email='doctor1@example.com',
            password='testpass123',
            role='medecin'
        )
        self.doctor2 = User.objects.create_user(
            username='doctor2',
            email='doctor2@example.com',
            password='testpass123',
            role='medecin'
        )
        
        # Create patients
        self.patient1 = User.objects.create_user(
            username='patient1',
            email='patient1@example.com',
            password='testpass123',
            role='patient'
        )
        self.patient2 = User.objects.create_user(
            username='patient2',
            email='patient2@example.com',
            password='testpass123',
            role='patient'
        )
        
        # Create test notes
        self.note1 = Note.objects.create(
            title='Diabetes Check',
            content='Patient shows symptoms of diabetes',
            patient=self.patient1,
            doctor=self.doctor1,
            tags='diabetes, urgent'
        )
        self.note2 = Note.objects.create(
            title='Heart Condition',
            content='Patient has elevated blood pressure',
            patient=self.patient1,
            doctor=self.doctor2,
            tags='cardiology'
        )

    def test_create_note_as_doctor(self):
        """Test that a doctor can create a note"""
        self.client.force_authenticate(user=self.doctor1)
        data = {
            'title': 'New Note',
            'content': 'New note content',
            'patient': self.patient2.id,
            'tags': 'test'
        }
        response = self.client.post('/api/notes/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Note.objects.count(), 3)

    def test_create_note_as_patient_fails(self):
        """Test that a patient cannot create a note"""
        self.client.force_authenticate(user=self.patient1)
        data = {
            'title': 'New Note',
            'content': 'New note content',
            'patient': self.patient2.id,
            'tags': 'test'
        }
        response = self.client.post('/api/notes/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_doctor_can_edit_own_note(self):
        """Test that a doctor can edit their own note"""
        self.client.force_authenticate(user=self.doctor1)
        data = {'title': 'Updated Title'}
        response = self.client.patch(f'/api/notes/{self.note1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.note1.refresh_from_db()
        self.assertEqual(self.note1.title, 'Updated Title')

    def test_doctor_cannot_edit_others_note(self):
        """Test that a doctor cannot edit another doctor's note"""
        self.client.force_authenticate(user=self.doctor2)
        data = {'title': 'Hacked Title'}
        response = self.client.patch(f'/api/notes/{self.note1.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_search_notes_by_keyword(self):
        """Test searching notes by keyword"""
        self.client.force_authenticate(user=self.doctor1)
        response = self.client.get('/api/notes/search/?q=diabetes')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Diabetes Check')
        self.assertIn('content', response.data[0])

    def test_get_notes_by_patient(self):
        """Test getting all notes for a specific patient"""
        self.client.force_authenticate(user=self.doctor1)
        response = self.client.get(f'/api/notes/by_patient/{self.patient1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should see both doctor1's and doctor2's notes on patient1
        self.assertEqual(len(response.data), 2)

    def test_get_notes_by_doctor(self):
        """Test getting all notes for a specific doctor"""
        self.client.force_authenticate(user=self.doctor1)
        response = self.client.get(f'/api/notes/by_doctor/{self.doctor1.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Diabetes Check')

    def test_list_notes_with_optional_filters(self):
        """Test filtering the main notes list with optional query params"""
        self.client.force_authenticate(user=self.doctor1)

        response = self.client.get('/api/notes/?q=heart')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Heart Condition')

        response = self.client.get(f'/api/notes/?patient_id={self.patient1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        response = self.client.get(f'/api/notes/?doctor_id={self.doctor1.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        response = self.client.get('/api/notes/?tags=cardiology')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'Heart Condition')

        response = self.client.get('/api/notes/?tags=diabetes,cardiology')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
