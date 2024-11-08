# Generated by Django 5.1.1 on 2024-11-01 10:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0012_rename_sex_profile_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='gender',
            field=models.CharField(choices=[('M', 'Muž'), ('F', 'Žena')], default='M', max_length=1),
        ),
    ]