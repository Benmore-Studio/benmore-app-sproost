
    def test_edit_contractor_profile_success(self):
        response = self.client.post(reverse('profile:contractor-edit-profile-request'), {
            'company_name': 'Updated Company Name',
            'registration_number': '987654321',
            'specialization': 'Updated Specialization',
            'company_address': 'Updated Company Address',
            'city': 'Updated City',
        })

        self.assertEqual(response.status_code, 302)

        # Refresh the contractor profile object from the database
        self.contractor_profile.refresh_from_db()

        # Check that the contractor profile fields have been updated correctly
        self.assertEqual(self.contractor_profile.company_name, 'Updated Company Name')
        self.assertEqual(self.contractor_profile.registration_number, '987654321')
        self.assertEqual(self.contractor_profile.specialization, 'Updated Specialization')
        self.assertEqual(self.contractor_profile.company_address, 'Updated Company Address')
        self.assertEqual(self.contractor_profile.city, 'Updated City')

     # checking for validation
    def test_edit_profile_validation(self):
        # Making a POST request to the edit profile view with invalid data
        response = self.client.post(reverse('profile:contractor-edit-profile-request'), {
        })

        # Checking ifresponse is not a redirect 
        self.assertEqual(response.status_code, 200)

        # Check that the form errors are displayed in the response
        self.assertContains(response, 'This field is required.')

    # checking authentication of the edit page
    def test_edit_profile_authentication(self):
        self.client.logout()
        # Making a GET request to the edit profile view
        response = self.client.get(reverse('profile:edit-profile'))
        # Checking that the response is a redirect (unauthenticated users are redirected)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/profiles/edit-profile/')


