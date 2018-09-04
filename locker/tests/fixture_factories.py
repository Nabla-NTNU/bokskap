import factory
from locker.models import Locker, RegistrationRequest

import faker
fake = faker.Faker("no_NO")


class LockerFactory(factory.DjangoModelFactory):
    class Meta:
        model = Locker

    locker_number = factory.Sequence(lambda n: n+1)
    room = Locker.ROOMS[0][0]


def fake_user_dict():
    udict = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }
    udict["username"] = udict["first_name"][:3].lower() + udict["last_name"][:3].lower()
    return udict


def fake_locker_registration_post_request():
    data = fake_user_dict()
    unused_locker = Locker.objects.filter(ownership__isnull=True).first()
    data['room'] = unused_locker.room
    data['locker_number'] = unused_locker.locker_number
    return data
