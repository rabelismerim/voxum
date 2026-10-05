"""
Module Description:

This module contains tasks and functions related to messaging functionalities using Celery and Redis for handling voting
 processes.

Classes:
- SendMessageTask: Sends messages to specific channels using Redis.
- SendVotingList: Handles sending voting lists to qualified creditors.
- SendVotingUserDetail: Manages sending voting details to connected users.
- ReceiveVotingTask: Receives and processes voting messages from Redis.

Functions/Methods:
- dispatch_voting_progress_detail: Dispatches the task to send the voting list upon Voting model instance save.
- dispatch_voting_user_detail: Dispatches the task to send voting details upon user connection.

"""
import copy
import json
import logging
import time

from core.abstract.exceptions import ValidationErrorAdapter
from celery.exceptions import MaxRetriesExceededError
from django.db import IntegrityError
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from utils import _

from apps.voxum_base.tasks import AbstractTask
from apps.voxum_base.utils import count_group_connections
from apps.creditor.models import Creditor
from apps.meetings.models import RepresentativeMeeting
from apps.voting.models import Voting, StatusVotingChoice, DefaultAssuntoChoices, TypeVotingChoices, \
    DefaultEscolhaChoices, VotingResult
from apps.voting.schemas import (VotingGuestDetailSchema, VotingResultGuestSchema,
                                 VotingResultRepresentativeGuestSchema, RepresentativeResultsSchema,
                                 VotingGuestWithoutDetailSchema)
from apps.web_sockets.signals import voting_end, update_representative_meeting_detail, voting_start
from apps.web_sockets.tasks import SendJsonMessageTask, SendNotificationToastTask, NotificationToastType
from config.celery import app as celery_app, REDIS_CONN
from config.settings import VOTING_RESULT_CH

PENDING_VOTES = 'pending_votes_voting_id_{}'
SUCCESS_VOTES = 'success_votes_voting_id_{}'


def json_response(data):
    try:
        return json.loads(json.dumps(data, default=str))
    except TypeError:
        return data


class SendVotingList(AbstractTask):
    """
    Task for sending voting list details.
    """
    redis_conn = REDIS_CONN

    max_retries = 3
    identifier = 'voting_id'

    def run(self, voting_id, meeting_id, send_creditor_representatives_detail=True, reset_count_pend_votes=False):
        if reset_count_pend_votes:
            self.redis_conn.set(PENDING_VOTES.format(voting_id), 0)

        creditors = Creditor.objects.filter(Q(online=True) | Q(representative__online=True),
                                            meeting_id=meeting_id).distinct()

        for creditor in creditors:
            if creditor.online:
                SendVotingUserDetailTask(creditor.guest.user.id, meeting_id, voting_id,
                                         send_creditor_representatives_detail=send_creditor_representatives_detail)

            for representative in creditor.representatives:
                if representative.online:
                    SendVotingUserDetailTask(representative.representative.guest.user.id, meeting_id, voting_id,
                                             send_creditor_representatives_detail=send_creditor_representatives_detail)
        return f'voting_id: {voting_id}, meeting_id: {meeting_id}'


class SendVotingUserDetail(AbstractTask):
    """
    Task for sending voting user details.
    """
    redis_conn = REDIS_CONN

    type = 'object'
    max_retries = 3

    def run(self, user_id, meeting_id, voting_id=None, send_creditor_representatives_detail=True):
        creditors = Creditor.objects.filter(
            Q(guest__user__id=user_id) | Q(representative__representative__guest__user__id=user_id)).filter(
            meeting_id=meeting_id)
        votings = []
        channel = 'voting_progress_detail_guest'
        voting = Voting.objects.filter(meeting_id=meeting_id, status=StatusVotingChoice.INICIADA).first()
        representatives_meeting_ids_sent = []
        for creditor in creditors:
            if not creditor:
                logging.warning(f'user_id guest conectado sem creditor {user_id}')
                return

            self.type = 'object' if send_creditor_representatives_detail else 'object_update'

            if creditor:
                voting_copy = copy.copy(voting)

                if creditor.online:
                    send_voting = self.send_voting(voting_copy, creditor, None, meeting_id, user_id,
                                                   send_creditor_representatives_detail=send_creditor_representatives_detail)
                    votings.append(send_voting)

                representatives_meeting = creditor.get_representatives_meeting(**{'online': True})

                for representative_meeting in representatives_meeting:

                    if representative_meeting.id in representatives_meeting_ids_sent:
                        continue

                    representatives_meeting_ids_sent.append(representative_meeting.id)

                    user_id_representative_meeting = representative_meeting.guest.user.id

                    setattr(representative_meeting, 'voting_id', voting_id)
                    update_representative_meeting_detail.send(instance=representative_meeting,
                                                              sender=RepresentativeMeeting)

                    send_voting = self.send_voting(voting_copy, creditor, representative_meeting, meeting_id,
                                                   user_id_representative_meeting,
                                                   send_creditor_representatives_detail=send_creditor_representatives_detail)

                    data = {
                        'channel': channel,
                        'room': f'{meeting_id}__{user_id_representative_meeting}',
                        'data': json.dumps(send_voting, default=str),
                        'channel_type': self.type,
                    }
                    SendJsonMessageTask.delay(**data)

        if votings:
            data = {
                'channel': channel,
                'room': f'{meeting_id}__{user_id}',
                'data': json.dumps(votings, default=str),
                'channel_type': self.type,
            }

            SendJsonMessageTask.delay(**data)

        return json_response(votings)

    def send_voting(self, voting, creditor, representative_m, meeting_id, user_id,
                    send_creditor_representatives_detail):
        room = f'{meeting_id}__{user_id}'

        group_info = count_group_connections(room)
        if not group_info:
            logging.debug(f'user: {user_id} not connected to meeting: {meeting_id}')
            return

        if creditor and str(creditor.guest.user.id) == str(user_id):
            representative_m = None
        else:
            creditor = None

        if voting:
            if send_creditor_representatives_detail:
                voting.qualified_creditor = voting.qualified_creditor(creditor)
                voting.guest_choices = voting.guest_choices(creditor)
                voting.qualified_representative = voting.qualified_representative(representative_m)
                if creditor:
                    voting.creditor_id = creditor.id
                voting = VotingGuestDetailSchema(voting).data
            else:
                voting = VotingGuestWithoutDetailSchema(voting).data
                self.type = 'object_patch'
        else:
            logging.warning(f'meeting_id:{meeting_id}, user_id:{user_id}, nao encontrado')

        return voting


