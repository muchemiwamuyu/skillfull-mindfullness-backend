from django.shortcuts import render
from rest_framework import viewsets
from .models import CreateBrandsFoundation, Module
from .serializers import CreateBrandsFoundationSerializer, ModuleSerializer
# Create your views here.


class BrandFoundationViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides default CRUD actions for CreateBrandsFoundation.
    """
    queryset = CreateBrandsFoundation.objects.all()
    serializer_class = CreateBrandsFoundationSerializer

class ModuleViewSet(viewsets.ModelViewSet):
    """
    Optional: A viewset to manage the individual Module entries.
    """
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
