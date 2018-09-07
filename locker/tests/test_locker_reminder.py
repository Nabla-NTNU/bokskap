"""Tests for locker reminders"""
from django.test import TestCase
from django.core import mail
from django.contrib.auth.models import User

from locker.utils import send_locker_reminder
from .fixture_factories import LockerFactory


class LockerReminderTest(TestCase):
    """Set up a user and some lockers and test sending locker reminder"""

    def setUp(self):
        self.user = User.objects.create(
            username="abc",
            email="abc@example.com",
        )
        self.lockers = LockerFactory.create_batch(10)

        self.lockers_registered = self.lockers[:2]
        for locker in self.lockers_registered:
            locker.register(self.user)
        mail.outbox.clear()

    def test_send_locker_reminder(self):
        """Test the sending of locker reminder"""
        # Send skappåmindelse
        send_locker_reminder(self.user)

        # Hent eposten som burde blitt sendt og skjekk om den ble sendt til
        # brukeren
        self.assertEqual(len(mail.outbox), 1)
        the_mail = mail.outbox.pop()
        self.assertIn(self.user.email, the_mail.to)

        # Skjekk om alle skapene ble nevnt i eposten.
        body = the_mail.body
        for locker in self.lockers_registered:
            self.assertIn(locker.room, body)
            self.assertIn(str(locker.locker_number), body)
