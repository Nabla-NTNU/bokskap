# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
import django.utils.timezone as timezone

from .fixture_factories import LockerFactory, fake_locker_registration_post_request
from locker.models import Locker, LockerReservedException, Ownership


class LockerModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="abc")
        self.lockers = LockerFactory.create_batch(10)

    def test_reserve(self):
        l = self.lockers[0]
        self.assertFalse(l.is_registered())

        before = timezone.now()
        l.register(self.user)
        after = timezone.now()

        ownership = Ownership.objects.get(locker=l)
        
        self.assertTrue(l.is_registered(),
                        "The locker is not registered when it should be.")
        self.assertEqual(l.owner, self.user,
                         "The locker is not registered to the correct user.")
        self.assertTrue(before <= ownership.time_reserved <= after,
                        "Check if registration time was set.")

    def test_unreserve(self):
        l = self.lockers[0]
        l.register(self.user)

        l.unregister()
        self.assertFalse(l.is_registered(), "Check if is registered")

    def test_str(self):
        for l in self.lockers:
            s = str(l)
            self.assertIn(l.room, s)
            self.assertIn(str(l.locker_number), s)

    def test_get_locker_from_post_data(self):
        data = fake_locker_registration_post_request()
        locker = Locker.objects.get_from_post_data(data)
        self.assertIsInstance(locker, Locker)
        self.assertEqual(locker.room, data["room"])
        self.assertEqual(locker.locker_number, data["locker_number"])

    def test_register_twice(self):
        user2 = User.objects.create(username="lala")
        l = self.lockers[0]
        l.register(self.user)
        with self.assertRaises(LockerReservedException):
            l.register(user2)
        self.assertEqual(l.owner, self.user)
