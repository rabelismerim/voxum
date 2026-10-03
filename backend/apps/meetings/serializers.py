from rest_framework import serializers
from apps.meetings.models import Meeting
from apps.presence.models import Attendance
from apps.voting.models import Poll, Vote

class MeetingSerializer(serializers.ModelSerializer):
    call_type_display = serializers.CharField(source='get_call_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Meeting
        fields = '__all__'

class AttendanceSerializer(serializers.ModelSerializer):
    creditor_name = serializers.CharField(source='creditor.name', read_only=True)

    class Meta:
        model = Attendance
        fields = '__all__'

class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'

class PollSerializer(serializers.ModelSerializer):
    votes = VoteSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = '__all__'