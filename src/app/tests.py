import os
from model_bakery import baker
from datetime import datetime, timedelta
from django.utils.timezone import make_aware, now

from django.test import TestCase

from app.models import *
from app.admin import *


class EligibilityTests(TestCase):
    def setUp(self):
        self.now = make_aware(datetime.now())
        self.person_with_legacy_ls_date = baker.make(
            "app.Person",
            legacy_last_served_date=self.now - timedelta(days=91),
        )
        self.person_without_legacy_ls_date = baker.make(
            "app.Person",
            legacy_last_served_date=None,
        )

    def test_set_last_served_date(self):
        letter_for_person_with_legacy_ls_date = baker.make(
            "app.Letter",
            person=self.person_with_legacy_ls_date,
            fulfilled_date=self.now,
            workflow_stage=WorkflowStage.FULFILLED,
        )
        letter_for_person_with_legacy_ls_date.save()
        self.assertEqual(
            len(
                letter_for_person_with_legacy_ls_date.person.letter_set.filter(
                    workflow_stage__in=[WorkflowStage.FULFILLED]
                )
            ),
            1,
        )
        self.assertEqual(letter_for_person_with_legacy_ls_date.fulfilled_date, self.now)
        self.assertEqual(
            letter_for_person_with_legacy_ls_date.person.has_been_served, True
        )
        self.assertEqual(
            letter_for_person_with_legacy_ls_date.person.last_served, self.now
        )

    def test_eligibility(self):
        pass
