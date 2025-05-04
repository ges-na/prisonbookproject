from django.db import models


class WorkflowStage(models.TextChoices):
    STAGE1_COMPLETE = "stage1_complete", "Stage 1 complete"
    FULFILLED = "fulfilled", "Fulfilled"
    JUST_PADA = "just_pada", "Just PADA"
    PROBLEM = "problem", "Problem"
    DISCARDED = "discarded", "Discarded"
