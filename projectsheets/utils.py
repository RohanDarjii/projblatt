import base64
import os,io
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
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
                    'name': img.image_name or 'Project Image'
                })
        """logo as base64 string"""
        logo_base64 = None
        logo_path = os.path.join(os.path.dirname(__file__), '../static/home/images/logo_kocks.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as logo_file:
                logo_base64 = base64.b64encode(logo_file.read()).decode()
        context = {
            'project': project,
            'images': images_data,
            'logo': f'data:image/png;base64,{logo_base64}' if logo_base64 else None
        }

        """" Render HTML from template and context"""
        html_content = render_to_string('pdf_template.html', context)

        """ Generate PDF from HTML content"""
        pdf_bytes = HTML(string=html_content).write_pdf()

        return pdf_bytes