from django.apps import AppConfig


class UrbantrendsOrdersConfig(AppConfig):
    name = 'urbantrends_orders'

    def ready(self):
        import urbantrends_orders.signals  # noqa: F401
