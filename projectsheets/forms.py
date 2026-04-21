from django import forms
from .models import ProjectSheet

# --- FIX START: Custom Classes to Handle Multiple Files ---

# 1. We create a custom widget that ALLOWS multiple files
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

# 2. We create a custom field that knows how to clean/process multiple files
class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        # We tell it to use our custom widget defined above
        kwargs.setdefault("widget", MultipleFileInput(attrs={'multiple': True}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        # If multiple files are uploaded, data is a list. We clean each one.
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

# --- FIX END ---

class ProjectSheetForm(forms.ModelForm):
    # Use our NEW custom field here instead of the standard forms.FileField
    photos = MultipleFileField(label="Upload All Project Photos", required=False)

    class Meta:
        model = ProjectSheet
        fields = '__all__'
        
        widgets = {
            'project_number': forms.TextInput(attrs={'class': 'form-control'}),
            'heading': forms.TextInput(attrs={'class': 'form-control'}),
            'project_title': forms.TextInput(attrs={'class': 'form-control'}),
            
            # Date Pickers
            'date_from': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_until': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # Text Areas
            'client_info': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'performance_short': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'task_description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'performance_description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'tech_value_header': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'tech_value_text': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'captions': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            
            # Language Dropdown
            'language': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply CSS class to any fields missed above
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'