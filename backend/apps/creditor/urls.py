from django.urls import path

from apps.creditor.views import (
    CreditorDetailApi,
    CreditorApi,
    CreditorMeetingApi,
    CreditorRepresentativeApi,
    RepresentativeDetailApi
)

urlpatterns = [
    path('', CreditorApi.as_view(), name='creditor'),
    path('<uuid:id>/', CreditorDetailApi.as_view(), name='creditor_detail'),
    path('meeting/<uuid:meeting_id>/', CreditorMeetingApi.as_view()),
    path('representative/<uuid:representative__representative__id>/', CreditorRepresentativeApi.as_view()),
    path('representative/detail/<uuid:id>/', RepresentativeDetailApi.as_view()),
]