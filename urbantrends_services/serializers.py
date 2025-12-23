from rest_framework import serializers
from .models import ServiceCategories, Service, ServiceTier

class ServiceTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTier
        fields = ["tier", "price", "features"]


class ServiceSerializer(serializers.ModelSerializer):
    tiers = ServiceTierSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "delivery_time",
            "tiers",
        ]


class ServiceCategorySerializer(serializers.ModelSerializer):
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceCategories
        fields = [
            "id",
            "title",
            "description",
            "services",
        ]