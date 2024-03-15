from django.test import TestCase, tag
from django.contrib.auth import get_user_model

@tag('login')
class LogInTestCase(TestCase):
    def test_user_login(self):
        # First I need to create user account using create_user() helper function
        get_user_model().objects.create_user("Erone Peter", "eronepeter@gmail.com", "petro77??")

        # Logging in the person with the account using login() method or function of the django's test client
        response = self.client.login(email="eronepeter@gmail.com", password="petro77??")

        self.assertTrue(response)



    

