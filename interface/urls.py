from django.conf.urls import url, patterns
import django.contrib.auth.views

urlpatterns = patterns('',
    url(r'^$', 'interface.views.home', name='home'),
    url(r'^accounts/login/$', django.contrib.auth.views.login, name='login'),
    url(r'^logout/$', 'interface.views.logout_view', name='interface_logout'),
    url(r'^jobs/add/$', 'interface.views.addjob', name='addjob'),
    url(r'^jobs/(?P<jobID>\d+)/$', 'interface.views.viewresults', name='viewjob'),
    url(r'^jobs/(?P<jobID>\d+)/remove/$', 'interface.views.removejob', name='removejob'),
    url(r'^jobs/(?P<jobID>\d+)/resubmit/$', 'interface.views.resubmitjob', name='resubmitjob'),
)
