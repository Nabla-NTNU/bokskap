from django.test import TestCase
from django.core import mail
import datetime

from locker.models import RegistrationRequest
from .fixture_factories import fake_locker_registration_post_request, LockerFactory, RegistrationRequestFactory


class TestRegistrationRequest(TestCase):
    def setUp(self):
        LockerFactory.create_batch(10)

    def test_create(self):
        post_data = fake_locker_registration_post_request()
        request = RegistrationRequest.objects.create_from_data(post_data)

        self.assertIsInstance(request, RegistrationRequest)

        self.assertEqual(RegistrationRequest.objects.count(), 1)
        confirmation_token = request.confirmation_token
        self.assertIsNotNone(confirmation_token)

        request2 = RegistrationRequest.objects.get(confirmation_token=request.confirmation_token)
        self.assertEqual(request.pk, request2.pk)

        self.assertIsInstance(request.creation_time, datetime.datetime)

        request.save()
        self.assertEqual(request.confirmation_token, confirmation_token)


class Test2(TestCase):
    def setUp(self):
        self.reg = RegistrationRequestFactory.create()

    def test_send_email(self):
        self.reg.send_confirmation_email()
        email = self.reg.get_email()

        the_mail = mail.outbox[0]
        self.assertIn(email, the_mail.to)

        body = the_mail.body
        self.assertIn(self.reg.locker.room, body)
        self.assertIn(str(self.reg.locker.locker_number), body)
        self.assertIn(self.reg.confirmation_token, body)

    def test_confirmation(self):
        self.reg.confirm()
        locker = self.reg.locker
        self.assertTrue(locker.is_registered())
        self.assertTrue(locker.owner.username, self.reg.username)

        # Request object is not deleted
        reg = RegistrationRequest.objects.get(id=self.reg.id)
        # but a confirmation_time has been set
        self.assertTrue(reg.has_been_confirmed())
        self.assertIsNotNone(reg.confirmation_time)

    def test_string_representation(self):
        s = str(self.reg)
        self.assertIn(self.reg.username, s)
        self.assertIn(str(self.reg.locker), s)
