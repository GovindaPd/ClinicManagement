from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from home.models import *


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

        # Permissions to assign
        # permission_codenames = ['add_post', 'change_post', 'delete_post']
        # list_of_models = [User, Clinic, Patient, Prescription, Notification, SeenNotification]
        
        # Get permissions
        # content_type = ContentType.objects.get_for_model(User)
        # permissions = Permission.objects.filter(content_type=content_type, codename__in=permission_codenames)

        # Assign permissions to group
        # group.permissions.set(permissions)

        # self.stdout.write(self.style.SUCCESS(f"Assigned permissions to group '{group_name}'"))