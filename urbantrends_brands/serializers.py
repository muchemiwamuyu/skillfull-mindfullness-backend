from rest_framework import serializers
from .models import CreateBrandsFoundation, Module

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['id', 'name']

class CreateBrandsFoundationSerializer(serializers.ModelSerializer):
    # Use SlugRelatedField to point to the 'name' field of the Module model
    modules = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Module.objects.all()
    )
    
    # Optional: Keep this if you still want the ID and Name breakdown in GET requests
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
        Intercepts the incoming list of strings. 
        If a module name doesn't exist, it creates it on the fly.
        """
        if 'modules' in data and isinstance(data['modules'], list):
            for module_name in data['modules']:
                # This ensures "jhdjkskjh" becomes a database record before validation
                Module.objects.get_or_create(name=module_name)
        
        return super().to_internal_value(data)