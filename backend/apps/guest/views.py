from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from utils import doc, _

from apps.guest.models import UserGuest
from apps.guest.schemas import UserGuestSchema, UserGuestDetailSchema, UserGuestCiamSchema
from core.permissions.views import IsUserGuestPermission, IsUserManagerOrConsultantPermission, \
    IsUserManagerOrReadOnlyConsultantPermission
from core.views import AbstractApi


@doc("""Visualização da API para lidar com Usuários convidados.

    Em uma assembleia para votação, um "credor" se refere a um indivíduo, entidade ou organização que tem direitos de
    voto ou representação em questões relacionadas a créditos, dívidas ou obrigações financeiras. Ocorre em
    uma assembleia de credores em processos de falência, reestruturação financeira ou acordos de pagamento.

    Para registrar os credores que podem ter acesso a plataforma para votação, deve ser registrado o UserGuest com as
    informações para identificação e autenticação.

    Métodos HTTP suportados:
        - GET
        - POST
    """)
class UserGuestApi(AbstractApi):
    serializer_class = UserGuestSchema
    model = UserGuest
    model_query = UserGuest.objects.all()
    http_method_names = ['get', 'post']
    pagination = True
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    query_params = [
        {
            "name": "is_representative",
            "field": "is_representative",
            "in": "query",
            "required": False,
            "description": str(_("Usuários que são ou não são representantes")),
            "schema": {"type": "bool"}
        },
    ]
    docs = {'get': _("""Lida com uma solicitação GET para recuperar os usuários convidados.

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados dos usuários."""),

            'post': _("""Lida com uma solicitação POST para criar um usuário convidado.

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados do usuário."""),
            }

    def get_queryset(self):
        return {'msaluserguest__isnull': False}


@doc("""Visualização da API para lidar com Usuários convidados.

    Em uma assembleia para votação, um "credor" se refere a um indivíduo, entidade ou organização que tem direitos de
    voto ou representação em questões relacionadas a créditos, dívidas ou obrigações financeiras. Ocorre em
    uma assembleia de credores em processos de falência, reestruturação financeira ou acordos de pagamento.

    Para registrar os credores que podem ter acesso a plataforma para votação, deve ser registrado o UserGuest com as
    informações para identificação e autenticação.

    Métodos HTTP suportados:
        - GET
        - POST
    """)
class UserGuestDetailApi(AbstractApi):
    serializer_class = UserGuestDetailSchema
    model = UserGuest
    model_query = UserGuest.objects.all()
    http_method_names = ['put', 'get']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrReadOnlyConsultantPermission]

    docs = {'put': _("""Lida com uma solicitação PUT para editar um usuário convidado com base no seu ID.

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados do usuário."""),
            }


# To Guest
@doc("""Visualização da API para lidar com Usuários convidados.

    Em uma assembleia para votação, um "credor" se refere a um indivíduo, entidade ou organização que tem direitos de
    voto ou representação em questões relacionadas a créditos, dívidas ou obrigações financeiras. Ocorre em
    uma assembleia de credores em processos de falência, reestruturação financeira ou acordos de pagamento.

    Para registrar os credores que podem ter acesso a plataforma para votação, deve ser registrado o UserGuest com as
    informações para identificação e autenticação.

    Métodos HTTP suportados:
        - GET
    """)
class UserGuestDetailApiGuest(AbstractApi):
    serializer_class = UserGuestDetailSchema
    model = UserGuest
    model_query = UserGuest.objects.all()
    http_method_names = ['get']
    permission_classes = [permissions.IsAuthenticated, IsUserGuestPermission]
    many = False
    docs = {'put': _("""Lida com uma solicitação GET para exibir um usuário convidado com base no usuário logado.

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados do usuário."""),
            }

    query_params = []

    def get_queryset(self):
        return {'user': self.request.user}


# To Guest
@doc("""Visualização da API para lidar com Usuários convidados.

    Em uma assembleia para votação, um "credor" se refere a um indivíduo, entidade ou organização que tem direitos de
    voto ou representação em questões relacionadas a créditos, dívidas ou obrigações financeiras. Ocorre em
    uma assembleia de credores em processos de falência, reestruturação financeira ou acordos de pagamento.

    Para registrar os credores que podem ter acesso a plataforma para votação, deve ser registrado o UserGuest com as
    informações para identificação e autenticação.

    Métodos HTTP suportados:
        - GET
    """)
class UserGuestResetOtpView(AbstractApi):
    serializer_class = UserGuestCiamSchema
    model = UserGuest
    http_method_names = ['post']
    permission_classes = [permissions.IsAuthenticated, IsUserManagerOrConsultantPermission]
    many = False
    docs = {'post': _("""Lida com uma solicitação POST para resetar o otp de um UserGuest

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados do pedido de reset."""),
            }

    query_params = []

    def get_user_guest(self, request, *args, **kwargs):
        user_guest_id = kwargs.get('id')
        return get_object_or_404(self.model, id=user_guest_id)

    def post(self, request, *args, **kwargs):
        user_guest = self.get_user_guest(request, *args, **kwargs)
        response = user_guest.user_ciam_reset_otp(request.user.email)

        return self.response(response, response['status'])


class UserGuestRevokeOtpView(UserGuestResetOtpView):
    operation_id_base = 'RevokeOtpView'
    docs = {'post': _("""Lida com uma solicitação POST para revogar o otp de um UserGuest

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados do pedido de revogação."""),
            }

    def post(self, request, *args, **kwargs):
        user_guest = self.get_user_guest(request, *args, **kwargs)
        response = user_guest.user_ciam_revoke_otp(request.user.email)
        return self.response(response, response['status'])


class UserGuestResetPasswordView(UserGuestResetOtpView):
    operation_id_base = 'ResetPasswordView'
    docs = {'post': _("""Lida com uma solicitação POST para resetar a senha de um UserGuest

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados do pedido de reset."""),
            }

    def post(self, request, *args, **kwargs):
        user_guest = self.get_user_guest(request, *args, **kwargs)
        response = user_guest.user_ciam_reset_password(request.user.email)
        return self.response(response, response['status'])


class UserGuestSendInviteCiamView(UserGuestResetOtpView):
    operation_id_base = 'SendInvite'
    docs = {'post': _("""Lida com uma solicitação POST para reenviar um convite de CIAM ao UserGuest

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados do pedido de reenvio."""),
            }

    def post(self, request, *args, **kwargs):
        user_guest = self.get_user_guest(request, *args, **kwargs)
        response = user_guest.sent_invite_ciam()
        return self.response(response, response['status'])


class UserGuestReSendInviteCiamView(UserGuestResetOtpView):
    operation_id_base = 'ReSendInvite'
    docs = {'post': _("""Lida com uma solicitação POST para reenviar um convite de CIAM ao UserGuest

    Retorna:
        JsonResponse: uma resposta JSON contendo os dados serializados do pedido de reenvio."""),
            }

    def post(self, request, *args, **kwargs):
        user_guest = self.get_user_guest(request, *args, **kwargs)
        response = user_guest.resend_invite()
        return self.response(response, response['status'])
