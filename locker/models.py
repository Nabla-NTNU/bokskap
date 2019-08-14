"""
Models for locker app
"""
import logging

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

from .utils import (random_string, stud_email_from_username,
                    send_confirmation_email, send_locker_is_registered_email,
                    get_confirmation_url, send_template_email)


logger = logging.getLogger(__name__)


class LockerManager(models.Manager):
    """Locker manager"""
    def get_from_post_data(self, data):
        """Get a specific locker from the data posted by the user"""
        return self.get(room=data["room"], locker_number=data["locker_number"])


class LockerReservedException(Exception):
    """Exception to be raised if a locker has already been reserved"""


class Locker(models.Model):
    """Model representing one of the lockers in the system"""

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
        """"
        Register locker to user

        Raises LockerReservedException if locker already registered.
        """
        Ownership.objects.create_ownership(locker=self, user=user)

    def unregister(self):
        """Make locker not owned by anyone"""
        self.ownership.unregister()

    def reset(self):
        """
        Unregister locker and send email to previous owner

        If the locker is not registered, do nothing.
        """
        if self.is_registered():
            self.ownership.reset()

    def is_registered(self):
        """Return whether the locker has a owner"""
        return bool(self.ownership)

    def is_reserved(self):
        """Returns True if there exists a RegistrationRequest
        with reserved=True and where the reserved expiry date has not passed"""
        is_reserved = RegistrationRequest.objects.filter(
            locker=self,
            reserved=True,
            reserved_expiry__gte=timezone.now()).exists()
        return is_reserved

    def is_registered_or_reserved(self):
        """Returns whether the locker is busy in any way,
        that is if it has an active owner or an
        active RegistrationRequest"""
        return self.is_registered() or self.is_reserved()

    @property
    def ownership(self):
        """"Return current active ownership object"""
        return Ownership.objects.filter(locker=self, time_unreserved=None).first()

    @property
    def owner(self):
        """Return the current owner of the locker"""
        return self.ownership.user

    def __str__(self):
        return f"({self.room}, {self.locker_number}) "


class OwnershipManager(models.Manager):
    """Custom manager for Ownwership model"""
    def create_ownership(self, locker, user):
        """
        Create an active ownership given locker and user

        Raises exception if locker is already registered to somebody.
        Sends email to the new owner.
        """
        if locker.is_registered():
            raise LockerReservedException(f"{locker} is already reserved")

        ownership = self.create(locker=locker, user=user, time_reserved=timezone.now())
        send_locker_is_registered_email(user.username, locker)
        logger.info("%s is now registered to %s", locker, user)
        return ownership


class Ownership(models.Model):
    """
    Model representing a registration of a locker.

    It can be either active or inactive.
    The inactive ownerships are saved to keep track of who used which lockers in the past.
    """
    locker = models.ForeignKey(
        Locker,
        blank=False,
        null=False,
        verbose_name="Skap",
        on_delete=models.CASCADE)
    user = models.ForeignKey(User, blank=False, null=False,
                             verbose_name="Bruker", on_delete=models.CASCADE)
    time_reserved = models.DateTimeField(blank=False, null=True)

    # Locker is active until unreserved
    time_unreserved = models.DateTimeField(blank=True, null=True)

    objects = OwnershipManager()

    class Meta:
        verbose_name = "Eierforhold"
        verbose_name_plural = "Eierforhold"

    def unregister(self):
        """Make ownership inactive"""
        if self.is_active():
            self.time_unreserved = timezone.now()
            self.save()

    def is_active(self):
        """Is the ownership active"""
        return self.time_unreserved is None

    def reset(self, reserved=False, reserved_expiry_date=timezone.now()):
        """
        Avregistrer et skap og sender mail hvor det kan registreres på nytt
        """
        request = RegistrationRequest.objects.create(
            locker=self.locker,
            username=self.user.username,
            reserved=reserved,
            reserved_expiry=reserved_expiry_date)

        self.unregister()

        context = {
            "confirmation_url": get_confirmation_url(request.confirmation_token),
            "room": self.locker.room,
            "locker_number": self.locker.locker_number
        }

        subject = "Registrere skap på nytt for neste semester"
        email = request.get_email()
        send_template_email("email/locker_reset.html", context, subject, [email])


class RegistrationRequestManager(models.Manager):
    """Custom manager for RegistrationRequest"""
    def create_from_data(self, data):
        """Create RegistrationRequest from validated user data"""
        return self.create(
            locker=Locker.objects.get_from_post_data(data),
            username=data['username'],
        )


class RegistrationRequest(models.Model):
    """
    Model representing a user's request for a locker
    """
    confirmation_token = models.CharField(max_length=20, unique=True, blank=True, null=True)
    creation_time = models.DateTimeField(
        verbose_name="Tidspunktet skapet ble forsøkt registrert.",
        auto_now_add=True)

    locker = models.ForeignKey(
        Locker,
        verbose_name="Skap",
        blank=False,
        on_delete=models.CASCADE)
    username = models.CharField("Brukernavn", max_length=30, blank=False)

    """Sometimes one wishes to reserve a locker for a user,
    for example when deregistering all lockers at the beginning of the year,
    so that no other user can take this locker for some period of time.

    We do this by creating a RegistrationRequest with `reserved=True`.
    These will then be reserved until `reserved_expiry`
    """
    reserved = models.BooleanField("Er reservert", default=False)
    reserved_expiry = models.DateTimeField(
        verbose_name="Utløp av reservasjonsperioden, normalt 14 dager etter creation_time",
        default=timezone.now)

    confirmation_time = models.DateTimeField(
        verbose_name="Tidspunktet forspørselen ble bekreftet", null=True, blank=True)

    objects = RegistrationRequestManager()

    class Meta:
        verbose_name = "Skapforespørsel"
        verbose_name_plural = "Skapforespørsler"

    def __str__(self):
        return f"{self.username} forespør {self.locker}"

    def save(self, **kwargs): #pylint: disable=W0221
        if self.confirmation_token is None:
            self.confirmation_token = random_string()
            logger.info("RegistrationRequest created: <%s>", self)
        super().save(**kwargs)

    def get_email(self):
        """Return ntnu-student email-address of username in request"""
        return stud_email_from_username(self.username)

    def send_confirmation_email(self, request=None):
        """Send email with link to """
        email = self.get_email()
        send_confirmation_email(email, self.locker, self.confirmation_token, request=request)
        logger.info("Confirmation mail sent to %s for locker: %s", email, self.locker)

    def confirm(self):
        """
        Confirm request and register the locker to the user

        If the request is already confirmed
        """
        if self.has_been_confirmed():
            return
        user, created = User.objects.get_or_create(username=self.username)

        try:
            self.locker.register(user)
        except LockerReservedException as ex:
            logger.info(str(ex))
            raise ex

        self.confirmation_time = timezone.now()
        self.save()
        logger.info("%s is confirmed", self)

    def has_been_confirmed(self):
        """Return if the request has been confirmed"""
        return self.confirmation_time is not None
