from django.urls import path

from src.app.views import contrib_letter_form, contrib_person_form, contrib_profile


urlpatterns = [
    path("contrib/letter/add/", contrib_letter_form, name="contrib_letter_add"),
    path("contrib/person/add/", contrib_person_form, name="contrib_person_add"),
    path("contrib/profile/", contrib_profile, name="contrib_profile"),
]
