from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from .fixture_factories import LockerFactory
from random import sample


NUMBER_OF_LOCKERS = 10
NUMBER_OF_UNREGISTERED_LOCKERS = 4

class TestResetAll(TestCase):
    def setUp(self):
        self.lockers = LockerFactory.create_batch(NUMBER_OF_LOCKERS)

    def test_reset_all(self):
        # Create a database with some active ownerships and some inactive
        
        for i, locker in enumerate(self.lockers):
            user = User.objects.create(username="username{}".format(i))
            locker.register(user)
            self.assertTrue(locker.is_registered())

        for locker in sample(self.lockers, NUMBER_OF_UNREGISTERED_LOCKERS):
            locker.reset()

        mail.outbox.clear()

        for locker in self.lockers:
            locker.reset()
            self.assertFalse(locker.is_registered())

        self.assertEqual(len(mail.outbox), NUMBER_OF_LOCKERS - NUMBER_OF_UNREGISTERED_LOCKERS)
