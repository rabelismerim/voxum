# import json
# import pickle
#
# from asgiref.sync import sync_to_async
# from channels.exceptions import DenyConnection
# from channels.generic.websocket import AsyncWebsocketConsumer
# from cloudpickle import cloudpickle
# from django.contrib.auth.models import AnonymousUser
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from utils import get_user_model
#
# from apps.voxum_base.views import SocketsLayout
# from apps.web_sockets.signals import user_connected, user_disconnected
# from apps.web_sockets.tasks import SendMessageTask
#
# User = get_user_model()
#
#
# class MeetingSocket(SocketsLayout, AsyncWebsocketConsumer):
#     current_protocol = 'V2'
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(args, kwargs)
#         self.room = None
#         self.user = None
#
#     def get_room(self):
#         return str(self.scope['url_route']['kwargs']['meeting_id'])
#
#     async def send_user_connected(self):
#         """Signal para indicação de User conectado"""
#         send_async = sync_to_async(user_connected.send)
#         await send_async(sender=User, instance=self.user, meeting_id=self.room)
#
#     async def send_user_disconnected(self):
#         """Signal para indicação de User desconectado"""
#         send_async = sync_to_async(user_disconnected.send)
#         await send_async(sender=User, instance=self.user, meeting_id=self.room)
#
#     async def connect(self):
#         user = self.scope['user']
#         if user == AnonymousUser() or user is None or user.is_authenticated is False:

#             await self.close(code=4004)
#             raise DenyConnection("Invalid User")
#
#         self.room = self.get_room()
#         await self.channel_layer.group_add(self.room, self.channel_name)
#         await self.accept(self.current_protocol)
#         self.user = user

#         await self.send_initial_data()
#         await self.send_user_connected()
#
#     async def receive(self, text_data=None, bytes_d=None):
#         await self.send_messages(self.get_layout('status', f'Mensagem recebida: {text_data}'))
#
#     async def send_messages(self, dt: dict):
#         data = dt.copy()
#         data['data'] = json.loads(data['data'])
#         data.pop('type', None)
#         await self.send(text_data=json.dumps(data, default=str))
#
#     async def websocket_disconnect(self, message):
#         if self.room:
#             await self.channel_layer.group_discard(self.room, self.channel_name)
#             await self.send_user_disconnected()

