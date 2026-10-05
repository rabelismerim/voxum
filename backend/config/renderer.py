import json

from rest_framework.renderers import JSONRenderer
from utils import get_user_model

from apps.voxum_base.utils import check_is_user_internal, check_is_user_guest

User = get_user_model()


class VoxumAPIRendererInterceptor(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response_string = super().render(data, accepted_media_type, renderer_context)
        if response_string:
            try:
                render = json.loads(response_string.decode('utf-8'))
            except (UnicodeDecodeError, AttributeError, json.JSONDecodeError):
                return response_string

            if renderer_context and 'request' in renderer_context:
                request = renderer_context['request']
                if isinstance(render, dict) and 'profile' in render and isinstance(render['profile'], dict):
                    render['profile']['is_user_guest'] = check_is_user_guest(request.user)
                    render['profile']['is_user_internal'] = check_is_user_internal(request.user)
            return json.dumps(render).encode('utf-8')
        return response_string