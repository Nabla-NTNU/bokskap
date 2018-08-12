import logging

from django.core.management.base import BaseCommand
from locker.models import Locker

logger = logging.getLogger(__name__)

class Command (BaseCommand):
    help = "Avregistrere samtlige skap, og sender mail til alle brukere der deres skap kan registreres på nytt"

    def handle(self, *args, **options):
        lockers = Locker.objects.all()
        for locker in lockers:
            locker.reset()
            logger.debug(f"Reset locker ({locker.room}, {locker.locker_number})")
            
        logger.info(f"Reset all lockers")
