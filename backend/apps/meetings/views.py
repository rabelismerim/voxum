"""
Módulo de visualização (Views) para gerenciar as Assembleias e seus fluxos.
"""
from datetime import timedelta

from core.abstract.views import AbstractViewApi
from django.db.models import ExpressionWrapper, F, DurationField, Q
from django.http import JsonResponse, Http404
from django_celery_results.models import TaskResult
from drf_yasg import openapi
from rest_framework import permissions
from utils import doc, _

from apps.guest.tasks import SendInvitationLinkCiamTask, SendMeetingLinkTask
from apps.meetings.models import Meeting, Classe, RepresentativeMeeting, UserMeeting, MeetingGroup
from apps.meetings.schemas import (
    MeetingListSchema, MeetingSchema, MeetingUpdateSchema, ClasseSchema,
    ChoicesOptionsSchema, RepresentativeMeetingSchema, StartRegisterPresenceSerializer,
    ExtendRegisterPresenceSerializer, EndRegisterPresenceSerializer, UserMeetingSchema,
    UserMeetingCreateSchema, UserMeetingUpdateSchema, SuspendMeetingSchema,
    MeetingGroupSchema, MeetingBigNumbersSchema, MeetingGuestSchema,
    RepresentativeMeetingBigNumberSchema, MeetingDispatchLinkCiamSchema
)
from core.permissions.views import (
    IsUserManagerOrConsultantPermission,
    IsUserManagerOrReadOnlyConsultantPermission,
    IsUserGuestPermission
)
from core.views import AbstractApi


@doc(_("""Visualização da API para listar e criar Assembleias."""))
class MeetingListApi(AbstractViewApi):
    serializer_class = MeetingSchema
    layout_serializers = {
        'default': MeetingListSchema,
        'get': MeetingListSchema,
        'post': MeetingSchema,
    }
    query_params = [
        {
            "name": "start_date",
            "field": "start_date__gte",
            "in": "query",
            "required": False,
            "description": str(_("Data do inicio")),
            "schema": {"type": "date"}
        },
    ]
    model = Meeting
    model_query = Meeting.objects.all()
    http_method_names = ['get', 'post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]


@doc(_("""Visualização da API para gerenciar detalhes de uma Assembleia específica."""))
class MeetingDetailApi(AbstractApi):
    serializer_class = MeetingUpdateSchema
    layout_serializers = {
        'default': MeetingSchema,
        'get': MeetingSchema,
        'put': MeetingUpdateSchema,
    }
    model = Meeting
    model_query = Meeting.objects.all()
    http_method_names = ['put', 'get']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrReadOnlyConsultantPermission]
    filter_check_user_voting_permission = 'meeting__id'


@doc(_("""Visualização da API para recuperar os Big Numbers de uma Assembleia."""))
class MeetingBigNumberApi(AbstractApi):
    serializer_class = MeetingBigNumbersSchema
    model = Meeting
    model_query = Meeting.objects.all()
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrReadOnlyConsultantPermission]
    filter_check_user_voting_permission = 'meeting__id'


@doc(_("""Visualização da API para cadastrar representantes em uma Assembleia."""))
class RepresentativeMeetingApi(AbstractApi):
    serializer_class = RepresentativeMeetingSchema
    model = RepresentativeMeeting
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]


@doc(_("""Visualização da API para listar representantes de uma Assembleia."""))
class RepresentativeMeetingListApi(AbstractApi):
    serializer_class = RepresentativeMeetingBigNumberSchema
    model = RepresentativeMeeting
    model_query = RepresentativeMeeting.objects.all()
    http_method_names = ['get']
    pagination = True
    query_slug = True
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    filter_check_user_voting_permission = 'meeting__id'
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
            "name": "code",
            "field": "code",
            "in": "query",
            "required": False,
            "description": str(_("Código do credor")),
            "schema": {"type": "string"}
        },
        {
            "name": "recovering",
            "field": "representative__creditor__recovering__name__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Nome da recuperanda")),
            "schema": {"type": "string"}
        },
        {
            "name": "classe",
            "field": "representative__creditor__classe__description__in",
            "in": "query",
            "required": False,
            "description": str(_("Classe")),
            "schema": {
                "type": openapi.TYPE_ARRAY,
                "items": {"type": openapi.TYPE_STRING}
            }
        },
        {
            "name": "voting_id",
            "field": "voting_id",
            "in": "query",
            "required": False,
            "description": str(_("ID da votação")),
            "schema": {"type": "string"}
        },
    ]

    map_ordering_fields = {
        'legal_number': 'guest__entity__legal_number',
        'first_name': 'guest__user__first_name',
    }

    def get_query_parameters(self):
        parameters = super().get_query_parameters()
        parameters.pop("voting_id", None)
        return parameters


