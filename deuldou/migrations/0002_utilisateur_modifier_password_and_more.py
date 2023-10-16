# Generated by Django 4.1.2 on 2023-03-26 11:28

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('deuldou', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='utilisateur',
            name='modifier_password',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='deuldou',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2023, 3, 26, 13, 28, 27, 782040)),
        ),
        migrations.AlterField(
            model_name='deuldou',
            name='jour',
            field=models.DateTimeField(default=datetime.datetime(2023, 3, 26, 13, 28, 27, 782040)),
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visible', models.BooleanField(default=True)),
                ('pseudo', models.CharField(blank=True, max_length=100, null=True)),
                ('commentaire', models.TextField(null=True)),
                ('rdv', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to='deuldou.deuldou')),
                ('statut', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='deuldou.statut')),
                ('tags', models.ManyToManyField(to='deuldou.tag')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='participants', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='participant',
            constraint=models.UniqueConstraint(fields=('rdv', 'user'), name='participation unique'),
        ),
    ]