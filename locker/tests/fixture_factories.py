import factory
from locker.models import Locker


class LockerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Locker

    locker_number = factory.Sequence(lambda n: n+1)
    room = Locker.ROOMS[0][0]
