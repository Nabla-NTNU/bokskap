from django.conf.urls import patterns, include, url


urlpatterns = patterns('locker.views',
    url(r'^$', 'index_page'),
    url(r'^list/(?P<room>\w+-\d+)', 'list_lockers'),
    url(r'^register/(?P<room>\w+-\d+)/(?P<locker_number>\d+)', 'register_locker'),
    url(r'^confirm/(?P<key>\w+)/', 'registration_confirmation'),
    url(r'^reminder', 'locker_reminder'),

)
