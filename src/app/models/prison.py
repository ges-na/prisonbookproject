from django.contrib.auth.models import User
from django.db import models

from ..utils import NO_PRISON_STR


class Prison(models.Model):
    class Types(models.TextChoices):
        SCI = "sci", "SCI"
        FCI = "fci", "FCI"
        USP = "usp", "USP"
        CITY = "city", "City"
        COUNTY = "county", "County"
        FDC = "fdc", "FDC"
        IMMIGRATION_DETENTION = (
            "immigration_detention",
            "Immigration Detention Facility",
        )
        BOOT_CAMP = "boot_camp", "Boot Camp"
        REHAB_FACILITY = "rehab_facility", "Rehab Facility"

    name = models.CharField(max_length=200)
    prison_type = models.CharField(max_length=200, choices=Types.choices)
    # TODO: STEAL FROM https://github.com/furious-luke/django-address/blob/develop/address/models.py
    legacy_address = models.CharField(max_length=200, blank=True)
    additional_mailing_headers = models.CharField(max_length=200, blank=True)
    mailing_address = models.CharField(max_length=200)
    mailing_city = models.CharField(max_length=200)
    mailing_state = models.CharField(max_length=50, default="PA")
    mailing_zipcode = models.CharField(max_length=200)
    restrictions = models.TextField(blank=True)
    # TODO: FEATURE
    # accepts_books =models.CharField(choices=[("true", "Yes"), ("restricted", "Yes, with restrictions"), ("false", "No"), ("unknown", "Unknown")], default="unknown")
    legacy_id = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        related_name="prison_created_by_user",
        on_delete=models.SET_NULL,
    )
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        User,
        null=True,
        related_name="prison_modified_by_user",
        on_delete=models.SET_NULL,
    )

    id: int

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class PersonPrison(models.Model):
    person = models.ForeignKey(
        "Person", on_delete=models.CASCADE, related_name="prisons"
    )
    prison = models.ForeignKey(
            "Prison", on_delete=models.CASCADE, related_name="people", null=True, blank=True
    )
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        related_name="personprison_created_by_user",
        on_delete=models.SET_NULL,
    )
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        if not self.prison:
            return f"{NO_PRISON_STR} - {self.person.last_name}"
        return f"{self.prison.name} - {self.person.last_name}"
