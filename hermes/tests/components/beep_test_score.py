from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult
from tests.score_tables import quick_calculate, calculate_beep_test_total_laps
from django.shortcuts import redirect


class BeepTestScoreView(UnicornView):
    template_name = "unicorn/beep_test_score.html"
    profile_id = None
    level = ""
    laps = ""
    max_hr = ""
    total_laps = None
    score = None
    profiles = []

    def mount(self):
        """Load profiles when component is initialized"""
        self.profiles = Profile.objects.all()
        print("Component mounted with profiles:", len(self.profiles))

    def calculate_beep_test_score(self):
        """Calculate score whenever inputs change"""
        if not self.profile_id:
            return

        try:
            profile = Profile.objects.get(id=self.profile_id)

            if self.level and self.laps:
                level = int(self.level)
                laps = int(self.laps)
                self.total_laps = calculate_beep_test_total_laps(level, laps)

                if self.total_laps:
                    self.score = quick_calculate(
                        profile.age, profile.gender, "beep_test", self.total_laps
                    )
                    print(
                        f"Score calculated: {self.score}, Total Laps: {self.total_laps}"
                    )

        except (Profile.DoesNotExist, ValueError) as e:
            print(f"Error calculating score: {e}")
            self.score = None
            self.total_laps = None

    def update_profile(self, profile_id):
        """Update profile_id and recalculate score"""
        self.profile_id = profile_id
        self.calculate_beep_test_score()

    def save_results(self):
        """Save the test results to the database"""
        if not self.profile_id:
            return False

        try:
            profile = Profile.objects.get(id=self.profile_id)
            test_result, created = TestResult.objects.get_or_create(profile=profile)

            if self.level and self.laps:
                test_result.beep_test_level = int(self.level)
                test_result.beep_test_laps = int(self.laps)
            if self.max_hr:
                test_result.max_hr = int(self.max_hr)
            if self.total_laps:
                test_result.beep_test_total_laps = self.total_laps
            if self.score:
                test_result.beep_test_score = self.score

            test_result.save()
            return redirect("adjudicator_dashboard")
        except Exception as e:
            print(f"Error saving results: {e}")
            return False
