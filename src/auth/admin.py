from django.contrib import admin
from src.auth.models import User

from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (("Permissions", {"fields": ("is_contributor",)}),)
    list_display = ["email", "first_name", "last_name", "is_active", "is_contributor", "is_staff", "is_superuser"]

admin.site.register(User, UserAdmin)
