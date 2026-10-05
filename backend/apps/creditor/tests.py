import datetime
import json
import logging
import secrets

import requests
from apps.voxum_base.base_tests import BaseTests
from apps.voxum_base.exceptions import ValidationErrorAdapter
from apps.voxum_base.tests import AbstractTest
from apps.voxum_base.models import Coin, Entity
from config.settings import TOKEN_TEST
from django.utils import timezone
from faker import Faker
from model_bakery import baker
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from utils import get_user_model, secret_number

from apps.creditor.models import Creditor, Representative
from apps.guest.models import UserGuest
from apps.meetings.models import Meeting, Classe, StatusMeetingChoices, RepresentativeMeeting
from apps.presence.models import Presence
from apps.recovering.models import Recovering
from apps.voting.models import Voting, Choice, StatusVotingChoice
from config.settings import HOST_TESTS, HOST_VERIFY

User = get_user_model()
faker = Faker()


def fake_model_data(model, quantity, **attrs):
    return baker.make(model, _quantity=quantity, **attrs)


def get_user():
    return fake_model_data(User, 1,
                           **{'email': f'fk_{secret_number(min_value=111111, max_value=999999)}_{faker.email()}',
                              'first_name': faker.name(), 'last_name': faker.name()})[
        0]


def get_fake_entity():
    return \
        fake_model_data(Entity, 1, **{'legal_number': f'{secret_number(min_value=1111111111, max_value=99999999999)}'})[
            0]


def get_guest():
    user = get_user()
    entity = get_fake_entity()
    return fake_model_data(UserGuest, 1, **{'user_id': user.id, 'entity_id': entity.id, 'is_representative': True})[0]


def get_meeting():
    meeting = Meeting.objects.first()
    if not meeting:
        meeting = fake_model_data(Meeting, 1, **{'name': faker.name(), 'description': faker.name()})[0]
    return meeting


def get_recovering():
    recovering = Recovering.objects.first()
    if recovering:
        return recovering
    return fake_model_data(Recovering, 1, **{'name': faker.name()})[0]


def get_coin():
    return fake_model_data(Coin, 1, **{'type': 'B'})[0]


def get_creditor(new=True):
    creditor_data = {'guest_id': get_guest().id, 'meeting_id': get_meeting().id}
    if not new:
        creditor = Creditor.objects.filter(**creditor_data).first()
        if creditor:
            return creditor
    return fake_model_data(Creditor, 1, **creditor_data)[0]


def get_classe_id():
    values = ['CLASSE I', 'CLASSE II', 'CLASSE III', 'CLASSE IV']
    class_name = secrets.choice(values).strip().title()

    try:
        return Classe.objects.filter(description__icontains=class_name).first().id
    except AttributeError:
        return fake_model_data(Classe, 1, **{'description': class_name})[0].id


def get_token(user):
    return Token.objects.get_or_create(user=user)[0]


def get_creditor_data():
    meeting = get_meeting()
    guest = get_guest()
    return {
        "guest_id": guest.id,
        "meeting_id": meeting.id,
        "classe_id": get_classe_id(),
        "recovering_id": get_recovering().id,
        "coin": {
            "type": "B"
        },
        "type_person": "F",
        "credit_value": 110,
        "converted_value": 110,
        "exchange_tax": 110,
        "contested_value": 110,
        "priority": 1
    }


all_creditors = list(Creditor.objects.filter(meeting_id=get_meeting().id, votingresult__isnull=True))


class AbstractCreditor(BaseTests):
    def create_creditor_url(self):
        path = 'creditor'
        url = self.format_url(path, {})
        creditor_data = get_creditor_data()
        payload = json.dumps(creditor_data, default=str)
        data = {'payload': payload, 'url': url}
        self.token = TOKEN_TEST

        response = requests.post(HOST_TESTS + url, payload, headers=self.get_headers(), verify=HOST_VERIFY, timeout=30)
        response = self.return_response(data, response)
        if response['success']:
            return Creditor.objects.filter(id=response['content']['id']).first()

    def get_creditor(self):
        creditor_data = get_creditor_data()
        creditor_data["coin"] = get_coin()
        return baker.make(Creditor, _quantity=1, **creditor_data)[0]

    def get_creditor_parameters(self, create_token=True):
        creditor = self.get_creditor()
        VotingDetail().start_voting()
        self.register_creditor_presence(creditor)

        if create_token:
            self.token = get_token(user=creditor.guest.user)

        classe_creditor = creditor.classe.id
        return {
            "vote_id": VotingChoiceDetail().get_choice(classe_creditor).id,
            "creditor_id": creditor.id,
            "has_reservations": False,
        }

    def register_creditor_presence(self, creditor):
        try:
            Presence.objects.create(creditor=creditor, is_accredited=True, accredited_by=creditor.guest.user,
                                    accredited_date=timezone.now())
        except (ValidationError, ValidationErrorAdapter):
            pass


class TestPostCreditor(AbstractTest):
    path = 'creditor'
    http_method_names = ['post']

    def parameters(self):
        return get_creditor_data()


class TestGetCreditor(AbstractTest):
    path = 'creditor_detail'
    http_method_names = ['get']

    @property
    def path_parameters(self):
        return {
            'id': get_creditor(new=False).id
        }


