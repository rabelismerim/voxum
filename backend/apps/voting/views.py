from django.db.models import ProtectedError
from django.http import JsonResponse
from drf_yasg import openapi
from rest_framework import permissions
from utils import _, doc

from apps.voxum_base.models import Coin
from apps.creditor.models import Creditor
from apps.meetings.models import RepresentativeMeeting
from apps.voting.models import Voting, Choice, VotingResult, StatusVotingChoice
from apps.voting.schemas import VotingAdminSchema, VotingAdminDetailSchema, CreditorResultSchema, \
    VotingAdminUpdateSchema, ChoiceSchema, ChoiceUpdateSchema, ChoiceCreateSchema, VotingResultSchema, \
    VotingResultDetailSchema, RepresentativeResultsSchema, StartVotingSerializer, \
    ExtendVotingSerializer, EndVotingSerializer, VotingResultGuestSchema, VotingGuestTaskSchema, \
    VotingResultRepresentativeGuestSchema, RepresentativeResultsByInternalSchema
from apps.voting.tasks import ProcessVotingTask, ProcessVotingRepresentativeTask
from core.permissions.views import VotingPermission, ChoiceVotingPostPermission, \
    ChoiceVotingPermission, IsUserManagerPermission, IsUserGuestPermission, IsUserManagerOrConsultantPermission, \
    IsUserManagerOrReadOnlyConsultantPermission, ChoiceGuestVoteChoicePostPermission, \
    ChoiceRepresentativeVoteChoicePostPermission
from core.views import AbstractApi


@doc(_("""Visualização da API para lidar com Votações.

    Uma Votação lida com as escolhas do credor com perguntas e respostas.

    Métodos HTTP suportados:
        - POST
    """))
class VotingMeetingApi(AbstractApi):
    serializer_class = VotingAdminDetailSchema
    model = Voting
    model_query = Voting.objects.all()
    http_method_names = ['get']
    query_slug = True
    pagination = True
    query_params = [
        {
            "name": "status",
            "field": "status__in",
            "in": "query",
            "required": False,
            "description": str(_("Status")),
            "schema": {"type": openapi.TYPE_ARRAY,
                       "items": {"type": openapi.TYPE_STRING,
                                 "enum": StatusVotingChoice.values}}
        },
        {
            "name": "description",
            "field": "description__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Descrição")),
            "schema": {"type": "string"}
        },
    ]

    docs = {'get': _("""Lida com solicitações GET para obter uma lista de Votações com base no meeting_id.

       Returns:
           JsonResponse: uma resposta JSON contendo os dados serializados das Votações."""),
            }
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]


@doc(_("""Visualização da API para lidar com Votações.

    Uma Votação lida com as escolhas do credor com perguntas e respostas.

    Métodos HTTP suportados:
        - POST
    """))
class VotingApi(AbstractApi):
    serializer_class = VotingAdminSchema
    model = Voting
    model_query = Voting.objects.all()
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]

    docs = {'post': _("""Lida com solicitações POST para criar uma Votação.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados de detalhes da Votação.""")
            }


@doc(_("""Visualização da API para lidar com Votações.

    Uma Votação lida com as escolhas do credor com perguntas e respostas.

    Métodos HTTP suportados:
        - GET
        - PUT
    """))
class VotingDetailApi(AbstractApi):
    serializer_class = VotingAdminDetailSchema
    layout_serializers = {
        'default': VotingAdminDetailSchema,
        'get': VotingAdminDetailSchema,
        'put': VotingAdminUpdateSchema,
    }
    model = Voting
    model_query = Voting.objects.all()
    http_method_names = ['get', 'delete', 'put']
    docs = {'get': _("""Lida com solicitações GET para obter uma Votação especifica com base no ID.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados de detalhes da Votação."""),

            'put': _("""Lida com solicitações PUT para atualizar uma Votação especifica com base no ID.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados de detalhes da Votação."""),

            'delete': _("""Lida com solicitações DELETE para deletar uma Votação especifica com base no ID.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados de detalhes da Votação.""")
            }
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission, VotingPermission]


