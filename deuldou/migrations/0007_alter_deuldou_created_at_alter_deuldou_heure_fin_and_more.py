# Generated by Django 4.1.2 on 2023-05-11 18:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('deuldou', '0006_rename_adresse_deuldou_lieu_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deuldou',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='deuldou',
            name='heure_fin',
            field=models.TimeField(default='00:00'),
        ),
        migrations.AlterField(
            model_name='deuldou',
            name='lieu',
            field=models.TextField(max_length=100),
        ),
        migrations.AlterField(
            model_name='participant',
            name='statut',
            field=models.CharField(choices=[('PR', 'Présent'), ('AB', 'Absent'), ('RE', 'En retard'), ('IN', 'Incertain'), ('VI', 'Non inscrit')], default='VI', max_length=2),
        ),
        migrations.AddConstraint(
            model_name='contact',
            constraint=models.UniqueConstraint(fields=('user', 'email'), name='contact unique'),
        ),
    ]
