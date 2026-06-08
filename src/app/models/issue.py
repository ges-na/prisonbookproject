from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models
from django.forms import ValidationError

from src.auth.models import User

if TYPE_CHECKING:
    from src.app.models.letter import Letter
    from src.app.models.person import Person


class Issue(models.Model):
    class Meta:
        abstract = True

    additional_note = models.TextField(null=True, blank=True)

    created_date = models.DateTimeField(auto_now_add=True)

    modified_date = models.DateTimeField(auto_now=True)

    resolved = models.BooleanField(null=False, blank=False, default=False)
    resolved_date = models.DateTimeField(null=True, blank=True)
    resolved_note = models.TextField(null=True, blank=True)


class PersonIssue(Issue):
    class IssueTypes(models.TextChoices):
        WRONG_PRISON = ("wrong_prison", "Wrong prison in record")
        OTHER = ("other", "Other")

    person: models.ForeignKey[Person] = models.ForeignKey(
        "Person", on_delete=models.CASCADE, null=False, blank=False
    )
    issue = models.CharField(choices=IssueTypes, blank=False, null=False)
    created_by = models.ForeignKey(
        User,
        null=True,
        related_name="person_issue_created_by_user",
        on_delete=models.SET_NULL,
    )
    modified_by = models.ForeignKey(
        User,
        null=True,
        related_name="person_issue_modified_by_user",
        on_delete=models.SET_NULL,
    )
    resolved_by = models.ForeignKey(
        User,
        null=True,
        related_name="person_issue_resolved_by_user",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"Person issue {self.created_date.date()}: {self.person.get_name_str()}"

    def clean(self):
        if self.issue == self.IssueTypes.OTHER and not self.additional_note:
            raise ValidationError("Issue type 'Other' requires a descriptive note.")


class LetterIssue(Issue):
    class IssueTypes(models.TextChoices):
        RETURNED_PACKAGE = "returned_package"
        WRONG_PRISON = ("wrong_prison", "Wrong prison in record")
        OTHER = ("other", "Other")

    letter: models.ForeignKey[Letter] = models.ForeignKey(
        "Letter", on_delete=models.CASCADE, null=False, blank=False
    )
    issue = models.CharField(choices=IssueTypes, blank=False, null=False)
    created_by = models.ForeignKey(
        User,
        null=True,
        related_name="letter_issue_created_by_user",
        on_delete=models.SET_NULL,
    )
    modified_by = models.ForeignKey(
        User,
        null=True,
        related_name="letter_issue_modified_by_user",
        on_delete=models.SET_NULL,
    )
    resolved_by = models.ForeignKey(
        User,
        null=True,
        related_name="letter_issue_resolved_by_user",
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"Letter issue {self.created_date.date()}: {self.letter.__str__()}"

    def clean(self):
        if self.issue == self.IssueTypes.OTHER and not self.additional_note:
            raise ValidationError("Issue type 'Other' requires a descriptive note.")
