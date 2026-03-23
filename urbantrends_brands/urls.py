from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrandFoundationViewSet, ModuleViewSet, BrandTierViewSet

router = DefaultRouter()
router.register(r'brands', BrandFoundationViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'tiers', BrandTierViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