class ProcessVoting(AbstractTask):
    """
    Task for processing voting data.
    """
    redis_conn = REDIS_CONN
    type = 'array'
    max_retries = 3

    def voting_meeting(self, data):
        try:
            meeting_id, voting_id = Voting.objects.filter(choice__id=data["vote_id"]).values_list("meeting_id",
                                                                                                  'id').first()

            return meeting_id, voting_id
        except (KeyError, TypeError):
            return None, None

    def run(self, post_data):
        response = {'success': False, 'task_id': self.request.id}
        errors = []
        user_id = post_data.get('user_id')
        data = post_data.get('data')

        meeting_id, voting_id = self.voting_meeting(data)

        if not meeting_id:
            raise ValidationErrorAdapter(_('Votação não encontrada'))

        redis_conn_voting_key = PENDING_VOTES.format(voting_id)
        self.redis_conn.incr(redis_conn_voting_key)

        voting = VotingResultGuestSchema(data=data, context={'user_id': user_id})

        if voting.is_valid(raise_exception=False):
            try:
                voting = voting.save()
                response['success'] = True
                response['data'] = VotingResultGuestSchema(voting).data
            except ValidationError as e:
                errors.extend(e.detail)
            except (KeyError, IntegrityError, ValueError) as f:
                errors.append(str(f))
            except Exception as g:
                errors.append(str(g))
        else:
            errors = voting.errors
        if errors:
            response['errors'] = errors
            logging.error(f'Vote by creditor errors: {errors}')

        SendJsonMessageTask.delay(VOTING_RESULT_CH, f'{meeting_id}__{user_id}', json.dumps(response, default=str),
                                  self.type)

        self.redis_conn.decr(redis_conn_voting_key)
        return json_response(response)


class ProcessVotingRepresentative(AbstractTask):
    """
    Task for processing voting data.
    """
    redis_conn = REDIS_CONN
    type = 'array'
    max_retries = 3

    def voting_ids(self, vote_ids):
        return list(set(Voting.objects.filter(choice__id__in=vote_ids).distinct().values_list('id', flat=True)))

    def run(self, post_data):
        response = {'success': False, 'task_id': self.request.id}
        errors = []
        user_id = post_data.get('user_id')

        data = post_data.get('data')
        voting = RepresentativeResultsSchema(data=data, context={'user_id': user_id})

        vote_ids = []
        for vote in data.get('creditors_voting', []):
            vote_ids.append(vote['vote_id'])

        voting_ids = self.voting_ids(list(set(vote_ids)))

        for voting_id in voting_ids:
            redis_conn_voting_key = PENDING_VOTES.format(voting_id)
            self.redis_conn.incr(redis_conn_voting_key)

        if voting.is_valid(raise_exception=False):
            try:
                voting = voting.save()
                response['success'] = True
                response['data'] = VotingResultRepresentativeGuestSchema(voting).data
            except ValidationError as e:
                errors.extend(e.detail)
            except (KeyError, IntegrityError, ValueError) as f:
                errors.append(str(f))
            except Exception as g:
                errors.append(str(g))
        else:
            errors = voting.errors
        if errors:
            response['errors'] = errors
            logging.error(f'Vote by representative errors: {errors}')

        SendJsonMessageTask.delay(VOTING_RESULT_CH, f'{data["meeting_id"]}__{user_id}',
                                  json.dumps(response, default=str),
                                  self.type)

        for voting_id in voting_ids:
            redis_conn_voting_key = PENDING_VOTES.format(voting_id)
            self.redis_conn.decr(redis_conn_voting_key)
        return json_response(response)


