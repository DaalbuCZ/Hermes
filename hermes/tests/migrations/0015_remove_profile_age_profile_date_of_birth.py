# Generated by Django 5.1.3 on 2024-11-22 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tests", "0014_alter_testresult_beep_test_score_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="profile",
            name="age",
        ),
        migrations.AddField(
            model_name="profile",
            name="date_of_birth",
            field=models.DateField(default="2000-01-01"),
            preserve_default=False,
        ),
    ]
