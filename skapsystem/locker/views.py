# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect
from django.views.generic import ListView, FormView

from .models import *
from .forms import *
from .utils import *


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
    """Viser alle skapene i et rom."""
    context_object_name = "lockers"

    def get_queryset(self):
        room = self.kwargs['room']
        return Locker.objects.filter(room=room).order_by('locker_number')


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


def view_locker(request, room, locker_number):
    the_view = LockerRegistrationView.as_view(initial={'room': room, 'locker_number': locker_number})
    return the_view(request)


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
            token = create_confirmation_token(locker, self.request.POST)
            send_confirmation_email(user, locker, token)
            messages.add_message(self.request, messages.INFO, u'En bekreftelsesepost er sendt til %s' % user.email)

        return redirect("index_page")


def registration_confirmation(request, key):
    try:
        user, locker = save_locker_registration(key)
    except KeyError:
        raise Http404
    messages.add_message(request, messages.INFO, u'Skap nummer %d i %s rom  er nå registrert på %s' % (locker.locker_number, locker.room, user.username))
    return redirect('/list/'+locker.room)