class VotingDetail:
    time_str = '01:00:00'
    time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S').time()

    @property
    def voting(self):
        meeting_id = get_meeting().id
        voting = Voting.objects.filter(meeting_id=meeting_id, status=StatusVotingChoice.INICIADA).first()

        if not voting:
            voting = Voting.objects.filter(meeting_id=meeting_id).first()

        if not voting:
            voting = fake_model_data(Voting, 1, **{'meeting_id': meeting_id, 'description': 'Teste de votação?'})[0]

        if voting.meeting.status != StatusMeetingChoices.INITIALIZED:
            voting.meeting.status = StatusMeetingChoices.INITIALIZED
            voting.meeting.able_to_register_presence = False
            voting.meeting.save()

        return voting

    def start_voting(self):
        try:
            self.voting.meeting.end_register_presence_voting()
        except (ValidationError, ValidationErrorAdapter):
            pass

        if self.voting.status != StatusVotingChoice.INICIADA:
            try:
                self.voting.start_voting(self.time_obj)
            except (ValidationError, ValidationErrorAdapter):
                pass


class VotingChoiceDetail:
    def get_choice(self, classe_id):
        values = ['Talvez', 'Sim', 'Não']
        voting_id = VotingDetail().voting.id
        randon_value = secrets.choice(values).strip().title()

        choice = Choice.objects.filter(voting_id=voting_id, classe_id=classe_id,
                                       value=randon_value).first()

        if not choice:
            choice = \
                fake_model_data(Choice, 1,
                                **{'voting_id': voting_id, 'classe_id': classe_id,
                                   'value': randon_value})[0]
        return choice


class TestPostVotingGuestCreditor(AbstractTest, AbstractCreditor):
    path = 'create_guest_result'
    http_method_names = ['post']

    def parameters(self):
        return self.get_creditor_parameters(create_token=True)


class TestPostVotingSystemCreditor(TestPostVotingGuestCreditor):
    path = 'create_system_voting_result'

    def parameters(self):
        return self.get_creditor_parameters(create_token=False)


class TestPostVotingSystemExistsCreditor(TestPostVotingGuestCreditor):
    path = 'create_system_voting_result'
    token = TOKEN_TEST

    def test_api_a_post(self):
        url = self.format_url(self.path, {})
        params = self.get_parameters()
        payload = json.dumps(params, default=str)
        data = {'payload': payload, 'url': url}
        self.token = TOKEN_TEST
        response = requests.post(HOST_TESTS + url, payload, headers=self.get_headers(), verify=HOST_VERIFY, timeout=30)
        response = self.return_response(data, response)
        return response

    def get_creditor(self):
        try:
            return all_creditors.pop()
        except IndexError:
            logging.error('Lista de credores sem votar vazia')
            raise ValidationErrorAdapter('Lista de credores sem votar vazia')

    def get_creditor_parameters(self, create_token=False):
        creditor = self.get_creditor()
        self.register_creditor_presence(creditor)
        classe_creditor = creditor.classe.id
        return {
            "vote_id": VotingChoiceDetail().get_choice(classe_creditor).id,
            "creditor_id": creditor.id,
            "has_reservations": False,
        }

    def parameters(self):
        return self.get_creditor_parameters(create_token=False)


class TestPostAccreditedCreditor(TestPostVotingGuestCreditor):
    path = 'accredited_guest'
    http_method_names = ['post']

    def parameters(self):
        creditor = self.get_creditor()
        voting_detail = VotingDetail()
        voting_detail.start_voting()

        self.token = Token.objects.get_or_create(user=creditor.guest.user)[0]
        self.path_parameters = {
            'meeting_id': voting_detail.voting.meeting.id
        }
        return {}


class TestPostVotingSystemCreditorByRepresentatives(TestPostVotingGuestCreditor):
    path = 'create_representatives_voting_result'
    _representative_meeting = None
    _path_parameters = None

    @property
    def representative_meeting(self):
        if self._representative_meeting:
            return self._representative_meeting
        meeting = self.get_representative_meeting()
        self._representative_meeting = meeting
        return meeting

    @property
    def path_parameters(self):
        path_parameters = {
            'representative_id': self.representative_meeting.id
        }
        self._path_parameters = path_parameters
        self._representative_meeting = None
        return path_parameters

    @property
    def meeting_id(self):
        return get_meeting().id

    def parameters(self):
        representative_meeting = self.representative_meeting
        creditors = []

        for _ in range(5):
            creditor = self.get_creditor_parameters(False)
            representative_data = {
                'priority': 1,
                'representative_id': representative_meeting.id,
                'creditor_id': creditor['creditor_id'],
                'online': True,
            }

            fake_model_data(Representative, 1, **representative_data)[0]
            creditors.append(creditor)

        parameters = {
            "creditors_voting": creditors,
            "meeting_id": self.meeting_id
        }

        return parameters

    def get_representative_meeting(self):
        guest = get_guest()
        params = {
            "meeting_id": self.meeting_id,
            "guest_id": guest.id
        }
        return fake_model_data(RepresentativeMeeting, 1, **params)[0]

    def create_representative_url(self, params):
        path = 'create_representative'
        url = self.format_url(path, {})
        payload = json.dumps(params, default=str)
        data = {'payload': payload, 'url': url}
        self.token = TOKEN_TEST
        response = requests.post(HOST_TESTS + url, payload, headers=self.get_headers(), verify=HOST_VERIFY, timeout=30)
        response = self.return_response(data, response)

        if response['success']:
            return RepresentativeMeeting.objects.filter(id=response['content']['id']).first()


class TestPostVotingGuestCreditorByRepresentatives(TestPostVotingSystemCreditorByRepresentatives):
    path = 'create_representatives_guest_result'

    def parameters(self):
        parameters = super().parameters()
        self.token = get_token(self.representative_meeting.guest.user)
        return parameters

    @property
    def path_parameters(self):
        return {}