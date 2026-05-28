from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import ProjectImage, ProjectSheet
from .forms import ProjectSheetForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils import PDFGenerator
from django.db.models import Q
from .countries import ALL_COUNTRIES

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
    project_title = request.GET.get("project_title")

    if country:
        projects = projects.filter(country__icontains=country)

    if language:
        projects = projects.filter(language=language)

    if project_number:
        projects = projects.filter(project_number__icontains=project_number)

    if project_title:
        projects = projects.filter(
            Q(project_title__icontains=project_title) |
            Q(performance_description__icontains=project_title) |
            Q(task_description__icontains=project_title) |
            Q(performance_short__icontains=project_title)
    )

    # Pagination
    paginator = Paginator(projects, 10)  # Show 10 projects per page
    page = request.GET.get('page')
    
    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        projects = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        projects = paginator.page(paginator.num_pages)

    context = {
        "projects": projects,
        "countries": sorted(ALL_COUNTRIES),
        "languages": ProjectSheet.LANGUAGE_CHOICES,
        "selected_country": country,
        "selected_language": language,
        "search_project_number": project_number,
        "search_project_title": project_title,
    }

    return render(request, "project_list.html", context)


@login_required(login_url='home')
def search_projects_ajax(request):
    """
    AJAX endpoint for live search filtering with pagination.
    Returns JSON with filtered project data and pagination info.
    """
    query = request.GET.get('q', '').strip()
    country = request.GET.get('country', '').strip()
    language = request.GET.get('language', '').strip()
    page = request.GET.get('page', 1)
    
    projects = ProjectSheet.objects.all().order_by("-created_at")
    
    # Apply country filter
    if country:
        projects = projects.filter(country__icontains=country)
    
    # Apply language filter
    if language:
        projects = projects.filter(language=language)
    
    # Apply search query to multiple fields
    if query:
        projects = projects.filter(
            Q(project_number__icontains=query) |
            Q(project_title__icontains=query) |
            Q(performance_description__icontains=query) |
            Q(task_description__icontains=query) |
            Q(performance_short__icontains=query) |
            Q(country__icontains=query) |
            Q(location__icontains=query)
        )
    
    # Pagination
    paginator = Paginator(projects, 10)  # Show 10 projects per page
    
    try:
        projects_page = paginator.page(page)
    except PageNotAnInteger:
        projects_page = paginator.page(1)
    except EmptyPage:
        projects_page = paginator.page(paginator.num_pages)
    
    # Convert to JSON-serializable format
    results = []
    for project in projects_page:
        results.append({
            'id': project.id,
            'project_number': project.project_number,
            'project_title': project.project_title,
            'country': project.country,
            'location': project.location,
            'language': project.get_language_display(),
            'date_from': project.date_from.strftime('%Y-%m-%d'),
            'date_until': project.date_until.strftime('%Y-%m-%d') if project.date_until else '—',
            'images_count': project.images.count(),
        })
    
    return JsonResponse({
        'results': results,
        'count': paginator.count,
        'page': projects_page.number,
        'total_pages': paginator.num_pages,
        'has_previous': projects_page.has_previous(),
        'has_next': projects_page.has_next(),
        'previous_page': projects_page.previous_page_number() if projects_page.has_previous() else None,
        'next_page': projects_page.next_page_number() if projects_page.has_next() else None,
    })


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
        