"""Testcases for reset of lockers"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from .fixture_factories import LockerFactory


class TestResetAll(TestCase):
    """Test reset of all lockers when not all are registered"""
    NUMBER_OF_LOCKERS = 10
    NUMBER_OF_REGISTERED_LOCKERS = 4
    def setUp(self):
        # Create a database with some active ownerships and some inactive
        self.lockers = LockerFactory.create_batch(self.NUMBER_OF_LOCKERS)
        for i, locker in zip(range(self.NUMBER_OF_REGISTERED_LOCKERS), self.lockers):
            user = User.objects.create(username=f"username{i}")
            locker.register(user)
        mail.outbox.clear()

    def test_reset_all(self):
        """Try to reset all lockers"""
        for locker in self.lockers:
            locker.reset()
            self.assertFalse(locker.is_registered())

        self.assertEqual(
            len(mail.outbox),
            self.NUMBER_OF_REGISTERED_LOCKERS)
