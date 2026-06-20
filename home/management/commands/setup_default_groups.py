from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from home.models import *

# Command to create default groups and assign permissions
#we had also created signals.py file to create groups automatically after migration if you don't want that you can delete signals.py file
class Command(BaseCommand):
    help = 'Creates default groups and assigns permissions'

    def handle(self, *args, **options):
        # Group name
        group_names = ["Clinic Admin", "Clinic Staff"]
    
        # Get or create group
        for group_name in group_names:
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group '{group_name}'"))
            else:
                self.stdout.write(self.style.WARNING(f"Group '{group_name}' already exists"))