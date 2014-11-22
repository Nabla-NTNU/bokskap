# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from locker.models import *

rooms = (("CU1-111", 664), ("CU2-021", 150), ("EU1-110", 185))


class Command(BaseCommand):
    args = "no args"
    help = "Creates all lockers"

    def handle(self, *args, **options):
        for room, num_lockers in rooms:
            for locker_number in range(1, num_lockers+1):
                l = Locker.objects.get_or_create(room=room,
                                                 locker_number=locker_number)
        print("Created the lockers")
