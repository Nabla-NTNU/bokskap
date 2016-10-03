"""
The previous way of confirming locker registrations was to save
them in the cache. This has been made obsolete by a new model called RegistrationRequest,
but the old way is kept here while migrating over to the new way.
"""

from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import get_object_or_404

from locker.utils import random_string


def create_confirmation_token(locker, post_data):
    """Lager en bekreftelsesnøkkel ved hjelp av gammel metode.

    Mellomlagrer også skapregistreringsinformasjonen.
    TODO: Fjern denne når det nye systemet har vært i bruk en stund.
    """

    confirmation_token = random_string()
    the_data = {'post_data': post_data,
                'room': locker.room,
                'locker_number': locker.locker_number,
                }

    cache.set(confirmation_token, the_data, None)
    return confirmation_token


def save_old_registration(token):
    """Tar i mot gammel bekreftelsesnøkkel fra gammel metode og lagrer skapregistreringen."""
    the_data = cache.get(token)
    if the_data is None:
        raise KeyError

    post_data = the_data['post_data']
    room = the_data['room']
    locker_number = the_data['locker_number']

    from .models import Locker

    locker = get_object_or_404(Locker, room=room, locker_number=locker_number)

    user = User.objects.get(username=post_data['username'])
    user.first_name = post_data['first_name']
    user.last_name = post_data['last_name']
    user.save()
    locker.reserve(user)
    return user, locker
