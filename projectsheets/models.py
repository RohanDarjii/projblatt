import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

# Create your models here.
class ProjectSheet(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('fr', 'French'),
        ('de', 'German'),
    ]
    language = models.CharField("Document Language", max_length=2, choices=LANGUAGE_CHOICES, default='de')
    # General Information
    project_number = models.CharField("Project Number", max_length=50)
    heading = models.CharField("Heading", max_length=200)
    project_title = models.CharField("Project Title", max_length=200)
    country = models.CharField("Country", max_length=100)
    location = models.CharField("Location", max_length=100)
    client_info = models.TextField("Client Details")
    financier = models.CharField("Financier", max_length=200, blank=True)
    object_name = models.CharField("Object Name", max_length=200)
    
    # Descriptions 
    performance_short = models.TextField("Performance (Bullets)")
    task_description = models.TextField("Task Description")
    performance_description = models.TextField("Performance Description")
    
    # Timeline & Costs
    date_from = models.DateField("Date From")
    date_until = models.DateField("Date Until", blank=True, null=True)
    processing_periods_months = models.IntegerField("Duration (Months)", blank=True, null=True)
    total_fee = models.CharField("Total Fee", max_length=100, blank=True)
    fee_kocks = models.CharField("Kocks Fee", max_length=100, blank=True)
    fee_planning = models.CharField("Fee Planning", max_length=100, blank=True)
    fee_construction = models.CharField("Fee Construction", max_length=100,blank=True)

    # Technical Details

    tech_value_header = models.TextField("Technical Headings", blank=True)
    tech_value_text = models.TextField("Technical Values", blank=True)
    
    staff_total = models.IntegerField("Total Staff", null=True, blank=True)
    staff_kocks = models.IntegerField("Kocks Staff", null=True, blank=True)
    senior_staff_names = models.TextField("Senior Staff Names", blank=True)
    man_months_total = models.DecimalField("Total Man-Months", max_digits=10, decimal_places=1, null=True, blank=True)
    man_months_kocks = models.DecimalField("Kocks Man-Months", max_digits=10, decimal_places=1, null=True, blank=True)
    partner_companies = models.TextField("Partner Companies", blank=True)
    
    captions = models.TextField("Photo Captions", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project_number} - {self.project_title} - {self.country} - {self.language}"

class ProjectImage(models.Model):
    project = models.ForeignKey(ProjectSheet, related_name="images", on_delete=models.CASCADE)

    # ✅ image stored in DATABASE
    image_data = models.BinaryField()
    content_type = models.CharField(max_length=50)

    # ✅ virtual folder (DB-level)
    folder_name = models.CharField(max_length=255, editable=False)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.folder_name = f"{self.project.project_title}_{self.project.project_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.folder_name}"