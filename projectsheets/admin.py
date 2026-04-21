from django.contrib import admin
from .models import ProjectSheet, ProjectImage
from django.utils.html import format_html
from django.urls import reverse
from django import forms


class ProjectImageForm(forms.ModelForm):
    """Custom form for ProjectImage to handle file uploads"""
    image_upload = forms.FileField(
        required=False,
        label="Upload Image",
        help_text="Select an image file to upload (JPG, PNG, GIF, WebP)"
    )

    class Meta:
        model = ProjectImage
        fields = ['project']

    def clean_image_upload(self):
        file_obj = self.cleaned_data.get('image_upload')
        if file_obj:
            # Validate file type
            valid_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if file_obj.content_type not in valid_types:
                raise forms.ValidationError("Please upload a valid image file (JPG, PNG, GIF, or WebP)")
            # Check file size (max 5MB)
            if file_obj.size > 5 * 1024 * 1024:
                raise forms.ValidationError("Image file size cannot exceed 5MB")
        return file_obj

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data.get('image_upload'):
            file_obj = self.cleaned_data['image_upload']
            instance.image_data = file_obj.read()
            instance.content_type = file_obj.content_type
        if commit:
            instance.save()
        return instance


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    form = ProjectImageForm
    extra = 1

    # Show upload field and preview
    readonly_fields = ("image_preview", "uploaded_at")
    fields = ("image_upload", "image_preview", "uploaded_at")

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
    list_display = ("project_number", "project_title", "country", "language", "edit_button")
    search_fields = ("project_title", "project_number")
    list_filter = ("language", "country")

    inlines = [ProjectImageInline]

    def edit_button(self, obj):
        """Add an Edit button to quickly access the edit form"""
        url = reverse('admin:projectsheets_projectsheet_change', args=[obj.pk])
        return format_html(
            '<a class="button" style="background-color: #417690; color: white; padding: 5px 15px; border-radius: 4px; text-decoration: none;" href="{}">Edit</a>',
            url
        )
    
    edit_button.short_description = "Actions"

    def has_add_permission(self, request):
        """Only allow users with 'add_projectsheet' permission"""
        return request.user.has_perm('projectsheets.add_projectsheet')

    def has_change_permission(self, request, obj=None):
        """Only allow users with 'change_projectsheet' permission"""
        return request.user.has_perm('projectsheets.change_projectsheet')

    def has_delete_permission(self, request, obj=None):
        """Only allow users with 'delete_projectsheet' permission"""
        return request.user.has_perm('projectsheets.delete_projectsheet')

    def has_view_permission(self, request, obj=None):
        """Only allow users with 'view_projectsheet' permission"""
        return request.user.has_perm('projectsheets.view_projectsheet')


class ProjectImageAdmin(admin.ModelAdmin):
    list_display = ("pk", "project", "uploaded_at")
    search_fields = ("project__project_title", "project__project_number")
    list_filter = ("uploaded_at",)

    def has_add_permission(self, request):
        """Only allow users with 'add_projectimage' permission"""
        return request.user.has_perm('projectsheets.add_projectimage')

    def has_change_permission(self, request, obj=None):
        """Only allow users with 'change_projectimage' permission"""
        return request.user.has_perm('projectsheets.change_projectimage')

    def has_delete_permission(self, request, obj=None):
        """Only allow users with 'delete_projectimage' permission"""
        return request.user.has_perm('projectsheets.delete_projectimage')

    def has_view_permission(self, request, obj=None):
        """Only allow users with 'view_projectimage' permission"""
        return request.user.has_perm('projectsheets.view_projectimage')


admin.site.register(ProjectSheet, ProjectSheetAdmin)
admin.site.register(ProjectImage, ProjectImageAdmin)