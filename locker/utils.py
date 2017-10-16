import string
import random
import logging

from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.html import strip_tags


FROM_EMAIL_ADDRESS = "bokskap@nabla.ntnu.no"

logger = logging.getLogger(__name__)


def send_template_email(template, context, subject, emails):
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



def send_locker_reminder(ownerships):
    """Sender på epost med info om hvilke skap brukeren har."""
    user = ownerships[0].user
    subject = u'Liste over bokskap tilhørende %s' % (user.get_full_name())
    c = {'ownerships': ownerships}
    send_template_email('email/locker_reminder.html', c, subject, [user.email])


def send_confirmation_email(email, locker, confirmation_token, request=None):
    """Sender bekfreftelsesepost til brukeren som prøvde å registrere seg."""

    subject = ('Fullfør registringen av skap {} i {}'
               .format(locker.locker_number, locker.room))
    confirmation_url = get_confirmation_url(confirmation_token, request=request)

    c = {
        "confirmation_url": confirmation_url,
        "room": locker.room,
        "locker_number": locker.locker_number
    }
    send_template_email('email/confirmation_email.html', c, subject, [email])


def send_locker_is_registered_email(username, locker):
    subject = ('Skap {locker.locker_number} i {locker.room} er nå registrert på {username}'
               .format(**locals()))
    message = render_to_string("email/registration_has_been_confirmed.txt", context=locals())
    email = stud_email_from_username(username)
    send_mail(subject, message, FROM_EMAIL_ADDRESS, [email])
    logger.info("Sent registration confirmed email to {email}".format(**locals()))


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
    else:
        site = Site.objects.get_current()
        return "http://{}{}".format(site.domain, relative_url)


def random_string(length=20, alphabet=string.ascii_letters+string.digits):
    return "".join(random.choice(alphabet) for _ in range(length))


def stud_email_from_username(username):
    return "{}@stud.ntnu.no".format(username)
