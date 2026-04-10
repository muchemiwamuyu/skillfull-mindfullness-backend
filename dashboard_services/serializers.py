from rest_framework import serializers
from .models import DashboardProject, DashboardTeams, DashboardCustomProject


class DashboardProjectSerializer(serializers.ModelSerializer):
    project_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DashboardProject
        fields = "__all__"
        read_only_fields = ["id", "created_at", "project_by", "updated_at"]


class DashboardCustomProjectSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    complexity_display = serializers.CharField(source="get_complexity_display", read_only=True)

    class Meta:
        model = DashboardCustomProject
        fields = "__all__"
        read_only_fields = [
            "id",
            "user",
            "estimated_duration",
            "status",
            "admin_notes",
            "created_at",
            "updated_at",
            "status_display",
            "complexity_display",
        ]


class DashboardCustomProjectStatusSerializer(serializers.ModelSerializer):
    """Staff-only serializer for updating status and admin notes."""

    class Meta:
        model = DashboardCustomProject
        fields = ["status", "admin_notes"]


class DashboardTeamsSerializer(serializers.ModelSerializer):
    added_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DashboardTeams
        fields = "__all__"
        read_only_fields = ["id", "created_at", "added_by", "updated_at"]
