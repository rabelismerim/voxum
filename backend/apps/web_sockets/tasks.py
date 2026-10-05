from concurrent.futures import ThreadPoolExecutor
from enum import Enum

from cloudpickle import cloudpickle
from django.core.cache import cache

from apps.voxum_base.tasks import AbstractTask
from apps.voxum_base.views import SocketsLayout
from config.celery import app as celery_app

from config.settings import WEB_PAGINATOR, PRIORITY_QUEUE


def delete_partialized_keys(cache_partialized_key_remove):
    cache.delete_many(keys=cache.keys(f'{cache_partialized_key_remove}*'))


class SendMessage(SocketsLayout, AbstractTask):
    max_retries = 3
    expires = 30

    def run(self, serializer, channel, many, room, get_data_parameters, channel_type, initial_data=False, **kwargs):
        serializer = cloudpickle.loads(serializer)
        # Deserializar a função e os argumentos para serem executados pela task
        get_data, parameters = cloudpickle.loads(get_data_parameters)

        if WEB_PAGINATOR and many:

            data = get_data(**parameters)
            tamanho_parte = 400

            pages = []
            for i in range(0, len(data) if data else 0, tamanho_parte):
                pages.append(data[i:i + tamanho_parte])

            num_of_pages = len(pages)
            total = len(data)

            def serialize_chunk(count, page_data):
                cache_key = f'{channel}_{room}_{channel_type}_{count}_{num_of_pages}_{total}'

                chunk_serializer = cache.get(cache_key, None) if initial_data else None

                if not chunk_serializer:
                    page_data = serializer(page_data, many=True).data
                    chunk_serializer = {
                        'page': count,
                        'data': page_data,
                        'num_of_pages': num_of_pages,
                        'total': total,
                    }

                    if data:
                        cache.set(cache_key, chunk_serializer, timeout=30)

                self.send_data(room, channel, chunk_serializer, channel_type)

            if data:
                with ThreadPoolExecutor() as executor:
                    for i, page in enumerate(pages):
                        executor.submit(serialize_chunk, count=i + 1, page_data=page)

            else:
                self.send_data(room, channel, {
                    'page': 1,
                    'data': [],
                    'num_of_pages': 1,
                    'total': 1,
                }, channel_type)
        else:
            cache_key = f'{channel}_{room}_{channel_type}'

            if initial_data:
                serialized_data = cache.get(cache_key, None)
            else:
                delete_partialized_keys(cache_key)
                serialized_data = None

            data = get_data(**parameters)

            if not serialized_data:
                data = get_data(**parameters)

                if many:
                    if not data:
                        data = []
                    serialized_data = serializer(data, many=many).data
                else:
                    if data:
                        serialized_data = serializer(data, many=many).data
                    else:
                        serialized_data = None

                if data:
                    cache.set(cache_key, serialized_data, timeout=30)

            self.send_data(room, channel, serialized_data, channel_type)


class SendPriorityMessage(SendMessage):
    queue = PRIORITY_QUEUE

    expires = 120
    priority = 0


class SendJsonMessage(SocketsLayout, AbstractTask):
    max_retries = 3

    def run(self, channel, room, data, channel_type):
        return self.send_data(room, channel, data, channel_type)


class NotificationToastType(Enum):
    SUCCESS = 'success'
    ERROR = 'error'
    INFO = 'info'
    WARNING = 'warning'


class SendNotificationToast(SocketsLayout, AbstractTask):
    max_retries = 3

    def run(self, channel, room, message, notification_type: NotificationToastType = NotificationToastType.INFO.value,
            duration=3000, id_toast=None):
        """
        Envia uma notificação toast para o canal especificado.

        Args:
            channel (str): Canal no qual a notificação será enviada.
            room (str): A sala de chat ou grupo onde a notificação será entregue.
            message (str): O conteúdo da mensagem a ser exibida no toast.
            notification_type (str): O tipo da notificação ('success', 'error', etc).
            duration (int, optional): O tempo em milissegundos para exibir a notificação. Default é 3000 ms.
            id_toast (str): O id da notificação para ser controlada a reebição

        Returns:
            dict: Retorno da função `send_data` que envia a notificação para o frontend.
        """
        toast_data = {
            'id': id_toast,
            'message': message,
            'type': str(notification_type),
            'duration': duration
        }

        return self.send_data(room, channel, toast_data, channel_type='object_update')


SendMessageTask = celery_app.register_task(SendMessage())
SendPriorityMessageTask = celery_app.register_task(SendPriorityMessage())
SendJsonMessageTask = celery_app.register_task(SendJsonMessage())
SendNotificationToastTask = celery_app.register_task(SendNotificationToast())