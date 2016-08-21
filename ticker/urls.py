from django.conf.urls import url

from ticker.views.startpage import start_page

urlpatterns = [
    url('', start_page),
]