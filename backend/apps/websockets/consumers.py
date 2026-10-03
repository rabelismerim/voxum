import json
from channels.generic.websocket import AsyncWebsocketConsumer


class MeetingConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.meeting_id = self.scope['url_route']['kwargs']['meeting_id']
        self.room_group_name = f'meeting_{self.meeting_id}'

        # Entra no grupo da assembleia
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Sai do grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')

        # Transmite a mensagem recebida para todos na sala
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'meeting_message',
                'message': message
            }
        )

    async def meeting_message(self, event):
        message = event['message']

        # Envia a mensagem via WebSocket para o cliente Vue
        await self.send(text_data=json.dumps({
            'message': message
        }))