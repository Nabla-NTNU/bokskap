from django.db import models

class Locker(models.Model):

    ROOMS = (
        ('CU1-111', 'CU1-111'),
        ('CU2-021', 'CU2-021'),
        ('EU1-110', 'EU1-110')
    )
    room = models.CharField(max_length = 10, choices = ROOMS, blank = False)
    locker_number = models.CharField(max_length = 1000, blank = False)
    owner = models.OneToOneField(User, blank = False)
    date_reserved = models.DateField(blank = False)
    
    class Meta:
        unique_together = ('room', 'locker_number',)


class InactiveLockerReservation(models.Model):
    date_reserved = models.DateField(blank = False)
 # Datoen enten brukeren avregistrerte skapet eller Nabla klippet opp l√sen og fjernet innholdet.
    date_unreserved = models.DateField(blank = False) 
    lock_cut = models.BooleanField(blank = False) # Indikerer om l√sen p√ •skapet ble klippet av Nabla
    owner = models.ForeignKey(User, blank = False)
    locker = models.ForeignKey(Locker, blank = False)

    

class User(models.Model):
    ntnu_username = models.CharField(max_length = 10, unique = True, blank = False)
    first_name = models.CharField(max_length = 30, blank = False)
    last_name = models.CharField(max_length = 30, blank = False)
    telephone = models.CharField(max_length = 15, blank = True)
