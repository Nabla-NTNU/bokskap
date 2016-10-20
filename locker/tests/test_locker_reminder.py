# -*- coding: utf-8 -*-

from django.test import TestCase
from django.core import mail
from django.contrib.auth.models import User

from locker.utils import send_locker_reminder
from .fixture_factories import LockerFactory


class LockerReminderTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="abc")
        self.lockers = LockerFactory.create_batch(10)

    def test_send_locker_reminder(self):
        # Hent brukeren
        u = self.user

        # Registrer noen skap på brukeren
        lockers_registered = self.lockers[:2]
        for l in lockers_registered:
            l.register(u)

        # Send skappåmindelse
        send_locker_reminder(u)

        # Hent eposten som burde blitt sendt og skjekk om den ble sendt til
        # brukeren
        the_mail = mail.outbox[0]
        self.assertIn(u.email, the_mail.to)

        # Skjekk om alle skapene ble nevnt i eposten.
        body = the_mail.body
        for l in lockers_registered:
            self.assertIn(l.room, body)
            self.assertIn(str(l.locker_number), body)
