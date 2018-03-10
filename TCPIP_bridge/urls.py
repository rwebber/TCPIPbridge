from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'TCPIP_bridge.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^$', include('bridgeApp.urls'), name='home'),  #  send root to bridgeAPP
    url(r'^api/sss_minute', include('mw_socketstream.urls'), name='mediawikisocketdata'),
    url(r'^api/', include('bridgeApp.urls'), name='command'),
    url(r'^admin/', include(admin.site.urls)))
