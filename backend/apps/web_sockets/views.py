from rest_framework.views import APIView
from rest_framework.response import Response
from utils import get_user_model, _, doc
from apps.web_sockets.schemas import SocketsSchema

User = get_user_model()


@doc(_("""Documentation for using sockets.

    The sending and output pattern will always be a dictionary

    Return:
        - dict: `{'channel': 'the reference channel', 'data': 'the information')}`
    """))
class SocketsApi(APIView):  # Substituído AbstractViewApi por APIView genérica do DRF
    http_method_names = ['get']
    serializer_class = SocketsSchema
    model = User
    many = False
    try_it_out = False
    custom_path = 'voxum/ws/V1/meetings/{meeting_id}/'
    tags = [_('Sockets')]

    docs = {
        'get': """Each key within the dictionary refers to the channel that will send or receive that information. In
        the get there is how the data will be sent and in the post how it should be sent"""
    }

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(instance=request.user, context={'request': request})
        return Response(serializer.data)