# Generated by Django 4.0.5 on 2022-08-08 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0033_prison_modified_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personprison',
            name='current',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='prison',
            name='modified_date',
            field=models.DateTimeField(null=True),
        ),
    ]