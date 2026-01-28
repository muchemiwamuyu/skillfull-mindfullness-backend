from rest_framework import serializers
from .models import DashboardProject

class DashboardProjectSerializer(serializers.ModelSerializer):
    project_by = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = DashboardProject
        fields = "__all__"
        read_only_fields = ["id", "created_at", "project_by", "updated_at"]