#
#     async def send_initial_data(self):
#         """
#         Asynchronously sends initial data for each subclass of Schema associated with the current room.
#
#         Iterates through all subclasses of Schema, checks if they have the attribute 'send_initial' set to True,
#         and sends initial data for those classes to the corresponding channels.
#
#         Returns:
#             None
#         """
#         subclasses = Schema.get_subclasses()
#         for sub in subclasses:
#             cls = sub
#             if cls.send_initial is False:
#                 continue
#             # Serializar a função e os argumentos para serem executados pela task
#             get_data_params = cloudpickle.dumps((cls.get_initial_data_by_room, {'room_id': str(self.room)}))
#             serializer_dumps = pickle.dumps(cls.serializer)
#             SendMessageTask.delay(serializer_dumps, cls.channel, cls.many, self.room, get_data_params)
#
#
# class BaseMeta(type):
#     """
#     Metaclass that sets the instance attribute on the class.
#     """
#
#     def __new__(mcs, name, bases, attrs):
#         cls = super().__new__(mcs, name, bases, attrs)
#         cls_instance = cls()
#         setattr(cls, 'instance', cls_instance)
#         return cls
#
#
# class Schema(metaclass=BaseMeta):
#     """
#     Base class for schema definitions.
#
#     Attributes:
#         signals (list): List of signals to listen to.
#         many (bool): Flag indicating if the schema handles multiple instances.
#         serializer: Serializer class for the schema.
#         channel: Channel to send the serialized data.
#         instance: Current instance of the schema.
#         filter_key: Key used for filtering the data.
#
#     Methods:
#         __init__: Initializes the schema instance.
#     """
#     signals = [post_save]
#     many = False
#     serializer = None
#     model = None
#     channel = None
#     instance = None
#     filter_key = None
#     only_initial = False
#     send_initial = True
#     has_filter = False
#
#     def __init__(self):
#         """
#        Initializes the schema instance and sets up signal receivers.
#        """
#         if type(self).__name__ != 'Schema':
#             for signal in self.signals:
#                 if self.only_initial and isinstance(signal, type(post_save)):
#                     continue
#
#                 sender = self.model or self.serializer.Meta.model
#
#                 @receiver(signal, sender=sender)
#                 def wrapper_schema(**kwargs):
#                     """
#                     This decorator function is used to send serialized data to a designated channel
#                     when a specified signal is received. It is intended to work in conjunction
#                     with a Schema instance and its associated serializer.
#
#                     Parameters:
#                     - **kwargs (dict): Keyword arguments passed when the signal is received.
#
#                     The decorator initializes the Schema's instance, serializes the data, and sends
#                     it to the specified channel asynchronously using the SendMessageTask.
#
#                     Note:
#                     This decorator should be used with signals and is specific to the Schema
#                     class and its related components.
#                     """
#                     self.instance = kwargs.get('instance')
#                     # Serializar a função e os argumentos para serem executados pela task
#                     get_data_params = cloudpickle.dumps((self.get_data, {}))
#                     serializer_dumps = pickle.dumps(self.serializer)
#                     SendMessageTask.delay(serializer_dumps, self.channel, self.many, self.get_room(), get_data_params)
#
#     def get_room(self):
#         """
#         Abstract method to get the room for sending the data.
#         This method should be implemented in subclasses.
#
#         Returns:
#             str: The room name.
#         """
#         raise NotImplementedError
#
#     def get_initial_filter(self):
#         """
#         Abstract method to get the initial filter for data retrieval.
#         This method should be implemented in subclasses.
#
#         Returns:
#             dict: The initial filter parameters.
#         """
#         raise NotImplementedError
#
#     def filter(self):
#         """
#         Abstract method to apply additional filters for data retrieval.
#         This method should be implemented in subclasses.
#
#         Returns:
#             dict: The filter parameters.
#         """
#         raise NotImplementedError
#
#     def get_data(self):
#         """
#         Get the data based on the schema configuration.
#
#         Returns:
#             QuerySet or Model instance: The retrieved data.
#         """
#         if self.many:
#             model = self.get_model()
#             filters = self.filter()
#             return model.objects.filter(**filters)
#         if self.has_filter:
#             model = self.get_model()
#             filters = self.filter()
#             return model.objects.filter(**filters).first()
#
#         return self.instance
#
#     def get_model(self):
#         """
#         Get the model class associated with the serializer.
#
#         Returns:
#             Model: The model class.
#         """
#         return self.serializer.Meta.model
#
#     @classmethod
#     def get_subclasses(cls):
#         """
#         Get the subclasses of the Schema class.
#
#         Returns:
#             list: List of subclasses.
#         """
#         return cls.__subclasses__()
#
#     @classmethod
#     def get_schemas(cls):
#         """
#         Get information about the available schemas.
#
#         Returns:
#             list: List of dictionaries containing schema information.
#                 Each dictionary contains the following keys:
#                 - class_name: Name of the schema class.
#                 - channel: Channel associated with the schema.
#                 - serializer: Serializer class associated with the schema.
#                 - many: Flag indicating if the schema handles multiple instances.
#         """
#         schemas = []
#         sub = cls.__subclasses__()
#         for subclass in sub:
#             schemas.append({
#                 'class_name': subclass.__name__,
#                 'channel': subclass.channel,
#                 'serializer': subclass.serializer,
#                 'many': subclass.many
#             })
#         return schemas
#
#     @classmethod
#     def get_initial_data_by_room(cls, room_id):
#         """
#         Asynchronously retrieve the initial data for a given room.
#
#         Args:
#             room_id (str): The ID of the room.
#
#         Returns:
#             list or Model instance: The initial data for the room.
#                 If `many` is True, a list of instances is returned.
#                 Otherwise, a single instance is returned.
#         """
#         filters = cls.get_filters(room_id)
#         model = cls.serializer.Meta.model
#         if cls.many:
#             return list(model.objects.filter(**filters))
#         return model.objects.filter(**filters).first()
#
#     @classmethod
#     def get_filters(cls, room_id):
#         """
#         Get the filters based on the room ID.
#
#         Args:
#             room_id (str): The ID of the room.
#
#         Returns:
#             dict: The filters to be applied for data retrieval.
#         """
#         return {cls.filter_key: room_id}
