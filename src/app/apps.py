from django.apps import AppConfig as DjAppConf


class AppConfig(DjAppConf):
    default_auto_field = "django.db.models.BigAutoField"
    name = "src.app"
    verbose_name = "Letter Processing"
