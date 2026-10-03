from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets
from .models import Creditor
from rest_framework import serializers

class CreditorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Creditor
        fields = '__all__'

class CreditorViewSet(viewsets.ModelViewSet):
    queryset = Creditor.objects.all()
    serializer_class = CreditorSerializer

router = DefaultRouter()
router.register(r'', CreditorViewSet, basename='creditor')

urlpatterns = [
    path('', include(router.urls)),
]