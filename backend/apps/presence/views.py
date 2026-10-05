from rest_framework import permissions
from utils import doc, _

from apps.presence.models import Presence, PresenceRepresentative
from apps.presence.schemas import (PresenceSchema, PresenceArrivalSchema, PresenceDepartureSchema,
                                   PresenceDetailSchema, PresenceGuestSchema, PresenceRepresentativeSchema,
                                   PresenceToRepresentativeSchema,
                                   PresenceRepresentativeGuestSchema)
from core.permissions.views import IsUserGuestPermission, IsUserManagerOrConsultantPermission
from core.views import AbstractApi


@doc(_("""Visualização da API para lidar com a Presença do Credor."""))
class PresenceApi(AbstractApi):
    serializer_class = PresenceSchema
    model = Presence
    model_query = Presence.objects.all()
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]


@doc(_("""Visualização da API para lidar com a Presença do Representante pelo usuário representante."""))
class PresenceToRepresentativeApi(AbstractApi):
    serializer_class = PresenceToRepresentativeSchema
    model = PresenceRepresentative
    model_query = PresenceRepresentative.objects.all()
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    filter_check_user_voting_permission = 'meeting__representativemeeting__representative__id'


@doc(_("""Visualização da API para detalhes da Presença do Credor."""))
class PresenceDetailApi(AbstractApi):
    serializer_class = PresenceSchema
    layout_serializers = {
        'default': PresenceSchema,
        'put': PresenceDetailSchema,
    }
    model = Presence
    model_query = Presence.objects.all()
    http_method_names = ['put']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]


@doc(_("""Visualização da API para registrar a chegada do Credor."""))
class PresenceArrivalApi(AbstractApi):
    serializer_class = PresenceSchema
    layout_serializers = {
        'default': PresenceSchema,
        'put': PresenceArrivalSchema,
    }
    model = Presence
    model_query = Presence.objects.all()
    http_method_names = ['put']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]


@doc(_("""Visualização da API para registrar a saída do Credor."""))
class PresenceDepartureApi(AbstractApi):
    serializer_class = PresenceSchema
    layout_serializers = {
        'default': PresenceSchema,
        'put': PresenceDepartureSchema,
    }
    model = Presence
    model_query = Presence.objects.all()
    http_method_names = ['put']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]


@doc(_("""Visualização da API para lidar com a Presença do Guest."""))
class PresenceGuestApi(AbstractApi):
    serializer_class = PresenceGuestSchema
    model = Presence
    model_query = Presence.objects.all()
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated, IsUserGuestPermission]


@doc(_("""Visualização da API para lidar com Representantes pela gestão/administração."""))
class PresenceRepresentativeManagementApi(AbstractApi):
    serializer_class = PresenceRepresentativeSchema
    model = Presence
    model_query = Presence.objects.all()
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    filter_check_user_voting_permission = 'meeting__representativemeeting__id'


@doc(_("""Visualização da API para lidar com Representantes pelo usuário Guest."""))
class PresenceRepresentativeGuestApi(AbstractApi):
    serializer_class = PresenceRepresentativeGuestSchema
    model = Presence
    model_query = Presence.objects.all()
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated]