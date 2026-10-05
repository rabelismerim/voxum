from apps.voxum_base.schemas import TaskResultSerializer
from core.abstract.schemas import AbstractDescriptionSchema
from rest_framework import serializers

from apps.report.models import ReportMeeting, ReportVoting


class ReportSchema(AbstractDescriptionSchema):
    task = TaskResultSerializer(read_only=True)
    file_url = serializers.URLField(read_only=True)
    meeting_id = serializers.UUIDField()

    class Meta:
        model = ReportMeeting
        fields = ('id', 'file', 'task', 'file_url', 'report_type', 'meeting_id', 'type_display', 'type', 'created_at',
                  'updated_at')
        read_only_fields = (
            'id', 'task_result', 'task_id', 'file', 'task', 'type_display', 'type', 'created_at', 'updated_at')

    def create(self, validated_data):
        report = ReportMeeting.objects.filter(meeting_id=validated_data['meeting_id'],
                                              report_type=validated_data['report_type']).first()
        if report:
            report.run_task()
            return report
        return super().create(validated_data)


class ReportVotingSchema(AbstractDescriptionSchema):
    task = TaskResultSerializer(read_only=True)
    file_url = serializers.URLField(read_only=True)
    voting_id = serializers.UUIDField()

    class Meta:
        model = ReportVoting
        fields = ('id', 'file', 'task', 'file_url', 'report_type', 'voting_id', 'type_display', 'type', 'created_at',
                  'updated_at')
        read_only_fields = (
        'id', 'task_result', 'task_id', 'file', 'task', 'type_display', 'type', 'created_at', 'updated_at')

    def create(self, validated_data):
        report = ReportVoting.objects.filter(voting_id=validated_data['voting_id'],
                                             report_type=validated_data['report_type']).first()
        if report:
            report.run_task()
            return report
        return super().create(validated_data)