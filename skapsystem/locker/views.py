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
from django.views.generic import ListView

from locker.models import *
from locker.forms import *


def index_page(request):
    if request.method == "POST":
        form = LockerSearchForm(request.POST)
        if form.is_valid() and Locker.objects.filter(room=form.data['room'],locker_number=form.data['locker_number']).exists():
            return redirect(register_locker, room=form.data['room'], locker_number = form.data['locker_number'])
    else:
        form = LockerSearchForm()
    context = {'lockerSearchForm': form}
    return render(request, 'index.html',context)


class LockerListView(ListView):
    context_object_name = "lockers"

    def get_queryset(self):
        room = self.kwargs['room']
        return Locker.objects.filter(room=room).order_by('locker_number')


def locker_reminder(request):
    if request.method == 'POST':
        username = request.POST['username']
        try:
            user = User.objects.get(username=username)
            subject = u'Liste over bokskap tilhørende %s' % (user.get_full_name())
            from_email = 'ikke_svar@nabla.ntnu.no'
            lockers = user.locker_set.all()

            c = Context({'lockers':lockers})
            html_content = render_to_string('email/locker_reminder.html',c)
            text_content = strip_tags(html_content)

            msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            messages.add_message(request, messages.INFO, u'En liste over dine skap har blitt sendt til %s' % user.email)
        except User.DoesNotExist:
            messages.add_message(request, messages.INFO, u'Brukeren {} finnes ikke i skapdatabasen.'.format(username))

    return render(request, 'forgotten_lockers.html')


def register_locker(request, room, locker_number):
    locker = get_object_or_404(Locker, room=room,locker_number=locker_number)
    if locker.owner:
        messages.add_message(request, messages.ERROR, u'Beklager. Skap nummer %s i rom %s er opptatt. Vennligst velg ett annet skap.' % (locker_number, room))
        return redirect("list_lockers", room=room)

    if request.method == "POST":
        userForm = UserForm(request.POST)
        if userForm.is_valid():
            user, created = User.objects.get_or_create(username=userForm.data['username'])
            if created or not(user.email):
                user.email = "%s@stud.ntnu.no" % user.username
                user.save()
            if user.locker_set.count() > 3 :
                messages.add_message(request, messages.ERROR, u'Beklager, men brukeren %s har nådd maksgrensen på tre skap.' % user.username)
            else:
                request.session['post_data'] = request.POST
                request.session['room'] = room
                request.session['locker_number'] = locker_number
                confirmation_key = hashlib.md5(str(random.random()).encode()).hexdigest()
                request.session['confirmation_key'] = confirmation_key
                confirmation_url = 'http://bokskap.nabla.no'+reverse(registration_confirmation, kwargs={'key':confirmation_key})
                subject = 'Bekreftelse av reservasjon av skap %s i %s' % (locker_number,room)
                from_email = 'ikke_svar@nabla.ntnu.no'

                c = Context({"confirmation_url":confirmation_url, "room":room, "locker_number":locker_number})
                html_content = render_to_string('email/confirmation_email.html',c)
                text_content = strip_tags(html_content)

                msg = EmailMultiAlternatives(subject, text_content, from_email, [user.email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
                messages.add_message(request, messages.INFO, u'En bekreftelsesepost er sendt til %s' % user.email)

    else:
        userForm = UserForm()

    c = {
           'userForm': userForm,
           'room':room,
           'locker_number': locker_number,
           'locker_rooms': [x for x in Locker.ROOMS],
    }
    return render(request, 'registration.html', c)

def registration_confirmation(request, key):
    try:
        confirmation_key = request.session['confirmation_key']
        if key != confirmation_key:
            raise KeyError
    except KeyError:
        raise Http404

    post_data = request.session['post_data']
    locker = get_object_or_404(Locker, room=request.session['room'],locker_number=request.session['locker_number'])
    user = User.objects.get(username = post_data['username'])
    user.first_name = post_data['first_name']
    user.last_name = post_data['last_name']
    user.save()
    locker.reserve(user)
    messages.add_message(request, messages.INFO, u'Skap nummer %d i %s rom  er nå registrert på %s' % (locker.locker_number,locker.room,user.username))
    return redirect('/list/'+locker.room)