@doc(_("""Visualização da API para lidar com os Credores qualificados para votação.

    Um Credor qualificado é aquele que pode votar.

    Métodos HTTP suportados:
        - GET
    """))
class VotingDetailQualifiedApi(AbstractApi):
    serializer_class = CreditorResultSchema
    model = Voting
    model_query = Voting.objects.all()
    http_method_names = ['get']
    pagination = True
    many = True
    query_slug = True
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]

    query_params = [
        {
            "name": "legal_number",
            "field": "guest__entity__legal_number__icontains",
            "in": "query",
            "required": False,
            "description": str(_("CPF/CNPJ")),
            "schema": {"type": "string"}
        },
        {
            "name": "first_name",
            "field": "guest__user__first_name__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Primeiro nome")),
            "schema": {"type": "string"}
        },
        {
            "name": "has_reservations",
            "field": "votingresult__has_reservations",
            "in": "query",
            "required": False,
            "description": str(_("Há ressalva")),
            "schema": {"type": "bool"}
        },
        {
            "name": "classe",
            "field": "classe__description__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Nome da Classe")),
            "schema": {"type": "string"}
        },
        {
            "name": "voto",
            "field": "votingresult__vote__value__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Descrição do voto")),
            "schema": {"type": "string"}
        },
    ]

    map_ordering_fields = {
        'legal_number': 'guest__entity__legal_number',
        'first_name': 'guest__user__first_name',
        'value': 'credit_value',
        'classe': 'classe__description',
        'has_reservations': 'votingresult__has_reservations',
        'vote_value': 'votingresult__vote__value',
    }

    @doc(_("""Lida com solicitações GET para obter os Credores qualificados para votação com base no ID da votação.

       Returns:
           JsonResponse: uma resposta JSON contendo os dados serializados dos Credores."""))
    def get(self, request, *args, **kwargs):
        voting = self.model.objects.filter(id=kwargs.get('id')).first()
        query_parameters = self.get_query_parameters()

        queryset = Creditor.objects.filter(meeting__voting=voting, **query_parameters)
        qualified_creditors = voting.annotate_voting_id_creditors(queryset)
        ordering = self.get_ordering(self.request, queryset, self)
        if ordering:
            qualified_creditors = qualified_creditors.order_by(*ordering)
        paginated_queryset = self.paginate_queryset(qualified_creditors)
        data = self.serializer(paginated_queryset, many=True)
        return self.get_paginated_response(data)


@doc(_("""Visualização da API para lidar com escolhas da Votação.

    Uma escolha lida com as opções que uma Votação pode ter.

    Métodos HTTP suportados:
        - POST
    """))
class VotingChoiceApi(AbstractApi):
    serializer_class = ChoiceCreateSchema
    model = Choice
    model_query = Choice.objects.all()
    http_method_names = ['post']
    docs = {'post': _("""Lida com solicitações POST para criar uma escolha.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados da Escolha.""")
            }
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission,
                          ChoiceVotingPostPermission, ]
    tags = [_('Voting - Choice')]


@doc(_("""Visualização da API para lidar com escolhas da Votação.

    Uma escolha lida com as opções que uma Votação pode ter.

    Métodos HTTP suportados:
        - POST
    """))
