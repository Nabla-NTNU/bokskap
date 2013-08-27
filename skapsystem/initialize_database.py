# -*- coding: utf-8 -*-
from django.core.management import setup_environ
import skapsystem.settings
setup_environ(skapsystem.settings)

from locker.models import *



rooms = (("CU1-111", 664), ("CU2-021", 150), ("EU1-110", 185) )

for room,num_lockers in rooms:
   for locker_number in xrange(1,num_lockers+1):
       l = Locker.objects.get_or_create(room = room, locker_number = locker_number)

