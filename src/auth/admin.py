from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from src.auth.models import User


class UserAdmin(DjangoUserAdmin):
    search_fields = ("email", "last_name", "first_name")
    ordering = ("-date_joined",)
    add_fieldsets = (
        (None, {"fields": ("email", "password1", "password2")}),
        (("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            ("Permissions"),
            {"fields": ("is_active", "is_contributor", "is_staff", "groups")},
        ),
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
    actions = (
        "enable_is_active",
        "enable_is_contributor",
        "enable_is_staff",
        "disable_is_active",
        "disable_is_contributor",
        "disable_is_staff",
    )
    readonly_fields = ("last_login", "date_joined")

    @admin.action(description="Enable user's active status", permissions=["change_is_active"])
    def enable_is_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="Disable user's active status", permissions=["change_is_active"])
    def disable_is_active(self, request, queryset):
        queryset.update(is_active=False)

    def has_change_is_active_permission(self, request):
        return bool("CustomAuth.change_is_active" in request.user.get_all_permissions())

    @admin.action(description="Enable user's contributor status", permissions=["change_is_contrib"])
    def enable_is_contributor(self, request, queryset):
        change = []
        for user in queryset:
            if not user.is_active:
                messages.error(
                    request,
                    f"User {user.email} is not currently active, cannot give contributor permission.",
                )
                continue
            else:
                change.append(user.id)
        queryset.filter(id__in=change).update(is_contributor=True)

    @admin.action(
        description="Disable user's contributor status", permissions=["change_is_contrib"]
    )
    def disable_is_contributor(self, request, queryset):
        queryset.update(is_contributor=False)

    def has_change_is_contrib_permission(self, request):
        return bool("CustomAuth.change_is_contrib" in request.user.get_all_permissions())

    @admin.action(description="Enable user's staff status", permissions=["change_is_staff"])
    def enable_is_staff(self, request, queryset):
        change = []
        for user in queryset:
            if not user.is_active:
                messages.error(
                    request,
                    f"User {user.email} is not currently active, cannot give staff permission.",
                )
                continue
            else:
                change.append(user.id)
        queryset.filter(id__in=change).update(is_staff=True)

    @admin.action(description="Disable user's staff status", permissions=["change_is_staff"])
    def disable_is_staff(self, request, queryset):
        queryset.update(is_staff=False)

    def has_change_is_staff_permission(self, request):
        return bool("CustomAuth.change_is_staff" in request.user.get_all_permissions())


admin.site.register(User, UserAdmin)
