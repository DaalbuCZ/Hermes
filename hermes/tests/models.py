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
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE)

    ladder_score = models.IntegerField(null=True, blank=True)
    ladder_time_1 = models.FloatField(null=True, blank=True)
    ladder_time_2 = models.FloatField(null=True, blank=True)

    hexagon_score = models.IntegerField(null=True, blank=True)
    hexagon_time_cw = models.FloatField(null=True, blank=True)
    hexagon_time_ccw = models.FloatField(null=True, blank=True)

    y_test_score = models.IntegerField(null=True, blank=True)
    y_test_index = models.FloatField(null=True, blank=True)
    y_test_ll_front = models.FloatField(null=True, blank=True)
    y_test_ll_left = models.FloatField(null=True, blank=True)
    y_test_ll_right = models.FloatField(null=True, blank=True)
    y_test_rl_front = models.FloatField(null=True, blank=True)
    y_test_rl_right = models.FloatField(null=True, blank=True)
    y_test_rl_left = models.FloatField(null=True, blank=True)
    y_test_la_left = models.FloatField(null=True, blank=True)
    y_test_la_front = models.FloatField(null=True, blank=True)
    y_test_la_back = models.FloatField(null=True, blank=True)
    y_test_ra_right = models.FloatField(null=True, blank=True)
    y_test_ra_front = models.FloatField(null=True, blank=True)
    y_test_ra_back = models.FloatField(null=True, blank=True)

    brace_score = models.IntegerField(null=True, blank=True)
    brace_time_1 = models.FloatField(null=True, blank=True)
    brace_time_2 = models.FloatField(null=True, blank=True)

    medicimbal_score = models.IntegerField(null=True, blank=True)
    medicimbal_throw_1 = models.FloatField(null=True, blank=True)
    medicimbal_throw_2 = models.FloatField(null=True, blank=True)
    medicimbal_throw_3 = models.FloatField(null=True, blank=True)

    jet_score = models.IntegerField(null=True, blank=True)
    jet_laps = models.IntegerField(null=True, blank=True)
    jet_sides = models.IntegerField(null=True, blank=True)
    jet_distance = models.IntegerField(null=True, blank=True)

    triple_jump_score = models.IntegerField(null=True, blank=True)
    triple_jump_distance_1 = models.FloatField(null=True, blank=True)
    triple_jump_distance_2 = models.FloatField(null=True, blank=True)
    triple_jump_distance_3 = models.FloatField(null=True, blank=True)

    beep_test_score = models.IntegerField(null=True, blank=True)
    beep_test_level = models.IntegerField(null=True, blank=True)
    beep_test_laps = models.IntegerField(null=True, blank=True)
    beep_test_total_laps = models.IntegerField(null=True, blank=True)
    max_hr = models.IntegerField(null=True, blank=True)


def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
