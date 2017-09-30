from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from .fixture_factories import LockerFactory


class TestResetAll(TestCase):
    def setUp(self):
        self.lockers = LockerFactory.create_batch(10)

    def test_reset_all(self):
        for i, locker in enumerate(self.lockers):
            user = User.objects.create(username="username{}".format(i))
            locker.register(user)
            self.assertTrue(locker.is_registered())

        mail.outbox.clear()

        for locker in self.lockers:
            locker.reset()
            self.assertFalse(locker.is_registered())

        self.assertEqual(len(mail.outbox), 10)
