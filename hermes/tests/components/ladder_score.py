from django_unicorn.components import UnicornView
from tests.models import Profile
from tests.score_tables import quick_calculate


class LadderScoreView(UnicornView):
    template_name = "unicorn/ladder_score.html"
    profile_id = None
    time_1 = None
    time_2 = None
    score_1 = 0
    score_2 = 0
    profiles = []
    errors = {"time_1": "", "time_2": "", "profile": ""}

    def mount(self):
        """Load profiles when component is initialized"""
        self.profiles = Profile.objects.all()

    def validate_time(self, time_value, field_name):
        """Validate time input"""
        if time_value is None:
            self.errors[field_name] = ""
            return False

        try:
            time_float = float(time_value)
            if time_float <= 0:
                self.errors[field_name] = "Time must be greater than 0"
                return False
            self.errors[field_name] = ""
            return True
        except ValueError:
            self.errors[field_name] = "Please enter a valid number"
            return False

    def calculate_ladder_score(self):
        """Calculate scores whenever inputs change"""
        if not self.profile_id:
            self.errors["profile"] = "Please select a profile"
            return

        self.errors["profile"] = ""
        time1_valid = self.validate_time(self.time_1, "time_1")
        time2_valid = self.validate_time(self.time_2, "time_2")

        if not (time1_valid or time2_valid):
            return

        try:
            profile = Profile.objects.get(id=self.profile_id)

            if time1_valid:
                time_1_value = float(self.time_1)
                self.score_1 = quick_calculate(
                    profile.age, profile.gender, "ladder", time_1_value
                )

            if time2_valid:
                time_2_value = float(self.time_2)
                self.score_2 = quick_calculate(
                    profile.age, profile.gender, "ladder", time_2_value
                )

        except Profile.DoesNotExist:
            self.errors["profile"] = "Selected profile not found"
            self.score_1 = 0
            self.score_2 = 0
