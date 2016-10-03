import random
import string

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags


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


def send_confirmation_email(email, locker, confirmation_token, request=None):
    """Sender bekfreftelsesepost til brukeren som prøvde å registrere seg."""

    subject = ('Bekreftelse av reservasjon av skap {} i {}'
               .format(locker.locker_number, locker.room))
    confirmation_url = get_confirmation_url(confirmation_token, request=request)

    c = {
            "confirmation_url": confirmation_url,
            "room": locker.room,
            "locker_number": locker.locker_number
        }
    send_template_email('email/confirmation_email.html', c, subject, [email])


def get_confirmation_url(token, request=None):
    """
    Return

    :param token: The confirmation token to be used in the url
    :param request: Optional HttpRequest-object to get the currently used absolute_uri.
                    Used mostly for testing-purposes when the absolute url is not the production url.
    :return: The abosulte url for confirming the locker_registration.
    """
    relative_url = reverse('registration_confirmation', kwargs={'key': token})
    if request is not None:
        return request.build_absolute_uri(relative_url)
    return 'http://bokskap.nabla.no' + relative_url


def create_confirmation_token(locker, post_data):
    """Lager en bekreftelsesnøkkel.

    Mellomlagrer også skapregistreringsinformasjonen."""

    confirmation_token = random_string()
    the_data = {'post_data': post_data,
                'room': locker.room,
                'locker_number': locker.locker_number,
                }

    cache.set(confirmation_token, the_data, None)
    return confirmation_token


def random_string(length=20, alphabet=string.ascii_letters+string.digits):
    return "".join(random.choice(alphabet) for _ in range(length))


def save_locker_registration(token):
    """Tar i mot bekreftelsesnøkkel og lagrer skapregistreringen."""
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


def stud_email_from_username(username):
    return "{}@stud.ntnu.no".format(username)
