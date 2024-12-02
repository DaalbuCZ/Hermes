from django_unicorn.components import UnicornView
from tests.models import Profile, TestResult, ActiveTest
from tests.score_tables import quick_calculate
from django.shortcuts import redirect
from datetime import datetime


class HexagonScoreView(UnicornView):
    template_name = "unicorn/hexagon_score.html"
    profile_id = None
    time_cw = ""
    time_ccw = ""
    score_cw = 0
    score_ccw = 0
    profiles = []
    active_test = None
    previous_result = None
    warning_message = ""

    def mount(self):
        # Load profiles when component is initialized
        self.profiles = Profile.objects.all()
        self.active_test = ActiveTest.objects.filter(is_active=True).first()
        print("Component mounted with profiles:", len(self.profiles))

    def check_profile_warning(self, profile):
        # Check if profile needs a warning based on height
        if profile.height <= 150:
            self.warning_message = "Warning: This person is using the <strong>smaller 50cm</strong> hexagon"
        else:
            self.warning_message = (
                "Warning: This person is using the <strong>larger 60cm</strong> hexagon"
            )

    def clean_measurement(self, value):
        # Clean and validate measurement input
        if not value and value != 0:  # Handle empty strings and None
            return None
        try:
            cleaned = float(str(value).strip())
            return cleaned if cleaned >= 0 else None
        except (ValueError, TypeError):
            return None

    def calculate_hexagon_score(self):
        # Calculate scores whenever inputs change
        print(
            f"Calculating scores - Profile ID: {self.profile_id}, Time CW: {self.time_cw}, Time CCW: {self.time_ccw}"
        )

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)

                # Clean and validate inputs
                clean_time_cw = self.clean_measurement(self.time_cw)
                clean_time_ccw = self.clean_measurement(self.time_ccw)

                if clean_time_cw is not None:
                    self.score_cw = quick_calculate(
                        profile.age, profile.gender, "hexagon", clean_time_cw
                    )
                if clean_time_ccw is not None:
                    self.score_ccw = quick_calculate(
                        profile.age, profile.gender, "hexagon", clean_time_ccw
                    )
                print(f"Scores calculated: {self.score_cw}, {self.score_ccw}")
            except Profile.DoesNotExist as e:
                print(f"Error calculating scores: {e}")
                self.score_cw = 0
                self.score_ccw = 0
        else:
            print("Missing profile_id")

    def update_profile(self, profile_id):
        # Update profile_id and load existing results if any
        self.profile_id = profile_id

        # Reset current values
        self.time_cw = ""
        self.time_ccw = ""
        self.score_cw = 0
        self.score_ccw = 0

        if self.profile_id:
            try:
                profile = Profile.objects.get(id=self.profile_id)
                # Try to get existing test result
                test_result = TestResult.objects.filter(
                    profile=profile, active_test=self.active_test
                ).first()

                if test_result:
                    # Populate existing values if they exist
                    if test_result.hexagon_time_cw is not None:
                        self.time_cw = str(test_result.hexagon_time_cw)
                    if test_result.hexagon_time_ccw is not None:
                        self.time_ccw = str(test_result.hexagon_time_ccw)

                    # Calculate scores for existing values
                    self.calculate_hexagon_score()
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
                test_result, created = TestResult.objects.get_or_create(
                    profile=profile, active_test=self.active_test
                )

                # Clean and validate inputs before saving
                clean_time_cw = self.clean_measurement(self.time_cw)
                clean_time_ccw = self.clean_measurement(self.time_ccw)

                if clean_time_cw is not None:
                    test_result.hexagon_time_cw = clean_time_cw
                if clean_time_ccw is not None:
                    test_result.hexagon_time_ccw = clean_time_ccw

                test_result.hexagon_score = max(
                    self.score_cw, self.score_ccw
                )  # FIXME: Use the calculate score method instead

                # Save active test information if available
                if self.active_test:
                    test_result.active_test = self.active_test
                    test_result.test_name = self.active_test.name
                    try:
                        test_result.test_date = datetime.strptime(
                            self.active_test.created_at, "%Y-%m-%dT%H:%M:%S.%fZ"
                        ).date()  # Convert to date
                    except ValueError:
                        test_result.test_date = datetime.strptime(
                            self.active_test.created_at, "%Y-%m-%d %H:%M:%S"
                        ).date()  # Fallback format
                    test_result.team = self.active_test.team
                test_result.save()

                return redirect("adjudicator_dashboard")
            except Exception as e:
                print(f"Error saving results: {e}")
                return False
        return False
