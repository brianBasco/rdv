# Generated by Django 4.1.2 on 2023-08-26 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('deuldou', '0010_remove_contact_contact unique_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deuldou',
            name='createur_participe',
        ),
        migrations.AlterField(
            model_name='participant',
            name='statut',
            field=models.CharField(choices=[('PR', 'Présent'), ('AB', 'Absent'), ('RE', 'En retard'), ('IN', 'Incertain'), ('PI', "Peux pas j'ai piscine"), ('VI', 'Je passe pour dire bonjour'), ('NI', 'Non inscrit')], default='NI', max_length=2),
        ),
    ]
