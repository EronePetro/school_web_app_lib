from django.test import TestCase, tag
from django.contrib.auth import get_user_model

@tag('general')
class TestNewUserCreation(TestCase):
    @tag('ordinary_user')
    def test_ordinary_user_account_creation(self):
        # Creating an ordinary account for the user
        person = get_user_model().objects.create_user("Peter Erone", "eronepeter@gmail.com", "petro77??")

        self.assertEqual(person.full_name, "Peter Erone")
        self.assertEqual(person.email, "eronepeter@gmail.com")
        self.assertEqual(str(person), "Peter Erone")
    
    @tag('administrator')
    def test_administrator_account_creation(self):
        person_1 = get_user_model().objects.create_superuser('Anne Ikapel', "ikapelanne@gmail.com", "itwani77??")

        self.assertEqual(person_1.full_name, "Anne Ikapel")
        self.assertEqual(person_1.email, "ikapelanne@gmail.com")
        self.assertTrue(person_1.is_superuser)
        self.assertTrue(person_1.is_staff)
        self.assertTrue(person_1.is_active)
        self.assertEqual(str(person_1), "Anne Ikapel")
    
    @tag('exceptions')
    def test_for_exceptions(self):
        # Testing user account creation minus email value
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(full_name="Eliud Erone", email="", password="petro77??")

        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(full_name="Faith Elizabeth", email="fei@gmail.com", password="petro77??", is_staff="False")

        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(full_name="Faith Elizabeth", email="fei@gmail.com", password="petro77??", is_superuser="False")


