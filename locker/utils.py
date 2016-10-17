import string

import random
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site
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
    else:
        site = Site.objects.get_current()
        return "http://{}{}".format(site.domain, relative_url)


def random_string(length=20, alphabet=string.ascii_letters+string.digits):
    return "".join(random.choice(alphabet) for _ in range(length))


def stud_email_from_username(username):
    return "{}@stud.ntnu.no".format(username)
