# Generated by Django 5.0.3 on 2024-04-03 16:27

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_catalog', '0011_alter_jobposting_expiration_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobposting',
            name='expiration_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 7, 2, 16, 27, 26, 248190, tzinfo=datetime.timezone.utc)),
        ),
    ]
