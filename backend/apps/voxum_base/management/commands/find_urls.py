import json
import logging
import re
from collections import OrderedDict

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import URLResolver, URLPattern
from drf_api_logger.models import APILogsModel


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        self.count_api_logs()

    def count_api_logs(self):
        urls = self.collect_urls()
        urls_map = {}
        for url in urls:
            original_url = url

            uuid_match = r'[0-9a-fA-F]{{8}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{4}}-[0-9a-fA-F]{{12}}'
            str_match = r'[^/]+'
            id_match = r'[^0-9]'

            matches = (('uuid', uuid_match), ('str', str_match), ('path', str_match), ('id', id_match))
            has_expression = False
            for match_attr, match in matches:
                match_findall = re.findall(rf'<{match_attr}:(\w+)', url)
                if match_findall:
                    has_expression = True
                    for match_pattern in match_findall:
                        url = re.sub(rf'<{match_attr}:{match_pattern}>', uuid_match, url)

            if has_expression:
                count_urls = APILogsModel.objects.filter(api__regex=url).count()
                logging.debug(url)
                logging.debug(f'{original_url}__{count_urls}\n')
            else:
                count_urls = APILogsModel.objects.filter(api__endswith=url).count()
                logging.debug(url)
                logging.debug(f'{original_url}__{count_urls}__not_match\n')
            urls_map[original_url] = count_urls

        sorted_urls_map = OrderedDict(sorted(urls_map.items(), key=lambda x: x[1], reverse=True))

        with open('urls_count_map.json', 'w') as f:
            f.write(json.dumps(sorted_urls_map, indent=4))

    def collect_urls(self):
        urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [''])

        def list_urls(lis, acc=None):
            if acc is None:
                acc = []
            if not lis:
                return
            l = lis[0]
            if isinstance(l, URLPattern):
                yield acc + [str(l.pattern)]
            elif isinstance(l, URLResolver):
                yield from list_urls(l.url_patterns, acc + [str(l.pattern)])
            yield from list_urls(lis[1:], acc)

        urls = []
        for p in list_urls(urlconf.urlpatterns):
            urls.append(''.join(p))
        return urls