#pylint: disable=C0111
"""Testcases for locker model"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from locker.models import Locker, LockerReservedException, Ownership
from .fixture_factories import LockerFactory, fake_locker_registration_post_request


class LockerModelTest(TestCase):
    """Test Locker model"""

    def setUp(self):
        self.user = User.objects.create(username="abc")
        self.lockers = LockerFactory.create_batch(10)

    def test_reserve(self):
        """Test registering a locker to a user"""
        locker = self.lockers[0]
        self.assertFalse(locker.is_registered())

        before = timezone.now()
        locker.register(self.user)
        after = timezone.now()

        ownership = Ownership.objects.get(locker=locker)

        self.assertTrue(locker.is_registered(),
                        "The locker is not registered when it should be.")
        self.assertEqual(locker.owner, self.user,
                         "The locker is not registered to the correct user.")
        self.assertTrue(before <= ownership.time_reserved <= after,
                        "Check if registration time was set.")

    def test_unreserve(self):
        """Test registering and unregistering locker"""
        locker = self.lockers[0]
        locker.register(self.user)

        locker.unregister()
        self.assertFalse(locker.is_registered(), "Check if is registered")

    def test_str(self):
        """Test string representation of Locker"""
        for locker in self.lockers:
            string_representation = str(locker)
            self.assertIn(locker.room, string_representation)
            self.assertIn(str(locker.locker_number), string_representation)

    def test_get_locker_from_post_data(self):
        """Test the custom manager method"""
        data = fake_locker_registration_post_request()
        locker = Locker.objects.get_from_post_data(data)
        self.assertIsInstance(locker, Locker)
        self.assertEqual(locker.room, data["room"])
        self.assertEqual(locker.locker_number, data["locker_number"])

    def test_register_twice(self):
        """Registering a locker should raise exception"""
        user2 = User.objects.create(username="lala")
        locker = self.lockers[0]
        locker.register(self.user)
        with self.assertRaises(LockerReservedException):
            locker.register(user2)
        self.assertEqual(locker.owner, self.user)


class OwnershipTest(TestCase):
    """Test Ownership model"""
    def setUp(self):
        self.lockers = LockerFactory.create_batch(10)
        self.locker = self.lockers[0]
        self.user = User.objects.create(username="abc")
        self.ownership = Ownership.objects.create_ownership(self.locker, self.user)

    def test_create_ownership_twice(self):
        """Creating ownerships twice should raise exception"""
        with self.assertRaises(Exception):
            Ownership.objects.create_ownership(self.locker, self.user)

    def test_is_active_when_newly_created(self):
        self.assertTrue(self.ownership.is_active())

    def test_deregistration_should_make_ownership_inactive(self):
        self.ownership.unregister()
        self.assertFalse(self.ownership.is_active())

    def test_deregistration_should_be_idempotent(self):
        """Deregistering for the second time should do nothing"""
        self.ownership.unregister()
        time1 = self.ownership.time_unreserved
        self.ownership.unregister()
        time2 = self.ownership.time_unreserved
        self.assertEqual(time1, time2)
