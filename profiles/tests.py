# Create your tests here.
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import UserProfile, ContractorProfile
from .forms import HomeOwnersEditForm

User= get_user_model()

class UserEditTestCase(TestCase):
    def setUp(self):
        # Create a User instance
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword123')

        self.client.force_login(self.user)  # Authenticate the user for the test

        # Create a userProfile instance for the user
        self.user_profile= UserProfile.objects.create(
            user=self.user,
            address='Test Company Address',
            city='Test City',
        )
        # Create a ContractorProfile instance for the user
        self.contractor_profile = ContractorProfile.objects.create(
            user=self.user,
            company_name='Test Company',
            specialization='Test Specialization',
            company_address='Test Company Address',
            city='Test City',
        )


    def test_edit_userprofile_success(self):
        # Make a POST request to the edit profile view with updated data
        valid_data = {
            'email' : 'test@gmail.com',
            'phone_number_0' : "NG" , # for the phone field
            'phone_number_1' : "7058985430",
            'address': '456 Avenue',
            'city': 'Test City',
            'state_province': 'Test State',
        }
        response = self.client.post(reverse('profile:edit-homeowners-profile-request'), valid_data)

        # Checking if the response is a redirect 
        self.assertEqual(response.status_code, 302)

        # Check if the redirect location matches the expected URL
        self.assertEqual(response.url, '/')

        # Refreshing the database
        self.user.refresh_from_db()

        # Checking if the user profile fields have been updated correctly
        self.assertEqual(self.user.user_profile.address, '456 Avenue')
        self.assertEqual(self.user.user_profile.city, 'Test City')
        self.assertEqual(self.user.user_profile.state_province, 'Test State')

    # checking for validation
    def test_edit_profile_validation(self):
        # Making a POST request to the edit profile view with invalid data
        response = self.client.post(reverse('profile:edit-homeowners-profile-request'), {
        })

        # Checking ifresponse is 200, which means the form was returned 
        print("validation", response)
        self.assertEqual(response.status_code, 200)

    # checking authentication of the edit page
    def test_edit_profile_authentication(self):
        self.client.logout()
        # Making a GET request to the edit profile view
        response = self.client.get(reverse('profile:edit-profile'))
        # Checking that the response is a redirect (unauthenticated users are redirected)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/profiles/edit-profile/')

    # contractor section
    def test_edit_contractorprofile_success(self):
        # Make a POST request to the edit profile view with updated data
        valid_data = {
            'email' : 'test@gmail.com',
            'phone_number_0' : "NG" , # for the phone field
            'phone_number_1' : "7058985430",
            'company_name': 'Avenue',
            'registration_number': '1',
            'company_address': '456 Avenue',
            'city': 'Test City',
            'specialization':'coding',
        }
        response = self.client.post(reverse('profile:contractor-edit-profile-request'), valid_data)
        print("edit", response)

        # Checking if the response is a redirect 
        self.assertEqual(response.status_code, 302)

        # Check if the redirect location matches the expected URL
        self.assertEqual(response.url, '/profiles/')

        # Refreshing the database
        self.user.refresh_from_db()

        print(self.user.user_profile.address)
        print('self.user_profile')

        # Checking if the user profile fields have been updated correctly
        self.assertEqual(self.user.contractor_profile.city, 'Test City')
        self.assertEqual(self.user.contractor_profile.specialization, 'coding')

    # checking for validation
    def test_edit_contractorprofile_validation(self):
        # Making a POST request to the edit profile view with invalid data
        response = self.client.post(reverse('profile:contractor-edit-profile-request'), {
        })

        # Checking ifresponse is 200, which means the form was returned 
        print("validation", response)
        self.assertEqual(response.status_code, 200)

    # checking authentication of the edit page
    def test_edit_contractorprofile_authentication(self):
        self.client.logout()
        # Making a GET request to the edit profile view
        response = self.client.get(reverse('profile:edit-profile'))
        # Checking that the response is a redirect (unauthenticated users are redirected)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/profiles/edit-profile/')


class SearchTestCase(TestCase):
    def setUp(self):
        # Create test users and profiles
        self.user_co = User.objects.create_user(username='emmanuel', email='emmanuel@g.com', password='123pass?%@', user_type='CO')
        
        # Create ContractorProfile instances
        self.profile_co_1 = ContractorProfile.objects.create(user=self.user_co, company_name='Company',company_address ='enugu', specialization='Specialization', city='City 1')
        self.client.force_login(self.user_co) 
    # search section
    def test_search_results(self):
        # Search for a term that matches multiple fields
        query = 'City 1'
        response = self.client.get(f'{reverse("profile:search_contractor")}?query={query}')
        self.assertEqual(response.status_code, 200)
        print("search1", response)
        # to ensure my seach functionality is beaving as expectd
        self.assertNotContains(response, 'Company')
        self.assertNotContains(response, 'enugu')

    # def test_empty_query(self):
    #     # Search with an empty query
    #     response = self.client.get(reverse("profile:search_contractor"))
    #     print("search2", response)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, 'No results found.')

    def test_search_fields(self):
        # Search for a term that matches specific fields
        query = 'ho@example.com'
        response = self.client.get(f'{reverse("profile:search_contractor")}?query={query}')
        print("search3", response)
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Company 1')
        self.assertNotContains(response, 'Company 2')
