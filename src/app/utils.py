from ajax_select.fields import render_to_string
from django.db import models

NO_PRISON_STR = "Not in custody"

class WorkflowStage(models.TextChoices):
    STAGE1_COMPLETE = "stage1_complete", "Stage 1 complete"
    FULFILLED = "fulfilled", "Fulfilled"
    JUST_PADA = "just_pada", "Just PADA"
    PROBLEM = "problem", "Problem"
    DISCARDED = "discarded", "Discarded"


def render_address_template(
    headers: list[str | None],
    address: str,
    city: str,
    state: str,
    zip: str,
):
    context = {
        "headers": headers,
        "address": address,
        "city": city,
        "state": state,
        "zip": zip,
    }
    return render_to_string("addresses/address.html", context=context)
