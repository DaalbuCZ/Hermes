from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult, ActiveTest
from tests.score_tables import calculate_score
from django.shortcuts import redirect
from datetime import datetime


class JetScoreView(UnicornView):
    template_name = "unicorn/jet_score.html"
    profile_id = None
    laps = ""
    sides = ""
    distance = 0
    score = 0
    profiles = []
    active_test = None
    previous_result = None

    def mount(self):
        # Load profiles when component is initialized
        self.profiles = Profile.objects.all()
        self.active_test = ActiveTest.objects.filter(is_active=True).first()
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
        self.previous_result = None

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=int(self.profile_id))
                # Try to get existing test result
                test_result = TestResult.objects.filter(
                    profile=profile, active_test=self.active_test
                ).first()

                if test_result:
                    # Populate existing values if they exist
                    if test_result.jet_laps is not None:
                        self.laps = str(test_result.jet_laps)
                    if test_result.jet_sides is not None:
                        self.sides = str(test_result.jet_sides)

                    # Calculate scores for existing values
                    self.calculate_jet_score()

                # Find and display previous test results if they exist
                previous_results = (
                    TestResult.objects.filter(profile=profile)
                    .exclude(active_test=self.active_test)
                    .order_by("-test_date")
                )

                for result in previous_results:
                    if result.jet_laps is not None or result.jet_sides is not None:
                        self.previous_result = result
                        print(
                            f"Previous Test Result - Laps: {self.previous_result.jet_laps}, Sides: {self.previous_result.jet_sides}, Score: {self.previous_result.jet_score}"
                        )
                        break

            except Profile.DoesNotExist:
                print("Selected profile not found")

    def save_results(self):
        # Save the test results to the database
        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)
                # Filter active test based on the profile's team
                self.active_test = ActiveTest.objects.filter(
                    is_active=True, team=profile.team
                ).first()

                if not self.active_test:
                    print(f"No active test found for team: {profile.team}")
                    return False

                profile = Profile.objects.get(id=int(self.profile_id))
                # Ensure unique constraint on profile and active_test
                test_result, created = TestResult.objects.update_or_create(
                    profile=profile,
                    active_test=self.active_test,
                    defaults={
                        "jet_laps": self.clean_measurement(self.laps) or 0,
                        "jet_sides": self.clean_measurement(self.sides) or 0,
                        "jet_distance": self.distance,
                        "jet_score": calculate_score(
                            profile.age,
                            profile.gender,
                            "jet",
                            (
                                (self.clean_measurement(self.laps) or 0) * 40
                                + (self.clean_measurement(self.sides) or 0) * 10
                            ),
                        ),
                        "test_name": (
                            self.active_test.name if self.active_test else None
                        ),
                        "test_date": (
                            datetime.strptime(
                                self.active_test.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"
                            ).date()
                            if self.active_test
                            else None
                        ),
                        "team": self.active_test.team if self.active_test else None,
                    },
                )

                test_result.save()

                return redirect("adjudicator_dashboard")
            except Exception as e:
                print(f"Error saving results: {e}")
                return False
        return False
