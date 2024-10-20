from django.test import TestCase

from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from quotes.models import QuoteRequest, Project, QuoteRequestStatus
from main.models import Media
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


User = get_user_model()

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from quotes.models import QuoteRequest
from main.models import Media
from profiles.models import UserProfile, ContractorProfile, AgentProfile  # Make sure to import the correct profiles
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class QuotesAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users with different roles
        self.home_owner = User.objects.create_user(username='homeowner', email='homeowner@example.com', 
                                                   password='password', user_type='HO')
        self.agent = User.objects.create_user(username='agent', email='agent@example.com', password='password', user_type='AG')

        # Create profiles for each user
        self.home_owner_profile = UserProfile.objects.create(user=self.home_owner, address="123 Test Address")
        self.agent_profile = AgentProfile.objects.create(user=self.agent)

        # Authenticate as home owner
        self.client.force_authenticate(user=self.home_owner)

    def test_get_initial_data_homeowner(self):
        url = reverse('quotes:request-quotes')
        response = self.client.get(url) 
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        self.assertEqual(data['contact_username'], self.home_owner.username)

    def test_create_quote_request_success(self):
        # Create a simple file to simulate a media upload
        media_file = SimpleUploadedFile("file.txt", b"file_content", content_type="text/plain")

        # Data for creating a quote request
        quote_data = {
            'title': 'New Quote Request',
            'summary': 'This is a test quote request',
            'contact_phone': '1234567890',
            'contact_username': self.home_owner.username,
            'property_address': '123 Test Street',
            'media': [media_file]
        }

        url = reverse('quotes:request-quotes')
        response = self.client.post(url, quote_data, format='multipart')  
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify the response structure
        data = response.json()
        print(data)
        self.assertIn('message', data)

        # Check that the quote request was created in the database
        quote_request = QuoteRequest.objects.first()
        self.assertEqual(quote_request.title, 'New Quote Request')
        self.assertEqual(quote_request.user, self.home_owner)

        # Check if the associated media was created
        self.assertEqual(Media.objects.filter(object_id=quote_request.id).count(), 1)

    def test_create_quote_request_invalid_data(self):
        invalid_data = {
            'title': '',  # Title is required, so this should cause validation to fail
            'summary': 'Invalid summary',
            'contact_phone': '123',
            'contact_username': '',
            'property_address': 'Invalid Address'
        }

        url = reverse('quotes:request-quotes')
        response = self.client.post(url, invalid_data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify the response structure for errors
        data = response.json()
        print(data)
        self.assertIn('title', data)  # Check that 'title' is flagged in the errors


class ProjectViewSetTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user and a quote request
        self.admin_user = User.objects.create_user(username='admin', email='admin@example.com', password='password', user_type='CO')
        self.quote_request = QuoteRequest.objects.create(
            user=self.admin_user,
            title='Test Quote',
            summary='This is a test quote',
            contact_phone='1234567890',
            contact_username=self.admin_user.username,
            property_address='123 Test Street'
        )

        # Create a project linked to the quote request
        self.project = Project.objects.create(admin=self.admin_user, quote_request=self.quote_request, is_approved=True)

        # Authenticate as the admin user
        self.client.force_authenticate(user=self.admin_user)

    def test_get_project_list(self):
        url = reverse('quotes:project-list')  # Corrected from 'projects-list'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)  # Ensure we get one project in the list

    def test_create_project(self):
        new_quote = QuoteRequest.objects.create(
            user=self.admin_user,
            title='Another Quote',
            summary='This is another test quote',
            contact_phone='9876543210',
            contact_username=self.admin_user.username,
            property_address='456 Test Avenue'
        )

        # Create a project linked to the new quote
        project_data = {
            'admin': self.admin_user.id,
            'quote_request': new_quote.id,
            'is_approved': False
        }

        url = reverse('quotes:project-list')  # Corrected from 'projects-list'
        response = self.client.post(url, project_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the project was created in the database
        project = Project.objects.get(quote_request=new_quote)
        self.assertEqual(project.admin, self.admin_user)
        self.assertEqual(project.quote_request, new_quote)

    def test_update_project(self):
        # Update the existing project's approval status
        update_data = {'is_approved': True}

        url = reverse('quotes:project-detail', kwargs={'pk': self.project.id})  # Corrected from 'projects-detail'
        response = self.client.patch(url, update_data, format='json')
       
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the project was updated
        self.project.refresh_from_db()
        self.assertTrue(self.project.is_approved)

    def test_delete_project(self):
        url = reverse('quotes:project-detail', kwargs={'pk': self.project.id})  # Corrected from 'projects-detail'
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Verify that the project was deleted
        with self.assertRaises(Project.DoesNotExist):
            Project.objects.get(id=self.project.id)
