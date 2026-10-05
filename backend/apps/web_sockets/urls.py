"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from home import views
    2. Add a URL to urlpatterns:  path('', views.HomeApi, name='home')
Class-based views
    1. Add an import:  from home import Home
    2. Add a URL to urlpatterns:  path('', HomeApi.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('home/', include('home.another_app.urls'))
"""
from django.urls import path

from apps.web_sockets.views import SocketsApi

urlpatterns = [
    path('', SocketsApi.as_view(), name="sockets-schema"),
]
