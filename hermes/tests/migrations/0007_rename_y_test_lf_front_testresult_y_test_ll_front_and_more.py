# Generated by Django 5.1.1 on 2024-10-24 19:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tests', '0006_rename_hexagon_time_l_testresult_hexagon_time_ccw_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='testresult',
            old_name='y_test_lf_front',
            new_name='y_test_ll_front',
        ),
        migrations.RenameField(
            model_name='testresult',
            old_name='y_test_lf_left',
            new_name='y_test_ll_left',
        ),
        migrations.RenameField(
            model_name='testresult',
            old_name='y_test_lf_right',
            new_name='y_test_ll_right',
        ),
        migrations.RenameField(
            model_name='testresult',
            old_name='y_test_rf_front',
            new_name='y_test_rl_front',
        ),
        migrations.RenameField(
            model_name='testresult',
            old_name='y_test_rf_left',
            new_name='y_test_rl_left',
        ),
        migrations.RenameField(
            model_name='testresult',
            old_name='y_test_rf_right',
            new_name='y_test_rl_right',
        ),
    ]