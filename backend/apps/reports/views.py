from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.reports.services import ExcelImportService

class ImportCreditorsView(APIView):
    """Endpoint para importação massiva de credores via ficheiro .xlsx."""

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        company_id = request.data.get('company_id')

        if not file_obj or not company_id:
            return Response(
                {"error": "Ficheiro e company_id são obrigatórios."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        result = ExcelImportService.import_creditors_from_excel(file_obj, company_id)
        return Response(result, status=status.HTTP_200_OK)