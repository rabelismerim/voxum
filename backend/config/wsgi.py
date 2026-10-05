"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

from config.settings import WHITENOISE_ALLOW_ALL_ORIGINS

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()


# Função que será chamada para adicionar cabeçalhos personalizados aos arquivos estáticos
def add_security_headers(headers, path_url, url):
    # Adicionando cabeçalhos de segurança
    headers.add_header('X-Content-Type-Options', 'nosniff')
    headers.add_header('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload')
    headers.add_header('X-XSS-Protection', '1; mode=block')
    headers.add_header(
        'Content-Security-Policy',
        "default-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'",
    )
    headers.add_header('Referrer-Policy', 'no-referrer-when-downgrade')
    headers.add_header('Cross-Origin-Opener-Policy', 'same-origin')
    headers.add_header('Vary', 'Cookie, Accept-Language')
    headers.add_header('X-Frame-Options', 'DENY')
    return headers


application = WhiteNoise(application, add_headers_function=add_security_headers,
                         allow_all_origins=WHITENOISE_ALLOW_ALL_ORIGINS)
