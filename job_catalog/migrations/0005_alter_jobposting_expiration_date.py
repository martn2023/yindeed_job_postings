# Generated by Django 5.0.3 on 2024-03-29 04:58

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_catalog', '0004_alter_jobposting_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobposting',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 6, 27, 4, 58, 24, 501885, tzinfo=datetime.timezone.utc)),
        ),
    ]
