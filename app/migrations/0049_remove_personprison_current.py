# Generated by Django 4.1.2 on 2023-02-01 21:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0048_alter_letter_workflow_stage"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="personprison",
            name="current",
        ),
    ]
