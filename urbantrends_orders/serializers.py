from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Order, BrandOrder
from urbantrends_services.models import ServiceTier
from urbantrends_brands.models import BrandTier

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


class BrandOrderSerializer(serializers.ModelSerializer):
    user = UserMinimalSerializer(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = BrandOrder
        fields = [
            "id",
            "user",
            "brand_tier",
            "brand_name",
            "tier_name",
            "price",
            "currency",
            "region",
            "selected_modules",
            "status",
            "status_display",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id", "user", "brand_name", "tier_name", "price",
            "currency", "region", "created_at", "updated_at",
        ]


class BrandOrderCreateSerializer(serializers.Serializer):
    brand_tier_id = serializers.IntegerField()
    selected_modules = serializers.ListField(child=serializers.CharField(), required=False, default=list)
    notes = serializers.CharField(required=False, default="")

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user

        tier = get_object_or_404(
            BrandTier.objects.select_related("brand").prefetch_related("brand__modules"),
            id=validated_data["brand_tier_id"],
            is_active=True,
        )

        order = BrandOrder.objects.create(
            user=user,
            brand_tier=tier,
            brand_name=tier.brand.brand_name,
            tier_name=tier.get_tier_display(),
            price=tier.price,
            currency=tier.currency,
            region=tier.region,
            selected_modules=validated_data.get("selected_modules", []),
            notes=validated_data.get("notes", ""),
        )
        return order

    def to_representation(self, instance):
        return BrandOrderSerializer(instance, context=self.context).data


class BrandOrderStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=BrandOrder.STATUS_CHOICES)