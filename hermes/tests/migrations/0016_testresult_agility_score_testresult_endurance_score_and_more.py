# Generated by Django 5.1.3 on 2024-11-24 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0015_remove_profile_age_profile_date_of_birth'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='agility_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='testresult',
            name='endurance_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='testresult',
            name='speed_score',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='testresult',
            name='strength_score',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
