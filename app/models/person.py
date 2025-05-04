from __future__ import annotations

from datetime import datetime, timedelta
from functools import cached_property
from typing import TYPE_CHECKING

from django.contrib.auth.models import User
from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.html import format_html
from django.utils.timezone import make_aware

from app.utils import WorkflowStage

if TYPE_CHECKING:
    from app.models.letter import Letter
    from app.models.prison import PersonPrison, Prison

ELIGIBILITY_INTERVAL_DAYS = 90


class Person(models.Model):
    class Statuses(models.TextChoices):
        SOLITARY = "solitary", "Solitary"
        LIFER = "lifer", "Lifer"

    inmate_number = models.CharField(max_length=50, unique=True)
    last_name = models.CharField(max_length=200)
    middle_name = models.CharField(max_length=200, blank=True)
    first_name = models.CharField(max_length=200)
    name_suffix = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=200, choices=Statuses.choices, blank=True)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        related_name="person_created_by_user",
        on_delete=models.SET_NULL,
    )
    modified_date = models.DateTimeField(auto_now=True)

    prisons: QuerySet[PersonPrison]
    letter_set: QuerySet[Letter]

    class Meta:
        verbose_name_plural = "people"

    def __str__(self):
        return self.last_name

    @property
    def current_prison(self) -> Prison | None:
        if person_prison := self.prisons.first():
            return person_prison.prison

    @cached_property
    def last_served(self):
        if fulfilled_letters := self.letter_set.filter(
            workflow_stage=WorkflowStage.FULFILLED,
            counts_against_last_served=True,
        ):
            return fulfilled_letters.order_by("fulfilled_date").last().fulfilled_date
        return

    @property
    def has_been_served(self):
        return bool(self.last_served)

    @property
    def has_pending_letters(self):
        return bool(self.pending_letter_count)

    @property
    def package_count(self):
        return self.letter_set.filter(workflow_stage=WorkflowStage.FULFILLED).count()

    @property
    def pending_letters(self):
        return self.letter_set.filter(
            workflow_stage__in=[
                WorkflowStage.STAGE1_COMPLETE,
            ]
        )

    @property
    def pending_letter_count(self):
        return self.pending_letters.count()

    @property
    def all_letters(self):
        return self.letter_set.all()

    @property
    def letter_count(self):
        return self.all_letters.count()

    def save(self, *args, **kwargs):
        if self.inmate_number == "":
            self.inmate_number = None
        super().save(*args, **kwargs)

    # TODO: REFACTOR
    # this is gross and repetitive of pending_letter_count in admin.py
    @property
    def eligibility(self):
        cooldown_interval = make_aware(
            (datetime.now() - timedelta(days=ELIGIBILITY_INTERVAL_DAYS))
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

        assert self.last_served
        eligible_date = self.last_served + timedelta(days=ELIGIBILITY_INTERVAL_DAYS)

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
