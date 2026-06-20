from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver



@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    # List of default groups
    groups = ["clinic_admin", "clinic_staff"]

    for group_name in groups:
        Group.objects.get_or_create(name=group_name)


# second options use migrations to create groups
# home/migrations/0002_create_default_groups.py
# from django.db import migrations

# def create_groups(apps, schema_editor):
#     Group = apps.get_model('auth', 'Group')
#     groups = ['Admin', 'Manager', 'User']
#     for g in groups:
#         Group.objects.get_or_create(name=g)

# class Migration(migrations.Migration):

#     dependencies = [
#         ('home', '0001_initial'),
#     ]

#     operations = [
#         migrations.RunPython(create_groups),
#     ]

# Then run:
# You can create a migration file that adds groups.
# python manage.py makemigrations --empty home