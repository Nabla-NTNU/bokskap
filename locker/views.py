"""
Views for locker app
"""
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


MAX_LOCKERS_PER_USER = 2


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
        self.messages.info(f'En liste over dine skap har blitt sendt til {user.email}')
        return redirect("index_page")


def view_locker(request, room, locker_number):
    """"
    Redirects to the locker registration view

    it is unnecessary and should be refactored away.
    """
    the_view = LockerRegistrationView.as_view(
        initial={'room': room, 'locker_number': locker_number})
    return the_view(request)


class LockerRegistrationView(MessageMixin, FormView):
    """View for showing the locker registration page and the posting the request"""
    template_name = "locker/locker_registration.html"
    form_class = LockerRegistrationForm

    def form_valid(self, form):
        username = form.cleaned_data["username"]
        user, created = User.objects.get_or_create(username=username)

        if created or not user.email:
            user.email = stud_email_from_username(user.username)
            user.save()
        max_lockers = MAX_LOCKERS_PER_USER
        if User.objects.filter(ownership__user=user,
                               ownership__time_unreserved=None).count() >= max_lockers:
            self.messages.error(
                f'{user.username} har nådd maksgrensen på {max_lockers} skap.')
            logger.info("%s tried to register more than max lockers (%d)", user, max_lockers)
        else:
            reg = RegistrationRequest.objects.create_from_data(form.cleaned_data)
            reg.send_confirmation_email(request=self.request)
            self.messages.error( # Error for color in bootstrap
                f'En bekreftelsesepost er sendt til {reg.get_email()}. ' +
                'Husk å bekrefte eposten som nå er sendt, hvis ikke så gjelder ikke reserveringen!')

        return redirect("index_page")


class RegistrationConfirmation(MessageMixin, TemplateView):
    """Process the confirmation"""
    template_name = "locker/confirm.html"

    def get_request(self):
        """Get the registration request object corresponding to the key"""
        return get_object_or_404(
            RegistrationRequest,
            confirmation_token=self.kwargs["key"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["regreq"] = self.get_request()
        return context

    def get(self, request, *args, **kwargs):
        """Process get request"""
        regreq = self.get_request()
        regreq.confirm()
        number = regreq.locker.locker_number
        room = regreq.locker.room
        username = regreq.username
        self.messages.info(
            f'Skap nummer {number} i rom {room} er nå registrert på {username}'
        )
        return super().get(request, **kwargs)


class UserList(PermissionRequiredMixin, ListView):
    """
    View to list all user with with list of all lockers that user uses.
    """
    model = User
    template_name = "locker/user_list.html"
    permission_required = "locker.add"
