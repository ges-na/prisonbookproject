from django.urls import path

from src.app.views import (
    contrib_letter_form,
    contrib_letter_issue_form,
    contrib_logout,
    contrib_person_form,
    contrib_person_issue_form,
    contrib_profile,
    not_contributor,
)

urlpatterns = [
    path("contrib/", contrib_profile, name="contrib_base"),
    path("contrib/letter/add/", contrib_letter_form, name="contrib_letter_add"),
    path("contrib/person/add/", contrib_person_form, name="contrib_person_add"),
    path("contrib/letter/issue/add/", contrib_letter_issue_form, name="contrib_letter_issue"),
    path("contrib/person/issue/add/", contrib_person_issue_form, name="contrib_person_issue"),
    path("contrib/profile/", contrib_profile, name="contrib_profile"),
    path("contrib/logout/", contrib_logout, name="contrib_logout"),
    path("contrib/profile/", contrib_profile, name="contrib_profile"),
    path("contrib/not_contributor/", not_contributor, name="not_contributor"),
]
