from django.apps import AppConfig


class UrbantrendsServicesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'urbantrends_services'

    def ready(self):
        import urbantrends_services.signals
