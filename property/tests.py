from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import AssignedAccount
from quotes.models import Project, QuoteRequest


class AgentsHomeOwnerAccountViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.home_owner = get_user_model().objects.create_user(username='homeowner', password='12345', user_type='HO')
        self.agent = get_user_model().objects.create_user(username='agent', password='12345', user_type='AG')
        self.assigned_account = AssignedAccount.objects.create(assigned_by=self.home_owner, assigned_to=self.agent)
        self.agents_home_owner_account_url = reverse('property:agent-homeowner-dashboard', kwargs={'pk': self.home_owner.pk})

    def test_get_with_assigned_agent(self):
        self.client.login(username='agent', password='12345')
        response = self.client.get(self.agents_home_owner_account_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/home.html')

    def test_get_with_unassigned_agent(self):
        unassigned_agent = get_user_model().objects.create_user(username='unassigned_agent', password='12345', user_type='AG')
        self.client.login(username='unassigned_agent', password='12345')
        response = self.client.get(self.agents_home_owner_account_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:home'))

    def test_get_with_nonexistent_home_owner(self):
        nonexistent_home_owner_url = reverse('property:agent-homeowner-dashboard', kwargs={'pk': 999})  # non-existing home owner id
        self.client.login(username='agent', password='12345')
        response = self.client.get(nonexistent_home_owner_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('main:home'))
