from django.conf.urls import include
from django.contrib import admin
from django.urls import path

from account.urls import urlpatterns as account_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(account_urls)),
]
