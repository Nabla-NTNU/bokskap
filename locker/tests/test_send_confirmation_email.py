from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail

from locker.utils import send_confirmation_email

from .fixture_factories import LockerFactory


class CreateConfirmationTokenTest(TestCase):
    def setUp(self):
        self.locker = LockerFactory.create()
        self.user = User.objects.create(username="username")

    def test_send_confirmation_email(self):
        token = "thetoken"
        u = self.user
        l = self.locker
        send_confirmation_email(u.email, self.locker, token)

        the_mail = mail.outbox[0]
        self.assertIn(u.email, the_mail.to)

        body = the_mail.body
        self.assertIn(l.room, body)
        self.assertIn(str(l.locker_number), body)
        self.assertIn(token, body)
