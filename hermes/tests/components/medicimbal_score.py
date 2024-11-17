from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult
from tests.score_tables import quick_calculate
from django.shortcuts import redirect


class MedicimbalScoreView(UnicornView):
    template_name = "unicorn/medicimbal_score.html"
    profile_id = None
    throw_1 = 0
    throw_2 = 0
    throw_3 = 0
    score_1 = 0
    score_2 = 0
    score_3 = 0
    profiles = []

    def mount(self):
        """Load profiles when component is initialized"""
        self.profiles = Profile.objects.all()
        print("Component mounted with profiles:", len(self.profiles))

    def calculate_medicimbal_score(self):
        """Calculate scores whenever inputs change"""
        print(
            f"Calculating scores - Profile ID: {self.profile_id}, Throws: {self.throw_1}, {self.throw_2}, {self.throw_3}"
        )

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)
                if self.throw_1:
                    self.score_1 = quick_calculate(
                        profile.age, profile.gender, "medicimbal", float(self.throw_1)
                    )
                if self.throw_2:
                    self.score_2 = quick_calculate(
                        profile.age, profile.gender, "medicimbal", float(self.throw_2)
                    )
                if self.throw_3:
                    self.score_3 = quick_calculate(
                        profile.age, profile.gender, "medicimbal", float(self.throw_3)
                    )
                print(
                    f"Scores calculated: {self.score_1}, {self.score_2}, {self.score_3}"
                )
            except (Profile.DoesNotExist, ValueError) as e:
                print(f"Error calculating scores: {e}")
                self.score_1 = self.score_2 = self.score_3 = 0
        else:
            print("Missing profile_id")

    def update_profile(self, profile_id):
        """Update profile_id and recalculate scores"""
        self.profile_id = profile_id
        self.calculate_medicimbal_score()

    def save_results(self):
        """Save the test results to the database"""
        if self.profile_id and (self.throw_1 or self.throw_2 or self.throw_3):
            try:
                profile = Profile.objects.get(id=self.profile_id)
                test_result, created = TestResult.objects.get_or_create(profile=profile)

                if self.throw_1:
                    test_result.medicimbal_throw_1 = float(self.throw_1)
                if self.throw_2:
                    test_result.medicimbal_throw_2 = float(self.throw_2)
                if self.throw_3:
                    test_result.medicimbal_throw_3 = float(self.throw_3)

                test_result.medicimbal_score = max(
                    self.score_1, self.score_2, self.score_3
                )
                test_result.save()

                return redirect("adjudicator_dashboard")
            except Exception as e:
                print(f"Error saving results: {e}")
                return False
        return False
