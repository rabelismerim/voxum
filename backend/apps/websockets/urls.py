from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class WebSocketStatusView(APIView):
    """Endpoint HTTP para verificar a disponibilidade do serviço de WebSocket."""
    
    def get(self, request):
        return Response(
            {"status": "Serviço WebSocket (Channels) ativo e aguardando conexões."},
            status=status.HTTP_200_OK
        )


urlpatterns = [
    path('', WebSocketStatusView.as_view(), name='websocket_status'),
]