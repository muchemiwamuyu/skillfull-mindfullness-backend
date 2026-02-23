from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Order
from urbantrends_services.models import ServiceTier


class OrderCreateSerializer(serializers.Serializer):
    tier_id = serializers.IntegerField()

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request and request.user.is_authenticated else None

        tier = get_object_or_404(
            ServiceTier.objects.select_related("service_item__services_category"),
            id=validated_data["tier_id"],
        )

        return Order.objects.create(
            user=user,
            category=tier.service_item.services_category.category,
            service_name=tier.service_item.name,
            tier_name=tier.tier,
            price=tier.price,
        )

#  Output serializer
class OrderSerializer(serializers.ModelSerializer):
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