@doc(_("""Visualização da API para gerenciar Classes de Credores."""))
class ClasseApi(AbstractApi):
    serializer_class = ClasseSchema
    model = Classe
    model_query = Classe.objects.all()
    http_method_names = ['get', 'post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    cache_timeout = 60 * 60 * 24


@doc(_("""Opções de escolhas disponíveis na plataforma (Choices)."""))
class ChoicesOptionsApi(AbstractViewApi):
    http_method_names = ['get']
    serializer_class = ChoicesOptionsSchema
    query_params = [
        {
            "name": "option",
            "field": "option",
            "in": "query",
            "required": False,
            "description": str(_("Option")),
            "schema": {"type": "string"}
        }
    ]
    model = Meeting
    model_query = Meeting.objects.all()
    cache_timeout = 60 * 60 * 24

    def get(self, request, *args, **kwargs):
        data = {}
        option = request.query_params.get('option')
        descriptions = self.serializer_class(many=False).descriptions
        for key, field in self.serializer_class(many=False).fields.items():
            list_options = None
            if option:
                if option in key:
                    list_options = list(field.data)
            else:
                list_options = list(field.data)

            if list_options:
                data[key] = {
                    'description': descriptions.get(key, ''),
                    'options': list_options
                }
        return JsonResponse(data)


@doc(_("""Visualização para iniciar o registro de presença da Assembleia."""))
class StartRegisterPresenceView(AbstractApi):
    serializer_class = MeetingSchema
    layout_serializers = {
        'default': MeetingSchema,
        'get': MeetingSchema,
        'put': StartRegisterPresenceSerializer,
    }
    model = Meeting
    model_query = Meeting.objects.all()
    http_method_names = ['put']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    filter_check_user_voting_permission = 'meeting__id'


@doc(_("""Visualização para estender o tempo do registro de presença."""))
class ExtendRegisterPresenceView(AbstractApi):
    serializer_class = MeetingSchema
    layout_serializers = {
        'default': MeetingSchema,
        'get': MeetingSchema,
        'put': ExtendRegisterPresenceSerializer,
    }
    model = Meeting
    model_query = Meeting.objects.all()
    http_method_names = ['put']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    filter_check_user_voting_permission = 'meeting__id'


@doc(_("""Visualização para encerrar o processo de registro de presença."""))
class EndRegisterPresenceView(AbstractApi):
    serializer_class = MeetingSchema
    layout_serializers = {
        'default': MeetingSchema,
        'get': MeetingSchema,
        'put': EndRegisterPresenceSerializer,
    }
    model = Meeting
    model_query = Meeting.objects.all()
    http_method_names = ['put']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    filter_check_user_voting_permission = 'meeting__id'


@doc(_("""Visualização para recuperar instâncias de UserMeeting (papéis do usuário na assembleia)."""))
class UserMeetingView(AbstractApi):
    serializer_class = UserMeetingSchema
    model = UserMeeting
    model_query = UserMeeting.objects.all()
    http_method_names = ['get']
    query_slug = True
    tags = ['Meeting - Management']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]


@doc(_("""Visualização para criar papéis (UserMeeting) para usuários na assembleia."""))
class UserMeetingCreateView(AbstractApi):
    serializer_class = UserMeetingSchema
    layout_serializers = {
        'default': UserMeetingSchema,
        'post': UserMeetingCreateSchema,
    }
    model = UserMeeting
    model_query = UserMeeting.objects.all()
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    tags = ['Meeting - Management']


@doc(_("""Visualização para detalhar e atualizar instâncias de UserMeeting."""))
class UserMeetingDetailView(AbstractApi):
    serializer_class = UserMeetingSchema
    layout_serializers = {
        'default': UserMeetingSchema,
        'get': UserMeetingSchema,
        'put': UserMeetingUpdateSchema,
    }
    model = UserMeeting
    model_query = UserMeeting.objects.all()
    http_method_names = ['get', 'put']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    tags = ['Meeting - Management']


@doc(_("""Visualização para suspender uma Assembleia e criar uma nova (duplicação)."""))
class MeetingSuspendApi(AbstractApi):
    serializer_class = MeetingSchema
    layout_serializers = {
        'default': MeetingSchema,
        'put': SuspendMeetingSchema,
    }
    model = Meeting
    model_query = Meeting.objects.all()
    http_method_names = ['put']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    tags = ['Meeting']


@doc(_("""Visualização para gerenciar o agrupamento de Assembleias."""))
class MeetingGroupApi(AbstractApi):
    serializer_class = MeetingGroupSchema
    model = MeetingGroup
    model_query = MeetingGroup.objects.all()
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    tags = ['Meeting']


@doc(_("""Visualização da API para detalhamento da Assembleia sob a ótica do Guest."""))
class MeetingDetailGuestApi(AbstractApi):
    serializer_class = MeetingGuestSchema
    model = Meeting
    model_query = Meeting.objects.all()
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated, IsUserGuestPermission]
    many = False
    query_slug = True

    def filter(self, id_, **kwargs):
        query = self.get_queryset()
        query.update(self.get_query_slug())
        query.update(self.get_query_parameters())
        query.update(kwargs)
        query['id'] = id_

        obj = self.get_model().exclude(**self.get_exclude_queryset()).filter(
            Q(creditor__guest__user=self.request.user) | Q(representativemeeting__guest__user=self.request.user),
            **query
        ).first()

        if not obj:
            raise Http404
        return obj


@doc(_("""Inicia o processo de envio de link CIAM para os credores."""))
class StartDispatchLinkCiamView(AbstractApi):
    serializer_class = MeetingDispatchLinkCiamSchema
    model = Meeting
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]

    def post(self, request, *args, **kwargs):
        SendInvitationLinkCiamTask.delay(kwargs.get('id'))
        return JsonResponse({'status': 'ok'})


@doc(_("""Inicia o processo de envio do link da assembleia para credores e representantes."""))
class StartDispatchLinkMeetingView(AbstractApi):
    serializer_class = MeetingDispatchLinkCiamSchema
    model = Meeting
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    operation_id_base = 'ViewLinkMeeting'

    def post(self, request, *args, **kwargs):
        force = request.data.get('force')
        meeting_id = kwargs.get('id')
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        link = f'{protocol}://{host}/voxum/guest/{meeting_id}/'
        SendMeetingLinkTask.delay(link, meeting_id, force)
        return JsonResponse({'status': 'ok'})