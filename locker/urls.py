from django.conf.urls import patterns, url
from .views import *


urlpatterns = patterns('locker.views',
    url(r'^$',
        IndexPage.as_view(), name="index_page"),
    url(r'^list/(?P<room>\w+-\d+)',
        LockerRoomView.as_view(),
        name="list_lockers"),
    url(r'^register/(?P<room>\w+-\d+)/(?P<locker_number>\d+)',
        view_locker,
        name="register_locker"),
    url(r'^register$',
        LockerRegistrationView.as_view(),
        name="locker_registration"),
    url(r'^confirm/(?P<key>\w+)/',
        registration_confirmation,
        name="registration_confirmation"),
    url(r'^reminder',
        LockerReminder.as_view(),
        name='locker_reminder'),
)
