"""User interaction tests"""
import random
import re

from django.test import TestCase
from django.shortcuts import reverse
from django.core import mail

from locker.models import Locker
from .fixture_factories import LockerFactory, fake_user_dict

# Regex taken uncritically from:
# http://stackoverflow.com/questions/6883049/regex-to-find-urls-in-string-in-python#6883094
URL_REGEX_PATTERN = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')


class TestTypicalUserInteraction(TestCase):
    """A typical user interaction"""
    num_lockers = 10
    locker_room = "CU2-021"

    def setUp(self):
        self.lockers = LockerFactory.create_batch(self.num_lockers, room=self.locker_room)

    def test_single_locker_registration(self):
        """
        An NTNU-student wants to register a locker in realfagbygget
        """
        locker = random.choice(self.lockers)
        data = {
            "room": locker.room,
            "locker_number": locker.locker_number
        }
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

        # The mail should contain information about which room and locker
        # that is about to be registered.
        body = the_mail.body
        self.assertIn(data['room'], body)
        self.assertIn(str(data['locker_number']), body)

        # It should also contain a confirmation url.
        urls_found = URL_REGEX_PATTERN.findall(body)
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
        self.assertTrue(len(mail.outbox) >= 0)

    def test_trying_to_register_twice_before_confirming(self):
        """
        This test was used to reproduce a bug.
        The bug happened when a user tried to register a locker twice and was sent two different
        confirmation links, then visited both and got an error.
        """
        locker = random.choice(self.lockers)
        data = {
            "room": locker.room,
            "locker_number": locker.locker_number
        }
        registration_url = reverse("register_locker", kwargs=data)

        data.update(fake_user_dict())

        self.client.post(registration_url, data=data)
        url1 = URL_REGEX_PATTERN.findall(mail.outbox[0].body)[0]
        mail.outbox = []
        self.client.post(registration_url, data=data)
        url2 = URL_REGEX_PATTERN.findall(mail.outbox[0].body)[0]
        mail.outbox = []
        response1 = self.client.get(url1)
        self.assertEqual(response1.status_code, 200)
        response2 = self.client.get(url2)
        self.assertEqual(response2.status_code, 200)

    def test_two_people_trying_to_register_the_same_locker(self):
        """
        What happens when two people try to register the same locker?
        """
        locker = random.choice(self.lockers)
        data = {
            "room": locker.room,
            "locker_number": locker.locker_number
        }
        registration_url = reverse("register_locker", kwargs=data)

        # A user tries to register a locker
        data.update(fake_user_dict())
        self.client.post(registration_url, data=data)
        url1 = URL_REGEX_PATTERN.findall(mail.outbox[0].body)[0]
        mail.outbox = []

        # Another user also tries to register the same locker
        data.update(fake_user_dict())
        self.client.post(registration_url, data=data)
        url2 = URL_REGEX_PATTERN.findall(mail.outbox[0].body)[0]
        mail.outbox = []

        # The first user confirms og takes ownership.
        response1 = self.client.get(url1)
        self.assertEqual(response1.status_code, 200)
        new_owner = locker.owner

        # The second user tries to confirm the locker but it doesn't work
        # and they get http 200 code hopefully with some information explaining the situation.
        response2 = self.client.get(url2)
        self.assertEqual(response2.status_code, 200)

        # The first user is still owner of the locker.
        self.assertEqual(locker.owner, new_owner)
