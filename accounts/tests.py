from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from unittest.mock import patch

User = get_user_model()

class AccountAPITestCase(APITestCase):

    def setUp(self):
        self.manual_signup_url = reverse('manual_signup')
        self.google_signup_url = reverse('google_signup')
        self.token_url = reverse('login')
        self.logout_url = reverse('logout')

        # Set up user data for manual signup
        self.manual_signup_data = {
            'username': 'johndoe',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@gmail.com',
            'password1': '7386pass?%@',
            'password2': '7386pass?%@',
            'password': '7386pass?%@',
            'user_type': 'HO',  # Homeowner
        }

    def test_manual_signup(self):
        """
        Test manual signup with valid data.
        """
        # Perform the POST request with valid signup d7386
        response = self.client.post(self.manual_signup_url, data=self.manual_signup_data, format='json')
        print(response)


        # Check that the response status code is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the user was successfully created in the database
        user = User.objects.filter(email=self.manual_signup_data['email']).first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, self.manual_signup_data['first_name'])
        self.assertEqual(user.last_name, self.manual_signup_data['last_name'])
        self.assertEqual(user.email, self.manual_signup_data['email'])

        # Ensure that the password was set properly (not the raw password)
        self.assertTrue(user.check_password(self.manual_signup_data['password1']))


    def test_missing_required_fields(self):
        """
        Test signup with missing required fields.
        """
        # Copy valid data and simulate missing email and other fields
        invalid_data = self.manual_signup_data.copy()
        invalid_data['email'] = ''  # Missing email
        
        # Check for user type-specific fields
        user_type = invalid_data.get('user_type')
        if user_type == 'HO':
            invalid_data['address'] = ''  # Homeowners must provide an address
        elif user_type == 'AG':
            invalid_data['registration_ID'] = ''  # Agents must provide registration ID
        elif user_type == "CO":
            invalid_data['company_address'] = ''
            invalid_data['company_name'] = ''
            invalid_data['specialization'] = ''
            invalid_data['city'] = ''
        
        # Perform the POST request with the invalid signup data
        response = self.client.post(self.manual_signup_url, data=invalid_data, format='json')

        # Check that the response status code is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check if the response contains the appropriate errors
        if user_type == 'HO':
            self.assertIn('address', response.data)  
        elif user_type == 'AG':
            self.assertIn('registration_ID', response.data)  
        elif user_type == 'CO':
            self.assertIn('company_name', response.data)  
            self.assertIn('company_address', response.data)
            self.assertIn('specialization', response.data)
            self.assertIn('city', response.data)
        
        # Regardless of user type, email and password should still be checked
        self.assertIn('email', response.data)
        
    @patch('accounts.views.requests.get')  # Mock the requests.get method used in authenticate_google_token
    def test_google_signup_invalid_token(self, mock_get):
        """
        Test Google signup with an invalid token.
        """
        # Set up the mock to return a response simulating an invalid token
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "error_description": "Invalid Value",
            "iss": "https://accounts.google.com",  # Ensure 'iss' field is present
            "email_verified": "false"  # Simulate email not verified
        }

        response = self.client.post(self.google_signup_url, data={'token': 'invalid_token'}, format='json')
        
        # Assert response status for invalid token
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('Invalid token', response.data['message'])

    @patch('accounts.views.requests.get')  # Mock the requests.get method used in authenticate_google_token
    def test_google_signup_valid_token(self, mock_get):
        """
        Test Google signup with a valid token.
        """
        # Simulate a valid token response from Google
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "iss": "https://accounts.google.com",
            "email_verified": "true",
            "email": "john.doe@gmail.com",
            "given_name": "John",
            "family_name": "Doe"
        }

        # Perform the Google signup request with a mock token
        response = self.client.post(self.google_signup_url, data={'token': 'valid_token'}, format='json')

        # Assert response status for valid token (201 Created)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the user was created successfully in the database
        user = User.objects.filter(email="john.doe@gmail.com").first()
        self.assertIsNotNone(user)
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.email, 'john.doe@gmail.com')

    # def test_logout(self):
    #     """
    #     Test logout by blacklisting the refresh token.
    #     """
    #     # Create a user and generate refresh token
    #     user = User.objects.create_user(username='testuser', password='123pass?%@')
    #     refresh = RefreshToken.for_user(user)

    #     # Log the user out (blacklist the refresh token)
    #     response = self.client.post(self.logout_url, data={'refresh_token': str(refresh)}, format='json')

    #     # Debugging step to see if there's any issue in response data
    #     print("Response data:", response.content)  # Use content as json might not work if content-type is not json

    #     # Check the status code
    #     self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

