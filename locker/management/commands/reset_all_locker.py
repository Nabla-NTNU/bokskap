"""Reset all lockers"""
import logging
from datetime import timedelta

from django.utils import timezone
from django.core.management.base import BaseCommand
from locker.models import Ownership


class Command(BaseCommand):
    """Management command for resetting all active lockers"""
    help = ("Avregistrere samtlige skap, "
            "og sender mail til alle brukere der deres skap kan registreres paa nytt")

    def handle(self, *args, **options):
        ownerships = Ownership.objects.filter(time_unreserved=None)
        logger = logging.getLogger(__name__)

        print("Deregister all lockers and send mail to owners with link to re-register.")
        print("Reserves lockers for previous owner for 14 days.")

        reservation_expiry_date = timezone.now() + timedelta(days=14)

        for ownership in ownerships:
            ownership.reset(reserved=True, reserved_expiry_date=reservation_expiry_date)
            logger.debug("Reset %s, which was owned by %s",
                         ownership.locker, ownership.user)

        logger.info("%s ownerships was reset", len(ownerships))
