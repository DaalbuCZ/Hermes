from django.db import models


class Profile(models.Model):
    person_name = models.CharField(max_length=100)
    age = models.IntegerField()
    weight = models.IntegerField()
    height = models.IntegerField()
    SEX_CHOICES = [
        ("M", "Muž"),
        ("F", "Žena"),
        ("U", "Nezadáno"),
    ]
    sex = models.CharField(
        max_length=1,
        choices=SEX_CHOICES,
        default="U",
    )

    def __str__(self):
        return self.person_name


class TestResult(models.Model):

    ladder_score = models.IntegerField()

    ladder_time_1 = models.FloatField()
    ladder_time_2 = models.FloatField()

    hexagon_score = models.IntegerField()
    hexagon_time_cw = models.FloatField()
    hexagon_time_ccw = models.FloatField()

    y_test_score = models.IntegerField()
    y_test_index = models.FloatField()
    y_test_ll_front = models.FloatField()
    y_test_ll_left = models.FloatField()
    y_test_ll_right = models.FloatField()
    y_test_rl_front = models.FloatField()
    y_test_rl_right = models.FloatField()
    y_test_rl_left = models.FloatField()
    y_test_la_left = models.FloatField()
    y_test_la_front = models.FloatField()
    y_test_la_back = models.FloatField()
    y_test_ra_right = models.FloatField()
    y_test_ra_front = models.FloatField()
    y_test_ra_back = models.FloatField()

    brace_score = models.IntegerField()
    brace_time_1 = models.FloatField()
    brace_time_2 = models.FloatField()

    medicimbal_score = models.IntegerField()
    medicimbal_throw_1 = models.FloatField()
    medicimbal_throw_2 = models.FloatField()
    medicimbal_throw_3 = models.FloatField()

    jet_score = models.IntegerField()
    jet_laps = models.IntegerField()
    jet_sides = models.IntegerField()
    jet_distance = models.IntegerField()

    triple_jump_score = models.IntegerField()
    triple_jump_distance_1 = models.FloatField()
    triple_jump_distance_2 = models.FloatField()
    triple_jump_distance_3 = models.FloatField()

    beep_test_score = models.IntegerField()
    beep_test_level = models.IntegerField()
    beep_test_laps = models.IntegerField()
    beep_test_total_laps = models.IntegerField()
    max_hr = models.IntegerField()


def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
