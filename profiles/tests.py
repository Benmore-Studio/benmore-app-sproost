from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from profiles.models import UserProfile, ContractorProfile, AgentProfile
from quotes.models import QuoteRequest, Project
from django.urls import reverse

import os
from django.conf import settings

User = get_user_model()

class HomeOwnerWithSlugNameViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a home owner and their profile
        self.home_owner = User.objects.create_user(username='homeowner', email='homeowner@example.com', password='password', user_type='HO', slug='homeowner-slug')
        UserProfile.objects.create(user=self.home_owner, city="City", state_province="State")

        # Create a QuoteRequest (which contains the title)
        self.quote = QuoteRequest.objects.create(user=self.home_owner, title='Test Quote')

        # Create a project linked to the QuoteRequest
        self.project = Project.objects.create(admin=self.home_owner, quote_request=self.quote)

        # Authenticate the client as the home_owner
        self.client.force_authenticate(user=self.home_owner)


    def test_homeowner_slug_view_success(self):
        # Accessing the view using the slug
        url = reverse('main:homeview-bypk', kwargs={'pk': self.home_owner.id})
        response = self.client.get(url) 

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        print('ddd', data)
        
        # Ensure the quotes and projects data is returned
        self.assertEqual(data['quote_count'], 1)
        self.assertEqual(data['projects_count'], 1)
        self.assertEqual(data['home_owner_slug'], 'homeowner-slug')

    def test_homeowner_slug_view_not_found(self):
        response = self.client.get('/api/homeowners/invalid-slug/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ContractorProfileAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a contractor user
        self.contractor = User.objects.create_user(
            username='contractor', email='contractor@example.com', password='password', user_type='CO'
        )
        ContractorProfile.objects.create(user=self.contractor, company_name='Test Company', city='Test City')

        # Create a home owner for unauthorized test
        self.home_owner = User.objects.create_user(
            username='homeowner', email='homeowner@example.com', password='password', user_type='HO'
        )

    def test_contractor_profile_view_success(self):
        self.client.force_authenticate(user=self.contractor)
        url = reverse('main:home')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['contractor_profile']['company_name'], 'Test Company')
        self.assertEqual(data['contractor_profile']['city'], 'Test City')

    def test_contractor_profile_view_unauthorized(self):
        # self.client.force_authenticate(user=self.home_owner)
        url = reverse('main:home')
        response = self.client.get(url)

        # Since the user is unauthorized, expect a 401 UNAUTHORIZED status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('You are not authorized. Please provide valid credentials.', response.json()['error'])


class EditUsersProfileAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a contractor user and profile
        self.contractor = User.objects.create_user(username='contractor', email='contractor@example.com', password='password', user_type='CO')
        self.contractor_profile = ContractorProfile.objects.create(user=self.contractor, company_name='Test Company', city='Test City')

        # Authenticate the user
        self.client.force_authenticate(user=self.contractor)

    def test_edit_contractor_profile_success(self):
        valid_data = {
            'company_name': 'Updated Company',
            'city': 'Updated City'
        }
        url = reverse('profile:edit-users-profile')
        response = self.client.patch(url, valid_data, format='json') 

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Profile updated successfully!', response.json()['message'])

        # Verify that the profile was updated
        self.contractor_profile.refresh_from_db()
        self.assertEqual(self.contractor_profile.company_name, 'Updated Company')
        self.assertEqual(self.contractor_profile.city, 'Updated City')

    def test_edit_profile_invalid_data(self):
        invalid_data = {'company_name': ''}
        url = reverse('profile:edit-users-profile')
        response = self.client.patch(url, invalid_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('This field may not be blank.', response.json()['company_name'])


class ContractorSearchAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a contractor user and profile
        self.contractor1 = User.objects.create_user(username='contractor1', email='contractor1@example.com', password='password', user_type='CO')
        self.contractor_profile1 = ContractorProfile.objects.create(user=self.contractor1, company_name='Company One', specialization='Specialization One', city='City One')

        self.contractor2 = User.objects.create_user(username='contractor2', email='contractor2@example.com', password='password', user_type='CO')
        self.contractor_profile2 = ContractorProfile.objects.create(user=self.contractor2, company_name='Company Two', specialization='Specialization Two', city='City Two')

        # Authenticate the user
        self.client.force_authenticate(user=self.contractor1)

    def test_search_contractor_success(self):
        query = 'Company One'
        url = reverse('profile:search_contractor') + f'?query={query}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)  # Check the length of the list directly
        self.assertEqual(data[0]['company_name'], 'Company One')

    def test_search_no_results(self):
        query = 'Non-existing Company'
        url = reverse('profile:search_contractor') + f'?query={query}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 0)  # Check if the list is empty


class ChangeProfilePictureAPIViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a contractor user and profile
        self.contractor = User.objects.create_user(username='contractor', email='contractor@example.com', password='password', user_type='CO')
        self.contractor_profile = ContractorProfile.objects.create(user=self.contractor)

        # Authenticate the user
        self.client.force_authenticate(user=self.contractor)

    def test_change_profile_picture_success(self):
        image_path = os.path.join(settings.BASE_DIR, 'static/images/agent.png')
        with open(image_path, 'rb') as img:
            data = {'image': img}
            url = reverse('profile:change-dp-request')
            response = self.client.post(url, data, format='multipart')

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn('Profile picture changed successfully!', response.json()['message'])

    def test_change_profile_picture_no_file(self):
        url = reverse('profile:change-dp-request')
        response = self.client.post(url, {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Please select an image', response.json()['error'])


