"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.urls import path

from apps.report.views import (
    ReportApi,
    ReportDetailApi,
    ReportCreateApi,
    ReportVotingCreateApi,
    ReportVotingApi,
    ReportVotingDetailApi
)

urlpatterns = [
    path('meeting/', ReportCreateApi.as_view()),
    path('meeting/<uuid:meeting_id>/', ReportApi.as_view()),
    path('meeting/detail/<uuid:id>/', ReportDetailApi.as_view()),

    path('voting/', ReportVotingCreateApi.as_view()),
    path('voting/<uuid:voting_id>/', ReportVotingApi.as_view()),
    path('voting/detail/<uuid:id>/', ReportVotingDetailApi.as_view())
]