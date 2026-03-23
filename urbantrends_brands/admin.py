from django.contrib import admin
from .models import CreateBrandsFoundation, Module, BrandTier


class BrandTierInline(admin.TabularInline):
    model = BrandTier
    extra = 1


@admin.register(CreateBrandsFoundation)
class BrandFoundationAdmin(admin.ModelAdmin):
    list_display = ['brand_name']
    inlines = [BrandTierInline]


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(BrandTier)
class BrandTierAdmin(admin.ModelAdmin):
    list_display = ['brand', 'tier', 'region', 'currency', 'price', 'support_level', 'is_active']
    list_filter = ['tier', 'region', 'currency', 'is_active']
    search_fields = ['brand__brand_name']
