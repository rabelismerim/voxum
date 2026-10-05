import json
import logging
import channels
import channels.layers

from config.settings import FERNET_KEY  # Ajustado para carregar do config local
from cryptography.fernet import Fernet
from asgiref.sync import async_to_sync


class SocketsLayout:
    type = 'send_messages'

    def get_layout(self, channel, data, channel_type='array'):
        try:
            data = json.loads(data)
        except (TypeError, KeyError, ValueError) as e:
            logging.debug(e)
        return {'type': self.type, 'channel': channel, 'data': json.dumps(data, default=str),
                'channel_type': channel_type}

    def send_data(self, room, channel, serialized_data, channel_type):
        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(str(room), self.get_layout(channel, serialized_data, channel_type))


class Security:
    f = Fernet(FERNET_KEY)

    def encrypt(self, value):
        return self.f.encrypt(self.__json_dumps(value).encode()).decode()

    def decrypt(self, value):
        return self.__json_loads(self.f.decrypt(value).decode())

    @staticmethod
    def __json_dumps(value):
        return json.dumps(value)

    @staticmethod
    def __json_loads(value):
        return json.loads(value)