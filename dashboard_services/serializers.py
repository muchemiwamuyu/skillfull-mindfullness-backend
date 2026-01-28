from rest_framework import serializers
from .models import DashboardProject

# serializers
class DashboardProjectSerializer(serializers.ModelSerializer):
    model = DashboardProject
    fields = '__all__'
    read_only_fields = ["id", "created_at", "project_by" "updated_at"]