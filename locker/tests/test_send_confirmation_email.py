"""Testcases for confirmation of locker registrations"""
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.core import mail
from django.contrib.sites.models import Site

from locker.utils import send_confirmation_email, get_confirmation_url

from .fixture_factories import LockerFactory


class SendConfirmationEmailTest(TestCase):
    """Testcase for testing sending of confirmation email to single user"""
    def setUp(self):
        self.locker = LockerFactory.create()
        self.user = User.objects.create(
            username="username",
            email="username@example.com",
        )

    def test_send_confirmation_email(self):
        """Do the test"""
        token = "thetoken"
        user = self.user
        locker = self.locker
        send_confirmation_email(user.email, self.locker, token)

        self.assertEqual(len(mail.outbox), 1)
        the_mail = mail.outbox.pop()

        self.assertIn(user.email, the_mail.to)

        body = the_mail.body
        self.assertIn(locker.room, body)
        self.assertIn(str(locker.locker_number), body)
        self.assertIn(token, body)


class ConfirmationUrlTest(TestCase):
    """Testcase for testing the confirmation url"""
    def setUp(self):
        self.domain = "testing.bokskap.nabla.no"
        site = Site.objects.get_current()
        site.domain = self.domain
        site.save()
        self.token = "asdfklhjasdfirawhgfklijausdh"

    def test_from_site(self):
        """Test the url when not supplying a request"""
        url = get_confirmation_url(self.token)
        self.assertIn(self.domain, url)
        self.assertIn("http", url)

    def test_from_request(self):
        """Test the url when supplying a request"""
        factory = RequestFactory()
        request = factory.get("/", secure=True)
        server_name = "bokskap.nabla.no"
        request.META["SERVER_NAME"] = server_name

        url = get_confirmation_url(self.token, request=request)
        self.assertIn(server_name, url)
        self.assertIn("https", url)
