from django.db.models import Q
from django.http import Http404
from rest_framework.permissions import BasePermission
from utils import _

from apps.creditor.models import Creditor
from apps.guest.models import UserGuest
from apps.meetings.models import Meeting
from apps.voting.models import Voting, Choice
from core.permissions.models import CustomPermissionChoices
from config.settings import BASE_API_URL


class VotingPostPermission(BasePermission):
    """
    Check if voting has the correct permission to access the requested view.

    Methods:
        has_permission(request, view):
            Check if the voting has permission to access the requested view.

            Args:
                request: the HTTP request object
                view: the view being accessed

            :return:
                True if the user has permission, False otherwise
    """
    message = _('A votação não pode ser aberta neste momento. Verifique o status da assembleia.')

    def has_permission(self, request, view):
        """
        Check if the voting has permission to access the requested view.

        Args:
            request: the HTTP request object
            view: the view being accessed

        :return:
            True if the user has permission, False otherwise
        """
        if request.path == f'/{BASE_API_URL}docs/redoc/':
            return True
        meeting_id = request.data.get('meeting_id')
        meeting = Meeting.objects.filter(id=meeting_id).first()
        if not meeting:
            self.message = _('A votação para esta assembleia não foi encontrada.')
            return False
        errors = meeting.get_is_ability_to_create_voting_errors()

        if errors:
            self.message = '. '.join([str(err) for err in errors])
            return False
        return True


def is_swagger(path):
    return path.startswith(f'/{BASE_API_URL}docs/redoc/')


class VotingPermission(BasePermission):
    """
    Check if voting has the correct permission to access the requested view.

    Methods:
        has_permission(request, view):
            Check if the voting has permission to access the requested view.

            Args:
                request: the HTTP request object
                view: the view being accessed

            :return:
                True if the user has permission, False otherwise
    """
    message = _('A votação não pode ser aberta neste momento. Verifique o status da assembleia.')

    def has_permission(self, request, view):
        """
        Check if the voting has permission to access the requested view.

        Args:
            request: the HTTP request object
            view: the view being accessed

        :return:
            True if the user has permission, False otherwise
        """

        if is_swagger(request.path) or request.method == "DELETE":
            return True
        meeting_id = view.kwargs.get('id')
        errors = Voting.objects.filter(id=meeting_id).first().meeting.get_is_ability_to_create_voting_errors()

        if errors:
            self.message = '. '.join([str(err) for err in errors])
            return False
        return True


class ChoiceVotingPostPermission(BasePermission):
    """
    Check if voting has the correct permission to access the requested view.

    Methods:
        has_permission(request, view):
            Check if the voting has permission to access the requested view.

            Args:
                request: the HTTP request object
                view: the view being accessed

            :return:
                True if the user has permission, False otherwise
    """
    message = _('A votação não pode ser aberta neste momento. Verifique o status da Votação.')

    def has_permission(self, request, view):
        """
        Check if the voting has permission to access the requested view.

        Args:
            request: the HTTP request object
            view: the view being accessed

        :return:
            True if the user has permission, False otherwise
        """
        if is_swagger(request.path):
            return True
        voting_id = request.data.get('voting_id')
        return Voting.objects.filter(id=voting_id).first().is_ability_to_create_choice()


class ChoiceVotingPermission(BasePermission):
    """
    Check if choice has the correct permission to access the requested view.

    Methods:
        has_permission(request, view):
            Check if the choice has permission to access the requested view.

            Args:
                request: the HTTP request object
                view: the view being accessed

            :return:
                True if the user has permission, False otherwise
    """
    message = _('A votação não pode ser aberta neste momento. Verifique o status da Votação.')

    def has_permission(self, request, view):
        """
        Check if the choice has permission to access the requested view.

        Args:
            request: the HTTP request object
            view: the view being accessed

        :return:
            True if the user has permission, False otherwise
        """
        if is_swagger(request.path):
            return True
        voting_id = view.kwargs.get('id')
        choice = Choice.objects.filter(id=voting_id).first()
        if not choice:
            raise Http404
        return choice.voting.is_ability_to_create_choice()


class IsUserManagerOrConsultantPermission(BasePermission):
    """
    Check if user has the correct permission to access the requested view.
    """
    message = _('Apenas gerentes ou consultores internos podem acessar essa área')

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the requested view, based on the group he is in

        Args:
            request: the HTTP request object
            view: the view being accessed

        :return:
            True if the user has permission, False otherwise
        """
        return request.user.has_perm(CustomPermissionChoices.MANAGER_PROJECT) or request.user.has_perm(
            CustomPermissionChoices.CONSULTANT_PROJECT)


class IsUserManagerOrReadOnlyConsultantPermission(BasePermission):
    """
    Check if user has the correct permission to access the requested view.
    """
    message = _('Apenas gerentes ou consultores internos podem acessar essa área')

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the requested view, based on the group he is in

        Args:
            request: the HTTP request object
            view: the view being accessed

        :return:
            True if the user has permission, False otherwise
        """
        method = request.method.upper()
        if method == 'GET':
            return request.user.has_perm(CustomPermissionChoices.MANAGER_PROJECT) or request.user.has_perm(
                CustomPermissionChoices.CONSULTANT_PROJECT)

        self.message = _('Apenas gerentes internos podem acessar essa área')
        return request.user.has_perm(CustomPermissionChoices.MANAGER_PROJECT)


