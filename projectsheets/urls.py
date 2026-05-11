from .views import home_view, create_project_sheet, serve_project_image, project_list, project_detail_view, edit_project_sheet, delete_project_sheet, view_project_pdf
from django.urls import path    

urlpatterns = [
    path('', home_view, name='home'),    
    path('create_project_sheet/', create_project_sheet, name='create_project_sheet'),
    path("project-image/<int:image_id>/", serve_project_image, name="serve_project_image"),
    path("project_list/",project_list, name="project_list" ),
    path("projects/<int:pk>/view/", project_detail_view, name="project_detail"),
    path("projects/<int:pk>/edit/", edit_project_sheet, name="edit_project_sheet"),
    path("projects/<int:pk>/delete/", delete_project_sheet, name="delete_project_sheet"),
    path("projects/<int:pk>/pdf/", view_project_pdf, name="view_project_pdf"),
]