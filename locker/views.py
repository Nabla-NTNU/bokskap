# -*- coding: utf-8 -*-
import logging

from django.contrib.auth.models import User
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, FormView, TemplateView

from braces.views import MessageMixin

from .models import Locker, RegistrationRequest
from .forms import LockerSearchForm, UsernameForm, LockerRegistrationForm
from .utils import send_locker_reminder, stud_email_from_username

logger = logging.getLogger(__name__)


MAX_LOCKERS_PER_USER = 3


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


class LockerReminder(MessageMixin, FormView):
    """View for å vise et skjema for påminnelse om skapnummer.

    Bruker UsernameForm for å skjekke om brukeren finnes
    for deretter å sende epost til brukeren.
    """
    template_name = "locker/forgotten_lockers.html"
    form_class = UsernameForm

    def form_valid(self, form):
        username = form.cleaned_data['username']
        user = User.objects.get(username=username)
        send_locker_reminder(user)
        self.messages.info('En liste over dine skap har blitt sendt til {}'.format(user.email))
        return redirect("index_page")


def view_locker(request, room, locker_number):
    the_view = LockerRegistrationView.as_view(
        initial={'room': room, 'locker_number': locker_number})
    return the_view(request)


class LockerRegistrationView(MessageMixin, FormView):
    template_name = "locker/locker_registration.html"
    form_class = LockerRegistrationForm

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        user, created = User.objects.get_or_create(username=username)

        if created or not user.email:
            user.email = stud_email_from_username(user.username)
            user.save()
        if user.locker_set.count() >= MAX_LOCKERS_PER_USER:
            self.messages.error(
                'Beklager, men brukeren {} har nådd maksgrensen på tre skap.'.format(user.username))
            logger.info("{} tried to register more than max lockers ({})".format(user, MAX_LOCKERS_PER_USER))
        else:
            reg = RegistrationRequest.objects.create_from_data(form.cleaned_data)
            reg.send_confirmation_email(request=self.request)
            self.messages.error('En bekreftelsesepost er sendt til %s. ' % reg.get_email() +  # Error for color in bootstrap
                                'Husk å bekrefte eposten som nå er sendt, hvis ikke så gjelder ikke reserveringen!')

        return redirect("index_page")


class RegistrationConfirmation(MessageMixin, TemplateView):
    template_name = "locker/confirm.html"

    def get_request(self):
        return get_object_or_404(
            RegistrationRequest,
            confirmation_token=self.kwargs["key"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["regreq"] = self.get_request()
        return context

    def post(self, request, **kwargs):
        regreq = self.get_request()
        regreq.confirm()
        locker = regreq.locker
        self.messages.info(
            'Skap nummer {} i rom {} er nå registrert på {}'.format(
                locker.locker_number,
                locker.room,
                locker.owner.username)
        )
        return redirect('list_lockers', room=locker.room)


class UserList(PermissionRequiredMixin, ListView):
    """
    View to list all user with with list of all lockers that user uses.
    """
    model = User
    template_name = "locker/user_list.html"
    permission_required = "locker.add"
