# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.cache import cache
from django.urls import reverse

from locker.models import Locker
from locker.old_confirmation_system import create_confirmation_token

from .fixture_factories import LockerFactory, fake_locker_registration_post_request


class CreateConfirmationTokenTest(TestCase):
    def setUp(self):
        self.locker = LockerFactory.create()
        self.user = User.objects.create(username="username")

    def test_create_confirmation_token(self):
        l = self.locker
        post_data = {'the_key': 'data'}

        token = create_confirmation_token(l, post_data)

        cache_data = cache.get(token)
        new_post_data = cache_data.get("post_data")
        locker_number = cache_data.get("locker_number")
        room = cache_data.get("room")

        self.assertEqual(room, l.room)
        self.assertEqual(locker_number, l.locker_number)
        self.assertEqual(post_data, new_post_data)


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