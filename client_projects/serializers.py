from datetime import date

from rest_framework import serializers

from .models import ClientProject


class ClientProjectSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ClientProject
        fields = [
            "id",
            # Core
            "project_name",
            "description",
            "email",
            "due_date",
            "status",
            "created_by",
            "created_at",
            "updated_at",
            # Repo input (token is write-only — never returned in responses)
            "repo_url",
            "repo_provider",
            "repo_branch",
            "repo_access_token",
            # Scaffold output (read-only — set by the background task)
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
        ]
        read_only_fields = [
            "id",
            "status",
            "created_by",
            "created_at",
            "updated_at",
            # All scaffold fields are populated by the background task
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
        ]
        extra_kwargs = {
            "repo_access_token": {"write_only": True},
        }

    def get_created_by(self, obj):
        if obj.created_by is None:
            return None
        return obj.created_by.get_full_name() or obj.created_by.username

    def validate_due_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate(self, attrs):
        email = attrs.get("email")
        project_name = attrs.get("project_name")

        qs = ClientProject.objects.filter(email=email, project_name=project_name)

        # On update, exclude the current instance
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "A project with this email and project name already exists."
            )

        return attrs
