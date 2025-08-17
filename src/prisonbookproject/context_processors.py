from django.conf import settings

def export_vars(request):
    return {"env_name": settings.ENV_NAME}
