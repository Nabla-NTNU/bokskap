import logging

from django.core.management.base import BaseCommand
from locker.models import Locker, Ownership

logger = logging.getLogger(__name__)

class Command (BaseCommand):
    help = "Avregistrere samtlige skap, og sender mail til alle brukere der deres skap kan registreres på nytt"

    def handle(self, *args, **options):
        ownerships = Ownership.objects.filter(time_unreserved=None)
        
        if(len(ownerships) == 0):
            logger.info("No ownerships to reset")
            return

        for ownership in ownerships:
            ownership.reset()
            logger.debug(f"Reset {ownership.locker}, which was owned by {ownership.user}")

        logger.info(f"Reset {len(ownerships)} ownerships")
       
