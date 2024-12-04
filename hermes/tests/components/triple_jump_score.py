from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult, ActiveTest
from tests.score_tables import quick_calculate, calculate_score
from django.shortcuts import redirect
from datetime import datetime


class TripleJumpScoreView(UnicornView):
    template_name = "unicorn/triple_jump_score.html"
    profile_id = None
    distance_1 = ""
    distance_2 = ""
    distance_3 = ""
    score_1 = 0
    score_2 = 0
    score_3 = 0
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

    def calculate_triple_jump_score(self):
        # Calculate scores whenever inputs change
        print(
            f"Calculating scores - Profile ID: {self.profile_id}, Distances: {self.distance_1}, {self.distance_2}, {self.distance_3}"
        )

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)

                # Clean and validate inputs
                clean_distance_1 = self.clean_measurement(self.distance_1)
                clean_distance_2 = self.clean_measurement(self.distance_2)
                clean_distance_3 = self.clean_measurement(self.distance_3)

                if clean_distance_1 is not None:
                    self.score_1 = quick_calculate(
                        profile.age, profile.gender, "triple_jump", clean_distance_1
                    )
                if clean_distance_2 is not None:
                    self.score_2 = quick_calculate(
                        profile.age, profile.gender, "triple_jump", clean_distance_2
                    )
                if clean_distance_3 is not None:
                    self.score_3 = quick_calculate(
                        profile.age, profile.gender, "triple_jump", clean_distance_3
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
        # Update profile_id and load existing results if any
        self.profile_id = profile_id

        # Reset current values
        self.distance_1 = ""
        self.distance_2 = ""
        self.distance_3 = ""
        self.score_1 = 0
        self.score_2 = 0
        self.score_3 = 0

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)
                # Try to get existing test result
                test_result = TestResult.objects.filter(
                    profile=profile, active_test=self.active_test
                ).first()

                if test_result:
                    # Populate existing values if they exist
                    if test_result.triple_jump_distance_1 is not None:
                        self.distance_1 = str(test_result.triple_jump_distance_1)
                    if test_result.triple_jump_distance_2 is not None:
                        self.distance_2 = str(test_result.triple_jump_distance_2)
                    if test_result.triple_jump_distance_3 is not None:
                        self.distance_3 = str(test_result.triple_jump_distance_3)

                    # Calculate scores for existing values
                    self.calculate_triple_jump_score()
                # Find and display previous test results if they exist
                previous_results = (
                    TestResult.objects.filter(profile=profile)
                    .exclude(id=test_result.id)
                    .order_by("-test_date")
                )
                if previous_results.exists():
                    self.previous_result = previous_results.first()
                    print(
                        f"Previous Test Result - Time 1: {self.previous_result.ladder_time_1}, Time 2: {self.previous_result.ladder_time_2}, Score: {self.previous_result.ladder_score}"
                    )

            except Profile.DoesNotExist:
                print("Selected profile not found")

    def save_results(self):
        # Save the test results to the database
        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)
                # Ensure unique constraint on profile and active_test
                test_result, created = TestResult.objects.update_or_create(
                    profile=profile,
                    active_test=self.active_test,
                    defaults={
                        "triple_jump_distance_1": self.clean_measurement(
                            self.distance_1
                        ),
                        "triple_jump_distance_2": self.clean_measurement(
                            self.distance_2
                        ),
                        "triple_jump_distance_3": self.clean_measurement(
                            self.distance_3
                        ),
                        "triple_jump_score": calculate_score(
                            profile.age,
                            profile.gender,
                            "triple_jump",
                            self.clean_measurement(self.distance_1),
                            self.clean_measurement(self.distance_2),
                            self.clean_measurement(self.distance_3),
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
