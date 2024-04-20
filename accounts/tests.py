from django.test import TestCase, Client
from profiles.models import ContractorProfile, User, UserProfile

class CustomSignupFormTest(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_form_save_user_type_co(self):
        response = self.client.post('/accounts/signup/', data={
            'phone_number_0' : "NG" , # for the phone field
            'phone_number_1' : "+2347058985430",
            'address': '123 Street',
            'user_type': 'CO',
            'company_name': 'Company',
            'specialization': 'Specialization',
            'company_address': 'Company Address',
            'email' : 'test@gmail.com',
            'password1' : '123pass?%@',
            'password2' : '123pass?%@',
        })
        self.assertEqual(response.status_code, 302)  # assuming it redirects after successful submission
        user = User.objects.first()
        self.assertEqual(user.user_type, 'CO')
        self.assertTrue(ContractorProfile.objects.filter(user=user).exists())
        
    def test_form_save_user_type_ho(self):
        response = self.client.post('/accounts/signup/', data={
            'phone_number_0' : "NG" , # for the phone field
            'phone_number_1' : "+2347058985430",
            'address': '123 Street',
            'user_type': 'HO',
            'first_name': 'John',
            'last_name': 'Doe',
            'city': 'City',
            'state': 'State',
            'email' : 'test@gmail.com',
            'password1' : '123pass?%@',
            'password2' : '123pass?%@',
        })
        self.assertEqual(response.status_code, 302) 
        user = User.objects.first()
        self.assertEqual(user.user_type, 'HO')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
        
    def test_form_save_user_type_ag(self):
        response = self.client.post('/accounts/signup/', data={
            'phone_number_0' : "NG" , # for the phone field
            'phone_number_1' : "+2347058985430",
            'address': '123 Street',
            'user_type': 'AG',
            'first_name': 'John',
            'last_name': 'Doe',
            'city': 'City',
            'state': 'State',
            'email' : 'test@gmai.com',
            'password1' : '123pass?%@',
            'password2' : '123pass?%@',
        })
        self.assertEqual(response.status_code, 302) 
        user = User.objects.first()
        self.assertEqual(user.user_type, 'AG')
        self.assertTrue(UserProfile.objects.filter(user=user).exists())
            