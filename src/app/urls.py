from django.urls import path

from src.app.views import (
    contrib_add_problem_note_form,
    contrib_letter_form,
    contrib_logout,
    contrib_person_form,
    contrib_profile,
    not_contributor,
)

urlpatterns = [
    path("contrib/", contrib_profile, name="contrib_base"),
    path("contrib/letter/add/", contrib_letter_form, name="contrib_letter_add"),
    path("contrib/person/add/", contrib_person_form, name="contrib_person_add"),
    path(
        "contrib/problem_note/add/", contrib_add_problem_note_form, name="contrib_problem_note_add"
    ),
    path("contrib/profile/", contrib_profile, name="contrib_profile"),
    path("contrib/logout/", contrib_logout, name="contrib_logout"),
    path("contrib/profile/", contrib_profile, name="contrib_profile"),
    path("contrib/not_contributor/", not_contributor, name="not_contributor"),
]
