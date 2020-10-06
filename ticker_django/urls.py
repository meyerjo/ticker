"""ticker_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import RedirectView

from ticker.views.offline_views import offline_appcache
from ticker.views.startpage import start_page, start_page_leagues, start_page_leagues_json

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^ticker/', include('ticker.urls')),
    url(r'^api/v1/json/', include('ticker.urls_api')),
    url(r'^offline.appcache$', offline_appcache),
    url(r'^simple/?$', RedirectView.as_view(url='/ticker/manage/ticker/simple/login/', permanent=True)),
    url(r'^$', start_page),
    url(r'^l/([^/]+)/$', start_page_leagues, name='start_page_leagues'),
    url(r'^l/([^/]+)/json/?$', start_page_leagues_json, name='start_page_leagues_json')
]

# handler404 = 'ticker.views.startpage.error_404_view'
