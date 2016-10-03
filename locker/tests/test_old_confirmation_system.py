from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import User

from locker.models import Locker
from locker.utils import create_confirmation_token
from .fixture_factories import LockerFactory, fake_locker_registration_post_request


class TestOldRegistration(TestCase):
    def setUp(self):
        self.lockers = LockerFactory.create_batch(10)

    def test_user_tried_to_register_before_new_confirmation_system(self):
        data = fake_locker_registration_post_request()

        locker = Locker.objects.get(room=data['room'], locker_number=data['locker_number'])
        User.objects.create(username=data["username"])
        token = create_confirmation_token(locker, data)

        self.client.get(reverse("registration_confirmation", kwargs={"key": token}))
        locker.refresh_from_db()
        self.assertTrue(locker.is_reserved())
        self.assertEqual(locker.owner.username, data['username'])
