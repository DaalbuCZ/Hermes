# Generated by Django 5.1.1 on 2024-10-31 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0008_testresult_y_test_index'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testresult',
            name='beep_test_laps',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='beep_test_level',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='beep_test_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='beep_test_total_laps',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='brace_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='brace_time_1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='brace_time_2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='hexagon_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='hexagon_time_ccw',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='hexagon_time_cw',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='jet_distance',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='jet_laps',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='jet_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='jet_sides',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='ladder_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='ladder_time_1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='ladder_time_2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='max_hr',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='medicimbal_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='medicimbal_throw_1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='medicimbal_throw_2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='medicimbal_throw_3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='triple_jump_distance_1',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='triple_jump_distance_2',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='triple_jump_distance_3',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='triple_jump_score',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_index',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_la_back',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_la_front',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_la_left',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_ll_front',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_ll_left',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_ll_right',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_ra_back',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_ra_front',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_ra_right',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_rl_front',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_rl_left',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_rl_right',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='testresult',
            name='y_test_score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
