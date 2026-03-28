from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import AuditLog
from .serializers import AuditLogSerializer
from .filters import AuditLogFilter


class IsStaffOrAdmin(permissions.BasePermission):
    """Allow access only to staff or admin users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        )


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only endpoint for staff/admin to query audit logs.
    Supports filtering by user, action, resource_type, start_date, end_date.
    """

    queryset = AuditLog.objects.select_related("user").all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsStaffOrAdmin]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = AuditLogFilter
    search_fields = ["user__username", "description", "resource_id"]
    ordering_fields = ["timestamp", "action", "resource_type"]
    ordering = ["-timestamp"]
