from datetime import datetime, timedelta

from rest_framework import permissions
from utils import doc, _

from apps.report.models import ReportMeeting, ReportVoting
from apps.report.schemas import ReportSchema, ReportVotingSchema
from core.permissions.views import IsUserManagerOrConsultantPermission
from core.views import AbstractApi


@doc(_("""Visualização da API para lidar com os relatórios da assembleia.

    Os relatórios da assembleia podem ser gerados de forma automática, baseado em eventos, ou solicitados por meio de
    um POST.

    Cada tipo de relatório pode haver apenas um arquivo para ele. Toda vez que é solicitado ou atualizado o arquivo, é
    gerado um novo relatório e salvo no lugar do anterior.

    Dentro do objeto relatório, há uma task de controle que informa o status de um arquivo
    """))
class ReportApi(AbstractApi):
    serializer_class = ReportSchema

    model = ReportMeeting
    model_query = ReportMeeting.objects.all()
    http_method_names = ['get']
    tags = ['Meeting - Report']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    filter_check_user_voting_permission = 'meeting_id'
    query_slug = True
    docs = {'get': _("""Lida com solicitações GET para obter os relatórios da assembleia com base no ID da assembleia.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados dos relatórios da assembleia.""")
            }


@doc(_("""Visualização da API para lidar com os relatórios da assembleia.

    Os relatórios da assembleia podem ser gerados de forma automática, baseado em eventos, ou solicitados por meio de
    um POST.

    Cada tipo de relatório pode haver apenas um arquivo para ele. Toda vez que é solicitado ou atualizado o arquivo, é
    gerado um novo relatório e salvo no lugar do anterior.

    Dentro do objeto relatório, há uma task de controle que informa o status de um arquivo
    """))
class ReportCreateApi(ReportApi):
    http_method_names = ['get', 'post']
    operation_id_base = 'ReportMeetingDetail'

    docs = {'post': _("""Lida com solicitações POST para criar um relatório com base no ID da assembleia e o tipo de
    relatório.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados do relatório criado.""")
            }

    def get_queryset(self):
        created_at_min = self.request.GET.get('created_at_min')
        created_at_max = self.request.GET.get('created_at_max')

        if not created_at_min and not created_at_max:
            created_at_max = datetime.now().date()
            created_at_min = created_at_max - timedelta(days=90)

        elif created_at_min:
            created_at_min = datetime.strptime(created_at_min, '%Y-%m-%d').date()
            if not created_at_max:
                created_at_max = created_at_min + timedelta(days=90)
        elif created_at_max:
            created_at_max = datetime.strptime(created_at_max, '%Y-%m-%d').date()
            if not created_at_min:
                created_at_min = created_at_max - timedelta(days=90)
        return {'created_at__gte': created_at_min, 'created_at__lte': created_at_max}


@doc(_("""Visualização da API para lidar com os relatórios da assembleia.

    Os relatórios da assembleia podem ser gerados de forma automática, baseado em eventos, ou solicitados por meio de
    um POST.

    Cada tipo de relatório pode haver apenas um arquivo para ele. Toda vez que é solicitado ou atualizado o arquivo, é
    gerado um novo relatório e salvo no lugar do anterior.

    Dentro do objeto relatório, há uma task de controle que informa o status de um arquivo
    """))
class ReportDetailApi(ReportApi):
    http_method_names = ['get']
    many = False
    query_slug = True
    filter_check_user_voting_permission = 'meeting__reportmeeting__id'
    docs = {'get': _("""Lida com solicitações GET para obter um relatório da assembleia específico, com base no ID.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados do relatório.""")
            }


@doc(_("""Visualização da API para lidar com os relatórios da assembleia.

    Os relatórios da assembleia podem ser gerados de forma automática, baseado em eventos, ou solicitados por meio de
    um POST.

    Cada tipo de relatório pode haver apenas um arquivo para ele. Toda vez que é solicitado ou atualizado o arquivo, é
    gerado um novo relatório e salvo no lugar do anterior.

    Dentro do objeto relatório, há uma task de controle que informa o status de um arquivo
    """))
class ReportVotingApi(AbstractApi):
    serializer_class = ReportVotingSchema

    model = ReportVoting
    model_query = ReportVoting.objects.all()
    http_method_names = ['get']
    tags = ['Meeting - Report']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    filter_check_user_voting_permission = 'meeting__voting__id'
    docs = {'get': _("""Lida com solicitações GET para obter os relatórios da assembleia com base no ID da assembleia.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados dos relatórios da assembleia.""")
            }


@doc(_("""Visualização da API para lidar com os relatórios da assembleia.

    Os relatórios da assembleia podem ser gerados de forma automática, baseado em eventos, ou solicitados por meio de
    um POST.

    Cada tipo de relatório pode haver apenas um arquivo para ele. Toda vez que é solicitado ou atualizado o arquivo, é
    gerado um novo relatório e salvo no lugar do anterior.

    Dentro do objeto relatório, há uma task de controle que informa o status de um arquivo
    """))
class ReportVotingCreateApi(ReportVotingApi):
    http_method_names = ['get', 'post']
    operation_id_base = 'ReportVotingDetail'

    docs = {'post': _("""Lida com solicitações POST para criar um relatório com base no ID da assembleia e o tipo de
    relatório.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados do relatório criado.""")
            }

    def get_queryset(self):
        created_at_min = self.request.GET.get('created_at_min')
        created_at_max = self.request.GET.get('created_at_max')

        if not created_at_min and not created_at_max:
            created_at_max = datetime.now().date()
            created_at_min = created_at_max - timedelta(days=90)

        elif created_at_min:
            created_at_min = datetime.strptime(created_at_min, '%Y-%m-%d').date()
            if not created_at_max:
                created_at_max = created_at_min + timedelta(days=90)
        elif created_at_max:
            created_at_max = datetime.strptime(created_at_max, '%Y-%m-%d').date()
            if not created_at_min:
                created_at_min = created_at_max - timedelta(days=90)
        return {'created_at__gte': created_at_min, 'created_at__lte': created_at_max}


@doc(_("""Visualização da API para lidar com os relatórios da assembleia.

    Os relatórios da assembleia podem ser gerados de forma automática, baseado em eventos, ou solicitados por meio de
    um POST.

    Cada tipo de relatório pode haver apenas um arquivo para ele. Toda vez que é solicitado ou atualizado o arquivo, é
    gerado um novo relatório e salvo no lugar do anterior.

    Dentro do objeto relatório, há uma task de controle que informa o status de um arquivo
    """))
class ReportVotingDetailApi(ReportVotingApi):
    http_method_names = ['get']
    many = False
    query_slug = True
    filter_check_user_voting_permission = 'meeting__reportvoting__voting__id'
    docs = {'get': _("""Lida com solicitações GET para obter um relatório da assembleia específico, com base no ID.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados do relatório.""")
            }