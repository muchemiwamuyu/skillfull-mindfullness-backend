from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework import generics
from .models import ServiceCategories
from .serializers import ServiceCategorySerializer

# Create your views here.
@api_view(['GET'])
def hello(request):
    return HttpResponse("Hello from urbantrends services api")

class ServiceCategoryListView(generics.ListAPIView):
    queryset = ServiceCategories.objects.prefetch_related(
        "services__tiers"
    )
    serializer_class = ServiceCategorySerializer

