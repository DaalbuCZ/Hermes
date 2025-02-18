# Generated by Django 5.1.1 on 2024-11-04 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0013_alter_profile_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testresult',
            name='beep_test_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='brace_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='hexagon_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='jet_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='ladder_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='medicimbal_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='triple_jump_score',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_score',
            field=models.IntegerField(default=0),
        ),
    ]
