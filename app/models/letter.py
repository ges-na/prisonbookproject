from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from app.utils import WorkflowStage


class Letter(models.Model):
    person = models.ForeignKey(
        "Person", on_delete=models.SET_NULL, null=True, blank=False
    )
    postmark_date = models.DateField(null=True, blank=True, default=now)
    stage1_complete_date = models.DateTimeField(null=True, blank=True, default=now)
    fulfilled_date = models.DateTimeField(null=True, blank=True)
    # TODO REFACTOR: Re-address (more addresses)
    counts_against_last_served = models.BooleanField(
        null=False, blank=False, default=True
    )
    prison_requested_from = models.ForeignKey(
        "Prison",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="letters_requested",
    )
    prison_sent_to = models.ForeignKey(
        "Prison",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="letters_fulfilled",
    )
    workflow_stage = models.CharField(
        max_length=200,
        choices=WorkflowStage.choices,
        default=WorkflowStage.STAGE1_COMPLETE,
    )
    notes = models.TextField(blank=True)
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
