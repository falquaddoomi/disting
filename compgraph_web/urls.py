from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'compgraph_web.views.home', name='home'),
    url(r'^DISTING/', include('interface.urls', namespace='interface')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    url(r'^$', RedirectView.as_view(url='/DISTING')),
)

# urlpatterns += patterns('django.contrib.staticfiles.views',
#     url(r'^static/(?P<path>.*)$', 'serve'),
# )
