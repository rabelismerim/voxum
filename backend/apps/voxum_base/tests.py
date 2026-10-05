import json

from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.location.models import Location
from apps.meetings.models import Meeting
from config.asgi import application
from apps.voxum_base.tasks import LockManager
from apps.voxum_base.utils import count_group_connections


class LocalDevelopmentTests(TestCase):
    def test_swagger_documents_the_live_api(self):
        response = self.client.get(
            reverse('schema-json', kwargs={'format': '.json'}),
            HTTP_HOST='localhost',
        )

        self.assertEqual(response.status_code, 200)
        schema = json.loads(response.content)
        self.assertEqual(schema['basePath'], '/voxum/api/v1')
        self.assertEqual(
            set(schema['paths']['/creditor/'])
            & {'get', 'post', 'put', 'patch', 'delete'},
            {'get', 'post'},
        )

    def test_authenticated_user_detail_returns_the_current_user(self):
        user = get_user_model().objects.create_user(username='local-test-user')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/voxum/api/v1/core/user/detail/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['id'], user.id)

    def test_local_token_login_returns_authenticated_user_and_permissions(self):
        call_command('create_voxum_groups', verbosity=0)
        user = get_user_model().objects.create_superuser(
            username='local-admin',
            email='local-admin@example.test',
            password='test-password',
        )
        client = APIClient()

        token_response = client.post(
            '/voxum/api/v1/auth/token/',
            {'username': user.username, 'password': 'test-password'},
            format='json',
        )

        self.assertEqual(token_response.status_code, 200)
        self.assertIn('token', token_response.json())
        client.credentials(HTTP_AUTHORIZATION=f"Token {token_response.json()['token']}")

        user_response = client.get('/voxum/api/v1/core/user/detail/')

        self.assertEqual(user_response.status_code, 200)
        self.assertEqual(user_response.json()['id'], user.id)
        self.assertTrue(user_response.json()['is_active'])
        self.assertIn(
            'can_manage_project',
            [permission['codename'] for permission in user_response.json()['user_permissions']],
        )
        self.assertEqual(client.get('/voxum/api/v1/core/user/group/').status_code, 200)

    def test_local_token_authenticates_general_websocket(self):
        call_command('create_voxum_groups', verbosity=0)
        user = get_user_model().objects.create_superuser(
            username='local-websocket-admin',
            email='local-websocket-admin@example.test',
            password='test-password',
        )
        user.groups.add(Group.objects.get(name='Gerente'))
        token = Token.objects.create(user=user)

        async def connect():
            communicator = WebsocketCommunicator(
                application,
                f'/voxum/ws/V1/general/?token={token.key}',
                subprotocols=['V2'],
            )
            connected, _ = await communicator.connect()
            if connected:
                await communicator.disconnect()
            return connected

        self.assertTrue(async_to_sync(connect)())

    def test_manager_can_create_meeting_with_model_default_status(self):
        call_command('create_voxum_groups', verbosity=0)
        user = get_user_model().objects.create_superuser(
            username='local-meeting-admin',
            email='local-meeting-admin@example.test',
            password='test-password',
        )
        user.groups.add(Group.objects.get(name='Gerente'))
        location = Location.objects.create(description='Rio de Janeiro')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post(
            '/voxum/api/v1/meeting/',
            {
                'name': 'Assembleia de teste',
                'description': 'Teste local',
                'location_id': str(location.id),
                'start_date': '2026-10-06T12:00:00Z',
            },
            format='json',
        )

        self.assertEqual(response.status_code, 201, response.json())
        meeting = Meeting.objects.get(id=response.json()['id'])
        self.assertEqual(meeting.status, 'S')

    def test_manager_can_load_meeting_options(self):
        call_command('create_voxum_groups', verbosity=0)
        user = get_user_model().objects.create_superuser(
            username='local-options-admin',
            email='local-options-admin@example.test',
            password='test-password',
        )
        user.groups.add(Group.objects.get(name='Gerente'))
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.get('/voxum/api/v1/meeting/options/')

        self.assertEqual(response.status_code, 200)
        self.assertIn('meeting_status_options', response.json())

    def test_in_memory_channel_layer_counts_group_members(self):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_add)('voxum-test', 'test-channel')
        try:
            self.assertEqual(count_group_connections('voxum-test'), 1)
        finally:
            async_to_sync(channel_layer.group_discard)('voxum-test', 'test-channel')

    def test_local_task_lock_can_be_acquired_and_released(self):
        lock_manager = LockManager()
        identifier = 'voxum-test-lock'

        self.assertTrue(lock_manager.acquire_lock(identifier))
        self.assertFalse(lock_manager.acquire_lock(identifier))
        lock_manager.release_lock(identifier)
        self.assertTrue(lock_manager.acquire_lock(identifier))
        lock_manager.release_lock(identifier)
