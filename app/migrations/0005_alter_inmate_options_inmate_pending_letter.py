# Generated by Django 4.0.4 on 2022-04-23 21:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_inmate_last_sent_inmate_package_count'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inmate',
            options={'ordering': ('-pending_letter',)},
        ),
        migrations.AddField(
            model_name='inmate',
            name='pending_letter',
            field=models.DateField(blank=True, null=True),
        ),
    ]
