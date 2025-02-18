# Generated by Django 5.1.3 on 2024-11-27 20:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0021_profile_created_by_profile_team_testresult_test_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testresult',
            name='test_name',
        ),
        migrations.AlterField(
            model_name='testresult',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='test_results', to='tests.profile'),
        ),
    ]
