from rest_framework import serializers
from .models import CreateBrandsFoundation, Module, BrandTier


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'name']


class BrandTierSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    region_display = serializers.CharField(source='get_region_display', read_only=True)
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    support_level_display = serializers.CharField(source='get_support_level_display', read_only=True)

    class Meta:
        model = BrandTier
        fields = [
            'id', 'tier', 'tier_display', 'description', 'price',
            'currency', 'region', 'region_display', 'features',
            'max_modules', 'support_level', 'support_level_display',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class CreateBrandsFoundationSerializer(serializers.ModelSerializer):
    modules = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Module.objects.all()
    )
    modules_details = ModuleSerializer(source='modules', many=True, read_only=True)
    tiers = BrandTierSerializer(many=True, required=False)

    class Meta:
        model = CreateBrandsFoundation
        fields = [
            'id',
            'brand_name',
            'brand_description',
            'image',
            'modules',
            'modules_details',
            'tiers',
        ]

    def to_internal_value(self, data):
        """
        Fixed to handle both standard JSON and FormData (QueryDict).
        """
        if hasattr(data, 'getlist'):
            modules_list = data.getlist('modules')
        else:
            modules_list = data.get('modules', [])

        if isinstance(modules_list, list):
            for name in modules_list:
                if name:
                    Module.objects.get_or_create(name=name)

        return super().to_internal_value(data)

    def create(self, validated_data):
        tiers_data = validated_data.pop('tiers', [])
        modules_data = validated_data.pop('modules', [])
        brand = CreateBrandsFoundation.objects.create(**validated_data)
        brand.modules.set(modules_data)
        for tier_data in tiers_data:
            BrandTier.objects.create(brand=brand, **tier_data)
        return brand

    def update(self, instance, validated_data):
        tiers_data = validated_data.pop('tiers', None)
        modules_data = validated_data.pop('modules', None)

        instance.brand_name = validated_data.get('brand_name', instance.brand_name)
        instance.brand_description = validated_data.get('brand_description', instance.brand_description)
        if 'image' in validated_data:
            instance.image = validated_data['image']
        instance.save()

        if modules_data is not None:
            instance.modules.set(modules_data)

        if tiers_data is not None:
            existing_tiers = {t.id: t for t in instance.tiers.all()}
            for tier_data in tiers_data:
                tier_id = tier_data.pop('id', None)
                if tier_id and tier_id in existing_tiers:
                    tier = existing_tiers[tier_id]
                    for attr, value in tier_data.items():
                        setattr(tier, attr, value)
                    tier.save()
                else:
                    BrandTier.objects.create(brand=instance, **tier_data)

        return instance


class BrandTierStandaloneSerializer(serializers.ModelSerializer):
    region_display = serializers.CharField(source='get_region_display', read_only=True)
    tier_display = serializers.CharField(source='get_tier_display', read_only=True)
    support_level_display = serializers.CharField(source='get_support_level_display', read_only=True)
    brand_name = serializers.CharField(source='brand.brand_name', read_only=True)

    class Meta:
        model = BrandTier
        fields = [
            'id', 'brand', 'brand_name', 'tier', 'tier_display',
            'description', 'price', 'currency', 'region', 'region_display',
            'features', 'max_modules', 'support_level', 'support_level_display',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
