import random
import hashlib

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Locker


def send_template_email(template_folder, context, subject, emails):
    from_email = 'ikke_svar@nabla.ntnu.no'

    html_content = render_to_string(template_folder, context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, emails)
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_locker_reminder(user):
    """Sender på epost med info om hvilke skap brukeren har."""
    subject = u'Liste over bokskap tilhørende %s' % (user.get_full_name())
    c = {'lockers': user.locker_set.all()}
    send_template_email('email/locker_reminder.html', c, subject, [user.email])


def send_confirmation_email(user, locker, confirmation_token):
    """Sender bekfreftelsesepost til brukeren som prøvde å registrere seg."""

    subject = ('Bekreftelse av reservasjon av skap {} i {}'
               .format(locker.locker_number, locker.room))
    confirmation_url = 'http://bokskap.nabla.no' + reverse('registration_confirmation',
                                                           kwargs={'key': confirmation_token})

    c = {
            "confirmation_url": confirmation_url,
            "room": locker.room,
            "locker_number": locker.locker_number
        }
    send_template_email('email/confirmation_email.html', c, subject, [user.email])


def create_confirmation_token(locker, post_data):
    """Lager en bekreftelsesnøkkel.

    Mellomlagrer også skapregistreringsinformasjonen."""

    confirmation_token = hashlib.md5(str(random.random()).encode()).hexdigest()
    the_data = {'post_data': post_data,
                'room': locker.room,
                'locker_number': locker.locker_number,
                }

    cache.set(confirmation_token, the_data, None)
    return confirmation_token


def save_locker_registration(token):
    """Tar i mot bekreftelsesnøkkel og lagrer skapregistreringen."""
    the_data = cache.get(token)
    if the_data is None:
        raise KeyError

    post_data = the_data['post_data']
    room = the_data['room']
    locker_number = the_data['locker_number']

    locker = get_object_or_404(Locker, room=room, locker_number=locker_number)

    user = User.objects.get(username=post_data['username'])
    user.first_name = post_data['first_name']
    user.last_name = post_data['last_name']
    user.save()
    locker.reserve(user)
    return user, locker
