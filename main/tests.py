from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from property.models import AssignedAccount
from profiles.models import AgentProfile, UserProfile, ContractorProfile
from quotes.models import Project, QuoteRequest

from rest_framework.test import APITestCase, APIClient
from rest_framework import status

User = get_user_model()
from rest_framework.test import APIClient, APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from profiles.models import ContractorProfile, AgentProfile
from quotes.models import QuoteRequest, Project
from property.models import AssignedAccount

User = get_user_model()

class HomeViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.home_url = reverse('main:home')

        # Create users for different user types
        self.home_owner = User.objects.create_user(
            username='homeowner', email='homeowner@example.com', password='testpass', user_type='HO'
        )
        self.contractor = User.objects.create_user(
            username='contractor', email='contractor@example.com', password='testpass', user_type='CO'
        )
        self.agent = User.objects.create_user(
            username='agent', email='agent@example.com', password='testpass', user_type='AG'
        )

        # Create related profiles
        ContractorProfile.objects.create(user=self.contractor)
        AgentProfile.objects.create(user=self.agent)

    def test_home_owner_view(self):
        self.client.force_authenticate(user=self.home_owner)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('quote_count', response.data)

    def test_contractor_view(self):
        self.client.force_authenticate(user=self.contractor)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('company_name', response.data['contractor_profile'])

    def test_agent_view(self):
        self.client.force_authenticate(user=self.agent)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('quotes', response.data)

    def test_redirect_for_unknown_user_type(self):
        unknown_user = User.objects.create_user(
            username='unknown', email='unknown@example.com', password='testpass', user_type='IV'
        )
        self.client.force_authenticate(user=unknown_user)
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)  # Check for redirection


class HomeViewByPkAPIViewTest(APITestCase):

    def setUp(self):
        self.client = APIClient()

        # Create users for different user types
        self.home_owner = User.objects.create_user(
            username='homeowner', email='homeowner@example.com', password='testpass', user_type='HO'
        )
        self.contractor = User.objects.create_user(
            username='contractor', email='contractor@example.com', password='testpass', user_type='CO'
        )
        self.agent = User.objects.create_user(
            username='agent', email='agent@example.com', password='testpass', user_type='AG'
        )

        # Create related profiles
        self.contractor_profile = ContractorProfile.objects.create(user=self.contractor)
        self.agent_profile = AgentProfile.objects.create(user=self.agent)
        self.user_profile = UserProfile.objects.create(user=self.home_owner)

        self.contractor_url = reverse('main:homeview-bypk', kwargs={'pk': self.contractor_profile.pk})
        self.agent_url = reverse('main:homeview-bypk', kwargs={'pk': self.agent_profile.pk})
        self.homeowner_url = reverse('main:homeview-bypk', kwargs={'pk': self.user_profile.pk})

    def test_get_contractor_profile(self):
        self.client.force_authenticate(user=self.contractor)
        response = self.client.get(self.contractor_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('company_name', response.data['contractor_profile'])

    def test_get_agent_profile(self):
        self.client.force_authenticate(user=self.agent)
        response = self.client.get(self.agent_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('registration_ID', response.data['agent_profile'])

    def test_get_homeowner_profile(self):
        self.client.force_authenticate(user=self.home_owner)
        response = self.client.get(self.homeowner_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('address', response.data['user_profile'])



class AssignAgentViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()  # Use APIClient for DRF views
        self.assign_agent_url = reverse('main:assign-agent')

        # Create unique users for each role
        self.home_owner = User.objects.create_user(
            username='homeowner', 
            password='12345', 
            user_type='HO', 
            email='homeowner@example.com'  # Provide unique email
        )
        self.agent = User.objects.create_user(
            username='agent', 
            password='12345', 
            user_type='AG', 
            email='agent@example.com'  # Provide unique email
        )
        self.agent_profile = AgentProfile.objects.create(
            user=self.agent, 
            registration_ID='12345FF', 
            address="123 Street"
        )

        # Authenticate the user (homeowner) before each test
        self.client.force_authenticate(user=self.home_owner)

    def test_get(self):
        """Test that GET requests are not allowed (Method Not Allowed)"""
        response = self.client.get(self.assign_agent_url)
        data = response.json()
        print(data)
        self.assertEqual(response.status_code, 405)  # Expecting 405 Method Not Allowed


    def test_post_with_valid_agent(self):
        """Test POST with a valid agent registration_ID"""
        agent_data = {
            'registration_ID': '12345FF'  # Correct field name
        }
        response = self.client.post(self.assign_agent_url, agent_data)
        data = response.json()
        print(data)
        self.assertEqual(response.status_code, 201)  # Expecting 201 Created
        self.assertTrue(AssignedAccount.objects.filter(assigned_to=self.agent, assigned_by=self.home_owner).exists())

    def test_post_with_invalid_agent(self):
        """Test POST with an invalid agent registration_ID"""
        agent_data = {
            'registration_ID': '2323232323'  # Invalid agent ID
        }
        response = self.client.post(self.assign_agent_url, agent_data)
        data = response.json()
        self.assertEqual(response.status_code, 404)  # Expecting 404 Not Found
        self.assertFalse(AssignedAccount.objects.filter(assigned_by=self.home_owner).exists())

# class AssignedProjectsViewTest(APITestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.assigned_projects_url = reverse('main:assigned-projects')

#         # Create a home owner user and related data
#         self.home_owner_user = User.objects.create_user(
#             username='homeowner', email='homeowner@example.com', password='testpass', user_type='HO'
#         )
#         self.client.force_authenticate(user=self.home_owner_user)

#         # Create an agent user (required for assigned_to)
#         self.agent_user = User.objects.create_user(
#             username='agent', email='agent@example.com', password='testpass', user_type='AG'
#         )

#         # Create quotes, projects, and accounts
#         self.quote = QuoteRequest.objects.create(user=self.home_owner_user, title="Test Quote")
#         self.project = Project.objects.create(admin=self.home_owner_user, quote_request=self.quote)
        
#         # Assign the account to the agent user instead of the homeowner user
#         self.account = AssignedAccount.objects.create(assigned_by=self.home_owner_user, assigned_to=self.agent_user)

#     def test_assigned_projects_data(self):
#         response = self.client.get(self.assigned_projects_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('quote_count', response.data)
#         self.assertIn('projects_count', response.data)
#         self.assertIn('accounts_len', response.data)