class VotingChoiceDetailApi(AbstractApi):
    serializer_class = ChoiceSchema
    layout_serializers = {
        'default': ChoiceSchema,
        'get': ChoiceSchema,
        'delete': ChoiceSchema,
        'put': ChoiceUpdateSchema,
    }
    model = Choice
    model_query = Choice.objects.all()
    http_method_names = ['get', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission, ChoiceVotingPermission]
    tags = [_('Voting - Choice')]

    docs = {'get': _("""Lida com solicitações GET para obter uma Escolha especifica com base no ID.

        Returns:
            JsonResponse: uma resposta JSON contendo os dados serializados de detalhes Escolha."""),

            'put': _("""Lida com solicitações PUT para atualizar uma Escolha especifica com base no ID.

        Returns:
            JsonResponse: uma resposta JSON contendo os dados serializados de detalhes da Escolha."""),
            'delete': _("""Lida com solicitações DELETE para deletar uma Escolha especifica com base no ID.

        Returns:
            JsonResponse: uma resposta JSON contendo os dados serializados de detalhes da Escolha.""")
            }


@doc(_("""Visualização da API para lidar com a Escolha do Credor.

    Lida com a escolha do Credor.

    Métodos HTTP suportados:
        - POST
    """))
class VotingResultApi(AbstractApi):
    serializer_class = VotingResultSchema
    model = VotingResult
    model_query = VotingResult.objects.all()
    tags = [_('Voting - Result')]
    http_method_names = ['post']

    docs = {'post': _("""Lida com solicitações POST para registrar a Escolha do Credor.

        Returns:
            JsonResponse: uma resposta JSON contendo os dados serializados da Escolha.""")
            }

    permission_classes = [permissions.IsAuthenticated]


@doc(_("""Visualização da API para lidar com a Escolha do Credor.

    Lida com a escolha do Credor.

    Métodos HTTP suportados:
        - GET
        - PUT
        - DELETE
    """))
class VotingResultDetailApi(AbstractApi):
    serializer_class = VotingResultDetailSchema
    model = VotingResult
    model_query = VotingResult.objects.all()
    tags = [_('Voting - Result')]
    http_method_names = ['get', 'put', 'delete']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerPermission]
    docs = {'get': _("""Lida com solicitações GET para obter uma Escolha especifica com base no ID.

            Returns:
                JsonResponse: uma resposta JSON contendo os dados serializados de detalhes Escolha."""),

            'put': _("""Lida com solicitações PUT para atualizar uma Escolha especifica com base no ID.

            Returns:
                JsonResponse: uma resposta JSON contendo os dados serializados de detalhes da Escolha."""),
            'delete': _("""Lida com solicitações DELETE para deletar uma Escolha especifica com base no ID.

            Returns:
                JsonResponse: uma resposta JSON contendo os dados serializados de detalhes da Escolha.""")
            }


@doc(_("""Visualização da API para lidar com os Representantes dos Credores qualificados para votação.

    Um Representante faz o papel do Credor qualificado a votar.

    Métodos HTTP suportados:
        - GET
        - POST
    """))
class VotingDetailQualifiedByRepresentativesApi(AbstractApi):
    serializer_class = RepresentativeResultsSchema
    layout_serializers = {
        'default': RepresentativeResultsByInternalSchema,
        'post': RepresentativeResultsByInternalSchema,
    }
    model = RepresentativeMeeting
    model_query = RepresentativeMeeting.objects.all()
    http_method_names = ['post']
    pagination = True
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrReadOnlyConsultantPermission,
                          ChoiceRepresentativeVoteChoicePostPermission]
    query_slug = True
    tags = [_('Voting - Representatives')]
    many = True

    @doc(_("""Lida com solicitações POST para registrar as escolhas dos Credores por meio do ID do
    Representante.

        Returns:
            JsonResponse: uma resposta JSON contendo os dados serializados dos resultados da votação.
        """))
    def post(self, request, *args, **kwargs):
        return JsonResponse(
            RepresentativeResultsSchema(self.create_object(), many=False, context={'request': self.request}).data,
            status=201, safe=False)


@doc(_("""Visualização de API para iniciar um processo de votação.

    Métodos HTTP suportados:
        - PUT
    """))
