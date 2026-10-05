from django.contrib.staticfiles.storage import ManifestStaticFilesStorage


class CustomManifestStaticFilesStorage(ManifestStaticFilesStorage):
    def stored_name(self, name):
        try:
            return super().stored_name(name)
        except ValueError:
            # Retorna o nome original se o arquivo não estiver no manifesto
            return name
