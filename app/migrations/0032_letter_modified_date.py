# Generated by Django 4.0.5 on 2022-08-08 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0031_alter_letter_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='letter',
            name='modified_date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
