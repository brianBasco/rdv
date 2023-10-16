# Generated by Django 4.1.2 on 2023-03-26 11:41

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('deuldou', '0002_utilisateur_modifier_password_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deuldou',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 3, 26, 13, 41, 37, 370403)),
        ),
        migrations.AlterField(
            model_name='deuldou',
            name='jour',
            field=models.DateTimeField(default=datetime.datetime(2023, 3, 26, 13, 41, 37, 370403)),
        ),
        migrations.AlterField(
            model_name='participant',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
