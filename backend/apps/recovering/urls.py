"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.urls import path

from apps.recovering.views import RecoveringApi

urlpatterns = [
    path('', RecoveringApi.as_view()),
]