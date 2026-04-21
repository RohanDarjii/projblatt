from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from projectsheets.models import ProjectSheet, ProjectImage


class Command(BaseCommand):
    help = 'Set up the "project manager" group with CRUD permissions for ProjectSheet and ProjectImage'

    def handle(self, *args, **options):
        # Get or create the "project manager" group
        group, created = Group.objects.get_or_create(name='project manager')
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created "project manager" group'))
        else:
            self.stdout.write('Group "project manager" already exists')

        # Get content types for our models
        projectsheet_ct = ContentType.objects.get_for_model(ProjectSheet)
        projectimage_ct = ContentType.objects.get_for_model(ProjectImage)

        # Get all CRUD permissions for both models
        permissions_to_add = []
        
        # ProjectSheet permissions: add, change, delete, view
        permissions_to_add.extend([
            Permission.objects.get(content_type=projectsheet_ct, codename='add_projectsheet'),
            Permission.objects.get(content_type=projectsheet_ct, codename='change_projectsheet'),
            Permission.objects.get(content_type=projectsheet_ct, codename='delete_projectsheet'),
            Permission.objects.get(content_type=projectsheet_ct, codename='view_projectsheet'),
        ])
        
        # ProjectImage permissions: add, change, delete, view
        permissions_to_add.extend([
            Permission.objects.get(content_type=projectimage_ct, codename='add_projectimage'),
            Permission.objects.get(content_type=projectimage_ct, codename='change_projectimage'),
            Permission.objects.get(content_type=projectimage_ct, codename='delete_projectimage'),
            Permission.objects.get(content_type=projectimage_ct, codename='view_projectimage'),
        ])

        # Add permissions to the group
        group.permissions.set(permissions_to_add)

        self.stdout.write(self.style.SUCCESS(
            f'Successfully assigned {len(permissions_to_add)} CRUD permissions to "project manager" group'
        ))
