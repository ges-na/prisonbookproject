# Generated by Django 4.0.4 on 2022-05-15 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_alter_letter_created_date_alter_letter_modified_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='prison',
            name='external_id',
            field=models.CharField(default='0', max_length=50, unique=True),
            preserve_default=False,
        ),
    ]