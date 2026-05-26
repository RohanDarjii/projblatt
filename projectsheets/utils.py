import base64
import os,io
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from django.utils.timezone import now

# Multi-language translation dictionaries for PDF labels
LANGUAGE_TRANSLATIONS = {
    'de': {
        'the_task': 'Die Aufgabe',
        'the_services': 'Die Leistungen',
        'project': 'PROJEKT',
        'client': 'AUFTRAGGEBER',
        'services': 'LEISTUNGEN',
        'location': 'STANDORT',
        'period': 'ZEITRAUM',
        'technical_description': 'Technische Beschreibung',
        'process_engineering': 'Verfahrenstechnik',
        'investment': 'INVESTITION',
        'biological_system': 'BIOLOGISCHES SYSTEM',
        'mechanical_system': 'MECHANISCHES SYSTEM',
        'page_of': 'Seite',
        'of': 'von',
    },
    'en': {
        'the_task': 'The Task',
        'the_services': 'The Services',
        'project': 'PROJECT',
        'client': 'CLIENT',
        'services': 'SERVICES',
        'location': 'LOCATION',
        'period': 'PERIOD',
        'technical_description': 'Technical Description',
        'process_engineering': 'Process Engineering',
        'investment': 'INVESTMENT',
        'biological_system': 'BIOLOGICAL SYSTEM',
        'mechanical_system': 'MECHANICAL SYSTEM',
        'page_of': 'Page',
        'of': 'of',
    },
    'es': {
        'the_task': 'La Tarea',
        'the_services': 'Los Servicios',
        'project': 'PROYECTO',
        'client': 'CLIENTE',
        'services': 'SERVICIOS',
        'location': 'UBICACIÓN',
        'period': 'PERÍODO',
        'technical_description': 'Descripción Técnica',
        'process_engineering': 'Ingeniería de Procesos',
        'investment': 'INVERSIÓN',
        'biological_system': 'SISTEMA BIOLÓGICO',
        'mechanical_system': 'SISTEMA MECÁNICO',
        'page_of': 'Página',
        'of': 'de',
    },
    'fr': {
        'the_task': 'La Tâche',
        'the_services': 'Les Services',
        'project': 'PROJET',
        'client': 'CLIENT',
        'services': 'SERVICES',
        'location': 'LOCALISATION',
        'period': 'PÉRIODE',
        'technical_description': 'Description Technique',
        'process_engineering': 'Ingénierie des Procédés',
        'investment': 'INVESTISSEMENT',
        'biological_system': 'SYSTÈME BIOLOGIQUE',
        'mechanical_system': 'SYSTÈME MÉCANIQUE',
        'page_of': 'Page',
        'of': 'sur',
    },
}

class PDFGenerator:
    
    @staticmethod
    def generate_pdf(project, include_images=True):
        """Generate PDF content using weasyprint"""
        images_data = []
        if include_images and project.images.exists():
            for img in project.images.all():
                img_base64 =base64.b64encode(img.image_data).decode()
                images_data.append({
                    'data': img_base64,
                    'content_type': img.content_type
                })
        
        """logo as base64 string"""
        logo_base64 = None
        logo_path = os.path.join(os.path.dirname(__file__), '../static/home/images/logo_kocks.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as logo_file:
                logo_base64 = base64.b64encode(logo_file.read()).decode()
        
        # Get language-specific translations (default to German if language not found)
        language = project.language if project.language in LANGUAGE_TRANSLATIONS else 'de'
        labels = LANGUAGE_TRANSLATIONS[language]
        
        context = {
            'project': project,
            'images': images_data,
            'logo': f'data:image/png;base64,{logo_base64}' if logo_base64 else None,
            'current_date': now(),
            'labels': labels,
            'language': language,
        }

        """" Render HTML from template and context"""
        html_content = render_to_string('pdf_template.html', context)

        """ Generate PDF from HTML content"""
        pdf_bytes = HTML(string=html_content).write_pdf()

        return pdf_bytes
