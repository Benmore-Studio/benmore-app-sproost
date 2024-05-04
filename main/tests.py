from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from property.models import AssignedAccount
from profiles.models import AgentProfile

user = get_user_model()
class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_url = reverse('main:home')
        self.user = user.objects.create_user(username='testuser', password='12345')

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(self.home_url)
        self.assertRedirects(response, reverse("account_login")) 

    def test_logged_in_with_homeowner_user(self):
        self.client.login(username='testuser', password='12345')
        self.user.user_type = 'HO'
        self.user.save()
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/home.html')
        
    def test_logged_in_with_contractor_user(self):
        self.client.login(username='testuser', password='12345')
        self.user.user_type = 'CO'
        self.user.save()
        response = self.client.get(self.home_url, follow=False)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("profile:contractor_profile"))
        
    def test_logged_in_with_agent_user(self):
        self.client.login(username='testuser', password='12345')
        self.user.user_type = 'AG'
        self.user.save()
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/agent_home.html')

class AssignAgentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.assign_agent_url = reverse('main:assign-agent')
        self.home_owner = user.objects.create_user(username='homeowner', password='12345', user_type='HO')
        self.agent = user.objects.create_user(username='agent', password='12345', user_type='AG')
        self.agent_profile = AgentProfile.objects.create(
            user=self.agent, 
            registration_ID='12345FF', 
            address = "123 Street"
        )

    def test_get(self):
        self.client.login(username='homeowner', password='12345')
        response = self.client.get(self.assign_agent_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/assignAgent.html')

    def test_post_with_valid_agent(self):
        self.client.login(username='homeowner', password='12345')
        agent_data = {
            'registration_id': '12345FF'
        }
        response = self.client.post(self.assign_agent_url, agent_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:home'))
        self.assertTrue(AssignedAccount.objects.filter(assigned_to=self.agent, assigned_by=self.home_owner).exists())

    def test_post_with_invalid_agent(self):
        self.client.login(username='homeowner', password='12345')
        agent_data = {
            'registration_id': '2323232323'
        }
        response = self.client.post(self.assign_agent_url, agent_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:assign-agent'))
        self.assertFalse(AssignedAccount.objects.filter(assigned_by=self.home_owner).exists())