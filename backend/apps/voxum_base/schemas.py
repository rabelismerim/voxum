from core.abstract.schemas import AbstractDescriptionSchema  # Ajustado para caminho limpo
from django_celery_results.models import TaskResult
from rest_framework import serializers

from apps.voxum_base.models import Entity, Coin, ExcelWorker, ErrorFile
from apps.voxum_base.utils import get_legal_number


class EntitySchema(AbstractDescriptionSchema):
    class Meta:
        model = Entity
        fields = '__all__'

    def validate_legal_number(self, legal_number):
        return get_legal_number(legal_number)

    def create(self, validated_data):
        legal_number = validated_data.get('legal_number')
        instance, created = Entity.objects.get_or_create(legal_number=legal_number)
        return instance


class EntityDetailSchema(EntitySchema):
    class Meta:
        model = Entity
        fields = '__all__'
        non_required_fields = '__all__'


class CoinSchema(AbstractDescriptionSchema):
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Coin
        fields = '__all__'


class TaskResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskResult
        fields = ('task_id', 'status', 'result', 'date_done', 'traceback')
        read_only_fields = fields


class ErrorFileSchema(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ErrorFile
        fields = ('id', 'error', 'data', 'status', 'status_display', 'traceback')
        read_only_fields = fields


class ErrorFileUpdateSchema(serializers.ModelSerializer):
    class Meta:
        model = ErrorFile
        fields = ('id', 'status', 'data')
        read_only_fields = ('id',)


class ExcelWorkerListSchema(serializers.ModelSerializer):
    class Meta:
        model = ExcelWorker
        fields = ('id', 'file', 'created_at', 'updated_at')
        read_only_fields = fields


class ExcelWorkerSchema(serializers.ModelSerializer):
    task = serializers.SerializerMethodField()
    file_url = serializers.SerializerMethodField()
    errors = ErrorFileSchema(many=True, read_only=True)

    class Meta:
        model = ExcelWorker
        fields = ('id', 'file', 'task', 'object_id', 'file_url', 'errors', 'created_at', 'updated_at')
        read_only_fields = ('id', 'task', 'file_url', 'errors', 'created_at', 'updated_at')

    def get_task(self, instance):
        task_status = {
            ExcelWorker.STATUS_PENDING: 'PENDING',
            ExcelWorker.STATUS_SUCCEEDED: 'SUCCESS',
            ExcelWorker.STATUS_FAILED: 'FAILURE',
        }
        return {'status': task_status[instance.status]}

    def get_file_url(self, instance):
        if not instance.file:
            return None
        request = self.context.get('request')
        url = instance.file.url
        return request.build_absolute_uri(url) if request else url