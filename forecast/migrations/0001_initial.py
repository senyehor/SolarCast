# Generated by Django 5.1.3 on 2024-12-06 12:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('locations', '0003_weatherdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField()),
                ('created_at', models.DateTimeField(auto_now=True)),
                ('location', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='model', to='locations.location')),
            ],
        ),
    ]

