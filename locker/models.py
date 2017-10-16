# -*- coding: utf-8 -*-
import logging

from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone as timezone

from .utils import (random_string, stud_email_from_username,
                    send_confirmation_email, send_locker_is_registered_email, get_confirmation_url, send_template_email)


logger = logging.getLogger(__name__)


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

    objects = LockerManager()

    class Meta:
        unique_together = ('room', 'locker_number',)
        verbose_name = "Skap"
        verbose_name_plural = "Skap"


    def is_registered(self):
        return Ownership.objects.filter(locker=self)
    
    def __str__(self):
        return "({0.room}, {0.locker_number}) ".format(self)

class LockerReservedException(Exception):
    pass


class OwnershipManager(models.Manager):
    def create_ownership(self, locker, owner):
        if Ownership.objects.filter(locker = locker, time_unreserved = None):
            raise LockerReservedException()
            
        ownership = self.create(locker=locker, owner=owner, time_reserved = timezone.now())
        send_locker_is_registered_email(owner.username, locker)
        logger.info(f"{locker} is now registered to {owner}")
        return ownership
        
    
class Ownership(models.Model):
    locker = models.ForeignKey(Locker, blank=False, null=False, verbose_name="Skap", on_delete=models.CASCADE) # Locker and user should not be deletd, but CASCADE just in case.
    owner = models.ForeignKey(User, blank=False, null=False, verbose_name="Skap", on_delete=models.CASCADE)
    time_reserved = models.DateTimeField(blank=False, null=True)
    
    lock_cut = models.BooleanField(default=False)
    time_unreserved = models.DateTimeField(blank=True, null=True) # Locker is active until unreserved

    objects = OwnershipManager()

    def unregister(self, lock_cut):
        self.time_unreserved = timezone.now()
        self.lock_cut = lock_cut
        self.save()

    def is_active(self):
        return self.time_unreserved is None #A locker is active until it is unreserved
        
    def reset(self):
        """
        Avregistrer et skap og sender mail hvor det kan registreres på nytt
        """
        request = RegistrationRequest.objects.create(
            locker=self.locker,
            username=self.owner.username,
            first_name=self.owner.first_name,
            last_name=self.owner.last_name)

        self.unregister()

        c = {
            "confirmation_url": get_confirmation_url(request.confirmation_token),
            "room": self.locker.room,
            "locker_number": self.locker.locker_number
        }

        subject = "Registrere skap på nytt for neste semester"
        email = request.get_email()
        send_template_email("email/locker_reset.html", c, subject, [email])

class RegistrationRequestManager(models.Manager):
    def create_from_data(self, data):
        return self.create(
            locker=Locker.objects.get_from_post_data(data),
            username=data['username'],
            first_name=data['first_name'],
            last_name=data['last_name'],
        )


class RegistrationRequest(models.Model):
    confirmation_token = models.CharField(max_length=20, unique=True, blank=True, null=True)
    creation_time = models.DateTimeField(
        verbose_name="Tidspunktet skapet ble forsøkt registrert.",
        auto_now_add=True)

    locker = models.ForeignKey(
        Locker,
        verbose_name="Skap",
        blank=False)
    username = models.CharField("Brukernavn", max_length=30, blank=False)
    first_name = models.CharField("Fornavn", max_length=30, blank=True)
    last_name = models.CharField("Etternavn", max_length=30, blank=True)

    confirmation_time = models.DateTimeField(
            verbose_name="Tidspunktet forspørselen ble bekreftet", null=True, blank=True)

    objects = RegistrationRequestManager()

    class Meta:
        verbose_name = "Skapforespørsel"
        verbose_name_plural = "Skapforespørsler"

    def __str__(self):
        return "{0.username} forespør {0.locker}".format(self)

    def save(self, **kwargs):
        if self.confirmation_token is None:
            self.confirmation_token = random_string()
            logger.info("RegistrationRequest created: <{}>".format(self))
        super().save(**kwargs)

    def get_email(self):
        return stud_email_from_username(self.username)

    def send_confirmation_email(self, request=None):
        email = self.get_email()
        send_confirmation_email(email, self.locker, self.confirmation_token, request=request)
        logger.info("Confirmation mail sent to {} for locker: {}".format(email, self.locker))

    def confirm(self):
        user, created = User.objects.get_or_create(username=self.username)
        try:
            ownership = Ownership.objects.create_ownership(locker=self.locker, owner=user)
        except LockerReservedException:
            logger.info(f"{self.locker} is allready reserved. Cannot reserve for {user}.")
        else:
            self.confirmation_time = timezone.now()
            self.save()
            logger.info("{} is confirmed".format(self))

    def has_been_confirmed(self):
        return self.confirmation_time is not None
