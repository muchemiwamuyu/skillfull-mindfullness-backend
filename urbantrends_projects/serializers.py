from rest_framework import serializers
from .models import DevProject


class DevProjectSerializer(serializers.ModelSerializer):
    # Include the username of the creator
    created_by = serializers.CharField(
        source="created_by.username", read_only=True
    )

    class Meta:
        model = DevProject
        fields = [
            "id",
            "title",
            "description",
            "live_link",
            "created_by",      # new field
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def validate_title(self, value):
        user = self.context["request"].user

        # If updating, exclude the current instance from duplicate check
        instance = getattr(self, "instance", None)
        qs = DevProject.objects.filter(title__iexact=value, created_by=user)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        if qs.exists():
            raise serializers.ValidationError(
                "You already have a project with this title."
            )

        return value

