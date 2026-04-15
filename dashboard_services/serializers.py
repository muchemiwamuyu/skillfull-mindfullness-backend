from rest_framework import serializers
from .models import DashboardProject, DashboardTeams, DashboardCustomProject
from client_projects.models import ClientProject


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


class StagingRepoSerializer(serializers.ModelSerializer):
    submitted_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ClientProject
        fields = [
            "id",
            "project_name",
            "email",
            "submitted_by",
            "status",
            "repo_url",
            "repo_provider",
            "repo_branch",
            "repo_slug",
            "scaffold_status",
            "detected_stack",
            "scaffold_output",
            "scaffold_graph",
            "scaffold_error",
            "scaffolded_at",
            "completeness_score",
            "integrity_score",
            "error_flags",
            "suggestions",
            "created_at",
            "updated_at",
        ]

    def get_submitted_by(self, obj):
        if obj.created_by is None:
            return None
        return obj.created_by.get_full_name() or obj.created_by.username


class DashboardTeamsSerializer(serializers.ModelSerializer):
    added_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DashboardTeams
        fields = "__all__"
        read_only_fields = ["id", "created_at", "added_by", "updated_at"]
