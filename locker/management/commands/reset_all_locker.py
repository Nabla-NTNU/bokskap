"""Reset all lockers"""
import logging

from django.core.management.base import BaseCommand
from locker.models import Ownership


class Command(BaseCommand):
    """Management command for resetting all active lockers"""
    help = ("Avregistrere samtlige skap, "
            "og sender mail til alle brukere der deres skap kan registreres på nytt")

    def handle(self, *args, **options):
        ownerships = Ownership.objects.filter(time_unreserved=None)
        logger = logging.getLogger(__name__)

        for ownership in ownerships:
            ownership.reset()
            logger.debug("Reset %s, which was owned by %s",
                         ownership.locker, ownership.user)

        logger.info("%s ownerships was reset", len(ownerships))
