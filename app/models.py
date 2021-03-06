from enum import Enum
from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now


class WorkflowStage(models.TextChoices):
    PROCESSED = "processed", "Processed"
    AWAITING_FULFILLMENT = "awaiting_fulfillment", "Awaiting fulfillment"
    FULFILLED = "fulfilled", "Fulfilled"
    JUST_PADA = "just_pada", "Just PADA"
    PROBLEM = "problem", "Problem"


class PersonManager(models.Manager):
    def get_queryset(self):
        pass


class Person(models.Model):


    class Statuses(models.TextChoices):
        SOLITARY = "solitary", "Solitary"
        LIFER = "lifer", "Lifer"

    inmate_number = models.CharField(max_length=50)
    last_name = models.CharField(max_length=200)
    first_name = models.CharField(max_length=200)
    created_date = models.DateTimeField(auto_now_add=True)
    legacy_prison_id = models.SmallIntegerField(null=True)
    legacy_last_served_date = models.DateTimeField(null=True, default=None)
    notes = models.CharField(max_length=500, blank=True)
    status = models.CharField(
        max_length=200,
        choices=Statuses.choices,
        blank=True
    )
    modified_date = models.DateTimeField(auto_now=True)
    modified_by=models.ForeignKey(User, null=True, related_name='person_modified_by_user', on_delete=models.SET_NULL, default=User)
    created_by=models.ForeignKey(User, null=True, related_name='person_created_by_user', on_delete=models.SET_NULL, default=User)

    class Meta:
        # ordering = ('-pending_letter',)
        verbose_name_plural = "people"

    def __str__(self):
        return self.last_name

    @property
    def current_prison(self):
        if person_prison := self.prisons.filter(current=True).first():
            return person_prison.prison

    @property
    def last_served(self):
        if fulfilled_letters := self.letter_set.filter(workflow_stage__in=[WorkflowStage.FULFILLED]):
            return fulfilled_letters.order_by("fulfilled_date").first().fulfilled_date
        elif self.legacy_last_served_date:
            return datetime.date(self.legacy_last_served_date)
        return

    @property
    def has_been_served(self):
        if not self.last_served:
            return False
        return True

    @property
    def has_pending_letters(self):
        if not self.pending_letter_count:
            return False
        return True

    @property
    def eligibility(self):
        if not self.has_been_served:
            if not self.has_pending_letters:
                return "Eligible"
            return f"Eligible, {self.pending_letter_count} letters pending"
        elif self.last_served <= (datetime.now().date() - timedelta(weeks=12)):
            if not self.has_pending_letters:
                return "Eligible"
            else:
                return f"Eligible, {self.pending_letter_count} letters pending"
        elif date_last_fulfilled := self.letter_set.filter(workflow_stage__in=[WorkflowStage.FULFILLED]):
            last_fulfilled_date = date_last_fulfilled.order_by(
            "fulfilled_date"
            ).first().fulfilled_date
            eligible_date = last_fulfilled_date + timedelta(weeks=12)
            return f"Eligible after {eligible_date.strftime('%B %-d, %Y')}"
        else:
            eligibility_from_legacy_date = self.legacy_last_served_date + timedelta(weeks=12)
            return f"Eligible after {eligibility_from_legacy_date.strftime('%B %-d, %Y')}"

    @property
    def package_count(self):
        return self.letter_set.filter(workflow_stage__in=[WorkflowStage.FULFILLED]).count()

    @property
    def pending_letter_count(self):
        return self.letter_set.filter(
            workflow_stage__in=[
                WorkflowStage.PROCESSED,
                WorkflowStage.AWAITING_FULFILLMENT
            ]
        ).count()

    @property
    def pending_letters(self):
        return self.letter_set.filter(
            workflow_stage__in=[
                WorkflowStage.PROCESSED,
                WorkflowStage.AWAITING_FULFILLMENT
            ]
        ).all()

    @property
    def letter_count(self):
        return self.letter_set.all().count()

    @property
    def all_letters(self):
        return self.letter_set.all()


class Prison(models.Model):


    class PrisonTypes(models.TextChoices):
        SCI = "sci", "SCI"
        FCI = "fci", "FCI"
        CITY = "city", "City"
        COUNTY = "county", "County"
        FDC = "fdc", "FDC"
        tMMIGRATION_DETENTION = "immigration_detention", "Immigration Detention Facility"
        BOOT_CAMP = "boot_camp", "Boot Camp"


    name = models.CharField(max_length=200)
    prison_type = models.CharField(
        max_length=200,
        choices=PrisonTypes.choices
    )
    legacy_address = models.CharField(max_length=200, blank=True)
    mailing_address = models.CharField(max_length=200, blank=True)
    mailing_city = models.CharField(max_length=200, blank=True)
    mailing_state = models.CharField(max_length=50, blank=True)
    mailing_zipcode = models.CharField(max_length=200, blank=True)
    restrictions = models.CharField(max_length=200, blank=True)
    legacy_id = models.CharField(max_length=50, unique=True, blank=True)
    notes = models.CharField(max_length=200, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by=models.ForeignKey(User, null=True, related_name='prison_modified_by_user', on_delete=models.SET_NULL)
    created_by=models.ForeignKey(User, null=True, related_name='prison_created_by_user', on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class Letter(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE)
    modified_by=models.ForeignKey(User, null=True, related_name='letter_modified_by_user', on_delete=models.SET_NULL, default=User)
    created_by=models.ForeignKey(User, null=True, related_name='letter_created_by_user', on_delete=models.SET_NULL, default=User)

    postmark_date = models.DateField(null=True, blank=True)
    processed_date = models.DateField(null=True, blank=True, default=now)
    awaiting_fulfillment_date = models.DateField(null=True, blank=True)
    fulfilled_date = models.DateField(null=True, blank=True)
    # change to choices
    workflow_stage = models.CharField(
        max_length=200,
        choices=WorkflowStage.choices,
        default=WorkflowStage.PROCESSED
    )
    notes = models.CharField(max_length=200, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    # modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.person.last_name} - {self.postmark_date}"


class PersonPrison(models.Model):
    person = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='prisons')
    prison = models.ForeignKey('Prison', on_delete=models.CASCADE, related_name='people')
    current = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by=models.ForeignKey(User, null=True, related_name='personprison_modified_by_user', on_delete=models.SET_NULL)
    created_by=models.ForeignKey(User, null=True, related_name='personprison_created_by_user', on_delete=models.SET_NULL)

    def __str__(self):
        return f"{self.prison.name} - {self.person.last_name}"
