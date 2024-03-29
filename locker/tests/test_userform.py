"""Test for forms"""
from django.test import TestCase
from locker.forms import UserForm

from .fixture_factories import fake_user_dict


class UserFormTest(TestCase):
    """Tests the form used for user validation"""

    def setUp(self):
        self.user_dict = fake_user_dict()

    def test_valid_username(self):
        """Valid usernames should be valid"""
        form = UserForm(self.user_dict)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], self.user_dict["username"])

    def test_email_instead_of_username(self):
        """Email-adresses are not valid usernames"""
        self.user_dict['username'] += '@stud.ntnu.no'
        form = UserForm(self.user_dict)
        self.assertFalse(form.is_valid())

    def test_non_alphanumeric_username(self):
        """Ntnu-usernames are alphanumeric"""
        self.user_dict['username'] = 'utropstegn!'
        form = UserForm(self.user_dict)
        self.assertFalse(form.is_valid())

    def test_username_with_space_at_end(self):
        """Test that the form strips whitespaces from usernames"""
        # It looks like form.CharField strips whitespaces as of django 1.9.
        # Didn't notice that before after the test was written.
        original_username = self.user_dict['username']

        self.user_dict['username'] = original_username + ' '

        form = UserForm(self.user_dict)
        self.assertTrue(form.is_valid())

        cleaned_username = form.cleaned_data['username']
        self.assertNotIn(' ', cleaned_username)
        self.assertEqual(cleaned_username, original_username)
