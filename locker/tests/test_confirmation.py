# -*- coding: utf-8 -*-

from django.test import TestCase
from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache

from locker.utils import create_confirmation_token, send_confirmation_email
from .fixture_factories import LockerFactory


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

    def test_send_confirmation_email(self):
        token = "thetoken"
        u = self.user
        l = self.locker
        send_confirmation_email(u, self.locker, token)

        the_mail = mail.outbox[0]
        self.assertIn(u.email, the_mail.to)

        body = the_mail.body
        self.assertIn(l.room, body)
        self.assertIn(str(l.locker_number), body)
        self.assertIn(token, body)

    def test_save_locker_registration(self):
        pass
