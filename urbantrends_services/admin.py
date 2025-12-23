from django.contrib import admin
from .models import ServiceCategories, Service, ServiceTier

# Register your models here.

class ServiceTierInline(admin.TabularInline):
    model = ServiceTier
    extra = 0
    min_num = 3
    max_num = 3
    can_delete = False


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "delivery_time")
    list_filter = ("category",)
    search_fields = ("name",)
    inlines = [ServiceTierInline]


@admin.register(ServiceCategories)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("title",)
    search_fields = ("title",)


@admin.register(ServiceTier)
class ServiceTierAdmin(admin.ModelAdmin):
    list_display = ("service", "tier", "price")
    list_filter = ("tier",)