class ProcessVotingResultAbstention(AbstractTask):
    redis_conn = REDIS_CONN
    type = 'array'
    identifier = 'voting_id'
    default_retry_delay = 3
    notification_time = 30
    notification_interval = notification_time // default_retry_delay
    max_retry_time = 60 * 5
    max_retries = int(max_retry_time // default_retry_delay)
    channel = 'notification_toast'

    def get_pending_votes(self, voting_id):
        redis_conn_voting_key = PENDING_VOTES.format(voting_id)
        pending_votes = self.redis_conn.get(redis_conn_voting_key)
        return int(pending_votes.decode('utf-8')) if pending_votes else 0

    def run(self, voting_id):
        """
        Executa a tarefa de processamento de votos de abstenção para um determinado ID de votação.

        Args:
            voting_id (int): ID da votação a ser processada.
        """
        voting: Voting = Voting.objects.filter(id=voting_id).first()
        if not voting:
            return json_response({'error': _('Votação não encontrada')})

        room = str(voting.meeting.id)
        self.process_pending_votes(voting, room)
        voting_results_bulk = self.process_abstention(voting)
        voting.set_results()
        self.send_notification_toast(room, _('Votação e processamento de votos encerrado!'),
                                     NotificationToastType.SUCCESS.value, SUCCESS_VOTES.format(voting_id))

        return json_response(voting_results_bulk)

    def send_notification_toast(self, room, message, notification_type=NotificationToastType.INFO.value, id_toast=None):
        SendNotificationToastTask.delay(self.channel, room, message, notification_type, id_toast)

    def process_pending_votes(self, voting, room):
        pending_votes = self.get_pending_votes(voting.id)
        if pending_votes > 0:
            retries = self.request.retries
            if retries > 0 and retries % self.notification_interval == 0:
                self.send_notification_toast(room,
                                             _('Votação encerrada, processando fila de votos. Aguarde uns instantes!'),
                                             PENDING_VOTES.format(voting.id))
            try:
                self.retry()
            except MaxRetriesExceededError:
                pass

    def process_abstention(self, voting):
        qualified_creditors = voting.qualified_creditors
        voting_results_bulk = []

        start_time = time.time()

        for choice in qualified_creditors:
            value = DefaultAssuntoChoices.ABSTENCAO.label if voting.type == TypeVotingChoices.ASSUNTO else \
                DefaultEscolhaChoices.ABSTENCAO.label
            choice_abstention = choice['choices'].filter(value=value).first()

            creditors = choice['creditors'].filter(voting_id__isnull=True)

            if choice_abstention:
                for creditor in creditors:
                    voting_result = VotingResult(vote=choice_abstention, creditor=creditor)
                    voting_results_bulk.append(voting_result)

                    elapsed_time = time.time() - start_time
                    if elapsed_time >= self.notification_time:
                        room = str(voting.meeting.id)
                        self.send_notification_toast(room,
                                                     _('Votação encerrada, processando fila de votos. Aguarde uns instantes!'),
                                                     PENDING_VOTES.format(voting.id))
                        start_time = time.time()

        VotingResult.objects.bulk_create(voting_results_bulk)
        return voting_results_bulk


SendVotingListTask = celery_app.register_task(SendVotingList())
SendVotingUserDetailTask = celery_app.register_task(SendVotingUserDetail())
ProcessVotingTask = celery_app.register_task(ProcessVoting())
ProcessVotingRepresentativeTask = celery_app.register_task(ProcessVotingRepresentative())
ProcessVotingResultAbstentionTask = celery_app.register_task(ProcessVotingResultAbstention())


@receiver(voting_start, sender=Voting)
def dispatch_voting_progress_start_detail_with_start_detail(instance, **kwargs):
    SendVotingListTask.delay(str(instance.id), str(instance.meeting.id), send_creditor_representatives_detail=True,
                             reset_count_pend_votes=True)


@receiver(post_save, sender=Voting)
def dispatch_voting_progress_start_detail(instance, **kwargs):
    logging.debug('signal dispatch_voting_progress_start_detail')
    SendVotingListTask.delay(str(instance.id), str(instance.meeting.id), send_creditor_representatives_detail=False)


@receiver(voting_end, sender=Voting)
def dispatch_voting_progress_end_detail(instance, **kwargs):
    ProcessVotingResultAbstentionTask.delay(str(instance.id))