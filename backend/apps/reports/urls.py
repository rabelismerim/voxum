from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ReportsOverviewView(APIView):
    """Endpoint inicial para visualização e exportação de relatórios."""
    
    def get(self, request):
        return Response(
            {"message": "Módulo de relatórios ativo"},
            status=status.HTTP_200_OK
        )


urlpatterns = [
    path('', ReportsOverviewView.as_view(), name='reports_overview'),
]