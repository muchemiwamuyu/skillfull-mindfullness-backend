from rest_framework import serializers
from .models import Services, ServiceItem, ServiceTier

class ServiceTierNestedSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # for updates

    class Meta:
        model = ServiceTier
        fields = ['id', 'tier', 'price', 'description']

class ServiceTierPickSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTier
        fields = ['id', 'tier', 'price', 'description']

class ServiceItemPickSerializer(serializers.ModelSerializer):
    tiers = ServiceTierPickSerializer(many=True, read_only=True)

    class Meta:
        model = ServiceItem
        fields = ['id', 'name', 'tiers']

class ServicesPickSerializer(serializers.ModelSerializer):
    service_items = ServiceItemPickSerializer(many=True, read_only=True)

    class Meta:
        model = Services
        fields = ['id', 'category', 'service_items']

class ServiceItemNestedSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # for updates
    tiers = ServiceTierNestedSerializer(many=True)

    class Meta:
        model = ServiceItem
        fields = ['id', 'name', 'tiers']

    def create(self, validated_data):
        tiers_data = validated_data.pop('tiers', [])
        service_category = self.context.get('services_category')
        item = ServiceItem.objects.create(services_category=service_category, **validated_data)
        for tier_data in tiers_data:
            ServiceTier.objects.create(service_item=item, **tier_data)
        return item

    def update(self, instance, validated_data):
        # Update item name
        instance.name = validated_data.get('name', instance.name)
        instance.save()

        tiers_data = validated_data.get('tiers', [])
        existing_tiers = {tier.id: tier for tier in instance.tiers.all()}

        for tier_data in tiers_data:
            tier_id = tier_data.get('id', None)
            if tier_id and tier_id in existing_tiers:
                # Update existing tier
                tier = existing_tiers[tier_id]
                tier.tier = tier_data.get('tier', tier.tier)
                tier.price = tier_data.get('price', tier.price)
                tier.description = tier_data.get('description', tier.description)
                tier.save()
            else:
                # Create new tier
                ServiceTier.objects.create(service_item=instance, **tier_data)
        return instance

class ServicesNestedSerializer(serializers.ModelSerializer):
    service_items = ServiceItemNestedSerializer(many=True)

    class Meta:
        model = Services
        fields = ['id', 'category', 'service_items']

    # ✅ Explicit create method for POST
    def create(self, validated_data):
        items_data = validated_data.pop('service_items', [])
        service_category = Services.objects.create(**validated_data)

        for item_data in items_data:
            item_serializer = ServiceItemNestedSerializer(
                data=item_data,
                context={'services_category': service_category}
            )
            item_serializer.is_valid(raise_exception=True)
            item_serializer.save()

        return service_category

    # Update method for PATCH
    def update(self, instance, validated_data):
        # Update category
        instance.category = validated_data.get('category', instance.category)
        instance.save()

        items_data = validated_data.get('service_items', [])
        existing_items = {item.id: item for item in instance.service_items.all()}

        for item_data in items_data:
            item_id = item_data.get('id', None)
            if item_id and item_id in existing_items:
                # Update existing item
                item_serializer = ServiceItemNestedSerializer(
                    instance=existing_items[item_id],
                    data=item_data,
                    context={'services_category': instance}
                )
                item_serializer.is_valid(raise_exception=True)
                item_serializer.save()
            else:
                # Create new item
                item_serializer = ServiceItemNestedSerializer(
                    data=item_data,
                    context={'services_category': instance}
                )
                item_serializer.is_valid(raise_exception=True)
                item_serializer.save()

        return instance
