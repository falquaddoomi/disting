from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'compgraph_web.views.home', name='home'),
    url(r'^', include('interface.urls', namespace='interface')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

# urlpatterns += patterns('django.contrib.staticfiles.views',
#     url(r'^static/(?P<path>.*)$', 'serve'),
# )
