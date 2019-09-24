"""
Forms for locker
"""
from django import forms
from django.contrib.auth.models import User
from .models import Locker, Ownership
from .utils import send_unregister_confirmation


class UserForm(forms.Form):
    """
    Validate user registration
    """
    username = forms.CharField(max_length=30, required=True, label='NTNU-brukernavn')

    def clean_username(self):
        """
        Make sure the user supplies a valid NTNU-username and not an email-address.

        There has been a lot users writing their ntnu-email-address instead of their username.
        """
        username = self.cleaned_data['username']
        if "@" in username:
            raise forms.ValidationError(
                "Dette ser ut som en epostadresse, men du ble bedt om NTNU-Brukernavn!")
        if not username.isalnum():
            raise forms.ValidationError(
                "Gyldige NTNU-brukernavn består kun av bokstaver og tall.")
        return username


class LockerSearchForm(forms.Form):
    """Skjema for å velge et skap."""

    room = forms.ChoiceField(choices=Locker.ROOMS, required=True, label="Rom")
    locker_number = forms.IntegerField(required=True, label="Skapnummer")
    locker = None

    def clean(self):
        print("LockerSearchForm clean")
        cleaned_data = super().clean()

        try:
            room = cleaned_data['room']
            number = cleaned_data['locker_number']
            self.locker = Locker.objects.get(room=room, locker_number=number)
        except Locker.DoesNotExist:
            raise forms.ValidationError("Dette skapet finnes ikke!")
        except KeyError:
            pass

        return cleaned_data


class LockerRegistrationForm(UserForm, LockerSearchForm):
    """Combined form for user and locker"""
    def clean(self):
        cleaned_data = super().clean()
        if self.locker.is_registered():
            raise forms.ValidationError(
                "Skapet er allerede i bruk. Velg et annet skap.")
        return cleaned_data


class UsernameForm(forms.Form):
    """Skjema for å skjekke om et brukernavn finnes."""
    username = forms.CharField(max_length=30, required=True,
                               label='NTNU-brukernavn')

    def clean(self):
        print("UsernameForm")
        cleaned_data = super().clean()
        username = cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(f'Brukeren {username} finnes ikke i skapdatabasen.')
        return cleaned_data


class LockerUnregistrationForm(UsernameForm, LockerSearchForm):
    """Form for unregistering lockers"""
    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data['username']
        user = User.objects.get(username=username)
        ownerships = Ownership.objects.filter(user=user, time_unreserved=None)
        lockers = []
        for l in ownerships:
            lockers.append(l.locker)
        if not self.locker in lockers:
            raise forms.ValidationError(
                "Dette skapet er ikke registrert på dette brukernavnet.")
        return cleaned_data


    def send_mail(self):
        cd = self.clean()
        username = cd['username']
        locker = self.locker
        user = User.objects.get(username=username)
        send_unregister_confirmation(user, locker)



