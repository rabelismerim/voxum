from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.meetings.models import Meeting
from apps.presence.models import Attendance
from apps.voting.models import Poll
from apps.voting.services import VotingResultService
from apps.meetings.serializers import MeetingSerializer, AttendanceSerializer, PollSerializer

class MeetingViewSet(viewsets.ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    filterset_fields = ['meeting', 'is_present']

class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    filterset_fields = ['meeting', 'status']

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        poll = self.get_object()
        results = VotingResultService.calculate_poll_results(poll)
        return Response(results, status=status.HTTP_200_OK)