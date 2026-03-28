from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user",
            "action",
            "action_display",
            "resource_type",
            "resource_id",
            "description",
            "ip_address",
            "user_agent",
            "timestamp",
            "extra_data",
        ]
        read_only_fields = fields
