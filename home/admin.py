from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import *


class CustomeUserAdmin(UserAdmin):
    list_display = ('custom_id', 'clinic', 'username', 'email', 'is_superuser', 'is_admin', 'is_admin_staff', 'is_active')
    list_filter = ('is_superuser', 'is_admin', 'is_admin_staff', 'is_active')
    search_fields = ('custom_id', 'clinic', 'username', 'eamil')
    readonly_fields = ('id', 'custom_id', 'date_joined', 'updated_at', 'last_login')
    ordering = ('date_joined',)

    fieldsets = (
        (_('Basic Info'), {'fields': ('username', 'password')}),
        (_('Personal Info'), {'fields': ('id', 'custom_id', 'first_name', 'last_name', 'email', 'phone',)}),
        (_('Additional Info'), {'fields': ('clinic', 'profile_img')}),
        (_('Permissions'), {'fields': ('is_active', 'is_superuser', 'is_admin', 'is_admin_staff', 'groups', 'user_permissions')}),
        (_('Read Only Fields'), {'fields': ('last_login', 'date_joined', 'updated_at')})
    )
    # include fields use either fields or exclude
    # fields = ('created_at', 'updated_at')
    
    # Exclude non-editable fields
    exclude = ('last_login', 'date_joined', 'updated_at')

    # Fields for the "Add User" form in the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'is_admin', 'is_admin_staff', 'is_active', 'password1', 'password2'),
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Handle password setting on creation."""
        if not obj.pk:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


# admin.site.register(User)
admin.site.register(User, CustomeUserAdmin)
admin.site.register(Clinic)
admin.site.register(Patient)
admin.site.register(Prescription)
admin.site.register(Notification)
admin.site.register(SeenNotification)

#ckeditor example
admin.site.register(CkModel)
