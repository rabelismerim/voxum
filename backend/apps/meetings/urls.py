from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import viewsets, serializers
from .models import Meeting

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

router = DefaultRouter()
router.register(r'', MeetingViewSet, basename='meeting')

urlpatterns = [
    path('', include(router.urls)),
]