from django.conf.urls import url

from bridgeApp.views import Launch, ClosePID, DisplayCIF

from . import views

# https://www.jetbrains.com/pycharm/quickstart/django_guide.html
# https://www.jetbrains.com/pycharm/help/run-debug-configuration-django-server.html


urlpatterns = [url(r'^$', views.index, name='index'),  # / or /cmd will hit here.
               url(r'^sss_minute', views.samplesocketstream, name='samplesocketstream'),  # blocking, CLOCK izzy project
               url(r'^testJSON', views.testJSON, name='testJSON'),  # test JSON - direct output.
               # url(r'^Launch/', Launch.as_view(template_name="api_Launch.html"), name='Launch'),
               url(r'^Launch', Launch.as_view(), name='Launch'),  # "Class Based Views" for Launch, Note: import above
               url(r'^Close', ClosePID.as_view(), name="ClosePID"),
               url(r'^DisplayCIF', DisplayCIF.as_view(), name="DisplayCIF"),  # Display_Capture_Image_File
               ]
