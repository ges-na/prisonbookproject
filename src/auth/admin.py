from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from src.auth.models import User


class UserAdmin(DjangoUserAdmin):
    search_fields = ("email", "last_name", "first_name")
    ordering = ("date_joined",)
    add_fieldsets = (
        (None, {"fields": ("email", "password1", "password2")}),
        (("Personal info"), {"fields": ("first_name", "last_name")}),
        (("Permissions"), {"fields": ("is_active", "is_contributor", "is_staff", "groups")}),
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_contributor",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = [
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_contributor",
        "is_staff",
        "is_superuser",
    ]


admin.site.register(User, UserAdmin)
