from django.urls import path

from apps.presence.views import (
    PresenceApi,
    PresenceDepartureApi,
    PresenceDetailApi,
    PresenceGuestApi,
    PresenceRepresentativeManagementApi,
    PresenceRepresentativeGuestApi
)

urlpatterns = [
    path('', PresenceApi.as_view()),
    path('guest/<uuid:meeting_id>/', PresenceGuestApi.as_view(), name='accredited_guest'),
    path('management/representatives/', PresenceRepresentativeManagementApi.as_view()),
    path('representatives/', PresenceRepresentativeGuestApi.as_view()),
    path('<uuid:id>/', PresenceDetailApi.as_view()),
    path('register/departure/<uuid:id>/', PresenceDepartureApi.as_view()),
]