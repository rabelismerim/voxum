from core.abstract.views import AbstractViewApi, CustomSchema as BaseSchema
from core.base_internal_user.models import STATUS_CHOICES
from django.contrib.auth.models import Group
from django.db import transaction
from django.http import JsonResponse, Http404
from drf_yasg import openapi
from rest_framework import permissions
from utils import _, get_user_model

from apps.voxum_base.utils import get_user_internal_group_names
from core.permissions.models import GroupUserGuest
from core.permissions.views import IsUserManagerPermission
from core.schemas import UserInternalEditSchema, VoxumGroupSchema, CustomUserInternalSchema


class CustomSchema(BaseSchema):
    pass


class AbstractApi(AbstractViewApi):
    swagger_schema = CustomSchema

    def create_object(self):
        with transaction.atomic():
            serializer_class = self.get_serializer_class()
            serializer = serializer_class(data=self.request.data, context={'request': self.request})
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()
        return obj

    def put(self, request, *args, **kwargs):
        """
        This method handles PUT requests for the view. It expects input data that conform to the serializer used by
        the view class. It updates the approved_calculation or date object of a specific comparative object using the
        given calculation_id from the query parameters and serializes the updated object in JSON format before
        returning it as an HTTP response.

        Parameters: request: The HTTP request object. args: Any additional positional arguments passed to the method.
        kwargs: Any additional keyword arguments passed to the method, with calculation_id identifying the
        comparative object to update. Returns: JsonResponse: An HTTP response containing the updated and serialized
        comparative object data.
        """
        with transaction.atomic():
            id_ = kwargs.get('id')
            exclude = self.get_exclude_values()
            serializer = self.get_serializer_class()
            query = self.get_queryset()
            model_objects = self.custom_objects or self.model.objects
            obj = model_objects.filter(id=id_, **query).first()

            if not obj:
                raise Http404
            serializer = serializer(instance=obj, data=request.data, exclude=exclude, context={'request': self.request})
            serializer.is_valid(raise_exception=True)
            obj = serializer.save()

        return JsonResponse(self.serializer_class(obj, many=False, context={'request': self.request}).data, safe=False)


class GroupApi(AbstractViewApi):
    """
    View API for Groups that contains a name and a list of permissions
    and defines what permissions the user has and what he can do within the system.

    Methods:
    - get: Returns a list of groups with their names and permissions.
    """
    allow_cache = False
    serializer_class = VoxumGroupSchema
    docs = {
        'init': _("""A classe `Group` representa um grupo de usuários no sistema. Contém propriedades comuns para
        gerenciar permissões de usuário e relacionamentos com o grupo. Ele contém uma propriedade `name` para
        identificar o grupo e também um campo `permissões` para definir as permissões atribuídas ao grupo. Os usuários
        podem ser adicionados a um grupo, que permite acesso a usuários pertencentes a um grupo específico.
        """),

        'get': _("""O grupo contém um nome e uma lista de permissões. Os grupos definem o que
        permissões que o usuário possui e o que ele pode fazer dentro do sistema.

        Retorna:
            JsonResponse: uma resposta JSON contendo uma lista de grupos.
        """)
    }

    permission_classes = [permissions.IsAuthenticated, IsUserManagerPermission]
    model = Group
    http_method_names = ['get']


