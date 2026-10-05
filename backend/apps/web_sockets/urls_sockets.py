from apps.web_sockets.views_guest_sockets import MeetingGuestSocket
from apps.web_sockets.views_sockets import MeetingSocket, GeneralSocket
from django.urls import path
from channels.routing import URLRouter
from config.settings import BASE_SOCKETS, BASE_SOCKETS_GUEST

websockets = URLRouter([
    path(f"{BASE_SOCKETS}meetings/<uuid:meeting_id>/", MeetingSocket.as_asgi()),
    path(f"{BASE_SOCKETS}general/", GeneralSocket.as_asgi()),
    path(f"{BASE_SOCKETS_GUEST}meetings/<uuid:meeting_id>/", MeetingGuestSocket.as_asgi()),
])
