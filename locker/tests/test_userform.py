from django.test import TestCase
from locker.forms import UserForm

from .fixture_factories import fake_user_dict


class UserFormTest(TestCase):

    def setUp(self):
        self.user_dict = fake_user_dict()

    def test_valid_username(self):
        form = UserForm(self.user_dict)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["username"], self.user_dict["username"])

    def test_email_instead_of_username(self):
        self.user_dict['username'] += '@stud.ntnu.no'
        form = UserForm(self.user_dict)
        self.assertFalse(form.is_valid())

    def test_non_alphanumeric_username(self):
        self.user_dict['username'] = 'utropstegn!'
        form = UserForm(self.user_dict)
        self.assertFalse(form.is_valid())
