# -*- coding: utf-8 -*-
import random
import hashlib

from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.template import Context
from django.template.loader import get_template, render_to_string
from django.utils.html import strip_tags
from django.views.generic import ListView, FormView

from locker.models import *
from locker.forms import *


class IndexPage(FormView):
    """Viser forsiden og tar seg av valg av skap.

    Hvis skapet finnes blir man sendt til registreringsiden til det skapet.
    """
    template_name = "locker/index.html"
    form_class = LockerSearchForm

    def form_valid(self, form):
        room = form.cleaned_data['room']
        number = form.cleaned_data['locker_number']
        return redirect(view_locker, room=room, locker_number=number)


class LockerRoomView(ListView):
    context_object_name = "lockers"

    def get_queryset(self):
        room = self.kwargs['room']
        return Locker.objects.filter(room=room).order_by('locker_number')


def send_locker_reminder(user):
    """Sender på epost med info om hvilke skap brukeren har."""

    subject = u'Liste over bokskap tilhørende %s' % (user.get_full_name())
    from_email = 'ikke_svar@nabla.ntnu.no'
    lockers = user.locker_set.all()

    c = Context({'lockers':lockers})
    html_content = render_to_string('email/locker_reminder.html',c)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


class LockerReminder(FormView):
    """View for å vise et skjema for påminnelse om skapnummer.

    Bruker UsernameForm for å skjekke om brukeren finnes for deretter å sende epost til brukeren.
    """
    template_name = "locker/forgotten_lockers.html"
    form_class = UsernameForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        user = User.objects.get(username=username)
        send_locker_reminder(user)
        messages.add_message(self.request, messages.INFO, u'En liste over dine skap har blitt sendt til %s' % user.email)
        return redirect("index_page")


def send_confirmation_email(user, locker, confirmation_key):
    confirmation_url = 'http://bokskap.nabla.no'+reverse(registration_confirmation, kwargs={'key': confirmation_key})
    subject = 'Bekreftelse av reservasjon av skap %s i %s' % (locker.locker_number, locker.room)
    from_email = 'ikke_svar@nabla.ntnu.no'

    c = Context({"confirmation_url": confirmation_url,
                 "room": locker.room,
                 "locker_number": locker.locker_number
                 })
    html_content = render_to_string('email/confirmation_email.html', c)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


class LockerRegistrationView(FormView):
    template_name = "locker/locker_registration.html"
    form_class = LockerRegistrationForm

    def form_valid(self, form):
        locker = form.locker
        username = form.cleaned_data["username"]
        user, created = User.objects.get_or_create(username=username)

        if created or not(user.email):
            user.email = "%s@stud.ntnu.no" % user.username
            user.save()
        if user.locker_set.count() > 3 :
            messages.add_message(self.request, messages.ERROR, u'Beklager, men brukeren %s har nådd maksgrensen på tre skap.' % user.username)
        else:
            confirmation_key = create_confirmation_key(locker, self.request)
            send_confirmation_email(user, locker, confirmation_key)
            messages.add_message(self.request, messages.INFO, u'En bekreftelsesepost er sendt til %s' % user.email)

        return redirect("index_page")


def create_confirmation_key(locker, request):

    confirmation_key = hashlib.md5(str(random.random()).encode()).hexdigest()
    request.session['confirmation_key'] = confirmation_key

    request.session['post_data'] = request.POST
    request.session['room'] = locker.room
    request.session['locker_number'] = locker.locker_number
    return confirmation_key


def get_user_and_locker_from_key(key, request):
    try:
        confirmation_key = request.session['confirmation_key']
    except KeyError:
        raise Http404
    if key != confirmation_key:
        raise Http404

    post_data = request.session['post_data']
    locker = get_object_or_404(Locker, room=request.session['room'], locker_number=request.session['locker_number'])
    user = User.objects.get(username = post_data['username'])
    user.first_name = post_data['first_name']
    user.last_name = post_data['last_name']
    return user, locker


def view_locker(request, room, locker_number):
    the_view = LockerRegistrationView.as_view(initial={'room': room, 'locker_number': locker_number})
    return the_view(request)


def registration_confirmation(request, key):
    user, locker = get_user_and_locker_from_key(key, request)
    user.save()
    locker.reserve(user)
    messages.add_message(request, messages.INFO, u'Skap nummer %d i %s rom  er nå registrert på %s' % (locker.locker_number, locker.room, user.username))
    return redirect('/list/'+locker.room)
