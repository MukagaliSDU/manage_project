# Generated by Django 4.2.4 on 2023-08-25 14:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jira', '0002_project_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 25, 14, 13, 58, 888245, tzinfo=datetime.timezone.utc)),
        ),
    ]