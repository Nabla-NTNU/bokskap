from django import forms
from locker.models import *

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
            l = Locker.objects.get(room=room, locker_number=number)
        except Locker.DoesNotExist:
            raise forms.ValidationError("Dette skapet finnes ikke!")
        except KeyError:
            pass

        return cleaned_data
