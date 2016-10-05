# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone as timezone

from .utils import random_string, stud_email_from_username, send_confirmation_email


class LockerManager(models.Manager):
    def get_from_post_data(self, data):
        return self.get(room=data["room"], locker_number=data["locker_number"])


class LockerException(Exception):
    pass


class Locker(models.Model):

    ROOMS = (
        ('CU1-111', 'CU1-111'),
        ('CU2-021', 'CU2-021'),
        ('EU1-110', 'EU1-110')
    )
    room = models.CharField(max_length=10, choices=ROOMS, blank=False,
                            editable=False, verbose_name="Rom")
    locker_number = models.IntegerField(blank=False, editable=False,
                                        verbose_name="Skapnummer")
    owner = models.ForeignKey(User, blank=True, null=True, verbose_name="Eier")
    time_reserved = models.DateTimeField(blank=True, null=True)

    objects = LockerManager()

    class Meta:
        unique_together = ('room', 'locker_number',)

    def reserve(self, user):
        if self.is_reserved():
            raise LockerException(("{0} is already registered to {0.owner}"
                                   " and can't be registered to {1}").format(self, user))
        self.owner = user
        self.time_reserved = timezone.now()
        self.save()

    def unreserve(self, lock_cut=False):
        if self.is_reserved():
            inactive = InactiveLockerReservation()
            inactive.owner = self.owner
            inactive.lock_cut = lock_cut
            inactive.locker = self
            inactive.time_unreserved = timezone.now()
            inactive.time_reserved = self.time_reserved
            inactive.save()
            self.time_reserved = None
            self.owner = None
            self.save()

    def is_reserved(self):
        return bool(self.owner)

    def __str__(self):
        return "({0.room}, {0.locker_number}) ".format(self)


class InactiveLockerReservation(models.Model):
    time_reserved = models.DateTimeField(blank=False)

    # Datoen enten brukeren avregistrerte skapet
    # eller Nabla klippet opp låsen og fjernet innholdet.
    time_unreserved = models.DateTimeField(blank=False)

    # Indikerer om låsen på skapet ble klippet av Nabla
    lock_cut = models.BooleanField(blank=False, default=False)

    owner = models.ForeignKey(User, blank=False)
    locker = models.ForeignKey(Locker, blank=False)

    def __str__(self):
        return "({0.locker}, {0.owner}) ".format(self)


class RegistrationRequest(models.Model):
    confirmation_token = models.CharField(max_length=20, unique=True, blank=True, null=True)
    creation_time = models.DateTimeField(auto_now_add=True)

    locker = models.ForeignKey(Locker, blank=False)
    username = models.CharField("Brukernavn", max_length=30, blank=False)
    first_name = models.CharField("Fornavn", max_length=30, blank=True)
    last_name = models.CharField("Etternavn", max_length=30, blank=True)

    @classmethod
    def from_post_data(cls, data):
        return RegistrationRequest.objects.create(
            locker=Locker.objects.get_from_post_data(data),
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
        )

    def save(self, **kwargs):
        if self.confirmation_token is None:
            self.confirmation_token = random_string()
        super().save(**kwargs)

    def get_email(self):
        return stud_email_from_username(self.username)

    def send_confirmation_email(self):
        email = self.get_email()
        send_confirmation_email(email, self.locker, self.confirmation_token)

    def confirm(self):
        user, created = User.objects.get_or_create(username=self.username)
        self.locker.reserve(user)
