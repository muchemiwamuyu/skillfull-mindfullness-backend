from django.apps import AppConfig


class UrbantrendsAuditConfig(AppConfig):
    name = 'urbantrends_audit'

    def ready(self):
        # Import auth signals (they use Django's built-in signals so no lazy load needed)
        import urbantrends_audit.signals as audit_signals  # noqa: F401
        audit_signals.connect_all_signals()
