# Generated by Django 4.1.2 on 2022-12-03 21:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        (
            "app",
            "0045_rename_awaiting_fulfillment_date_letter_in_packing_pipeline_date_and_more",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="letter",
            name="prison_sent_to",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="app.prison",
            ),
        ),
    ]
