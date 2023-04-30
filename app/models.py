from datetime import datetime, timedelta
from enum import Enum

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.timezone import make_aware, now


ELIGIBILITY_INTERVAL = 90


class WorkflowStage(models.TextChoices):
    STAGE1_COMPLETE = "stage1_complete", "Stage 1 complete"
    FULFILLED = "fulfilled", "Fulfilled"
    JUST_PADA = "just_pada", "Just PADA"
    PROBLEM = "problem", "Problem"
    DISCARDED = "discarded", "Discarded"


class PrisonTypes(models.TextChoices):
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


class PersonManager(models.Manager):
    def get_queryset(self):
        pass


class Person(models.Model):
    class Statuses(models.TextChoices):
        SOLITARY = "solitary", "Solitary"
        LIFER = "lifer", "Lifer"

    inmate_number = models.CharField(max_length=50, unique=True)
    last_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, blank=True)
    first_name = models.CharField(max_length=200)
    name_suffix = models.CharField(max_length=200, blank=True)
    legacy_prison_id = models.SmallIntegerField(null=True)
    legacy_last_served_date = models.DateTimeField(null=True, default=None)
    notes = models.CharField(max_length=500, blank=True)
    status = models.CharField(max_length=200, choices=Statuses.choices, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        related_name="person_created_by_user",
        on_delete=models.SET_NULL,
    )
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        # ordering = ('-pending_letter',)
        verbose_name_plural = "people"

    def __str__(self):
        return self.last_name

    @property
    def current_prison(self):
        if person_prison := self.prisons.first():
            return person_prison.prison

    @property
    def last_served(self):
        if fulfilled_letters := self.letter_set.filter(
            workflow_stage__in=[WorkflowStage.FULFILLED],
            counts_against_last_served=True,
        ):
            return fulfilled_letters.order_by("fulfilled_date").last().fulfilled_date
        elif self.legacy_last_served_date:
            return self.legacy_last_served_date
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

    # this is gross and repetitive of pending_letter_count in admin.py
    @property
    def eligibility(self):
        cooldown_interval = make_aware(
            (datetime.now() - timedelta(days=ELIGIBILITY_INTERVAL))
        )

        if self.has_pending_letters:
            pending_letters_string = format_html(
                f"<a href={reverse('admin:app_letter_changelist')}?person={self.id}&workflow_stage__in={WorkflowStage.STAGE1_COMPLETE}>{self.pending_letter_count} letters pending</a>"
            )

        # If the person has never been served, they are eligible
        ## and may have letters pending
        if not self.has_been_served:
            if not self.has_pending_letters:
                return "Eligible"
            return format_html(f"Eligible; {pending_letters_string}")

        eligible_date = self.last_served + timedelta(days=ELIGIBILITY_INTERVAL)

        # If the person was last served less than ELIGIBILITY_INTERVAL days ago,
        ## they are ineligible but may have letters pending
        if self.last_served > cooldown_interval:
            if not self.has_pending_letters:
                return format_html(
                    f"Eligible after {eligible_date.strftime('%B %-d, %Y')}"
                )
            return format_html(
                f"Eligible after {eligible_date.strftime('%B %-d, %Y')}; {pending_letters_string}"
            )

        # If the person was last served more than or exactly ELIGIBILITY_INTERVAL days ago
        ## (that is, cooldown_interval is a "bigger" or more recent date)
        ## they are eligible and may have letters pending
        elif self.last_served <= cooldown_interval:
            if not self.has_pending_letters:
                return "Eligible"
            return format_html(f"Eligible; {pending_letters_string}")

    @property
    def package_count(self):
        return self.letter_set.filter(
            workflow_stage__in=[WorkflowStage.FULFILLED]
        ).count()

    @property
    def pending_letter_count(self):
        return self.letter_set.filter(
            workflow_stage__in=[
                WorkflowStage.STAGE1_COMPLETE,
            ]
        ).count()

    @property
    def pending_letters(self):
        return self.letter_set.filter(
            workflow_stage__in=[
                WorkflowStage.STAGE1_COMPLETE,
            ]
        ).all()

    @property
    def letter_count(self):
        return self.letter_set.all().count()

    @property
    def all_letters(self):
        return self.letter_set.all()

    def save(self, *args, **kwargs):
        if self.inmate_number == "":
            self.inmate_number == None
        super().save(*args, **kwargs)


class Prison(models.Model):

    name = models.CharField(max_length=200)
    prison_type = models.CharField(max_length=200, choices=PrisonTypes.choices)
    legacy_address = models.CharField(max_length=200, blank=True)
    additional_mailing_headers = models.CharField(max_length=200, blank=True)
    mailing_address = models.CharField(max_length=200)
    mailing_city = models.CharField(max_length=200)
    mailing_state = models.CharField(max_length=50, default="PA")
    mailing_zipcode = models.CharField(max_length=200)
    restrictions = models.CharField(max_length=200, blank=True)
    accepts_books = models.CharField(
        max_length=200, choices=[(True, "True"), (False, "False"), (None, "Unknown")]
    )
    legacy_id = models.CharField(max_length=50, blank=True)
    notes = models.CharField(max_length=200, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        related_name="prison_created_by_user",
        on_delete=models.SET_NULL,
    )
    modified_date = models.DateTimeField(auto_now=True)
    # not sure about this, only implemented here currently, see save method on PrisonAdmin
    modified_by = models.ForeignKey(
        User,
        null=True,
        related_name="prison_modified_by_user",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]


class Letter(models.Model):
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    postmark_date = models.DateField(null=True, blank=True, default=now)
    stage1_complete_date = models.DateTimeField(null=True, blank=True, default=now)
    fulfilled_date = models.DateTimeField(null=True, blank=True)
    counts_against_last_served = models.BooleanField(
        null=False, blank=False, default=True
    )
    # TODO: this should probably have an on_delete.SET() argument that writes the prison name
    prison_sent_to = models.ForeignKey(
        "Prison",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    workflow_stage = models.CharField(
        max_length=200,
        choices=WorkflowStage.choices,
        default=WorkflowStage.STAGE1_COMPLETE,
    )
    notes = models.CharField(max_length=200, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        related_name="letter_created_by_user",
        on_delete=models.SET_NULL,
    )
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.person.last_name} - {self.postmark_date}"


class PersonPrison(models.Model):
    person = models.ForeignKey(
        "Person", on_delete=models.CASCADE, related_name="prisons"
    )
    prison = models.ForeignKey(
        "Prison", on_delete=models.CASCADE, related_name="people"
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
        return f"{self.prison.name} - {self.person.last_name}"
