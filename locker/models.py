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


class LockerReservedException(Exception):
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

    def register(self, user):
        Ownership.objects.create_ownership(locker=self, user=user)

    def unregister(self):
        self.ownership.unregister()

    def reset(self):
        self.ownership.reset()
            
    def is_registered(self):
        return bool(self.ownership)

    @property
    def ownership(self):
        return Ownership.objects.filter(locker=self, time_unreserved=None).first()
    
    @property
    def owner(self):
        return self.ownership.user
    
    def __str__(self):
        return "({0.room}, {0.locker_number}) ".format(self)


class OwnershipManager(models.Manager):
    def create_ownership(self, locker, user):
        if locker.is_registered():
            raise LockerReservedException(f"{locker} is allready reserved")

        ownership = self.create(locker=locker, user=user, time_reserved = timezone.now())
        send_locker_is_registered_email(user.username, locker)
        logger.info(f"{locker} is now registered to {user}")
        return ownership
        
    
class Ownership(models.Model):
    locker = models.ForeignKey(Locker, blank=False, null=False, verbose_name="Skap", on_delete=models.CASCADE) # Locker and user should not be deletd, but CASCADE just in case.
    user = models.ForeignKey(User, blank=False, null=False, verbose_name="Bruker", on_delete=models.CASCADE)
    time_reserved = models.DateTimeField(blank=False, null=True)
    
    time_unreserved = models.DateTimeField(blank=True, null=True) # Locker is active until unreserved

    objects = OwnershipManager()

    class Meta:
        verbose_name = "Eierforhold"
        verbose_name_plural = "Eierforhold"

    def unregister(self):
        self.time_unreserved = timezone.now()
        self.save()

    def reset(self):
        """
        Avregistrer et skap og sender mail hvor det kan registreres på nytt
        """
        request = RegistrationRequest.objects.create(
            locker=self.locker,
            username=self.user.username,
            first_name=self.user.first_name,
            last_name=self.user.last_name)

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
        
        if created:
            user.first_name=self.first_name
            user.last_name=self.last_name
            user.save()
        
        try:
            self.locker.register(user)
        except LockerReservedException as e:
            logger.info(str(e))
            raise e
        
        self.confirmation_time = timezone.now()
        self.save()
        logger.info("{} is confirmed".format(self))

    def has_been_confirmed(self):
        return self.confirmation_time is not None
