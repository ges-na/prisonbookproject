from django.apps import AppConfig as DjAppConfig
from django.contrib.admin.apps import AdminConfig as DjAdminConfig


class AppConfig(DjAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.app"
    verbose_name = "Letter Processing"


class AdminConfig(DjAdminConfig):
    default_site = "src.app.admin_site.AdminSite"
