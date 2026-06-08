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
        "change_is_contributor_permission",
        "change_is_active_permission",
        "change_is_staff_permission",
    )
    readonly_fields = ("last_login", "date_joined")

    @admin.action(description="Change user's active status")
    def change_is_active_permission(self, request, queryset):
        breakpoint()
        if "CustomAuth.change_is_active" not in request.user.get_all_permissions():
            messages.error(request, "You do not have permission to change active status")
            return
        change = []
        for user in queryset:
            change.append(user.id)
        queryset.filter(id__in=change).update(is_active=True)

    @admin.action(description="Change user's contributor status")
    def change_is_contributor_permission(self, request, queryset):
        if "CustomAuth.change_is_contrib" not in request.user.get_all_permissions():
            messages.error(request, "You do not have permission to change contributor status")
            return
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

    def change_is_staff_permission(self, request, queryset):
        if "CustomAuth.change_is_staff" not in request.user.get_all_permissions():
            messages.error(request, "You do not have permission to change staff status")
            return
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


admin.site.register(User, UserAdmin)
