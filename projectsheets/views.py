from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
from .models import ProjectImage, ProjectSheet
from .forms import ProjectSheetForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .utils import PDFGenerator

# Create your views here.
@login_required(login_url='home')
def serve_project_image(request, image_id):
    img = ProjectImage.objects.get(id=image_id)
    return HttpResponse(img.image_data, content_type=img.content_type)

def home_view(request):
    return render(request, 'home.html')

@login_required(login_url='home')
def create_project_sheet(request):
    if request.method == 'POST':
        # 1. Load Data and Files into the Form
        form = ProjectSheetForm(request.POST, request.FILES)
        
        # --- DEBUG: Check if files are arriving ---
        files = request.FILES.getlist('photos')
        print(f"DEBUG: Form received {len(files)} files.") 

        if form.is_valid():
            # 2. Save the Project Data (Title, Number, etc.) first
            project = form.save()
            print(f"DEBUG: Project '{project.project_title}' saved with ID: {project.id}")
            # 3. Save the Photos
            # We loop through the list of files caught by the form widget
            for f in files:
                ProjectImage.objects.create(
                    project=project,
                    image_data=f.read(),          # ✅ binary data
                    content_type=f.content_type   # ✅ mime type
                )
            return redirect('home')
            
        else:
            print("DEBUG: Form Validation Errors:", form.errors)
            
    else:
        form = ProjectSheetForm()
        
    return render(request, 'create_project_sheet.html', {'form': form})


@login_required(login_url='home')
def project_list(request):
    projects = ProjectSheet.objects.all().order_by("-created_at")

    country = request.GET.get("country")
    language = request.GET.get("language")
    project_number = request.GET.get("project_number")

    if country:
        projects = projects.filter(country__icontains=country)

    if language:
        projects = projects.filter(language=language)

    if project_number:
        projects = projects.filter(project_number__icontains=project_number)

    countries = (
        ProjectSheet.objects
        .values_list("country", flat=True)
        .distinct()
        .order_by("country")
    )

    context = {
        "projects": projects,
        "countries": countries,
        "languages": ProjectSheet.LANGUAGE_CHOICES,
        "selected_country": country,
        "selected_language": language,
        "search_project_number": project_number,
    }

    return render(request, "project_list.html", context)


@login_required(login_url='home')
def project_detail_view(request, pk):
    project = get_object_or_404(ProjectSheet, pk=pk)
    
    # Check if user has permission to edit
    can_edit = request.user.has_perm('projectsheets.change_projectsheet')
    
    # Check if user has permission to delete
    can_delete = request.user.has_perm('projectsheets.delete_projectsheet')

    # Load form with instance
    form = ProjectSheetForm(instance=project)

    # 🔒 Make ALL fields read-only by default
    for field in form.fields.values():
        field.disabled = True

    return render(request, "project_detail.html", {
        "form": form,
        "project": project,
        "can_edit": can_edit,
        "can_delete": can_delete,
    })

@login_required(login_url='home')
def delete_project_sheet(request, pk):
    project = get_object_or_404(ProjectSheet, pk=pk)
    if not request.user.has_perm('projectsheets.delete_projectsheet'):
        raise PermissionDenied("You don't have permission to delete this project.")
    if request.method == 'POST':
        project.delete()
        return redirect('project_list')
    return render(request, 'delete_project_sheet.html', {'project': project})


@login_required(login_url='home')
def edit_project_sheet(request, pk):
    project = get_object_or_404(ProjectSheet, pk=pk)
    
    # Check permission - only users with change_projectsheet permission can edit
    if not request.user.has_perm('projectsheets.change_projectsheet'):
        raise PermissionDenied("You don't have permission to edit this project.")
    
    if request.method == 'POST':
        # Handle image deletion first
        images_to_delete = request.POST.getlist('delete_images')
        for image_id in images_to_delete:
            try:
                image = ProjectImage.objects.get(id=image_id, project=project)
                image.delete()
            except ProjectImage.DoesNotExist:
                pass
        
        form = ProjectSheetForm(request.POST, request.FILES, instance=project)
        
        if form.is_valid():
            project = form.save()
            
            # Handle new image uploads
            files = request.FILES.getlist('photos')
            for f in files:
                ProjectImage.objects.create(
                    project=project,
                    image_data=f.read(),
                    content_type=f.content_type
                )
            
            # Redirect back to project detail
            return redirect('project_detail', pk=project.pk)
        else:
            print("DEBUG: Form Validation Errors:", form.errors)
    else:
        form = ProjectSheetForm(instance=project)
    
    return render(request, "edit_project_sheet.html", {
        "form": form,
        "project": project,
        "is_edit": True,
        "existing_images": project.images.all(),
    })


@login_required(login_url='home')
def view_project_pdf(request, pk):
    project = get_object_or_404(ProjectSheet, pk=pk)
    
    try:
        # Check permission - only users with view_projectsheet permission can export
        if not request.user.has_perm('projectsheets.view_projectsheet'):
            raise PermissionDenied("You don't have permission to export this project.")
        
        # Generate PDF content using the utility function
        pdf_content = PDFGenerator.generate_pdf(project, include_images=True)

        # Create HTTP response with PDF content
        response = HttpResponse(pdf_content, content_type='application/pdf')
        filename = f'project_{project.project_title}.pdf'
        response['Content-Disposition'] = f'inline; filename="{filename}"'
        
        return response
    
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return HttpResponse("An error occurred while generating the PDF.", status=500)
        