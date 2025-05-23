# Generated by Django 5.1.1 on 2024-10-23 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0003_remove_testresult_person_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testresult',
            name='beep_test_laps',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='beep_test_level',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='beep_test_score',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='beep_test_total_laps',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='brace_score',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='brace_time_1',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='brace_time_2',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='hexagon_score',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='hexagon_time_l',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='hexagon_time_r',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='jet_distance',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='jet_laps',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='jet_score',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='jet_sides',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='ladder_score',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='ladder_time_1',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='ladder_time_2',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='max_hr',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='medicimbal_score',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='medicimbal_throw_1',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='medicimbal_throw_2',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='medicimbal_throw_3',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='triple_jump_distance_1',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='triple_jump_distance_2',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='triple_jump_distance_3',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='triple_jump_score',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_la_back',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_la_front',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_la_left',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_lf_front',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_lf_left',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_lf_right',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_ra_back',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_ra_front',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_ra_right',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_rf_front',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_rf_left',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_rf_right',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_score',
            field=models.IntegerField(),
        ),
    ]
