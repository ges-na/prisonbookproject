from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path, include
from django.urls import reverse

from ajax_select import urls as ajax_select_urls

urlpatterns = [
    path(r"admin/", admin.site.urls),
    # path(r"/", HttpResponseRedirect(reverse(admin.site.urls))),
    path(r"ajax_select/", include(ajax_select_urls)),
]

admin.site.site_header = "Pittsburgh Prison Book Project"
admin.site.site_title = "Pittsburgh Prison Book Project"
