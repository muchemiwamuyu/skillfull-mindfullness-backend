from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import Services, ServiceItem, ServiceTier, Order, OrderItem
from django.contrib.auth.models import User


# ---------- Service / Tier Serializers ----------

class ServiceTierSerializer(serializers.ModelSerializer):
    service_item_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceItem.objects.all(),
        source="service_item",
        write_only=True
    )

    def validate(self, attrs):
        # Handle both create & update
        service_item = attrs.get(
            "service_item",
            getattr(self.instance, "service_item", None)
        )

        qs = ServiceTier.objects.filter(service_item=service_item)

        # Exclude current instance during updates
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.count() >= 3:
            raise serializers.ValidationError(
                "A service item can only have 3 tiers."
            )

        return attrs

    class Meta:
        model = ServiceTier
        fields = [
            "id",
            "service_item_id",
            "tier",
            "price",
            "description",
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=ServiceTier.objects.all(),
                fields=["service_item", "tier"],
                message="This tier already exists for this service."
            )
        ]


class ServiceItemSerializer(serializers.ModelSerializer):
    tiers = ServiceTierSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceItem
        fields = ["id", "services_category", "name", "tiers"]


class ServicesSerializer(serializers.ModelSerializer):
    service_items = ServiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Services
        fields = ["id", "category", "service_items"]


# ---------- Order / OrderItem Serializers ----------

class OrderItemSerializer(serializers.ModelSerializer):
    service_item = ServiceItemSerializer(read_only=True)
    tier = ServiceTierSerializer(read_only=True)

    service_item_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceItem.objects.all(),
        source="service_item",
        write_only=True
    )
    tier_id = serializers.PrimaryKeyRelatedField(
        queryset=ServiceTier.objects.all(),
        source="tier",
        write_only=True
    )

    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "service_item",
            "tier",
            "quantity",
            "service_item_id",
            "tier_id",
            "total_price",
        ]

    def get_total_price(self, obj):
        return obj.total_price()


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = serializers.StringRelatedField(read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "status",
            "created_at",
            "updated_at",
            "items",
            "total_price",
        ]

    def get_total_price(self, obj):
        return obj.total_price()

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order