class StartVotingView(AbstractApi):
    serializer_class = VotingAdminDetailSchema
    layout_serializers = {
        'default': VotingAdminDetailSchema,
        'get': VotingAdminDetailSchema,
        'put': StartVotingSerializer,
    }
    model = Voting
    model_query = Voting.objects.all()
    http_method_names = ['put']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    docs = {
        'put': _("""Método PUT para iniciar um processo de votação.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados da votação.
        """)
    }


@doc(_("""Visualização de API para estender um processo de votação em andamento.

    Métodos HTTP suportados:
        - PUT
    """))
class ExtendVotingView(AbstractApi):
    serializer_class = VotingAdminDetailSchema
    layout_serializers = {
        'default': VotingAdminDetailSchema,
        'get': VotingAdminDetailSchema,
        'put': ExtendVotingSerializer,
    }
    model = Voting
    model_query = Voting.objects.all()
    http_method_names = ['put']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    docs = {
        'put': _("""Método PUT para extender o tempo de processo de votação.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados da votação.
        """)
    }


@doc(_("""Visualização de API para encerrar um processo de votação.

    Métodos HTTP suportados:
        - PUT
    """))
class EndVotingView(AbstractApi):
    serializer_class = VotingAdminDetailSchema
    layout_serializers = {
        'default': VotingAdminDetailSchema,
        'get': VotingAdminDetailSchema,
        'put': EndVotingSerializer,
    }
    model = Voting
    model_query = Voting.objects.all()
    http_method_names = ['put']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    docs = {
        'put': _("""Método PUT para finalizar uma votação.

    Returns:
        JsonResponse: uma resposta JSON contendo os dados serializados dos resultados da votação.
        """)
    }


# To Guest User
@doc(_("""Visualização da API para lidar com a Escolha do Credor.

    Lida com a escolha do Credor.

    Métodos HTTP suportados:
        - POST
    """))
class VotingResultGuestApi(AbstractApi):
    serializer_class = VotingResultGuestSchema
    model = VotingResult
    model_query =VotingResult.objects.all()
    tags = [_('Voting - Result')]
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated, IsUserGuestPermission, ChoiceGuestVoteChoicePostPermission]

    docs = {'post': _("""Lida com solicitações POST para registrar a Escolha do Credor pelo usuário externo.

        Returns:
            JsonResponse: uma resposta JSON contendo os dados serializados da Escolha.""")
            }

    responses = {
        201: {
            "content": VotingGuestTaskSchema,
            "serializer": VotingGuestTaskSchema,
            "description": str(
                _("Sucesso ao registrar voto.")
            ),
        }
    }

    def post(self, request, *args, **kwargs):
        task = ProcessVotingTask.delay({'user_id': request.user.id, 'data': request.data})
        return JsonResponse({'task_id': task.id}, status=201)


@doc(_("""Visualização da API para lidar com a Escolha do Credor, pelo representante.

    Lida com a escolha do Credor.

    Métodos HTTP suportados:
        - POST
    """))
class VotingResultRepresentativeGuestApi(AbstractApi):
    serializer_class = VotingResultRepresentativeGuestSchema
    model = VotingResult
    model_query = VotingResult.objects.all()
    tags = [_('Voting - Result')]
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated, IsUserGuestPermission,
                          ChoiceRepresentativeVoteChoicePostPermission]

    docs = {'post': _("""Lida com solicitações POST para registrar a Escolha do Credor pelo usuário externo, feito pelo
    representante.

        Returns:
            JsonResponse: uma resposta JSON contendo os dados serializados da Escolha.""")
            }

    responses = {
        201: {
            "content": VotingGuestTaskSchema,
            "serializer": VotingGuestTaskSchema,
            "description": str(
                _("Sucesso ao registrar voto.")
            ),
        }
    }

    def post(self, request, *args, **kwargs):
        task = ProcessVotingRepresentativeTask.delay({'user_id': request.user.id, 'data': request.data})
        return JsonResponse({'task_id': task.id}, status=201)


def clear_db():
    for x in Coin.objects.all():
        try:
            x.delete()
        except ProtectedError:
            pass