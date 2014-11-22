# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
import django.utils.timezone as timezone

from locker.models import Locker


class LockerModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="abc")
        self.lockers = [Locker.objects.create(locker_number=i, room="CU1-111") for i in range(10)]

    def test_reserve(self):
        l = self.lockers[0]
        self.assertFalse(l.is_reserved())

        before = timezone.now()
        l.reserve(self.user)
        after = timezone.now()

        self.assertTrue(l.is_reserved(),
                        "The locker is not registered when it should be.")
        self.assertEqual(l.owner, self.user,
                         "The locker is not registered to the correct user.")
        self.assertTrue(before <= l.time_reserved <= after,
                        "Check if registration time was set.")

    def test_unreserve(self):
        l = self.lockers[0]
        l.reserve(self.user)

        l.unreserve()
        self.assertFalse(l.is_reserved(), "Check if is registered")
