from django.db import models
from datetime import date


class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    admins = models.ManyToManyField("auth.User", related_name="teams")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ActiveTest(models.Model):
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, related_name="created_tests"
    )

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"


class Profile(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    weight = models.IntegerField()
    height = models.IntegerField()
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_profiles",
    )
    GENDER_CHOICES = [
        ("M", "Muž"),
        ("F", "Žena"),
    ]
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default="M",
    )

    @property
    def age(self):
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
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
        return f"{self.surname} {self.name}"

    def get_latest_test_result(self):
        return TestResult.objects.filter(profile=self).order_by("-test_date").first()

    def get_last_three_test_results(self):
        # Get the last three test results for the profile, ordered by most recent first.
        return TestResult.objects.filter(profile=self).order_by("-test_date")[:3]

    @property
    def full_name(self):
        return f"{self.surname} {self.name}"


class TestResult(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="test_results"
    )
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)
    test_date = models.DateField(auto_now_add=True)
    test_name = models.CharField(max_length=100, null=True, blank=True)
    active_test = models.ForeignKey(
        ActiveTest,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="test_results",
    )

    ladder_score = models.IntegerField(default=0)
    ladder_time_1 = models.FloatField(null=True, blank=True)
    ladder_time_2 = models.FloatField(null=True, blank=True)

    hexagon_score = models.IntegerField(default=0)
    hexagon_time_cw = models.FloatField(null=True, blank=True)
    hexagon_time_ccw = models.FloatField(null=True, blank=True)

    y_test_score = models.IntegerField(default=0)
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

    brace_score = models.IntegerField(default=0)
    brace_time_1 = models.FloatField(null=True, blank=True)
    brace_time_2 = models.FloatField(null=True, blank=True)

    medicimbal_score = models.IntegerField(default=0)
    medicimbal_throw_1 = models.FloatField(null=True, blank=True)
    medicimbal_throw_2 = models.FloatField(null=True, blank=True)
    medicimbal_throw_3 = models.FloatField(null=True, blank=True)

    jet_score = models.IntegerField(default=0)
    jet_laps = models.IntegerField(null=True, blank=True)
    jet_sides = models.IntegerField(null=True, blank=True)
    jet_distance = models.IntegerField(null=True, blank=True)

    triple_jump_score = models.IntegerField(default=0)
    triple_jump_distance_1 = models.FloatField(null=True, blank=True)
    triple_jump_distance_2 = models.FloatField(null=True, blank=True)
    triple_jump_distance_3 = models.FloatField(null=True, blank=True)

    beep_test_score = models.IntegerField(default=0)
    beep_test_level = models.IntegerField(null=True, blank=True)
    beep_test_laps = models.IntegerField(null=True, blank=True)
    beep_test_total_laps = models.IntegerField(null=True, blank=True)
    max_hr = models.IntegerField(null=True, blank=True)

    strength_score = models.FloatField(null=True, blank=True)
    # medicimbal_score + triple_jump_score /2
    speed_score = models.FloatField(null=True, blank=True)
    # ladder_score + hexagon_score /2
    endurance_score = models.FloatField(null=True, blank=True)
    # beep_test_score + jet_score /2
    agility_score = models.FloatField(null=True, blank=True)
    # brace_score + y_test_score /2

    def __str__(self):
        return f"{self.profile.surname} {self.profile.name} - {self._meta.model_name}"

    def save(self, *args, **kwargs):
        # Calculate composite scores before saving
        if self.medicimbal_score is not None and self.triple_jump_score is not None:
            self.strength_score = (self.medicimbal_score + self.triple_jump_score) / 2
        if self.ladder_score is not None and self.hexagon_score is not None:
            self.speed_score = (self.ladder_score + self.hexagon_score) / 2
        if self.beep_test_score is not None and self.jet_score is not None:
            self.endurance_score = (self.beep_test_score + self.jet_score) / 2
        if self.brace_score is not None and self.y_test_score is not None:
            self.agility_score = (self.brace_score + self.y_test_score) / 2
        super().save(*args, **kwargs)
