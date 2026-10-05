from core.abstract.views import AbstractViewApi
from rest_framework import permissions
from utils import doc, _

from apps.location.models import Location
from apps.location.schemas import LocationSchema
from core.permissions.views import IsUserManagerOrConsultantPermission


@doc("""O Local está relacionado a uma Assembleia, identificando onde fica o local

    Métodos HTTP suportados:
        - GET
        - POST
    """)
class LocationApi(AbstractViewApi):
    serializer_class = LocationSchema

    model = Location
    model_query = Location.objects.all()
    http_method_names = ['get', 'post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]

    docs = {'get': _("""Lida com uma solicitação GET para recuperar as localizações.

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados das localizações."""),

            'post': _("""Lida com uma solicitação POST para criar uma localização.

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados da localização."""),
            }

    cache_timeout = 60 * 60 * 24
