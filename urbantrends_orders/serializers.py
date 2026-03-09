from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Order
from urbantrends_services.models import ServiceTier

User = get_user_model()

class UserMinimalSerializer(serializers.ModelSerializer):
    """Provides basic customer info for the admin dashboard"""
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class OrderSerializer(serializers.ModelSerializer):
    # Use the nested serializer for GET requests
    user = UserMinimalSerializer(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "category",
            "service_name",
            "tier_name",
            "price",
            "created_at",
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    tier_id = serializers.IntegerField()

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None

        tier = get_object_or_404(
            ServiceTier.objects.select_related("service_item__services_category"),
            id=validated_data["tier_id"],
        )

        order = Order.objects.create(
            user=user,
            category=tier.service_item.services_category.category,
            service_name=tier.service_item.name,
            tier_name=tier.tier,
            price=tier.price,
        )
        return order

    def to_representation(self, instance):
        """Pass the created order through the output serializer for a rich response"""
        return OrderSerializer(instance, context=self.context).data