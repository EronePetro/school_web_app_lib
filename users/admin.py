from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin

class UserAdminConfig(UserAdmin):
    ordering = ['-date_joined']
    list_display = ('full_name', 'email', 'is_active', 'is_staff')
    search_fields = ('email', 'full_name')
    list_filter = ('email', 'is_active', 'is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('full_name', 'email')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'is_librarian',  'is_classteacher', 'is_active', 'groups', 'user_permissions')}),

    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('full_name', 'email', 'password1', 'password2', 'date_joined', 'is_staff',
                       'is_superuser', 'is_librarian', 'is_classteacher', 'is_active')
           }
        ),
    )
    
admin.site.register(User, UserAdminConfig)