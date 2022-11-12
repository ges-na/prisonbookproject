from django.contrib import admin
from django.urls import path, include

from ajax_select import urls as ajax_select_urls

from app.views import redirect_to_admin

urlpatterns = [
    path(r"admin/", admin.site.urls),
    path("", redirect_to_admin),
    path(r"ajax_select/", include(ajax_select_urls)),
]

admin.site.site_header = "Pittsburgh Prison Book Project"
admin.site.site_title = "Pittsburgh Prison Book Project"
