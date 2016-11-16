from django.core.management.base import BaseCommand, CommandError
from locker.models import *
from locker import utils



class Command (BaseCommand):
    help = "Avregistrert samtlige skap, og sender mail til alle brukere om at disse trengs å reaktiveres"


    def handle(self):
        lockers = Locker.objects.all()
        for locker in lockers:
            locker.unregister()

            request = RegistrationRequest.objects.create(
                locker=locker,
                username=locker.owner.username,
                first_name = locker.owner.first_name,
                last_name = locker.owner.las_name)

            c= {
                "confirmation_url": utils.get_confirmation_url(request.token),
                "room": locker.room,
                "locker_number": locker.locker_number
            }

            subject = "Registrirere skap på nytt på nytt for neste semester"

            email = request.get_email()

            utils.send_template_email("locker_reset.html", c, subject, [email])


