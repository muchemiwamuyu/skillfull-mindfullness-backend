import django_filters
from .models import AuditLog


class AuditLogFilter(django_filters.FilterSet):
    user = django_filters.CharFilter(field_name="user__username", lookup_expr="icontains")
    action = django_filters.ChoiceFilter(choices=AuditLog.ACTION_CHOICES)
    resource_type = django_filters.CharFilter(lookup_expr="icontains")
    start_date = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="gte")
    end_date = django_filters.DateTimeFilter(field_name="timestamp", lookup_expr="lte")

    class Meta:
        model = AuditLog
        fields = ["user", "action", "resource_type", "start_date", "end_date"]
