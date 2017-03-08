from django.core.management.base import BaseCommand
from locker.models import Locker


class Command (BaseCommand):
    help = "Avregistrere samtlige skap, og sender mail til alle brukere der deres skap kan registreres på nytt"

    def handle(self):
        lockers = Locker.objects.all()
        for locker in lockers:
            locker.reset()
