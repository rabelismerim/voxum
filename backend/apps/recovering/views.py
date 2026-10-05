from rest_framework import permissions
from utils import _, doc

from apps.recovering.models import Recovering
from apps.recovering.schemas import RecoveringSchema
from core.permissions.views import IsUserManagerOrConsultantPermission
from core.views import AbstractViewApi


@doc(_("""Visualização da API para lidar com Recuperandas.

    Uma Recuperanda se refere à empresa em dificuldades financeiras que busca a reestruturação de suas dívidas por
    meio do processo de recuperação judicial ou de falência.

    Métodos HTTP suportados:
        - GET
        - POST
    """))
class RecoveringApi(AbstractViewApi):
    serializer_class = RecoveringSchema
    model = Recovering
    model_query = Recovering.objects.all()
    http_method_names = ['get', 'post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]

    docs = {'get': _("""Lida com uma solicitação GET para recuperar Recuperandas.

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados das Recuperandas."""),

            'post': _("""Lida com solicitações POST para criar uma Recuperanda.

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados de detalhes da Recuperandas.""")
            }