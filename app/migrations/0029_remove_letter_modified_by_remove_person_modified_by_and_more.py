# Generated by Django 4.0.5 on 2022-08-08 02:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0028_alter_person_inmate_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='letter',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='person',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='personprison',
            name='modified_by',
        ),
        migrations.RemoveField(
            model_name='prison',
            name='modified_by',
        ),
    ]