class UserInternalApi(AbstractApi):
    """HTTP methods for interacting with internal user data."""
    docs = {
        'init': _("""A classe `User` representa um usuário no sistema, possui propriedades comuns como `username`
        `email`, `senha`, bem como informações adicionais como `role` , `status` , `first_name`, `last_name`
        `userpicture ` e `is_active` (se o usuário estiver ativo) Ele também pode ser um membro da equipe e ter acesso
        ao site de administração, conforme controlado pelo campo `is_staff`, alguns campos de permissão que podem ser
        usados para controlar o acesso
        aos recursos do sistema.
        O status(`Ativo`, `Inativo`, `Pendente`, `Rejeitado`, `Férias`) controla se o usuário está ativo ou
        inativo.
        """),
        'get': _("""Obtenha a lista de todos os usuários. Inclui campos de usuário como `nome`, `userpicture`, `lista
        de permissões`, etc.

        Retorna:
            JsonResponse: uma resposta JSON contendo os dados serializados dos usuários.
        """),
    }
    serializer_class = CustomUserInternalSchema
    layout_serializers = {
        'default': CustomUserInternalSchema,
        'get': CustomUserInternalSchema,
        'put': UserInternalEditSchema,
    }
    permission_classes = [permissions.IsAuthenticated, IsUserManagerPermission]
    model = get_user_model()
    allow_cache = False
    http_method_names = ['get']
    pagination = True

    query_params = [
        {
            "name": "userinternal",
            "field": "userinternal",
            "in": "query",
            "required": False,
            "description": str(_("Selecionar usuários convidados ou internos")),
            "schema": {"type": "bool"}
        },
        {
            "name": "first_name",
            "field": "first_name__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Selecionar usuários pelo nome")),
            "schema": {"type": "string"}
        },
        {
            "name": "email",
            "field": "email__icontains",
            "in": "query",
            "required": False,
            "description": str(_("Selecionar usuários pelo email")),
            "schema": {"type": "string"}
        },
        {
            "name": "is_active",
            "field": "is_active",
            "in": "query",
            "required": False,
            "description": str(_("Selecionar usuários ativos/inativos")),
            "schema": {"type": "bool"}
        },
        {
            "name": "status",
            "field": "status__in",
            "in": "query",
            "required": False,
            "description": str(_("Selecionar usuários pelo status")),
            "schema": {"type": openapi.TYPE_ARRAY,
                       "items": {"type": openapi.TYPE_STRING,
                                 "enum": [str(status[0]) for status in STATUS_CHOICES]}}
        },
    ]

    def get_query_parameters(self):
        parameters = super().get_query_parameters()
        parameters.pop("userinternal", None)
        return parameters

    def filter(self, id_, **kwargs):
        userinternal = self.request.query_params.get("userinternal")

        filtered_queryset = super().filter(id_, **kwargs)

        if userinternal is not None:
            if str(userinternal).lower() in ['true', 'yes', 'verdadeiro', 'verdade', 'on']:
                filtered_queryset = filtered_queryset.filter(groups__name__in=get_user_internal_group_names())
            else:
                filtered_queryset = filtered_queryset.filter(groups__name=GroupUserGuest)

        return filtered_queryset


class UserInternalDetailApi(UserInternalApi):
    http_method_names = ['get', 'put']
    pagination = False
    many = False
    docs = {
        'init': _("""A classe `User` representa um usuário no sistema, possui propriedades comuns como `username`
        `email`, `senha`, bem como informações adicionais como `role` , `status` , `first_name`, `last_name`
        `userpicture ` e `is_active` (se o usuário estiver ativo) Ele também pode ser um membro da equipe e ter acesso
        ao site de administração, conforme controlado pelo campo `is_staff`, alguns campos de permissão que podem ser
        usados para controlar o acesso
        aos recursos do sistema.
        O status(`Ativo`, `Inativo`, `Pendente`, `Rejeitado`, `Férias`) controla se o usuário está ativo ou
        inativo.
        """),
        'get': _("""Obtenha a lista de todos os usuários. Inclui campos de usuário como `nome`, `userpicture`, `lista
        de permissões`, etc.

        Retorna:
            JsonResponse: uma resposta JSON contendo os dados serializados do usuário.
        """),

        'put': _("""Lida com uma solicitação PUT para atualizar o user com base no seu ID.

        Retorna:
            JsonResponse: uma resposta JSON contendo os dados serializados do user."""),
    }


class UserInternalDetailGuestApi(UserInternalApi):
    http_method_names = ['get']
    docs = {
        'init': _("""A classe `User` representa um usuário no sistema, possui propriedades comuns como `username`
        `email`, `senha`, bem como informações adicionais como `role` , `status` , `first_name`, `last_name`
        `userpicture ` e `is_active` (se o usuário estiver ativo) Ele também pode ser um membro da equipe e ter acesso
        ao site de administração, conforme controlado pelo campo `is_staff`, alguns campos de permissão que podem ser
        usados para controlar o acesso
        aos recursos do sistema.
        O status(`Ativo`, `Inativo`, `Pendente`, `Rejeitado`, `Férias`) controla se o usuário está ativo ou
        inativo.
        """),
        'get': _("""Obtenha a lista de todos os usuários. Inclui campos de usuário como `nome`, `userpicture`, `lista
        de permissões`, etc.

        Retorna:
            JsonResponse: uma resposta JSON contendo os dados serializados do usuário.
        """),

        'put': _("""Lida com uma solicitação PUT para atualizar o user com base no seu ID.

        Retorna:
            JsonResponse: uma resposta JSON contendo os dados serializados do user."""),
    }
    permission_classes = [permissions.IsAuthenticated]

    default_query_params = []
    many = False
    pagination = False
    operation_id_base = 'UserDetail'

    def get_queryset(self):
        return self.model.objects.filter(id=self.request.user.id)