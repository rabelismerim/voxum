import json
import logging

from asgiref.sync import sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncWebsocketConsumer
from cloudpickle import cloudpickle
from django.contrib.auth.models import AnonymousUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from utils import get_user_model

from apps.voxum_base.utils import receiver_commit, check_is_user_privileged  # Atualizado para a app 'base' limpa
from apps.voxum_base.views import SocketsLayout
from apps.web_sockets.signals import user_connected, user_disconnected
from apps.web_sockets.tasks import SendMessageTask, SendPriorityMessageTask

User = get_user_model()


class BaseMeta(type):
    def __new__(mcs, name, bases, attrs):
        cls = super().__new__(mcs, name, bases, attrs)
        cls_instance = cls()
        setattr(cls, 'instance', cls_instance)
        return cls


class BaseChema(metaclass=BaseMeta):
    signals = [post_save]
    many = False
    serializer = None
    model = None
    channel = None
    instance = None
    filter_key = None
    send_initial = True
    has_filter = False
    type = 'array'
    is_priority = False
    identifier = None
    order_by = []

    def get_identifier_prefix(self):
        return self.__class__.__name__

    def __init__(self):
        if type(self).__name__ not in ['BaseChema', 'Schema', 'SchemaGuest', 'SchemaGeneral']:
            sender = self.model or self.serializer.Meta.model
            for index, signal in enumerate(self.signals):
                wrapper = receiver_commit if signal == post_save else receiver

                @wrapper(signal, sender=sender)
                def wrapper_schema(**kwargs):
                    self.instance = kwargs.get('instance')
                    identifier_key = None
                    if self.identifier:
                        identifier_key = (f'{self.get_identifier_prefix()}:{self.identifier}:{self.get_room()}:'
                                          f'{self.instance.id}')

                    get_data_params = cloudpickle.dumps((self.get_data, {}))
                    serializer_dumps = cloudpickle.dumps(self.serializer)
                    task_class = SendPriorityMessageTask if self.is_priority else SendMessageTask

                    task_class.delay(serializer_dumps, self.channel, self.many, self.get_room(), get_data_params,
                                     self.type, initial_data=False, identifier_key=identifier_key)

                setattr(self.__class__, f'wrapper_schema_{index}', wrapper_schema)

    def get_room(self):
        raise NotImplementedError

    def get_initial_filter(self):
        raise NotImplementedError

    def filter(self):
        raise NotImplementedError

    def get_data(self):
        if self.many:
            model = self.get_model()
            filters = self.filter()
            query_set = model.objects.filter(**filters).select_related()
            if self.order_by:
                return query_set.order_by(*self.order_by)
            return query_set
        if self.has_filter:
            model = self.get_model()
            filters = self.filter()
            return model.objects.filter(**filters).first()
        return self.instance

    def get_model(self):
        return self.serializer.Meta.model

    @classmethod
    def get_subclasses(cls):
        return cls.__subclasses__()

    @classmethod
    def get_schemas(cls):
        schemas = []
        for subclass in cls.__subclasses__():
            schemas.append({
                'class_name': subclass.__name__,
                'channel': subclass.channel,
                'serializer': subclass.serializer,
                'many': subclass.many
            })
        return schemas

    @classmethod
    def get_initial_data_by_room(cls, room_id, meeting_id, user_id):
        filters = cls.get_filters(room_id)
        model = cls.serializer.Meta.model
        if cls.many:
            query_set = model.objects.filter(**filters).select_related()
            if cls.order_by:
                return list(query_set.order_by(*cls.order_by))
            return list(query_set)
        return model.objects.filter(**filters).first()

    @classmethod
    def get_filters(cls, room_id):
        return {cls.filter_key: room_id}


class Schema(BaseChema, metaclass=BaseMeta):
    pass


class SchemaGuest(BaseChema, metaclass=BaseMeta):
    pass


class SchemaGeneral(BaseChema, metaclass=BaseMeta):
    pass


class AbstractMeetingSocket(SocketsLayout, AsyncWebsocketConsumer):
    current_protocol = 'V2'
    schema = Schema
    only_admin = True
    permission_classes = []

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.room = None
        self.user = None
        self.meeting_id = None

    def get_room(self):
        return str(self.scope['url_route']['kwargs']['meeting_id'])

    def get_meeting_id(self):
        return str(self.scope['url_route']['kwargs']['meeting_id'])

    async def send_user_connected(self):
        send_async = sync_to_async(user_connected.send)
        await send_async(sender=User, instance=self.user, meeting_id=self.meeting_id)

    async def send_user_disconnected(self):
        send_async = sync_to_async(user_disconnected.send)
        await send_async(sender=User, instance=self.user, meeting_id=self.meeting_id)

    async def get_user(self):
        user = self.scope['user']
        if user == AnonymousUser() or user is None or user.is_authenticated is False:
            logging.debug('Usuário nao autenticado\n')
            await self.close(code=4004)
            raise DenyConnection("Usuário inválido")

        is_user_privileged = await sync_to_async(check_is_user_privileged)(user)

        if self.only_admin and is_user_privileged is False:
            logging.debug('Area não autorizada\n')
            await self.close(code=4003)
            raise DenyConnection('Area não autorizada')
        return user

    async def connect(self):
        try:
            self.user = await self.get_user()
            self.room = self.get_room()
            logging.debug(f'Usuário {self.user.username} esperando conexão na sala {self.room}\n')
            self.meeting_id = self.get_meeting_id()
            await self.channel_layer.group_add(self.room, self.channel_name)
            await self.check_permissions()
        except DenyConnection as message_error:
            return await self.close(code=4003, reason=str(message_error))

        await self.accept(self.current_protocol)
        logging.debug(f'Usuário {self.user.username} conectado na sala {self.room}\n')
        await self.send_initial_data()
        await self.send_user_connected()

    async def check_permissions(self):
        for perm in self.permission_classes:
            perm_obj = perm(**{'scope': self.scope})
            perm_obj_async = sync_to_async(perm_obj.has_sockets_permission)
            if not await perm_obj_async():
                raise DenyConnection(perm_obj.message)

    async def send_messages(self, dt: dict):
        data = dt.copy()
        data['data'] = json.loads(data['data'])
        data.pop('type', None)
        await self.send(text_data=json.dumps(data, default=str))

    async def disconnect(self, code):
        if self.room:
            await self.channel_layer.group_discard(self.room, self.channel_name)
            await self.send_user_disconnected()
            logging.debug(f'Usuário {self.user.username} desconectado\n')

    async def send_initial_data(self):
        for sub in self.schema.get_subclasses():
            if sub.send_initial is False:
                continue
            get_data_params = cloudpickle.dumps(
                (sub.get_initial_data_by_room,
                 {'room_id': str(self.room), 'meeting_id': str(self.meeting_id), 'user_id': str(self.user.id)}))
            serializer_dumps = cloudpickle.dumps(sub.serializer)
            await sync_to_async(SendPriorityMessageTask.delay)(
                serializer_dumps,
                sub.channel,
                sub.many,
                self.room,
                get_data_params,
                sub.type,
                True,
            )