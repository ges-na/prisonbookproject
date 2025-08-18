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

from src.app.utils import WorkflowStage

if TYPE_CHECKING:
    from src.app.models.letter import Letter
    from src.app.models.prison import PersonPrison, Prison

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

    id: int
    prisons: QuerySet[PersonPrison]
    letter_set: QuerySet[Letter]

    class Meta:
        verbose_name_plural = "people"

    def __str__(self):
        return self.last_name

    def save(self, *args, **kwargs):
        if self.inmate_number == "":
            self.inmate_number = None
        super().save(*args, **kwargs)

    @property
    def current_prison(self) -> Prison | None:
        if person_prison := self.prisons.first():
            return person_prison.prison

    @property
    def full_name(self) -> str:
         return f"{self.first_name} {self.middle_name if self.middle_name else ''} {self.last_name}{' ' + self.name_suffix if self.name_suffix else ''}"

    @cached_property
    def last_served(self):
        if fulfilled_letters := self.letter_set.filter(
            workflow_stage=WorkflowStage.FULFILLED,
            counts_against_last_served=True,
        ):
            if last_letter := fulfilled_letters.order_by("fulfilled_date").last():
                return last_letter.fulfilled_date
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

    def get_name_str(self):
        return f"{self.first_name} {self.middle_name + " " if self.middle_name else ""}{self.last_name}{" " + self.name_suffix if self.name_suffix else ""}"

    @property
    def eligible(self) -> bool:
        if not self.has_been_served:
            return True
        assert self.last_served
        cooldown_interval = make_aware(
            (datetime.now() - timedelta(days=ELIGIBILITY_INTERVAL_DAYS))
        )
        return self.last_served <= cooldown_interval

    def get_eligibility_str(self) -> str:
        pending_letters_string = None
        if self.has_pending_letters:
            pending_letters_string = format_html(
                "<a href={}?person={}&workflow_stage__in={}>{}</a>",
                reverse('admin:app_letter_changelist'),
                self.id,
                WorkflowStage.STAGE1_COMPLETE,
                f"{self.pending_letter_count} letters pending",
            )
        if not self.eligible:
            assert self.last_served
            eligible_dt = self.last_served + timedelta(days=ELIGIBILITY_INTERVAL_DAYS)
            eligible_date_str = eligible_dt.strftime('%B %-d, %Y')
            if not self.has_pending_letters:
                return f"Eligible after {eligible_date_str}"
            elif pending_letters_string:
                return format_html("Eligible after {}; {}", eligible_date_str, pending_letters_string)
            else:
                # Should not happen, doesn't need to blow up
                return "Error finding eligibility; please report"
        if not pending_letters_string:
            return "Eligible"
        return format_html("Eligible; {}", pending_letters_string)

    setattr(get_eligibility_str, "short_description", "Eligibility")
