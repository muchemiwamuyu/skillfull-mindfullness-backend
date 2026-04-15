from django.contrib import admin

from .models import ClientProject


@admin.register(ClientProject)
class ClientProjectAdmin(admin.ModelAdmin):
    list_display = [
        "project_name",
        "email",
        "status",
        "scaffold_status",
        "completeness_score",
        "integrity_score",
        "due_date",
        "created_at",
    ]
    list_filter = ["status", "scaffold_status", "repo_provider"]
    search_fields = ["project_name", "email", "created_by__username", "created_by__email"]
    readonly_fields = [
        "scaffold_status",
        "detected_stack",
        "scaffold_output",
        "scaffold_graph",
        "scaffold_error",
        "scaffolded_at",
        "completeness_score",
        "integrity_score",
        "error_flags",
        "suggestions",
        "created_at",
        "updated_at",
    ]
    fieldsets = (
        ("Project", {
            "fields": ("project_name", "description", "email", "due_date", "status", "created_by"),
        }),
        ("Repository", {
            "fields": ("repo_url", "repo_provider", "repo_branch", "repo_access_token"),
        }),
        ("Scaffold Results", {
            "classes": ("collapse",),
            "fields": (
                "scaffold_status", "scaffold_error", "scaffolded_at",
                "detected_stack", "completeness_score", "integrity_score",
                "error_flags", "suggestions",
            ),
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )
