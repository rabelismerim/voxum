from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Endpoints de Autenticação JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Endpoints dos Apps da Aplicação
    path('api/creditors/', include('apps.creditors.urls')),
    path('api/meetings/', include('apps.meetings.urls')),
    path('api/presence/', include('apps.presence.urls')),
    path('api/reports/', include('apps.reports.urls')),
    path('api/voting/', include('apps.voting.urls')),
]