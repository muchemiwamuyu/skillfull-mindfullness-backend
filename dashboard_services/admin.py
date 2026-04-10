from django.contrib import admin
from .models import DashboardProject, DashboardTeams, DashboardCustomProject


@admin.register(DashboardCustomProject)
class DashboardCustomProjectAdmin(admin.ModelAdmin):
    list_display = ["id", "project_type", "user", "complexity", "estimated_duration", "status", "created_at"]
    list_filter = ["status", "complexity"]
    search_fields = ["project_type", "user__username", "user__email"]
    readonly_fields = ["estimated_duration", "created_at", "updated_at"]
    fields = [
        "user", "project_type", "description", "requirements",
        "complexity", "budget", "budget_currency",
        "estimated_duration", "status", "admin_notes",
        "created_at", "updated_at",
    ]


admin.site.register(DashboardProject)
admin.site.register(DashboardTeams)
