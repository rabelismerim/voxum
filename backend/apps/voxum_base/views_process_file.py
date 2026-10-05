from io import BytesIO
from pathlib import PurePath

from django.contrib.contenttypes.models import ContentType
from django.http import Http404, HttpResponse
from openpyxl import Workbook
from rest_framework import permissions, status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.meetings.models import Meeting
from apps.voxum_base.models import ErrorFile, ExcelWorker
from apps.voxum_base.schemas import (
    ErrorFileSchema,
    ErrorFileUpdateSchema,
    ExcelWorkerListSchema,
    ExcelWorkerSchema,
)
from core.permissions.views import IsUserManagerOrConsultantPermission


TEMPLATE_PATH = 'meeting_creditors'
TEMPLATE_NAME = 'massive_create_creditors'


def get_worker_or_404(worker_id):
    try:
        return ExcelWorker.objects.get(id=worker_id)
    except ExcelWorker.DoesNotExist as error:
        raise Http404 from error


class CreateExcelWorkerApi(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated, IsUserManagerOrConsultantPermission)

    def post(self, request, path, name):
        if (path, name) != (TEMPLATE_PATH, TEMPLATE_NAME):
            raise Http404

        uploaded_file = request.FILES.get('file')
        object_id = request.data.get('object_id')
        if uploaded_file is None:
            raise ValidationError({'file': 'Envie uma planilha.'})
        if PurePath(uploaded_file.name).suffix.lower() not in {'.xls', '.xlsx'}:
            raise ValidationError({'file': 'O arquivo precisa ter extensão .xls ou .xlsx.'})
        if not object_id or not Meeting.objects.filter(id=object_id).exists():
            raise ValidationError({'object_id': 'Informe uma assembleia válida.'})

        worker = ExcelWorker.objects.create(
            file=uploaded_file,
            content_type=ContentType.objects.get_for_model(Meeting),
            object_id=object_id,
        )
        return Response(
            ExcelWorkerSchema(worker, context={'request': request}).data,
            status=status.HTTP_201_CREATED,
        )


class ExcelWorkerDetailApi(APIView):
    permission_classes = (permissions.IsAuthenticated, IsUserManagerOrConsultantPermission)

    def get(self, request, id):
        worker = get_worker_or_404(id)
        return Response(ExcelWorkerSchema(worker, context={'request': request}).data)


class ExcelWorkerListApi(APIView):
    permission_classes = (permissions.IsAuthenticated, IsUserManagerOrConsultantPermission)

    def get(self, request, object_id):
        workers = ExcelWorker.objects.filter(object_id=object_id).order_by('-created_at')
        return Response(ExcelWorkerListSchema(workers, many=True, context={'request': request}).data)


class ErrorFileListApi(APIView):
    permission_classes = (permissions.IsAuthenticated, IsUserManagerOrConsultantPermission)

    def get(self, request, file_id):
        worker = get_worker_or_404(file_id)
        errors = worker.errors.order_by('-created_at')
        return Response(ErrorFileSchema(errors, many=True).data)


class ErrorFileDetailApi(APIView):
    permission_classes = (permissions.IsAuthenticated, IsUserManagerOrConsultantPermission)

    def put(self, request, id):
        try:
            error = ErrorFile.objects.get(id=id)
        except ErrorFile.DoesNotExist as not_found:
            raise Http404 from not_found
        serializer = ErrorFileUpdateSchema(error, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, id):
        try:
            error = ErrorFile.objects.get(id=id)
        except ErrorFile.DoesNotExist as not_found:
            raise Http404 from not_found
        error.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WorkerExampleNamesApi(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        return Response([{'name': TEMPLATE_PATH}])


class WorkerExampleDetailApi(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, name):
        if name != TEMPLATE_PATH:
            raise Http404

        from apps.works.models import CreditorTitle

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'Credores'
        worksheet.append([column['title'] for column in CreditorTitle.columns])

        content = BytesIO()
        workbook.save(content)
        content.seek(0)
        response = HttpResponse(
            content.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = f'attachment; filename="{name}.xlsx"'
        return response
