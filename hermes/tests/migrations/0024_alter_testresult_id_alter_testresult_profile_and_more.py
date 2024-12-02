# Generated by Django 5.1.3 on 2024-12-02 21:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0023_testresult_test_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testresult',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tests.profile'),
        ),
        migrations.AlterUniqueTogether(
            name='testresult',
            unique_together={('profile', 'active_test')},
        ),
    ]