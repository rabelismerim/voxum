"""
Módulo de Sockets para manipulação de schemas relacionados a detalhes de Assembleias e Representantes.

Este módulo contém classes de esquema para detalhes de Assembleias e Representantes, projetadas para serem utilizadas em
aplicações de comunicação por websocket.

Classes de Esquema:
- `ExcelWorkerDetail`: Classe de esquema para detalhes de processamento de planilhas.
"""

from django.db.models.signals import post_save

from apps.voxum_base.schemas import ExcelWorkerListSchema
from apps.voxum_base.views_sockets import Schema


class ExcelWorkerDetail(Schema):
    """
    Schema class for meeting detail.

    Attributes:
        serializer: Serializer class for the schema.
        channel: Channel to send the serialized data.
        filter_key: Key used for filtering the data.

    Methods:
        get_room: Get the room for sending the data.
        filter: Apply additional filters for data retrieval.
    """

    serializer = ExcelWorkerListSchema
    channel = 'process_file'
    filter_key = 'object_id'
    type = 'list'
    signals = [post_save]
    send_initial = True
    many = True

    def get_room(self):
        """
        Get the room for sending the data.

        Returns:
            str: The room name.
        """
        return self.instance.object_id

    def filter(self):
        """
        Apply additional filters for data retrieval.

        Returns:
            dict: The filter parameters.
        """
        return {self.filter_key: self.instance.object_id}