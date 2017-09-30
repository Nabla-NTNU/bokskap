from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core import mail
from django.contrib.sites.models import Site

from locker.utils import send_confirmation_email, get_confirmation_url

from .fixture_factories import LockerFactory


class CreateConfirmationTokenTest(TestCase):
    def setUp(self):
        self.locker = LockerFactory.create()
        self.user = User.objects.create(
            username="username",
            email="username@example.com",
        )

    def test_send_confirmation_email(self):
        token = "thetoken"
        u = self.user
        l = self.locker
        send_confirmation_email(u.email, self.locker, token)

        self.assertEqual(len(mail.outbox), 1)
        the_mail = mail.outbox.pop()

        self.assertIn(u.email, the_mail.to)

        body = the_mail.body
        self.assertIn(l.room, body)
        self.assertIn(str(l.locker_number), body)
        self.assertIn(token, body)


class ConfirmationUrlTest(TestCase):
    def setUp(self):
        self.domain = "testing.bokskap.nabla.no"
        site = Site.objects.get_current()
        site.domain = self.domain
        site.save()
        self.token = "asdfklhjasdfirawhgfklijausdh"

    def test_from_site(self):
        url = get_confirmation_url(self.token)
        self.assertIn(self.domain, url)
        self.assertIn("http", url)

    def test_from_request(self):
        factory = RequestFactory()
        request = factory.get("/", secure=True)
        server_name = "bokskap.nabla.no"
        request.META["SERVER_NAME"] = server_name

        url = get_confirmation_url(self.token, request=request)
        self.assertIn(server_name, url)
        self.assertIn("https", url)
