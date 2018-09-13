"""
Management command to create locker-objects corresponding to all lockers
handled by Nabla in Realfagbygget.
"""
from django.core.management.base import BaseCommand
from locker.models import Locker


class Command(BaseCommand):
    """Create all lockers in Realfagbygget"""
    args = "no args"
    help = "Creates all lockers"
    rooms = (("CU1-111", 664), ("CU2-021", 150), ("EU1-110", 185))

    def handle(self, *args, **options):
        Locker.objects.bulk_create(
            Locker(room=room, locker_number=locker_number)
            for room, num_lockers in self.rooms
            for locker_number in range(1, num_lockers+1)
        )
        print("Created the lockers")
