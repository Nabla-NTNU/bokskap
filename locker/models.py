# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone as timezone


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

    class Meta:
        unique_together = ('room', 'locker_number',)

    def reserve(self, User):
        self.owner = User
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

    def __unicode__(self):
        return u'(%s , %s) ' % (self.room, self.locker_number)


class InactiveLockerReservation(models.Model):
    time_reserved = models.DateTimeField(blank=False)

    # Datoen enten brukeren avregistrerte skapet
    # eller Nabla klippet opp låsen og fjernet innholdet.
    time_unreserved = models.DateTimeField(blank=False)

    # Indikerer om låsen på skapet ble klippet av Nabla
    lock_cut = models.BooleanField(blank=False, default=False)

    owner = models.ForeignKey(User, blank=False)
    locker = models.ForeignKey(Locker, blank=False)

    def __unicode__(self):
        return u'(%s , %s) ' % (self.locker, self.owner)