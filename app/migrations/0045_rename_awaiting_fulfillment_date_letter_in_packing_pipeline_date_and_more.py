# Generated by Django 4.1.2 on 2022-12-03 20:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0044_remove_person_eligibility_status"),
    ]

    operations = [
        migrations.RenameField(
            model_name="letter",
            old_name="awaiting_fulfillment_date",
            new_name="in_packing_pipeline_date",
        ),
        migrations.AlterField(
            model_name="letter",
            name="workflow_stage",
            field=models.CharField(
                choices=[
                    ("stage1_complete", "Stage 1 complete"),
                    ("in_packing_pipeline", "In packing pipeline"),
                    ("fulfilled", "Fulfilled"),
                    ("just_pada", "Just PADA"),
                    ("problem", "Problem"),
                ],
                default="stage1_complete",
                max_length=200,
            ),
        ),
    ]