from django.test import TestCase
from django.shortcuts import reverse
from django.core import mail

import random
import re

from .fixture_factories import LockerFactory, fake_user_dict
from locker.models import Locker

# Regex taken uncritically from:
# http://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python#6883094
url_regex_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


class TestTypicalUserInteraction(TestCase):
    num_lockers = 10
    locker_room = "CU2-021"

    def setUp(self):
        self.lockers = LockerFactory.create_batch(self.num_lockers, room=self.locker_room)

    def get_random_locker(self):
        return random.choice(self.lockers)

    def get_locker_dict(self, locker):
        return {
            "room": locker.room,
            "locker_number": locker.locker_number
        }

    def test_single_locker_registration(self):
        # An NTNU-student wants to register a locker in realfagbygget
        data = self.get_locker_dict(self.get_random_locker())
        registration_url = reverse("register_locker", kwargs=data)

        data.update(fake_user_dict())

        # He/she posts the information.
        self.client.post(registration_url, data=data)

        # The locker should not be registered yet,
        locker = Locker.objects.get(room=data['room'], locker_number=data['locker_number'])
        self.assertFalse(locker.is_registered())

        # but the user should be sent an email containing an url to confirm the registration
        the_mail = mail.outbox[0]
        self.assertIn(data['username']+'@stud.ntnu.no', the_mail.to)

        # The mail should contain information about which room and locker that is about to be registered.
        body = the_mail.body
        self.assertIn(data['room'], body)
        self.assertIn(str(data['locker_number']), body)

        # It should also contain a confirmation url.
        urls_found = url_regex_pattern.findall(body)
        self.assertTrue(urls_found)

        # When the user clicks the link
        response = self.client.get(urls_found[0])
        # she sees at button that she has to press
        # which sends a post request to the same url

        self.client.post(urls_found[0])

        # the locker should then be registered.
        locker.refresh_from_db()
        self.assertTrue(locker.is_registered())

        # If the user tries to get the confirmation page again
        # she gets a page telling her that the locker has already
        # been registered.
        response = self.client.get(urls_found[0])
        self.assertEqual(response.status_code, 200)

        # The user should also have been sent an email saying
        # that the registration has been confirmed
        confirmed_email = mail.outbox[1]
        confirmed_email
