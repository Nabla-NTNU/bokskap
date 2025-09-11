"""
Utility functions for locker app
"""
import string
import random
import logging
import hashlib

from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.html import strip_tags

FROM_EMAIL_ADDRESS = "bokskap@nabla.no"


def send_template_email(template, context, subject, emails):
    """Send email using a django-template"""
    from_email = FROM_EMAIL_ADDRESS

    html_content = render_to_string(template, context)
    text_content = strip_tags(html_content)

    send_mail(
        subject=subject,
        message=text_content,
        from_email=from_email,
        recipient_list=emails,
        html_message=html_content,
    )


def encrypt_string(hash_string):
    sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature


def send_unregister_confirmation(user, locker):
    from .models import Ownership
    '''Sends an email with confirmation link to unregister locker'''
    ownership_id = Ownership.objects.get(user=user, locker=locker, time_unreserved=None).id
    ownership_time = Ownership.objects.get(user=user, locker=locker,time_unreserved=None).time_reserved
    sha_string = str(ownership_id) + str(ownership_time)
    sha_id = encrypt_string(sha_string)
    subject = f'Avregistreringsbekreftelse skap {locker}'
    context = {'locker': locker, 'name':user.get_full_name(), 'sha_id': sha_id}
    send_template_email('email/locker_unregistration.html', context, subject, [user.email])


def send_locker_reminder(user):
    from .models import Ownership
    """Sender på epost med info om hvilke skap brukeren har."""
    subject = f'Liste over bokskap tilhørende {user.get_full_name()}'
    ownerships = Ownership.objects.filter(user=user, time_unreserved=None)
    context = {'ownerships': ownerships}
    send_template_email('email/locker_reminder.html', context, subject, [user.email])


def send_confirmation_email(email, locker, confirmation_token, request=None):
    """Sender bekfreftelsesepost til brukeren som prøvde å registrere seg."""
    subject = f'Fullfør registringen av skap {locker.locker_number} i {locker.room}'
    confirmation_url = get_confirmation_url(confirmation_token, request=request)

    context = {
        "confirmation_url": confirmation_url,
        "room": locker.room,
        "locker_number": locker.locker_number
    }
    send_template_email('email/confirmation_email.html', context, subject, [email])


def send_locker_is_registered_email(username, locker):
    """Send email telling user that the locker is now registered to them"""
    subject = f'Skap {locker.locker_number} i {locker.room} er nå registrert på {username}'
    message = render_to_string("email/registration_has_been_confirmed.txt", context=locals())
    email = stud_email_from_username(username)
    send_mail(subject, message, FROM_EMAIL_ADDRESS, [email])
    logging.getLogger(__name__).info("Sent registration confirmed email to %s", email)


def get_confirmation_url(token, request=None):
    """
    Return

    :param token: The confirmation token to be used in the url
    :param request: Optional HttpRequest-object to get the currently used absolute_uri.
                    Used mostly for testing-purposes when the absolute url
                    is not the production url.
    :return: The abosulte url for confirming the locker_registration.
    """
    relative_url = reverse('registration_confirmation', kwargs={'key': token})
    if request is not None:
        return request.build_absolute_uri(relative_url)
    return f"http://{Site.objects.get_current().domain}{relative_url}"


def random_string(length=20, alphabet=string.ascii_letters+string.digits):
    """Return random string from given alphabet of characters"""
    return "".join(random.choice(alphabet) for _ in range(length))


def stud_email_from_username(username):
    """Get the corresponding student email address from the username"""
    return f"{username}@stud.ntnu.no"
