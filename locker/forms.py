from django import forms
from django.contrib.auth.models import User
from .models import *


class UserForm(forms.Form):
    username = forms.CharField(max_length=30, required=True, label='NTNU-brukernavn')
    first_name = forms.CharField(max_length=30, required=True, label='Fornavn')
    last_name = forms.CharField(max_length=30, required=True, label='Etternavn')


class LockerSearchForm(forms.Form):
    """Skjema for å velge et skap."""

    room = forms.ChoiceField(choices=Locker.ROOMS, required=True, label="Rom")
    locker_number = forms.IntegerField(required=True, label="Skapnummer")

    def clean(self):
        cleaned_data = super(LockerSearchForm, self).clean()

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

    def clean(self):
        cleaned_data = super(LockerRegistrationForm, self).clean()
        if self.locker.is_reserved():
            raise forms.ValidationError(
                "Skapet er allerede i bruk. Velg et annet skap.")
        return cleaned_data


class UsernameForm(forms.Form):
    "Skjema for å skjekke om et brukernavn finnes."
    username = forms.CharField(max_length=30, required=True,
                               label='NTNU-brukernavn')

    def clean(self):
        cleaned_data = super(UsernameForm, self).clean()
        try:
            username = cleaned_data['username']
            u = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(
                'Brukeren {} finnes ikke i skapdatabasen.'.format(username))
        except KeyError:
            pass
        return cleaned_data
