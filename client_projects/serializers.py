from rest_framework import serializers
from .models import ClientProject
import re

class ClientProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProject
        fields = "__all__"
        read_only_fields = ["id",
            "status",
            "created_at",
            "updated_at",]

    def validate_phone(self, value):
        # allows +254, spaces, hyphens — but blocks garbage
        pattern = r"^\+?[0-9\s\-]{7,20}$"
        if not re.match(pattern, value):
            raise serializers.ValidationError("Invalid phone number format.")
        return value

    def validate_due_date(self, value):
        from datetime import date
        if value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

    def validate(self, attrs):
        """
        Extra guard: prevent duplicate submissions
        """
        email = attrs.get("email")
        project_name = attrs.get("project_name")

        if ClientProject.objects.filter(
            email=email,
            project_name=project_name
        ).exists():
            raise serializers.ValidationError(
                "A project with this email and project name already exists."
            )

        return attrs
