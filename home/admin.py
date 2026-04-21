from django.contrib import admin
from projectsheets.models import ProjectSheet, ProjectImage
from django.utils.html import format_html
from django.urls import reverse
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

    # Show preview only (image_data is edited via upload)
    readonly_fields = ("image_preview",)
    fields = ("image_preview",)

    def image_preview(self, obj):
        if obj.pk:
            url = reverse("serve_project_image", args=[obj.pk])
            return format_html(
                '<img src="{}" style="max-height:150px; max-width:150px; border-radius:6px;" />',
                url
            )
        return "No image"

    image_preview.short_description = "Preview"


class ProjectSheetAdmin(admin.ModelAdmin):
    list_display = ("project_number", "project_title", "country", "language")
    search_fields = ("project_title", "project_number")
    list_filter = ("language", "country")

    inlines = [ProjectImageInline]

    
admin.site.register(ProjectSheet)
admin.site.register(ProjectImage)