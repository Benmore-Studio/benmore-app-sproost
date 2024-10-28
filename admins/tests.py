from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from quotes.models import Project, QuoteRequest, QuoteRequestStatus
from profiles.models import ContractorProfile, AgentProfile, UserProfile
from django.urls import reverse


User = get_user_model()

class AdminDashboardAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            user_type='AD'  # Assuming 'AD' is the admin user_type
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create other users
        self.home_owner = User.objects.create_user(
            username='homeowner',
            email='homeowner@example.com',
            password='homeownerpass',
            user_type='HO'
        )
        self.agent = User.objects.create_user(
            username='agent',
            email='agent@example.com',
            password='agentpass',
            user_type='AG'
        )
        self.contractor = User.objects.create_user(
            username='contractor',
            email='contractor@example.com',
            password='contractorpass',
            user_type='CO'
        )

        self.quote_request = QuoteRequest.objects.create(
            user=self.admin_user,
            title='Sample Quote Request',
            summary='A summary of the quote request',
            contact_phone='1234567890',
            contact_username='John Doe',
            property_address='123 Main St'
        )

        self.project = Project.objects.create(
            admin=self.admin_user,
            quote_request=self.quote_request,
            is_approved=True
        )


    def test_admin_dashboard(self):
        url = reverse('admins:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Check if the counts are correct
        self.assertEqual(data['counts']['home_owner_count'], 1)
        self.assertEqual(data['counts']['agent_count'], 1)
        self.assertEqual(data['counts']['contractor_count'], 1)
        self.assertEqual(data['active_projects'], 1)

        # Check if recent users and projects are serialized correctly
        self.assertIn('recent_home_owners', data)
        self.assertIn('recent_agents', data)
        self.assertIn('recent_contractors', data)
        self.assertIn('recent_quote_requests', data)


class ContractorsListAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a contractor user
        self.contractor = User.objects.create_user(
            username='contractor',
            email='contractor@example.com',
            password='contractorpass',
            user_type='CO'
        )
        self.contractor_profile = ContractorProfile.objects.create(user=self.contractor)

        # Authenticate as an admin or any user with access
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            user_type='AD'  # Assuming 'AD' is the admin user_type
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_list_contractors(self):
        url = reverse('admins:contractors')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['email'], 'contractor@example.com')


class HomeOwnersAndAgentsListAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an admin user for authentication
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            user_type='AD'
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create homeowners
        self.homeowner1 = User.objects.create_user(
            username='homeowner1',
            email='homeowner1@example.com',
            password='homeownerpass',
            user_type='HO'
        )
        UserProfile.objects.create(user=self.homeowner1, city='City1', state_province='State1')

        self.homeowner2 = User.objects.create_user(
            username='homeowner2',
            email='homeowner2@example.com',
            password='homeownerpass',
            user_type='HO'
        )
        UserProfile.objects.create(user=self.homeowner2, city='City2', state_province='State2')

        # Create agents
        self.agent1 = User.objects.create_user(
            username='agent1',
            email='agent1@example.com',
            password='agentpass',
            user_type='AG'
        )
        AgentProfile.objects.create(user=self.agent1)

        self.agent2 = User.objects.create_user(
            username='agent2',
            email='agent2@example.com',
            password='agentpass',
            user_type='AG'
        )
        AgentProfile.objects.create(user=self.agent2)

    def test_list_homeowners(self):
        url = reverse('admins:homeowners')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # The response data is a list of homeowners
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['email'], 'homeowner2@example.com')  # Sorted by '-id'
        self.assertEqual(data[1]['email'], 'homeowner1@example.com')

    def test_list_agents(self):
        url = reverse('admins:agents')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # The response data is a list of agents
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['email'], 'agent2@example.com')  # Sorted by '-id'
        self.assertEqual(data[1]['email'], 'agent1@example.com')


class ProjectRequestListAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an admin user for authentication
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            user_type='AD'
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create quote requests
        self.quote_request1 = QuoteRequest.objects.create(
            user=self.admin_user,
            title='First Quote Request',
            summary='First summary',
            contact_phone='1234567890',
            contact_username='admin',
            property_address='123 Test St'
        )
        self.quote_request2 = QuoteRequest.objects.create(
            user=self.admin_user,
            title='Second Quote Request',
            summary='Second summary',
            contact_phone='0987654321',
            contact_username='admin',
            property_address='456 Test St'
        )

    def test_list_project_requests(self):
        url = reverse('admins:project-requests')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the length of the data directly
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['title'], 'Second Quote Request')  # Sorted by '-id'
        self.assertEqual(data[1]['title'], 'First Quote Request')


class ActiveProjectListAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create an admin user for authentication
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            user_type='AD'
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create quote requests and projects
        self.quote_request1 = QuoteRequest.objects.create(
            user=self.admin_user,
            title='Quote for Active Project 1',
            summary='First project summary',
            contact_phone='1234567890',
            contact_username='admin',
            property_address='123 Test St'
        )
        self.project1 = Project.objects.create(
            admin=self.admin_user,
            quote_request=self.quote_request1,
            is_approved=True
        )

        self.quote_request2 = QuoteRequest.objects.create(
            user=self.admin_user,
            title='Quote for Active Project 2',
            summary='Second project summary',
            contact_phone='0987654321',
            contact_username='admin',
            property_address='456 Test St'
        )
        self.project2 = Project.objects.create(
            admin=self.admin_user,
            quote_request=self.quote_request2,
            is_approved=True
        )

    def test_list_active_projects(self):
        url = reverse('admins:active-projects')
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the length of the data directly
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['quote_request'], self.quote_request2.id)  # Sorted by '-id'
        self.assertEqual(data[1]['quote_request'], self.quote_request1.id)


class ProjectRequestDetailAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user and authenticate
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass'
        )
        self.client.force_authenticate(user=self.user)

        # Create a quote request
        self.quote_request = QuoteRequest.objects.create(
            user=self.user,
            title='Test Project',
            summary='Test Summary',
            contact_phone='1234567890',
            contact_username='testuser',
            property_address='123 Test St',
            is_quote=True
        )

        # Create a project associated with the quote request
        self.project_request = Project.objects.create(
            admin=self.user,
            quote_request=self.quote_request,
            is_approved=True
        )

    def test_get_project_request_detail(self):
        # Use the correct URL for accessing the detail of a specific project request
        url = reverse('admins:project-requests', args=[self.project_request.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()

        # Update the test to check the actual structure of the response
        self.assertEqual(data['title'], 'Test Project')
        self.assertEqual(data['summary'], 'Test Summary')
        self.assertEqual(data['status'], 'Approved')
        self.assertEqual(data['contact_phone'], '1234567890')
        self.assertEqual(data['contact_username'], 'testuser')
        self.assertEqual(data['property_address'], '123 Test St')


class ChangeQuoteStatusAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a user and authenticate
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            user_type='AD'
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create a project and quote request
        self.quote_request = QuoteRequest.objects.create(
            user=self.admin_user,
            title='Test Quote Request',
            summary='Test summary',
            contact_phone='1234567890',
            contact_username='admin',
            property_address='123 Test St',
            status=QuoteRequestStatus.pending
        )

    def test_change_quote_status(self):
        # Use the correct status value from QuoteRequestStatus
        data = {'status': QuoteRequestStatus.approved}

        quote_id = self.quote_request.id
        url = reverse('admins:change-quote', kwargs={'pk': quote_id})
        response = self.client.put(url, data, format='json')
        response_data = response.json()

        # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify the status change
        self.quote_request.refresh_from_db()
        self.assertEqual(self.quote_request.status, QuoteRequestStatus.approved)


class UpdateUsersAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.contractor = User.objects.create_user(
            username='contractor',
            email='contractor@example.com',
            password='contractorpass',
            user_type='CO'
        )
        
        self.agent_user = User.objects.create_user(
            username='agent',
            email='agent@example.com',
            password='contractorpass',
            user_type='AG'
        )
        self.home_owner_user = User.objects.create_user(
            username='home_owner',
            email='home_owner@example.com',
            password='contractorpass',
            user_type='HO'
        )
        
        self.contractor_profile = ContractorProfile.objects.create(user=self.contractor)
        self.user_profile = UserProfile.objects.create(user=self.home_owner_user)
        self.agent_profile = AgentProfile.objects.create(user=self.agent_user)
        self.client.force_authenticate(user=self.contractor)
        self.client.force_authenticate(user=self.agent_user)
        self.client.force_authenticate(user=self.home_owner_user)

    def test_update_contractor_profile(self):
        contractor_id = self.contractor_profile.id

        # Flat data structure for the update request
        data = {
            'username': "username",
            'first_name': 'Updated Name',
            'last_name': 'Updated Last',
            'email': 'updated_email@example.com',
            'user_type': 'CO',
            'company_name': 'Updated Company',
            'registration_number': '75875767674546',  # Ensure the registration number is a string
            'city': 'city'
        }

        # Generate the URL for the update view
        url = reverse('admins:update-contractor', kwargs={'pk': contractor_id})
        response = self.client.patch(url, data, format='json')

        # Print response content for debugging
        print("Response data:", response.json())

        # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the contractor's data was updated in the database
        self.contractor.refresh_from_db()
        self.assertEqual(self.contractor.first_name, 'Updated Name')
        self.assertEqual(self.contractor.email, 'updated_email@example.com')
        self.assertEqual(self.contractor.contractor_profile.company_name, 'Updated Company')


    def test_update_agent_profile(self):
        contractor_id = self.agent_profile.id

        data = {
            'username': "username",
            'first_name': 'Updated Name',
            'last_name': 'Updated Last',
            'email': 'updated_email@example.com',
            'user_type': 'AG',
            'registration_ID': '75875767674546', 
            'address': 'er',
          
        }

        # Generate the URL for the update view
        url = reverse('admins:update-agent', kwargs={'pk': contractor_id})
        response = self.client.patch(url, data, format='json', partial=True)

        # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the contractor's data was updated in the database
        self.agent_user.refresh_from_db()
        self.assertEqual(self.agent_user.first_name, 'Updated Name')
        self.assertEqual(self.agent_user.email, 'updated_email@example.com')
        self.assertEqual(self.agent_user.agent_profile.registration_ID, '75875767674546')
        # self.assertEqual(self.user.agent_profile.address, 'er')

    
    def test_update_homeowners_profile(self):
        home_owner_id = self.user_profile.id

        data = {
            'username': "username",
            'first_name': 'Updated Name',
            'last_name': 'Updated Last',
            'email': 'updated_email@example.com',
            'user_type': 'HO',
            'address': 'Updated address',
            
        }

        # Generate the URL for the update view
        url = reverse('admins:update-home_owner', kwargs={'pk': home_owner_id})
        response = self.client.patch(url, data, format='json', partial=True)

        # Check that the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the contractor's data was updated in the database
        self.home_owner_user.refresh_from_db()
        self.assertEqual(self.home_owner_user.first_name, 'Updated Name')
        self.assertEqual(self.home_owner_user.email, 'updated_email@example.com')
        self.assertEqual(self.home_owner_user.user_profile.address, 'Updated address')



