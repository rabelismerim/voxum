"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from guest import views
    2. Add a URL to urlpatterns:  path('', views.GuestApi, name='guest')
Class-based views
    1. Add an import:  from guest import Guest
    2. Add a URL to urlpatterns:  path('', GuestApi.as_view(), name='guest')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('guest/', include('guest.another_app.urls'))
"""
from django.urls import path

from apps.guest.views import UserGuestApi, UserGuestDetailApi, UserGuestDetailApiGuest, UserGuestResetOtpView, \
    UserGuestRevokeOtpView, UserGuestResetPasswordView, UserGuestSendInviteCiamView, UserGuestReSendInviteCiamView

urlpatterns = [
    path('', UserGuestApi.as_view()),
    path('<uuid:id>/', UserGuestDetailApi.as_view()),
    path('detail/', UserGuestDetailApiGuest.as_view()),
    path('ciam/reset_otp/<uuid:id>/', UserGuestResetOtpView.as_view()),
    path('ciam/revoke_otp/<uuid:id>/', UserGuestRevokeOtpView.as_view()),
    path('ciam/reset_password/<uuid:id>/', UserGuestResetPasswordView.as_view()),
    path('ciam/send_invite/<uuid:id>/', UserGuestSendInviteCiamView.as_view()),
    path('ciam/resend_invite/<uuid:id>/', UserGuestReSendInviteCiamView.as_view()),

]
