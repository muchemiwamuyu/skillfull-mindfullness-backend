from rest_framework import serializers
from .models import CreateBrandsFoundation, Module

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'name']

class CreateBrandsFoundationSerializer(serializers.ModelSerializer):
    modules = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Module.objects.all()
    )
    
    modules_details = ModuleSerializer(source='modules', many=True, read_only=True)

    class Meta:
        model = CreateBrandsFoundation
        fields = [
            'id', 
            'brand_name', 
            'brand_description', 
            'image', 
            'modules', 
            'modules_details'
        ]

    def to_internal_value(self, data):
        """
        Fixed to handle both standard JSON and FormData (QueryDict).
        """
        # 1. Extract the list correctly regardless of the request type
        if hasattr(data, 'getlist'):
            modules_list = data.getlist('modules')
        else:
            modules_list = data.get('modules', [])

        # 2. Ensure each string in the list exists in the Module table
        if isinstance(modules_list, list):
            for name in modules_list:
                if name:  # Avoid creating empty strings
                    Module.objects.get_or_create(name=name)

        # 3. Call super to let DRF perform the standard validation
        return super().to_internal_value(data)