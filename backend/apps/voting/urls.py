"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.urls import path
from apps.voting.views import VotingApi, VotingDetailApi, VotingDetailQualifiedApi, \
    VotingChoiceApi, VotingChoiceDetailApi, VotingMeetingApi, VotingResultApi, VotingResultDetailApi, \
    VotingDetailQualifiedByRepresentativesApi, StartVotingView, ExtendVotingView, EndVotingView, VotingResultGuestApi, \
    VotingResultRepresentativeGuestApi

urlpatterns = [
    path('', VotingApi.as_view(), name='create_voting'),
    path('meeting/<uuid:meeting_id>/', VotingMeetingApi.as_view()),
    path('<uuid:id>/', VotingDetailApi.as_view()),
    path('start/<uuid:id>/', StartVotingView.as_view(), name='start_voting'),
    path('extend/<uuid:id>/', ExtendVotingView.as_view(), name='extend_voting'),
    path('end/<uuid:id>/', EndVotingView.as_view(), name='stop_voting'),
    path('qualified_creditors/<uuid:id>/', VotingDetailQualifiedApi.as_view()),
    path('choice/', VotingChoiceApi.as_view()),
    path('choice/<uuid:id>/', VotingChoiceDetailApi.as_view()),

    # Voto para usuários internos
    path('result/', VotingResultApi.as_view(), name='create_internal_voting_result'),
    path('result/<uuid:id>/', VotingResultDetailApi.as_view()),
    path('representatives/<uuid:representative_id>/', VotingDetailQualifiedByRepresentativesApi.as_view(),
         name='create_representatives_voting_result'),

    # Voto para usuários externos (Guest)
    path('guest/result/', VotingResultGuestApi.as_view(), name='create_guest_result'),
    path('guest/representatives/result/', VotingResultRepresentativeGuestApi.as_view(),
         name='create_representatives_guest_result'),
]