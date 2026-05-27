from ajax_select import urls as ajax_select_urls
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

from src.app.views import RegistrationView, redirect_to_admin, redirect_to_contrib_profile
from src.viz.urls import urlpatterns

urlpatterns = [
    path(r"admin/", admin.site.urls),
    path("", redirect_to_admin),
    path("viz/", include(urlpatterns)),
    path(r"ajax_select/", include(ajax_select_urls)),
    path(
        "accounts/register/",
        RegistrationView.as_view(),
        name="django_registration_register",
    ),
    path("accounts/", include("django_registration.backends.activation.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/profile/", redirect_to_contrib_profile),
    path("", include("src.app.urls")),
    path("logout/", LogoutView.as_view(next_page="contrib_logout"), name="logout"),
]

admin.site.site_header = "Pittsburgh Prison Book Project"
admin.site.site_title = "Pittsburgh Prison Book Project"
