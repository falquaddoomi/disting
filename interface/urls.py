from django.conf.urls import url, patterns
import django.contrib.auth.views

urlpatterns = patterns('',
    url(r'^$', 'interface.views.home', name='home'),
    url(r'^home_auth/$', 'interface.views.home_auth', name='home_auth'),
    url(r'^queue/$', 'interface.views.queue', name='queue'),
    url(r'^accounts/login/$', django.contrib.auth.views.login, name='login'),
    url(r'^logout/$', 'interface.views.logout_view', name='interface_logout'),
    url(r'^jobs/add/$', 'interface.views.addjob', name='addjob'),
    # url(r'^jobs/add_alt/$', 'interface.views.addjob_alt', name='addjob_alt'),
    url(r'^jobs/(?P<jobID>\d+)/$', 'interface.views.viewresults', name='viewjob'),
    url(r'^jobs/(?P<jobID>\d+)/edit/$', 'interface.views.editjob', name='editjob'),
    # url(r'^jobs/(?P<jobID>\d+)/edit_alt/$', 'interface.views.editjob_alt', name='editjob_alt'),
    url(r'^jobs/(?P<jobID>\d+)/remove/$', 'interface.views.removejob', name='removejob'),
    url(r'^jobs/(?P<jobID>\d+)/resubmit/$', 'interface.views.resubmitjob', name='resubmitjob'),
    url(r'^jobs/(?P<jobID>\d+)/cancel/$', 'interface.views.canceljob', name='canceljob'),
)
