"""Testcases for RegistrationRequest model and views"""
from django.test import TestCase
from django.core import mail

from locker.models import RegistrationRequest
from .fixture_factories import fake_locker_registration_post_request, LockerFactory


class TestRegistrationRequest(TestCase):
    """Testcase for a single registration request"""
    def setUp(self):
        lockers = LockerFactory.create_batch(10)
        self.reg = RegistrationRequest.objects.create(
            locker=lockers[0],
            username="testytest",
            first_name="Test",
            last_name="Testesen")

    def test_create_from_post_data(self):
        """Tests creation of a new registration request from data posted by user"""
        post_data = fake_locker_registration_post_request()
        request = RegistrationRequest.objects.create_from_data(post_data)

        self.assertIsNotNone(request.confirmation_token)

        request2 = RegistrationRequest.objects.get(confirmation_token=request.confirmation_token)
        self.assertEqual(request.pk, request2.pk)

    def test_send_email(self):
        """Test sending of confirmation email via a registration request"""
        self.reg.send_confirmation_email()
        email = self.reg.get_email()

        self.assertEqual(len(mail.outbox), 1)
        the_mail = mail.outbox.pop()
        self.assertIn(email, the_mail.to)

        body = the_mail.body
        self.assertIn(self.reg.locker.room, body)
        self.assertIn(str(self.reg.locker.locker_number), body)
        self.assertIn(self.reg.confirmation_token, body)

    def test_confirmation(self):
        """Test confirmation of registration request"""
        self.reg.confirm()
        locker = self.reg.locker
        self.assertTrue(locker.is_registered())
        self.assertEqual(locker.owner.username, self.reg.username)

        # Request object is not deleted
        reg = RegistrationRequest.objects.get(id=self.reg.id)
        # but a confirmation_time has been set
        self.assertTrue(reg.has_been_confirmed())
        self.assertIsNotNone(reg.confirmation_time)

    def test_string_representation(self):
        """Make sure the string representation of registration request makes sense"""
        string_rep = str(self.reg)
        self.assertIn(self.reg.username, string_rep)
        self.assertIn(str(self.reg.locker), string_rep)

    def test_confirm_twice(self):
        """
        Make sure that confirmations can be done twice without crashing.

        Confirmations should be idempotent.
        """
        self.reg.confirm()
        self.reg.confirm()
