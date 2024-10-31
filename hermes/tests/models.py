from django.db import models


class Profile(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    age = models.IntegerField()
    weight = models.IntegerField()
    height = models.IntegerField()
    GENDER_CHOICES = [
        ("M", "Muž"),
        ("F", "Žena"),
        ("U", "Nezadáno"),
    ]
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default="U",
    )

    def get_ladder_times(self):
        test_result = self.get_latest_test_result()
        return {
            "time_1": getattr(test_result, "ladder_time_1", None),
            "time_2": getattr(test_result, "ladder_time_2", None),
        }

    def get_brace_times(self):
        test_result = self.get_latest_test_result()
        return {
            "time_1": getattr(test_result, "brace_time_1", None),
            "time_2": getattr(test_result, "brace_time_2", None),
        }

    def get_hexagon_times(self):
        test_result = self.get_latest_test_result()
        return {
            "time_cw": getattr(test_result, "hexagon_time_cw", None),
            "time_ccw": getattr(test_result, "hexagon_time_ccw", None),
        }

    def get_medicimbal_throws(self):
        test_result = self.get_latest_test_result()
        return {
            "throw_1": getattr(test_result, "medicimbal_throw_1", None),
            "throw_2": getattr(test_result, "medicimbal_throw_2", None),
            "throw_3": getattr(test_result, "medicimbal_throw_3", None),
        }

    def get_jet_results(self):
        test_result = self.get_latest_test_result()
        return {
            "laps": getattr(test_result, "jet_laps", None),
            "sides": getattr(test_result, "jet_sides", None),
            "distance": getattr(test_result, "jet_distance", None),
        }

    def get_y_test_results(self):
        test_result = self.get_latest_test_result()
        return {
            "ll_front": getattr(test_result, "y_test_ll_front", None),
            "ll_left": getattr(test_result, "y_test_ll_left", None),
            "ll_right": getattr(test_result, "y_test_ll_right", None),
            "rl_front": getattr(test_result, "y_test_rl_front", None),
            "rl_right": getattr(test_result, "y_test_rl_right", None),
            "rl_left": getattr(test_result, "y_test_rl_left", None),
            "la_left": getattr(test_result, "y_test_la_left", None),
            "la_front": getattr(test_result, "y_test_la_front", None),
            "la_back": getattr(test_result, "y_test_la_back", None),
            "ra_right": getattr(test_result, "y_test_ra_right", None),
            "ra_front": getattr(test_result, "y_test_ra_front", None),
            "ra_back": getattr(test_result, "y_test_ra_back", None),
        }

    def get_triple_jump_results(self):
        test_result = self.get_latest_test_result()
        return {
            "distance_1": getattr(test_result, "triple_jump_distance_1", None),
            "distance_2": getattr(test_result, "triple_jump_distance_2", None),
            "distance_3": getattr(test_result, "triple_jump_distance_3", None),
        }

    def get_beep_test_results(self):
        test_result = self.get_latest_test_result()
        return {
            "level": getattr(test_result, "beep_test_level", None),
            "laps": getattr(test_result, "beep_test_laps", None),
            "total_laps": getattr(test_result, "beep_test_total_laps", None),
            "max_hr": getattr(test_result, "max_hr", None),
        }

    def __str__(self):
        return f"{self.name} {self.surname}"


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

    def __str__(self):
        return f"{self.profile.name} {self.profile.surname} - {self._meta.model_name}"


def save(self, *args, **kwargs):
    super().save(*args, **kwargs)
