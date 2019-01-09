"""
Utility code for creating valid data for the tests
"""
import factory
import faker
from locker.models import Locker

fake = faker.Faker("no_NO")


class LockerFactory(factory.DjangoModelFactory):
    """Factory for easily creating lockers in testing code"""
    class Meta:
        model = Locker

    locker_number = factory.Sequence(lambda n: n+1)
    room = Locker.ROOMS[0][0]


def fake_user_dict():
    """Make a dictionary of user info to be used for testing"""

    # Even though the first and last name of users has been removed, this is a good way to generate usernames.
    udict = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
    }
    udict["username"] = udict["first_name"][:3].lower() + udict["last_name"][:3].lower()
    return udict


def fake_locker_registration_post_request():
    """Make a valid locker registration request to be used for testing"""
    data = fake_user_dict()
    unused_locker = Locker.objects.filter(ownership__isnull=True).first()
    data['room'] = unused_locker.room
    data['locker_number'] = unused_locker.locker_number
    return data
