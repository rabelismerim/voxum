"""
Serializes the fields of the Home model for use in the API.

This module defines a Django REST Framework serializer that inherits from both
`serializers.ModelSerializer` and a custom `AbstractModelSchema` class. The serializer
converts instances of the `Home` model to and from JSON format, and
validates incoming data based on the model's fields.

Attributes:
    - `Meta`: A nested class that specifies metadata for the serializer. The `model`
      attribute specifies the model class that the serializer should be based on, and
      `fields` lists the names of all fields that should be included in the serialized
      representation.
"""
from apps.voxum_base.schemas import TaskResultSerializer
from core.abstract.schemas import AbstractDescriptionSchema
from rest_framework import serializers

from apps.report.models import ReportMeeting, ReportVoting


class ReportSchema(AbstractDescriptionSchema):
    """
    Serializes the fields of the Home model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Home
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = PresenceSchema()
    """
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
    """
    Serializes the fields of the Home model for use in the API.

    This class defines a Django REST Framework serializer that inherits from a custom
    AbstractDescriptionSchema class. The serializer converts instances of the Home
    model to and from JSON format, and validates incoming data based on the model's fields.

    Usage example:
    serializer = PresenceSchema()
    """
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