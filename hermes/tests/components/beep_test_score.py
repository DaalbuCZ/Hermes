from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult, ActiveTest
from tests.score_tables import calculate_score, calculate_beep_test_total_laps
from django.shortcuts import redirect
from datetime import datetime


class BeepTestScoreView(UnicornView):
    template_name = "unicorn/beep_test_score.html"
    profile_id = None
    level = ""
    laps = ""
    max_hr = ""
    total_laps = 0
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

    def calculate_beep_test_score(self):
        # Calculate score whenever inputs change
        if not self.profile_id:
            return

        try:
            profile = Profile.objects.get(id=self.profile_id)
            clean_level = self.clean_measurement(self.level)

            if clean_level is None:  # Level is required
                self.score = None
                self.total_laps = None
                return

            clean_laps = self.clean_measurement(self.laps) or 0
            self.total_laps = calculate_beep_test_total_laps(clean_level, clean_laps)

            if self.total_laps is not None:
                self.score = calculate_score(
                    profile.age, profile.gender, "beep_test", self.total_laps
                )
                print(f"Score calculated: {self.score}, Total Laps: {self.total_laps}")

        except (Profile.DoesNotExist, ValueError) as e:
            print(f"Error calculating score: {e}")
            self.score = None
            self.total_laps = None

    def update_profile(self, profile_id):
        # Update profile_id and load existing results if any
        self.profile_id = profile_id

        # Reset current values
        self.level = ""
        self.laps = ""
        self.max_hr = ""
        self.total_laps = 0
        self.score = 0

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)
                # Try to get existing test result
                test_result = TestResult.objects.filter(
                    profile=profile, active_test=self.active_test
                ).first()

                if test_result:
                    # Populate existing values if they exist
                    if test_result.beep_test_level is not None:
                        self.level = str(test_result.beep_test_level)
                    if test_result.beep_test_laps is not None:
                        self.laps = str(test_result.beep_test_laps)
                    else:
                        self.laps = ""
                    if test_result.max_hr is not None:
                        self.max_hr = str(test_result.max_hr)

                    # Calculate scores for existing values
                    self.calculate_beep_test_score()
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
        if not self.profile_id:
            return False

        try:
            profile = Profile.objects.get(id=self.profile_id)
            # Filter active test based on the profile's team
            self.active_test = ActiveTest.objects.filter(
                is_active=True, team=profile.team
            ).first()

            if not self.active_test:
                print(f"No active test found for team: {profile.team}")
                return False

            test_result, created = TestResult.objects.update_or_create(
                profile=profile,
                active_test=self.active_test,
                defaults={
                    "beep_test_level": self.clean_measurement(self.level),
                    "beep_test_laps": self.clean_measurement(self.laps) or 0,
                    "max_hr": self.clean_measurement(self.max_hr),
                    "beep_test_total_laps": self.total_laps,
                    "beep_test_score": calculate_score(
                        profile.age, profile.gender, "beep_test", self.total_laps
                    ),
                    "test_name": self.active_test.name if self.active_test else None,
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
