from django import forms
from locker.models import *

class UserForm(forms.Form):
    username = forms.CharField(max_length=30, required=True, label='NTNU-brukernavn')
    first_name = forms.CharField(max_length=30, required=True, label='Fornavn')
    last_name = forms.CharField(max_length=30, required=True, label='Etternavn')


class LockerSearchForm(forms.Form):
    room = forms.ChoiceField(choices = Locker.ROOMS)
    locker_number = forms.IntegerField()
