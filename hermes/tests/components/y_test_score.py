from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult
from tests.score_tables import quick_calculate, calculate_y_test_index
from django.shortcuts import redirect


class YTestScoreView(UnicornView):
    template_name = "unicorn/y_test_score.html"
    profile_id = None
    # Left Leg
    ll_front = ""
    ll_left = ""
    ll_right = ""
    # Right Leg
    rl_front = ""
    rl_left = ""
    rl_right = ""
    # Left Arm
    la_left = ""
    la_front = ""
    la_back = ""
    # Right Arm
    ra_right = ""
    ra_front = ""
    ra_back = ""
    # Score
    y_test_score = None
    y_test_index = None
    profiles = []

    def mount(self):
        """Load profiles when component is initialized"""
        self.profiles = Profile.objects.all()

    def calculate_y_test_score(self):
        """Calculate score whenever any input changes"""
        if not self.profile_id:
            return

        try:
            profile = Profile.objects.get(id=self.profile_id)
            height = profile.height

            measurements = [
                self.ll_front, self.ll_left, self.ll_right,
                self.rl_front, self.rl_left, self.rl_right,
                self.la_left, self.la_front, self.la_back,
                self.ra_right, self.ra_front, self.ra_back
            ]
            
            # Check if all measurements are present and valid
            if all(m and str(m).strip() for m in measurements):
                float_measurements = [float(m) for m in measurements]
                
                self.y_test_index = calculate_y_test_index(height, *float_measurements)
                
                if self.y_test_index:
                    self.y_test_score = quick_calculate(
                        profile.age, profile.gender, "y_test", self.y_test_index
                    )
                    print(f"Score calculated: {self.y_test_score}, Index: {self.y_test_index}")
                
        except Exception as e:
            print(f"Error calculating score: {e}")

    def update_profile(self, profile_id):
        """Update profile_id and recalculate score"""
        self.profile_id = profile_id
        self.calculate_y_test_score()

    def save_results(self):
        """Save the test results to the database"""
        if not self.profile_id:
            return False

        try:
            profile = Profile.objects.get(id=self.profile_id)
            test_result, created = TestResult.objects.get_or_create(profile=profile)

            # Update all measurements
            measurements = {
                'y_test_ll_front': self.ll_front,
                'y_test_ll_left': self.ll_left,
                'y_test_ll_right': self.ll_right,
                'y_test_rl_front': self.rl_front,
                'y_test_rl_left': self.rl_left,
                'y_test_rl_right': self.rl_right,
                'y_test_la_left': self.la_left,
                'y_test_la_front': self.la_front,
                'y_test_la_back': self.la_back,
                'y_test_ra_right': self.ra_right,
                'y_test_ra_front': self.ra_front,
                'y_test_ra_back': self.ra_back,
            }

            for field, value in measurements.items():
                if value and str(value).strip():
                    setattr(test_result, field, float(value))

            if self.y_test_score is not None:
                test_result.y_test_score = self.y_test_score
            if self.y_test_index is not None:
                test_result.y_test_index = self.y_test_index

            test_result.save()
            return redirect("adjudicator_dashboard")
        except Exception as e:
            print(f"Error saving results: {e}")
            return False

