from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult
from tests.score_tables import calculate_score
from django.shortcuts import redirect


class JetScoreView(UnicornView):
    template_name = "unicorn/jet_score.html"
    profile_id = None
    laps = ""
    sides = ""
    distance = 0
    score = 0
    profiles = []

    def mount(self):
        # Load profiles when component is initialized
        self.profiles = Profile.objects.all()
        print("Component mounted with profiles:", len(self.profiles))

    def clean_measurement(self, value):
        # Clean and validate measurement input
        if not value and value != 0:  # Handle empty strings and None
            return None
        try:
            cleaned = int(str(value).strip())
            return cleaned if cleaned >= 0 else None
        except (ValueError, TypeError):
            return None

    def calculate_jet_score(self):
        # Calculate score whenever inputs change
        if not self.profile_id:
            return

        try:
            profile = Profile.objects.get(id=int(self.profile_id))

            # Clean and validate inputs, defaulting to 0 if None
            clean_laps = self.clean_measurement(self.laps) or 0
            clean_sides = self.clean_measurement(self.sides) or 0

            # Calculate distance using actual or default values
            self.distance = (clean_laps * 40) + (clean_sides * 10)

            # Only calculate score if we have a valid distance
            if self.distance is not None and self.distance >= 0:
                self.score = calculate_score(
                    profile.age, profile.gender, "jet", self.distance
                )
                print(f"Score calculated: {self.score}, Distance: {self.distance}")
            else:
                self.score = None
                print("Invalid distance value")

        except (Profile.DoesNotExist, ValueError) as e:
            print(f"Error calculating score: {e}")
            self.score = None
            self.distance = None

    def update_profile(self, profile_id):
        # Update profile_id and load existing results if any
        self.profile_id = str(profile_id)

        # Reset current values
        self.laps = ""
        self.sides = ""
        self.distance = 0
        self.score = 0

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=int(self.profile_id))
                # Try to get existing test result
                test_result = TestResult.objects.filter(profile=profile).first()

                if test_result:
                    # Populate existing values if they exist
                    if test_result.jet_laps is not None:
                        self.laps = str(test_result.jet_laps)
                    if test_result.jet_sides is not None:
                        self.sides = str(test_result.jet_sides)

                    # Calculate scores for existing values
                    self.calculate_jet_score()
            except Profile.DoesNotExist:
                print("Selected profile not found")

    def save_results(self):
        # Save the test results to the database
        if not self.profile_id:
            return False

        try:
            profile = Profile.objects.get(id=int(self.profile_id))
            test_result, created = TestResult.objects.get_or_create(
                profile=profile, active_test=self.active_test
            )
            # Clean and validate inputs before saving, defaulting to 0 if None
            clean_laps = self.clean_measurement(self.laps) or 0
            clean_sides = self.clean_measurement(self.sides) or 0

            # Always save the values since we're defaulting to 0
            test_result.jet_laps = clean_laps
            test_result.jet_sides = clean_sides

            if self.distance is not None:
                test_result.jet_distance = self.distance
            if self.score is not None:
                test_result.jet_score = self.score

            test_result.save()
            return redirect("adjudicator_dashboard")
        except Exception as e:
            print(f"Error saving results: {e}")
            return False
