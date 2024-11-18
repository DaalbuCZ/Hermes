from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult
from tests.score_tables import quick_calculate
from django.shortcuts import redirect


class MedicimbalScoreView(UnicornView):
    template_name = "unicorn/medicimbal_score.html"
    profile_id = None
    throw_1 = ""
    throw_2 = ""
    throw_3 = ""
    score_1 = 0
    score_2 = 0
    score_3 = 0
    profiles = []
    errors = {"throw_1": "", "throw_2": "", "throw_3": "", "profile": "", "general": ""}

    def mount(self):
        """Load profiles when component is initialized"""
        self.profiles = Profile.objects.all()
        print("Component mounted with profiles:", len(self.profiles))

    def clean_measurement(self, value):
        """Clean and validate measurement input"""
        if not value and value != 0:  # Handle empty strings and None
            return None
        try:
            cleaned = float(str(value).strip())
            return cleaned if cleaned >= 0 else None
        except (ValueError, TypeError):
            return None

    def calculate_medicimbal_score(self):
        """Calculate scores whenever inputs change"""
        print(
            f"Calculating scores - Profile ID: {self.profile_id}, Throws: {self.throw_1}, {self.throw_2}, {self.throw_3}"
        )

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)

                # Clean and validate inputs
                clean_throw_1 = self.clean_measurement(self.throw_1)
                clean_throw_2 = self.clean_measurement(self.throw_2)
                clean_throw_3 = self.clean_measurement(self.throw_3)

                if clean_throw_1 is not None:
                    self.score_1 = quick_calculate(
                        profile.age, profile.gender, "medicimbal", clean_throw_1
                    )
                if clean_throw_2 is not None:
                    self.score_2 = quick_calculate(
                        profile.age, profile.gender, "medicimbal", clean_throw_2
                    )
                if clean_throw_3 is not None:
                    self.score_3 = quick_calculate(
                        profile.age, profile.gender, "medicimbal", clean_throw_3
                    )
                print(
                    f"Scores calculated: {self.score_1}, {self.score_2}, {self.score_3}"
                )
            except Profile.DoesNotExist as e:
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
        if not self.profile_id:
            self.errors["profile"] = "Please select a profile"
            return False

        try:
            profile = Profile.objects.get(id=self.profile_id)
            test_result, created = TestResult.objects.get_or_create(profile=profile)

            # Clean and validate inputs before saving
            clean_throw_1 = self.clean_measurement(self.throw_1, "throw_1")
            clean_throw_2 = self.clean_measurement(self.throw_2, "throw_2")
            clean_throw_3 = self.clean_measurement(self.throw_3, "throw_3")

            if not any([clean_throw_1, clean_throw_2, clean_throw_3]):
                self.errors["general"] = (
                    "At least one valid throw measurement is required"
                )
                return False

            if clean_throw_1 is not None:
                test_result.medicimbal_throw_1 = clean_throw_1
            if clean_throw_2 is not None:
                test_result.medicimbal_throw_2 = clean_throw_2
            if clean_throw_3 is not None:
                test_result.medicimbal_throw_3 = clean_throw_3

            test_result.medicimbal_score = max(self.score_1, self.score_2, self.score_3)
            test_result.save()

            return redirect("adjudicator_dashboard")
        except Exception as e:
            self.errors["general"] = f"Error saving results: {str(e)}"
            return False
