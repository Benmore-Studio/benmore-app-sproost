# from rest_framework.test import APITestCase, APIClient
# from django.urls import reverse
# from django.contrib.auth import get_user_model
# from rest_framework.authtoken.models import Token
# from .models import AssignedAccount

# class AgentsHomeOwnerAccountViewTest(APITestCase):
#     def setUp(self):
#         self.client = APIClient()  # Use APIClient instead of Client

#         # Create users with unique emails
#         self.home_owner = get_user_model().objects.create_user(
#             username='homeowner', 
#             password='7386peters', 
#             user_type='HO',
#             email='homeowner@example.com'
#         )

#         self.agent = get_user_model().objects.create_user(
#             username='agent', 
#             password='7386peters', 
#             user_type='AG',
#             email='agent@example.com'
#         )

#         # Create assigned account
#         self.assigned_account = AssignedAccount.objects.create(assigned_by=self.home_owner, assigned_to=self.agent)

#         # Create tokens for the users
#         self.home_owner_token = Token.objects.create(user=self.home_owner)
#         self.agent_token = Token.objects.create(user=self.agent)

#         # URL for the agent-homeowner dashboard
#         self.agents_home_owner_account_url = reverse('property:agent-homeowner-dashboard', kwargs={'pk': self.home_owner.pk})

#     def test_get_with_assigned_agent(self):
#         # Log in as the agent (using token authentication)
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.agent_token.key))

#         # Make the GET request
#         response = self.client.get(self.agents_home_owner_account_url)
#         print(f"Response Status Code: {response.status_code}, Response Data: {response.data}")  # Debugging assistance

#         # Ensure the response is successful
#         self.assertEqual(response.status_code, 200)

#     def test_get_with_unassigned_agent(self):
#         # Create another unassigned agent
#         unassigned_agent = get_user_model().objects.create_user(
#             username='unassigned_agent', 
#             password='12345', 
#             user_type='AG',
#             email='unassigned_agent@example.com'
#         )

#         # Create token for the unassigned agent
#         unassigned_agent_token = Token.objects.create(user=unassigned_agent)

#         # Log in as the unassigned agent (using token authentication)
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(unassigned_agent_token.key))

#         # Make the GET request
#         response = self.client.get(self.agents_home_owner_account_url)
#         print(f"Response Status Code: {response.status_code}, Response Data: {response.data}")  # Debugging assistance

#         # Ensure that the unassigned agent is forbidden (since they are not assigned)
#         self.assertEqual(response.status_code, 403)

#     def test_get_with_nonexistent_home_owner(self):
#         # Log in as the agent
#         self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.agent_token.key))

#         # Test with a non-existent home owner ID
#         nonexistent_home_owner_url = reverse('property:agent-homeowner-dashboard', kwargs={'pk': 999})

#         # Make the GET request
#         response = self.client.get(nonexistent_home_owner_url)
#         print(f"Response Status Code: {response.status_code}, Response Data: {response.data}")  # Debugging assistance

#         # Ensure that the agent receives a NotFound response
#         self.assertEqual(response.status_code, 404)
