from django.conf.urls import url
from django.views.generic import TemplateView
from .views import (IndexPage, LockerRoomView, view_locker,
                    LockerRegistrationView, registration_confirmation, LockerReminder,
                    UserList)


urlpatterns = [
    url(r'^$',
        IndexPage.as_view(), name="index_page"),
    url(r'^skapregler$',
        TemplateView.as_view(template_name="locker/locker_rules.html"),
        name="locker_rules"),
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
    url(r'^userlist$',
        UserList.as_view(),
        name='user_list'),
]
