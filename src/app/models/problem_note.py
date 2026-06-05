from django.db import models
from django.forms import ValidationError

from src.app.models.letter import Letter
from src.app.models.person import Person
from src.auth.models import User


class ProblemNote(models.Model):
    person: models.ForeignKey[Person | None] = models.ForeignKey(
        "Person", on_delete=models.CASCADE, null=True, blank=True
    )
    letter: models.ForeignKey[Letter | None] = models.ForeignKey(
        "Letter", on_delete=models.CASCADE, null=True, blank=True
    )
    note = models.TextField(null=False, blank=False)
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        null=True,
        related_name="note_created_by_user",
        on_delete=models.SET_NULL,
    )
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(
        User,
        null=True,
        related_name="note_modified_by_user",
        on_delete=models.SET_NULL,
    )

    def clean(self):
        if not self.person and not self.letter:
            raise ValidationError("ProblemNote requires either a Person or a Letter.")
