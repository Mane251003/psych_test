# Generated by Django 5.1.5 on 2025-02-04 20:50

import core.models
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('question_type', models.CharField(choices=[('yes_no', 'YES/NO'), ('multiple_choice', 'Multiple Choice'), ('open_text', 'Open Text')], default='yes_no', max_length=50)),
                ('scale', models.CharField(choices=[('neuroticism', 'Neuroticism'), ('extroversion', 'Extroversion'), ('psychoticism', 'Psychoticism'), ('sincerity', 'Sincerity')], max_length=50)),
                ('options', models.JSONField(blank=True, default=core.models.default_option, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=100)),
                ('neuroticism_score', models.FloatField(default=0)),
                ('neuroticism_yes', models.FloatField(default=0)),
                ('neuroticism_no', models.FloatField(default=0)),
                ('extroversion_score', models.FloatField(default=0)),
                ('extroversion_yes', models.FloatField(default=0)),
                ('extroversion_no', models.FloatField(default=0)),
                ('psychoticism_score', models.FloatField(default=0)),
                ('psychoticism_yes', models.FloatField(default=0)),
                ('psychoticism_no', models.FloatField(default=0)),
                ('sincerity_score', models.FloatField(default=0)),
                ('sincerity_yes', models.FloatField(default=0)),
                ('sincerity_no', models.FloatField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(max_length=100)),
                ('choice', models.CharField(max_length=250)),
                ('test_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.question')),
            ],
        ),
    ]
