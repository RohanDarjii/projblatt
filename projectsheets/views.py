from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse, JsonResponse
from httpcore import request
from .models import ProjectImage, ProjectSheet
from .forms import ProjectSheetForm
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils import PDFGenerator
from django.db.models import Q, Count, Case, When, IntegerField, F, DecimalField, Sum, Avg
from django.db.models.functions import ExtractYear, TruncMonth
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from datetime import timedelta
from collections import defaultdict
import json
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
            project = form.save(commit=False)
            # Capture who created this project
            if request.user.is_authenticated:
                project.created_by = request.user
            project.save()
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
            project = form.save(commit=False)
            # Capture who last updated this project
            if request.user.is_authenticated:
                project.updated_by = request.user
            project.save()
            
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


@login_required(login_url='home')
def dashboard(request):
    is_superuser = request.user.is_superuser
    if not (
        request.user.is_superuser or
        request.user.groups.filter(
            name="Project Manager"
        ).exists()
    ):
        raise PermissionDenied(
            "You don't have access to the dashboard."
        )
    
    # ===== KPI CARDS =====
    total_projects = ProjectSheet.objects.count()
    total_countries = ProjectSheet.objects.values('country').distinct().count()
    total_images = ProjectImage.objects.count()
    languages_available = ProjectSheet.objects.values('language').distinct().count()
    
    # Projects missing images and descriptions
    projects_missing_images = ProjectSheet.objects.filter(images__isnull=True).count()
    projects_missing_descriptions = ProjectSheet.objects.filter(
        Q(task_description__isnull=True) | Q(task_description='') |
        Q(performance_description__isnull=True) | Q(performance_description='')
    ).count()
    
    # Calculate averages
    avg_images_per_project = (
        ProjectSheet.objects.annotate(image_count=Count('images'))
        .aggregate(avg=Avg('image_count'))['avg'] or 0
    )
    avg_images_per_project = round(float(avg_images_per_project), 2)
    
    # Data Quality Score (0-100)
    total_quality_checks = total_projects * 3  # 3 quality checks per project
    quality_passes = (
        (total_projects - projects_missing_images) +
        (total_projects - projects_missing_descriptions) +
        (ProjectSheet.objects.filter(client_info__isnull=False).exclude(client_info='').count())
    )
    data_quality_score = int((quality_passes / total_quality_checks * 100)) if total_quality_checks > 0 else 0
    
    # ===== PROJECTS BY COUNTRY =====
    projects_by_country = (
        ProjectSheet.objects.values('country')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    projects_by_country_list = list(projects_by_country)
    
    # ===== LANGUAGE DISTRIBUTION =====
    language_dist = (
        ProjectSheet.objects.values('language')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    language_dist_list = list(language_dist)
    language_names = {code: name for code, name in ProjectSheet.LANGUAGE_CHOICES}
    
    # ===== PROJECTS BY YEAR =====
    projects_by_year = (
        ProjectSheet.objects.annotate(year=ExtractYear('date_from'))
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )
    projects_by_year_list = list(projects_by_year)
    
    # ===== REVENUE BY YEAR (in Euros) =====
    # Parse fee_kocks field and group by year
    all_projects_with_year = ProjectSheet.objects.annotate(
        year=ExtractYear('date_from')
    ).values('year', 'fee_kocks').order_by('year')
    
    revenue_by_year_dict = defaultdict(float)
    for project in all_projects_with_year:
        if project['year'] and project['fee_kocks']:
            # Parse the fee_kocks value (e.g., "130k EUR", "90000", "€ 125,000")
            fee_str = str(project['fee_kocks']).strip().upper()
            
            # Remove currency labels
            fee_str = fee_str.replace('EUR', '').replace('€', '').replace('$', '').strip()
            
            # Handle 'k' suffix (thousands)
            has_k_suffix = 'K' in fee_str
            if has_k_suffix:
                fee_str = fee_str.replace('K', '').strip()
            
            # Handle both comma and dot as decimal separator
            if ',' in fee_str and '.' in fee_str:
                # Has both - assume dot is decimal, comma is thousands
                fee_str = fee_str.replace(',', '')
            elif ',' in fee_str:
                # Has only comma - check position to determine if thousands or decimal
                last_comma_pos = fee_str.rfind(',')
                if len(fee_str) - last_comma_pos <= 3:
                    # Comma is thousands separator
                    fee_str = fee_str.replace(',', '')
                else:
                    # Comma is decimal separator
                    fee_str = fee_str.replace(',', '.')
            
            try:
                revenue = float(fee_str)
                # If had 'k' suffix, multiply by 1000
                if has_k_suffix:
                    revenue *= 1000
                revenue_by_year_dict[project['year']] += revenue
            except (ValueError, TypeError):
                # Skip if can't parse as number
                pass
    
    # Convert to sorted list format for chart
    revenue_by_year_list = [
        {'year': year, 'revenue': round(revenue, 2)} 
        for year, revenue in sorted(revenue_by_year_dict.items())
    ]
    
    # ===== LATEST PROJECTS TABLE (Top 10) =====
    latest_projects = (
        ProjectSheet.objects.annotate(
            image_count=Count('images'),
            has_description=Case(
                When(
                    task_description__isnull=False,
                    task_description__gt='',
                    then=True
                ),
                default=False,
                output_field=IntegerField()
            )
        )
        .order_by('-created_at')[:10]
    )
    
    # ===== DATA QUALITY PANEL =====
    projects_missing_images_list = (
        ProjectSheet.objects.filter(images__isnull=True)
        .values_list('project_number', 'project_title', 'country')[:5]
    )
    
    projects_missing_descriptions_list = (
        ProjectSheet.objects.filter(
            Q(task_description__isnull=True) | Q(task_description='')
        )
        .values_list('project_number', 'project_title')[:5]
    )
    
    projects_missing_client_info = (
        ProjectSheet.objects.filter(
            Q(client_info__isnull=True) | Q(client_info='')
        )
        .values_list('project_number', 'project_title')[:5]
    )
    
    # ===== TOP 10 COUNTRIES (by project count) =====
    top_countries = (
        ProjectSheet.objects.values('country')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    top_countries_list = list(top_countries)
    
    # ===== TOP 10 CLIENTS =====
    top_clients = (
        ProjectSheet.objects.values('client_info')
        .filter(client_info__isnull=False)
        .exclude(client_info='')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    top_clients_list = list(top_clients)
    
    # ===== PROJECTS CREATED PER MONTH (Last 12 months) =====
    months_ago = timezone.now() - timedelta(days=365)
    projects_per_month = (
        ProjectSheet.objects.filter(created_at__gte=months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )
    # Convert datetime objects to strings for JSON serialization
    projects_per_month_list = []
    for item in projects_per_month:
        projects_per_month_list.append({
            'month': item['month'].strftime('%Y-%m-%d') if item['month'] else None,
            'count': item['count']
        })
    
    # ===== PROJECTS BY LANGUAGE DETAILED =====
    projects_by_language = (
        ProjectSheet.objects.values('language')
        .annotate(count=Count('id'))
        .order_by('-count')
    )
    projects_by_language_list = list(projects_by_language)
    
    # ===== RECENT ACTIVITY FEED =====
    recent_activity = ProjectSheet.objects.order_by('-created_at')[:8]
    
    # ===== WORLD MAP DATA (Country Count) =====
    # Convert country names to codes for Leaflet visualization
    country_data = {}
    for country in ProjectSheet.objects.values('country').annotate(count=Count('id')).order_by('-count'):
        country_name = country['country']
        country_data[country_name] = country['count']
    
    # ===== JSON SERIALIZATION FOR CHARTS =====
    # Convert all chart data to JSON strings for safe template rendering
    chart_data_json = {
        'projectsByCountry': json.dumps(projects_by_country_list, cls=DjangoJSONEncoder),
        'languageDistribution': json.dumps(language_dist_list, cls=DjangoJSONEncoder),
        'languageNames': json.dumps(language_names, cls=DjangoJSONEncoder),
        'projectsByYear': json.dumps(projects_by_year_list, cls=DjangoJSONEncoder),
        'revenueByYear': json.dumps(revenue_by_year_list, cls=DjangoJSONEncoder),
        'topCountries': json.dumps(top_countries_list, cls=DjangoJSONEncoder),
        'topClients': json.dumps(top_clients_list, cls=DjangoJSONEncoder),
        'projectsPerMonth': json.dumps(projects_per_month_list, cls=DjangoJSONEncoder),
        'countryData': json.dumps(country_data, cls=DjangoJSONEncoder),
    }
    
    context = {
        # KPI Cards
        "total_projects": total_projects,
        "total_countries": total_countries,
        "total_images": total_images,
        "languages_available": languages_available,
        "projects_missing_images": projects_missing_images,
        "projects_missing_descriptions": projects_missing_descriptions,
        "avg_images_per_project": avg_images_per_project,
        "data_quality_score": data_quality_score,
        
        # Chart data (JSON strings)
        "chart_data": chart_data_json,
        
        # Chart data (for tables, kept as lists)
        "projects_by_country": projects_by_country_list,
        "language_dist": language_dist_list,
        "language_names": language_names,
        "projects_by_year": projects_by_year_list,
        
        # Tables
        "latest_projects": latest_projects,
        "projects_missing_images_list": projects_missing_images_list,
        "projects_missing_descriptions_list": projects_missing_descriptions_list,
        "projects_missing_client_info": projects_missing_client_info,
        
        # Additional charts
        "top_countries": top_countries_list,
        "top_clients": top_clients_list,
        "projects_per_month": projects_per_month_list,
        "projects_by_language": projects_by_language_list,
        
        # Other
        "recent_activity": recent_activity,
        "country_data": country_data,
        "is_superuser": is_superuser,
    }
    
    return render(request, "dashboard.html", context)