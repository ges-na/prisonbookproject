from django.urls import path

from src.app.views import (
    contrib_letter_form_add,
    contrib_letter_form_change,
    contrib_letter_issue_form,
    contrib_logout,
    contrib_person_form_add,
    contrib_person_form_change,
    contrib_person_issue_form,
    contrib_person_prison_change_form,
    contrib_profile,
    not_contributor,
)

urlpatterns = [
    path("contrib/", contrib_profile, name="contrib_base"),
    path("contrib/letter/add/", contrib_letter_form_add, name="contrib_letter_add"),
    path("contrib/letter/change/", contrib_letter_form_change, name="contrib_letter_change"),
    path("contrib/person/add/", contrib_person_form_add, name="contrib_person_add"),
    path(
        "contrib/person/change/",
        contrib_person_form_change,
        name="contrib_person_change",
    ),
    path("contrib/letter/issue/add/", contrib_letter_issue_form, name="contrib_letter_issue"),
    path("contrib/person/issue/add/", contrib_person_issue_form, name="contrib_person_issue"),
    path(
        "contrib/personprison/change/",
        contrib_person_prison_change_form,
        name="contrib_personprison_change",
    ),
    path("contrib/profile/", contrib_profile, name="contrib_profile"),
    path("contrib/logout/", contrib_logout, name="contrib_logout"),
    path("contrib/profile/", contrib_profile, name="contrib_profile"),
    path("contrib/not_contributor/", not_contributor, name="not_contributor"),
]
