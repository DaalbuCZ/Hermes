from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult, ActiveTest
from tests.score_tables import quick_calculate, calculate_score
from django.shortcuts import redirect
from django.core.exceptions import ValidationError
from datetime import datetime


class LadderScoreView(UnicornView):
    template_name = "unicorn/ladder_score.html"
    profile_id = None
    time_1 = ""
    time_2 = ""
    score_1 = 0
    score_2 = 0
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
            cleaned = float(str(value).strip())
            return cleaned if cleaned >= 0 else None
        except (ValueError, TypeError):
            return None

    def calculate_ladder_score(self):
        # Calculate scores whenever inputs change
        print(
            f"Calculating scores - Profile ID: {self.profile_id}, Time 1: {self.time_1}, Time 2: {self.time_2}"
        )

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)

                # Clean and validate inputs
                clean_time_1 = self.clean_measurement(self.time_1)
                clean_time_2 = self.clean_measurement(self.time_2)

                if clean_time_1 is not None:
                    self.score_1 = quick_calculate(
                        profile.age, profile.gender, "ladder", clean_time_1
                    )
                if clean_time_2 is not None:
                    self.score_2 = quick_calculate(
                        profile.age, profile.gender, "ladder", clean_time_2
                    )
                print(f"Scores calculated: {self.score_1}, {self.score_2}")
            except Profile.DoesNotExist as e:
                print(f"Error calculating scores: {e}")
                self.score_1 = self.score_2 = 0
        else:
            print("Missing profile_id")

    def update_profile(self, profile_id):
        self.profile_id = profile_id
        # Update profile_id and load existing results if any

        # Reset current values
        self.time_1 = ""
        self.time_2 = ""
        self.score_1 = 0
        self.score_2 = 0
        self.previous_result = None

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)
                # Try to get existing test result
                test_result = TestResult.objects.filter(
                    profile=profile, active_test=self.active_test
                ).first()

                if test_result:
                    # Populate existing values if they exist
                    if test_result.ladder_time_1 is not None:
                        self.time_1 = str(test_result.ladder_time_1)
                    if test_result.ladder_time_2 is not None:
                        self.time_2 = str(test_result.ladder_time_2)

                    # Calculate scores for existing values
                    self.calculate_ladder_score()

                # Find and display previous test results if they exist
                previous_results = (
                    TestResult.objects.filter(profile=profile)
                    .exclude(active_test=self.active_test)
                    .order_by("-test_date")
                )

                for result in previous_results:
                    if (
                        result.ladder_time_1 is not None
                        or result.ladder_time_2 is not None
                    ):
                        self.previous_result = result
                        print(
                            f"Previous Test Result - Time 1: {self.previous_result.ladder_time_1}, Time 2: {self.previous_result.ladder_time_2}, Score: {self.previous_result.ladder_score}"
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

                # Ensure unique constraint on profile and active_test
                test_result, created = TestResult.objects.update_or_create(
                    profile=profile,
                    active_test=self.active_test,
                    defaults={
                        "ladder_time_1": self.clean_measurement(self.time_1),
                        "ladder_time_2": self.clean_measurement(self.time_2),
                        "ladder_score": calculate_score(
                            profile.age,
                            profile.gender,
                            "ladder",
                            self.clean_measurement(self.time_1),
                            self.clean_measurement(self.time_2),
                        ),
                        "test_name": (
                            self.active_test.name if self.active_test else None
                        ),
                        "test_date": (
                            self.active_test.created_at.date()
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
