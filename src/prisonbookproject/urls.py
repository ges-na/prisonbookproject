from ajax_select import urls as ajax_select_urls
from django.contrib import admin
from django.urls import include, path

from src.app.views import redirect_to_admin
from src.viz.urls import urlpatterns

urlpatterns = [
    path(r"admin/", admin.site.urls),
    path("", redirect_to_admin),
    path("viz/", include(urlpatterns)),
    path(r"ajax_select/", include(ajax_select_urls)),
]

admin.site.site_header = "Pittsburgh Prison Book Project"
admin.site.site_title = "Pittsburgh Prison Book Project"
