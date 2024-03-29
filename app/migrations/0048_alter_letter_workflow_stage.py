# Generated by Django 4.1.2 on 2022-12-18 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0047_alter_prison_options_alter_letter_postmark_date"),
    ]

    operations = [
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
                    ("discarded", "Discarded"),
                ],
                default="stage1_complete",
                max_length=200,
            ),
        ),
    ]