class IsUserManagerPermission(BasePermission):
    """
    Check if user has the correct permission to access the requested view.
    """
    message = _('Apenas gerentes internos podem acessar essa área')

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the requested view, based on the group he is in

        Args:
            request: the HTTP request object
            view: the view being accessed

        :return:
            True if the user has permission, False otherwise
        """
        return request.user.has_perm(CustomPermissionChoices.MANAGER_PROJECT)


class IsUserConsultantPermission(BasePermission):
    """
    Check if user has the correct permission to access the requested view.
    """
    message = _('Apenas usuários internos podem acessar essa área')

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the requested view, based on the group he is in

        Args:
            request: the HTTP request object
            view: the view being accessed

        :return:
            True if the user has permission, False otherwise
        """
        return request.user.has_perm(CustomPermissionChoices.CONSULTANT_PROJECT)


class IsUserGuestPermission(BasePermission):
    """
    Check if user has the correct permission to access the requested view.
    """
    message = _('Apenas usuários convidados podem acessar essa área')

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the requested view, based on the group he is in

        Args:
            request: the HTTP request object
            view: the view being accessed

        :return:
            True if the user has permission, False otherwise
        """
        return hasattr(request.user, 'userguest')


class BasePermissionSockets(BasePermission):

    def __init__(self, **kwargs):
        self.scope = kwargs.pop('scope', None)
        super().__init__(**kwargs)

    def has_sockets_permission(self):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        if not self.scope:
            return False
        return True


class CheckUserVotingPermissionSockets(BasePermissionSockets):
    """
    Exemplo de classe de permissão personalizada.
    Você pode personalizar os métodos como `has_permission`, `has_object_permission`, etc.
    """
    message = _('Apenas usuários internos com permissão para visualizar projeto podem acessar essa área')

    def has_sockets_permission(self):
        scope = self.scope
        user = scope['user']
        return user.has_perm(CustomPermissionChoices.CONSULTANT_PROJECT) or user.has_perm(
            CustomPermissionChoices.MANAGER_PROJECT)


class CheckGuestUserMeetingPermissionSockets(BasePermissionSockets):
    """
    Exemplo de classe de permissão personalizada.
    Você pode personalizar os métodos como `has_permission`, `has_object_permission`, etc.
    """
    message = _('Apenas usuários Guest convidados para essa Assembleia podem acessar essa área')

    def has_sockets_permission(self):
        scope = self.scope
        meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        user = scope['user']
        return UserGuest.objects.filter(
            Q(creditor__meeting_id=meeting_id) | Q(representativemeeting__meeting_id=meeting_id), user=user).exists()


class ChoiceGuestVoteChoicePostPermission(BasePermission):
    """
    Check if voting has the correct permission to access the requested view.

    Methods:
        has_permission(request, view):
            Check if the voting has permission to access the requested view.

            Args:
                request: the HTTP request object
                view: the view being accessed

            :return:
                True if the user has permission, False otherwise
    """
    message = _('A votação não pode ser aberta neste momento. Verifique o status da Votação.')

    def has_permission(self, request, view):
        """
        Check if the voting has permission to access the requested view.

        Args:
            request: the HTTP request object
            view: the view being accessed

        :return:
            True if the user has permission, False otherwise
        """
        if is_swagger(request.path):
            return True

        voting_id = request.data.get('vote_id')
        creditor_id = request.data.get('creditor_id')
        voting = Voting.objects.filter(choice__id=voting_id).first()

        if not voting:
            self.message = _('A votação não foi encontrada.')
            return False

        if not voting.check_started_voting():
            return False

        creditor = self.get_creditor_by_id(request, creditor_id)

        if not creditor:
            self.message = _('Credor não encontrado.')
            return False

        if not creditor.is_accredited:
            self.message = _('Credor não credenciado.')
            return False

        return True

    def get_creditor_by_id(self, request, creditor_id):
        return Creditor.objects.filter(id=creditor_id, guest__user_id=request.user.id).first()


class ChoiceGuestByInternalVoteChoicePostPermission(ChoiceGuestVoteChoicePostPermission):
    def get_creditor_by_id(self, request, creditor_id):
        return Creditor.objects.filter(id=creditor_id).first()


class ChoiceRepresentativeVoteChoicePostPermission(BasePermission):
    """
    Check if voting has the correct permission to access the requested view, by representatives

    Methods:
        has_permission(request, view):
            Check if the voting has permission to access the requested view.

            Args:
                request: the HTTP request object
                view: the view being accessed

            :return:
                True if the user has permission, False otherwise
    """
    message = _('A votação não pode ser aberta neste momento. Verifique o status da Votação.')

    def has_permission(self, request, view):
        """
        Check if the voting has permission to access the requested view.

        Args:
            request: the HTTP request object
            view: the view being accessed

        :return:
            True if the user has permission, False otherwise
        """
        if is_swagger(request.path):
            return True

        vote_ids = []
        creditor_ids = []

        for creditor in request.data['creditors_voting']:
            creditor_ids.append(creditor['creditor_id'])
            vote_ids.append(creditor['vote_id'])

        vote_ids = list(set(vote_ids))
        creditor_ids = list(set(creditor_ids))

        votes = Voting.objects.filter(choice__id__in=vote_ids)

        for vote_id in vote_ids:

            vote = votes.filter(choice__id=vote_id).first()

            if not vote:
                self.message = _('A votação não foi encontrada.')
                return False

            if not vote.check_started_voting():
                return False

        creditors = Creditor.objects.filter(id__in=creditor_ids)

        for creditor in creditors:

            creditor = creditors.filter(id=creditor.id).first()

            if not creditor:
                self.message = _('Credor não encontrado.')
                return False

            # TODO: definir regra de negócio para saber se o User Interno precisa fazer a validação
            if not creditor.is_accredited:
                self.message = _('Credor não credenciado.')
                return False

        return True