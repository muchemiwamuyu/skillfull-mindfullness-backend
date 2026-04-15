from django.apps import AppConfig


class ClientProjectsConfig(AppConfig):
    name = "client_projects"

    def ready(self):
        import client_projects.signals  # noqa: F401
