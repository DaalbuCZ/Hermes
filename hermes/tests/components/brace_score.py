from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult
from tests.score_tables import quick_calculate
from django.shortcuts import redirect


class BraceScoreView(UnicornView):
    template_name = "unicorn/brace_score.html"
    profile_id = None
    time_1 = 0
    time_2 = 0
    score_1 = 0
    score_2 = 0
    profiles = []

    def mount(self):
        """Load profiles when component is initialized"""
        self.profiles = Profile.objects.all()
        print("Component mounted with profiles:", len(self.profiles))

    def calculate_brace_score(self):
        """Calculate scores whenever inputs change"""
        print(
            f"Calculating scores - Profile ID: {self.profile_id}, Time 1: {self.time_1}, Time 2: {self.time_2}"
        )

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)
                if self.time_1:
                    self.score_1 = quick_calculate(
                        profile.age, profile.gender, "brace", float(self.time_1)
                    )
                if self.time_2:
                    self.score_2 = quick_calculate(
                        profile.age, profile.gender, "brace", float(self.time_2)
                    )
                print(f"Scores calculated: {self.score_1}, {self.score_2}")
            except (Profile.DoesNotExist, ValueError) as e:
                print(f"Error calculating scores: {e}")
                self.score_1 = 0
                self.score_2 = 0
        else:
            print("Missing profile_id")

    def update_profile(self, profile_id):
        """Update profile_id and recalculate scores"""
        self.profile_id = profile_id
        self.calculate_brace_score()

    def save_results(self):
        """Save the test results to the database"""
        if self.profile_id and (self.time_1 or self.time_2):
            try:
                profile = Profile.objects.get(id=self.profile_id)
                test_result, created = TestResult.objects.get_or_create(profile=profile)

                if self.time_1:
                    test_result.brace_time_1 = float(self.time_1)
                if self.time_2:
                    test_result.brace_time_2 = float(self.time_2)

                test_result.brace_score = max(self.score_1, self.score_2)
                test_result.save()

                return redirect("adjudicator_dashboard")
            except Exception as e:
                print(f"Error saving results: {e}")
                return False
        return False
