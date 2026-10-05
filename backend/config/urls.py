"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseNotFound, HttpResponseForbidden, HttpResponse
from django.urls import path, include, re_path
from django.conf.urls.static import static

from config.settings import BASE_API_URL

from django.urls import path, include
from django.shortcuts import redirect

from apps.voxum_base.utils import check_is_user_internal
from config.settings import STATIC_URL, MEDIA_URL, MEDIA_ROOT, APP_NAME
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.views import obtain_auth_token


schema_view = get_schema_view(
    openapi.Info(
        title='Voxum API',
        default_version='v1',
        description='API for managing meetings, creditors, guests, presence, reports and voting.',
    ),
    public=True,
    permission_classes=(AllowAny,),
)


def clear_filepath(filepath):
    return filepath.replace(APP_NAME, '').replace('media', '').replace(MEDIA_URL, '').replace(MEDIA_ROOT, '').replace(
        '/', '').replace('\\', '').strip().lower()


@login_required()
def protected_media(request, path, document_root=None, **kwargs):
    filepath = clear_filepath(path)

    if (filepath.startswith('converter') or filepath.startswith('process_files')) and not check_is_user_internal(
            request.user):
        return HttpResponse(status=404)
    return serve(request, path, document_root=document_root, **kwargs)


urlpatterns = [
    path('favicon.ico', lambda _: redirect(f'{STATIC_URL}favicon.ico', permanent=True)),

    re_path(r'^{}/media/(?P<path>.*)$'.format(APP_NAME), protected_media, {'document_root': MEDIA_ROOT}),

    path(f'{BASE_API_URL}auth/token/', obtain_auth_token, name='api-token-auth'),
    path(f'{BASE_API_URL}process_file/', include('apps.voxum_base.urls_process_file')),
    path(f'{BASE_API_URL}meeting/', include("apps.meetings.urls")),
    path(f'{BASE_API_URL}creditor/', include("apps.creditor.urls")),
    path(f'{BASE_API_URL}location/', include("apps.location.urls")),
    path(f'{BASE_API_URL}sockets/', include("apps.web_sockets.urls")),
    path(f'{BASE_API_URL}guest/', include("apps.guest.urls")),
    path(f'{BASE_API_URL}recovering/', include("apps.recovering.urls")),
    path(f'{BASE_API_URL}voting/', include("apps.voting.urls")),
    path(f'{BASE_API_URL}presence/', include("apps.presence.urls")),
    path(f'{BASE_API_URL}report/', include("apps.report.urls")),
    path(f'{BASE_API_URL}core/user/', include("core.urls")),
    re_path(
        rf'^{BASE_API_URL}docs(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json',
    ),
    path(f'{BASE_API_URL}docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path(f'{BASE_API_URL}docs/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('favicon.ico', lambda _: redirect(f'{STATIC_URL}favicon.ico', permanent=True)),
]

urlpatterns += static("/" + MEDIA_URL, document_root=MEDIA_ROOT)